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


class RhythmwebInterface(object):

    def __init__(self, plugin):
        self.plugin = plugin
        self.player = plugin.player
        #self.shell = plugin.shell
        #self.db = plugin.db
        #self.queue = self.shell.props.queue_source
        #self.playlist_rows = self.queue.props.query_model

    def shutdown(self):
        del self.plugin
        del self.player
        #del self.shell
        #del self.db
        #del self.queue

    def html(self, start_response):
        response_headers = [('Content-type', 'text/html; charset=UTF-8')]
        start_response('200 OK', response_headers)
        player_html = open(self.plugin.find_file('player.html'))
        return player_html.read()

        # From __init__.RhythmwebServer
        #player = self.plugin.player
        #shell = self.plugin.shell
        #db = self.plugin.db
        #queue = shell.props.queue_source
        #playlist_rows = queue.props.query_model

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
                    #player.do_next()
                #elif action == 'prev':
                    #player.do_previous()
                #elif action == 'stop':
                    #player.stop()
                #elif action == 'vol-up':
                    #player.set_volume(player.get_volume() + 0.1)
                #elif action == 'vol-down':
                    #player.set_volume(player.get_volume() - 0.1)

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

    def play_pause(self):
        if not self.player.get_playing():
            if not self.player.get_playing_source():
                if self.playlist_rows.get_size() > 0:
                    self.player.play_entry(
                        iter(self.playlist_rows).next()[0],
                        queue)
            else:
                self.player.play()
        else:
            self.player.pause()

    def play_next(self):
        pass

    def play_prev(self):
        pass

    def volume_up(self):
        pass

    def volume_down(self):
        pass
