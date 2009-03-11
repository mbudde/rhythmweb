/*
 * Rhythmweb - a web site for your Rhythmbox.
 * Copyright (C) 2009 Michael Budde
 *
 * See COPYING for license information.
 */

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
    },

    parse: function(obj) {
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
        }
        else { /* Playback is stopped */
            this.options.elements.each(function(elem) {
                elem.hide().getChildren('cite').set('text', '');
            });
            this.options.elements.title.show()
                .getChildren('cite').set('text', 'Not Playing');
        }
        if (obj.duration != null)
            this.duration = obj.duration;
        if (obj.played != null)
            this.played = obj.played;
    },

    update: function() {
        if (this.state == 'stopped')
            this.options.elements.time.set('text', '');
        else {
            this.options.elements.time
                .set('text', this.timeToString());
        }
        if ((this.state == 'playing') &&
            ((this.duration == 0) ||
            (this.played < this.duration)))
            this.played += 1;
    },

    timeToString: function() {
        if (this.duration != 0)
            return this.secondsToPretty(this.played) + ' of ' +
                this.secondsToPretty(this.duration);
        else
            return this.secondsToPretty(this.played);
    },

    secondsToPretty: function(s) {
        var hours = Math.floor(s/60/60);
        var mins = Math.floor(s/60-hours*60);
        var secs = Math.floor(s-hours*60-mins*60);
        var secs = (secs < 10) ? "0"+secs : secs;
        if (hours > 0)
            return [hours, mins, secs].join(":");
        else
            return [mins, secs].join(":");
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
        this.playing_info.update.periodical(1000, this.playing_info);
        this.timeout_id = null;
    },

    sendRequest: function(request) {
        if (typeof(request) == 'string')
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
        this.playing_info.parse(obj);
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
