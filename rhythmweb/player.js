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
        this.duration = obj.duration;
        if (obj.finish_time && this.duration) {
            var now = new Date();
            var remaining = obj.finish_time - now.getTime();
            remaining = (remaining/1000).round();
            this.played = this.duration - remaining;
        }
        else if (obj.played && obj.played_time) {
            var now = new Date();
            var corr_time = now.getTime() - obj.played_time;
            corr_time = (corr_time/1000).round();
            this.played = obj.played + corr_time;
        }
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

    var player = new Player();
    $$('#toolbar button').addEvent('click', function() {
        player.sendRequest(this.value);
    });
    $$('#refresh a').addEvent('click', function() {
        player.sendRequest('info');
    });
    player.sendRequest('info');
});
