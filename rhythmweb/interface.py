#
# Rhythmweb - a web site for your Rhythmbox.
# Copyright (C) 2009 Michael Budde
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from datetime import datetime, timedelta
from xml.dom.minidom import getDOMImplementation
from socket import gethostname

import rhythmdb

class RhythmwebInterface(object):
    """Take care of sending html and xml to the client and handle
    the Ajax requests the client sends."""

    def __init__(self, plugin):
        self.plugin = plugin
        self.player = plugin.player
        self.db = plugin.db

    def shutdown(self):
        del self.plugin
        del self.player
        del self.db

    def send(self, start_response):
        """Send player html to the client. The client must send a
        Ajax request to get info about playing song ect."""
        headers = [('Content-type', 'text/html; charset=UTF-8')]
        start_response('200 OK', headers)
        player_html = open(self.plugin.find_file('player.html'))
        return player_html.read() % {'hostname': gethostname()}

    def handle_action(self, action, start_response):
        """Handle an Ajax request forwarded to us from the server.
        Depending on the action we might respond with some info in
        xml format."""
        if action == 'play':
            self.play_pause()
        elif action == 'next':
            self.play_next()
        elif action == 'prev':
            self.play_prev()
        elif action == 'vol-up':
            self.volume_up()
        elif action == 'vol-down':
            self.volume_down()

        headers = [('Content-type', 'text/xml; charset=UTF-8')]
        start_response('200 OK', headers)
        info = self.player_info(action)
        return dict2xml(info, 'info')

    def player_info(self, action=None):
        """Gather info about the playing song and the state of
        the player. The gathered info depends on the action."""
        info = {}
        playing = self.player.get_playing_entry()
        if playing:
            if self.player.get_playing():
                info['state'] = 'playing'
            else:
                info['state'] = 'paused'
        else:
            info['state'] = 'stopped'

        if playing and (action in ['next', 'prev', 'play', 'info']):
            info['artist'] = self.db.entry_get(playing, rhythmdb.PROP_ARTIST)
            info['album'] = self.db.entry_get(playing, rhythmdb.PROP_ALBUM)
            info['title'] = self.db.entry_get(playing, rhythmdb.PROP_TITLE)
            stream_title = \
                self.db.entry_request_extra_metadata(
                        playing, 'rb:stream-song-title'
                )
            if stream_title:
                info['stream'] = info['title']
                info['title'] = stream_title
                if not info['artist']:
                    info['artist'] = \
                        self.db.entry_request_extra_metadata(
                            playing, 'rb:stream-song-artist'
                        )
                if not info['album']:
                    info['album'] = \
                        self.db.entry_request_extra_metadata(
                            playing, 'rb:stream-song-album'
                        )
            info['duration'] = self.player.get_playing_song_duration()
            # FIXME: This is weird. get_playing_time() seems to return
            # the playing time of the previous song even though
            # everything else has been updated.
            if action in ['next', 'prev']:
                played = 0
            else:
                played = self.player.get_playing_time()
            if info['duration'] == 0:
                info['played'] = played
                info['played_time'] = datetime.utcnow().ctime()
            else:
                finish_time = datetime.utcnow() + \
                        timedelta(seconds=info['duration']-played)
                info['finish_time'] = finish_time.ctime()

        if action in ['vol-up', 'vol-down', 'info']:
            info['volume'] = self.player.get_volume()

        return info

    def play_pause(self):
        self.player.playpause()

    def play_next(self):
        self.player.do_next()

    def play_prev(self):
        self.player.do_previous()

    def volume_up(self):
        self.player.set_volume_relative(0.1)

    def volume_down(self):
        self.player.set_volume_relative(-0.1)


def dict2xml(d, rootname):
    """Return a DOM representation of a dictionary with the root
    element named accordingly to rootname."""
    dom = getDOMImplementation().createDocument(None, rootname, None)
    root = dom.documentElement

    def dict2dom(root, d):
        for key, val in d.iteritems():
            elem = dom.createElement(key)
            if type(val) == dict:
                dict2elem(elem, val)
            elif val != None:
                elem.appendChild(dom.createTextNode(str(val)))
            root.appendChild(elem)

    dict2dom(root, d)
    xml = dom.toxml()
    dom.unlink()
    return xml
        

        # From __init__.RhythmwebServer

        ## handle any action
        #if environ['REQUEST_METHOD'] == 'POST':
            #params = parse_post(environ)
            #if 'action' in params:
                #action = params['action'][0]
                #if action == 'play':
                    #if not player.get_playing():
                        #if not player.get_playing_source():
                            #if playlist_rows.get_size() > 0:
                                #player.play_entry(iter(playlist_rows).next()[0],
                                                  #queue)
                        #else:
                            #player.play()
                    #else:
                        #player.pause()
                #elif action == 'pause':
                    #player.pause()
                #elif action == 'next':
                #elif action == 'prev':
                #elif action == 'stop':
                #elif action == 'vol-up':
                #elif action == 'vol-down':

            #return return_redirect('/', environ, response)

        ## generate the playing headline
        #title = 'Rhythmweb'
        #playing = '<span id="not-playing">Not playing</span>'
        #if self.stream or self.title:
            #playing = ''
            #title = ''
            #if self.title:
                #playing = '<cite id="title">%s</cite>' % self.title
                #title = self.title
            #if self.artist:
                #playing = ('%s by <cite id="artist">%s</cite>' %
                           #(playing, self.artist))
                #title = '%s by %s' % (title, self.artist)
            #if self.album:
                #playing = ('%s from <cite id="album">%s</cite>' %
                           #(playing, self.album))
                #title = '%s from %s' % (title, self.album)
            #if self.stream:
                #if playing:
                    #playing = ('%s <cite id="stream">(%s)</cite>' %
                               #(playing, self.stream))
                    #title = '%s (%s)' % (title, self.album)
                #else:
                    #playing = self.stream
                    #title = self.stream

        ## generate the playlist
        #playlist = '<tr><td colspan="3">Playlist is empty</td></tr>'
        #if playlist_rows.get_size() > 0:
            #playlist = cStringIO.StringIO()
            #for row in playlist_rows:
                #entry = row[0]
                #playlist.write('<tr><td>')
                #playlist.write(db.entry_get(entry, rhythmdb.PROP_TITLE))
                #playlist.write('</td><td>')
                #playlist.write(db.entry_get(entry, rhythmdb.PROP_ARTIST))
                #playlist.write('</td><td>')
                #playlist.write(db.entry_get(entry, rhythmdb.PROP_ALBUM))
                #playlist.write('</td></tr>')
            #playlist = playlist.getvalue()

        ## handle player state
        #play = ''
        #refresh = ''
        #if player.get_playing():
            #play = 'class="active"'
            #duration = player.get_playing_song_duration()
            #if duration > 0:
                #refresh = duration - player.get_playing_time() + 2
                #refresh = '<meta http-equiv="refresh" content="%s">' % refresh

        ## display the page
        #player_html = open(resolve_path('player.html'))
        #response_headers = [('Content-type','text/html; charset=UTF-8')]
        #response('200 OK', response_headers)
        #return player_html.read() % { 'title': title,
                                      #'refresh': refresh,
                                      #'play': play,
                                      #'playing': playing,
                                      #'playlist': playlist }
