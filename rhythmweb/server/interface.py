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

import time;
from xml.dom.minidom import getDOMImplementation
from socket import gethostname

import rhythmdb

import json

class RhythmwebInterface(object):
    """Takes care of sending HTML and JSON to the client and handle
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
        """Send player HTML to the client. The client must send a
        Ajax request to get info about playing song, ect."""
        headers = [('Content-type', 'text/html; charset=UTF-8')]
        start_response('200 OK', headers)
        player_html = open(self.plugin.find_file('client/player.html'))
        return player_html.read() % {'hostname': gethostname()}

    def handle_action(self, action, start_response):
        """Handle an Ajax request forwarded to us from the server.
        Depending on the action we might respond with some info in
        JSON format."""
        response_obj = None
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
        elif action == 'get-queue':
            response_obj = self.get_queue()

        headers = [('Content-type', 'application/json; charset=UTF-8')]
        start_response('200 OK', headers)
        if response_obj == None:
            response_obj = self.player_info(action)
        return json.write(response_obj)

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
            info['played'] = played

        if action in ['vol-up', 'vol-down', 'info']:
            info['volume'] = self.player.get_volume()

        return info

    def get_queue(self):
        db = self.plugin.db
        queue_source = self.plugin.shell.props.queue_source
        queue_rows = queue_source.props.query_model
        queue = []
        for row in queue_rows:
            queue_entry = row[0]
            entry = {}
            entry['title'] = db.entry_get(queue_entry,
                                          rhythmdb.PROP_TITLE)
            entry['artist'] = db.entry_get(queue_entry,
                                           rhythmdb.PROP_ARTIST)
            entry['album'] = db.entry_get(queue_entry,
                                          rhythmdb.PROP_ALBUM)
            queue.append(entry)
        return queue

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

