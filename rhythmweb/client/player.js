/*
 * Rhythmweb - a web site for your Rhythmbox.
 * Copyright (C) 2009 Michael Budde
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 */


function secsToStr(s, hour_disp) {
    var hours = Math.floor(s/3600);
    var mins = Math.floor((s-hours*3600)/60);
    var secs = Math.floor(s-hours*3600-mins*60);
    secs = (secs < 10) ? '0'+secs : secs;
    if (hours > 0 || hour_disp) {
        mins = (mins < 10) ? '0'+mins : mins;
        return [hours, mins, secs].join(':');
    }
    else
        return [mins, secs].join(':');
}


var PlayingInfo = new Class({
    Implements: [Options, Events],

    options: {
        elements: new Hash({
            title: 'title',
            artist: 'artist',
            album: 'album',
            stream: 'stream',
            time: 'time'
        }),
        onUpdate: $empty
    },

    initialize: function(options) {
        this.setOptions(options);
        this.state = null;
        this.duration = null;
        this.played = null;
        this.options.elements = new Hash(this.options.elements);
        this.options.elements = this.options.elements.map(
            function(value, key) {
                return $(value);
            }
        );
        this.tick.periodical(1000, this);
    },

    update: function(obj) {
        this.state = obj.state;
        if (this.state && this.state != 'stopped') {
            this.options.elements.each(function(elem, key) {
                if (key in obj) {
                    if (obj[key] == '')
                        elem.hide();
                    else
                        elem.show()
                            .getChildren('cite')
                            .set('text', obj[key]);
                }
            });
            this.options.elements.time.show();
            if (obj.title && obj.artist && document.title) {
                document.title = obj.title + ' - ' + obj.artist;
                if (this.state == 'paused')
                    document.title = '[Paused] ' + document.title;
            }
        }
        else { /* Playback is stopped */
            this.options.elements.each(function(elem) {
                elem.hide().getChildren('cite').set('text', '');
            });
            this.options.elements.title.show()
                .getChildren('cite').set('text', 'Not Playing');
            if (document.title)
                document.title = 'Rhythmweb';
        }
        if (obj.duration != null)
            this.duration = obj.duration;
        if (obj.played != null)
            this.played = obj.played;
        this.fireEvent('update');
    },

    tick: function() {
        if (this.state == 'stopped')
            this.options.elements.time.set('text', '');
        else {
            this.options.elements.time
                .set('text', this.formatTime());
        }
        if ((this.state == 'playing') &&
            ((this.duration == 0) ||
            (this.played < this.duration)))
            this.played += 1;
    },

    formatTime: function() {
        if (this.duration > 0) {
            if (this.duration > 3600)
                return secsToStr(this.played, true) + ' of ' +
                    secsToStr(this.duration);
            else
                return secsToStr(this.played) + ' of ' +
                    secsToStr(this.duration);
        }
        else
            return secsToStr(this.played);
    }
});

var Player = new Class({
    Implements: [Options, Events],

    options: {
        elements: null,
        onUpdated: $empty
    },

    initialize: function(options) {
        this.setOptions(options);
        this.controlRequest = new Request.JSON({
            url: 'control',
            onSuccess: this.handleRequest.bind(this)
        });
        this.playing_info = new PlayingInfo();
        this.timeout_id = null;
    },

    sendRequest: function(request) {
        if ($type(request) == 'string')
            this.controlRequest.send({data: {action: request}});
        else
            this.controlRequest.send({data: request});
    },

    handleRequest: function(obj) {
        if ('state' in obj) {
            this.state = obj['state'];
            if (this.state == 'playing')
                $('play').addClass('active');
            else
                $('play').removeClass('active');
        }
        this.playing_info.update(obj);
        if (this.timeout_id)
            this.timeout_id = $clear(this.timeout_id);
        if (this.state == 'playing') {
            var update_in = (this.playing_info.duration -
                this.playing_info.played)*1000;
            this.timeout_id = this.sendRequest.delay(
                update_in,
                this,
                'info'
            );
        }
        this.fireEvent('update');
    }
});

var Playlist = new Class({
    Implements: [Options, Events],

    options: {
        action: null,
        element: null,
        onUpdate: $empty
    },

    initialize: function(options) {
        this.setOptions(options);
        this.playlistRequest = new Request.JSON({
            url: 'control',
            data: {action: this.options.action},
            onSuccess: this.populate.bind(this)
        });
        this.options.element = $(this.options.element);
    },

    sendRequest: function() {
        this.playlistRequest.send();
    },

    populate: function(obj) {
        var tbody = this.options.element.getChildren('tbody')[0];
        tbody.empty();
        obj.each(function(entry) {
            var row = new Element('tr');
            new Element('td', {text: entry.title}).inject(row)
            new Element('td', {text: entry.artist}).inject(row)
            new Element('td', {text: entry.album}).inject(row)
            new Element('td', {text: secsToStr(entry.duration)}).inject(row)
            row.inject(tbody);
        });
        this.fireEvent('update');
    }
});

window.addEvent('domready', function() {
    Element.implement({
        show: function() {
            this.setStyle('display', '');
            return this;
        },
        hide: function() {
            this.setStyle('display', 'none');
            return this;
        }
    });

    var playlist = new Playlist({
        action: 'get-queue',
        element: $('playlist')
    });
    var player = new Player({
        onUpdate: playlist.sendRequest.bind(playlist)
    });
    $$('#toolbar button').addEvent('click', function() {
        player.sendRequest(this.value);
    });
    $$('#refresh a').addEvent('click', function() {
        player.sendRequest('info');
    });
    player.sendRequest('info');
});
