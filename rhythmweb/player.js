/*
 * Rhythmweb - a web site for your Rhythmbox.
 * Copyright (C) 2009 Michael Budde
 *
 * See COPYING for license information.
 */

info = {};
info["played"] = null;
info["duration"] = null;
info["state"] = null;
info["timeout_id"] = null;

function getelem(expr, context) {
    var elem = $(expr, context);
    return (elem.length == 0) ? null : elem;
}

function secs2str(s) {
    var hours = Math.floor(s/60/60);
    var mins = Math.floor(s/60-hours*60);
    var secs = Math.floor(s-hours*60-mins*60);
    var secs = (secs < 10) ? "0"+secs : secs;
    if (hours > 0)
        return [hours, mins, secs].join(":");
    else
        return [mins, secs].join(":");
}

function control(act, callback) {
    if (!callback)
        var callback = update_info
    $.post("control", {action: act}, callback, "xml");
}

function update_playing_time() {
    if (info["state"] == "stopped")
        $("#playingtime").html("");
    else {
        if (info["duration"] != 0) { /* Playing a song */
            if (info["played"] <= info["duration"])
                $("#playingtime").html(
                    secs2str(info["played"]) + " of " +
                    secs2str(info["duration"])
                );
        }
        else { /* Playing a stream */
            $("#playingtime").html(secs2str(info["played"]));
        }
        if (info["state"] == "playing") 
            info["played"] += 1;
    }
}
    
function update_info(data) {
    if (state = getelem("state", data)) {
        info["state"] = state.text();
        if (state.text() == "playing")
            $("#toolbar #play").addClass("active");
        if (state.text() == "paused" || state.text() == "stopped")
            $("#toolbar #play").removeClass("active");
    }
    if (info["state"] != "stopped") {
        var tags = ["title", "artist", "album", "stream"];
        for (var i in tags) {
            var elem = getelem(tags[i], data);
            if (elem) {
                if (elem.text() != "")
                    $("#"+tags[i]+" > cite").html(elem.text()).parent().show();
                else
                    $("#"+tags[i]).hide();
            }
        }
        var duration = getelem("duration", data);
        if (duration) {
            if (info["timeout_id"])
                clearTimeout(info["timeout_id"]);
            info["duration"] = parseInt(duration.text());
            if (info["duration"] != 0) {
                /* We are playing a song so update info when the song ends */
                var finish_time = getelem("finish_time", data);
                var finish = new Date(Date.parse(finish_time.text()+" UTC"));
                var now = new Date();
                var remaining = Math.floor((finish - now)/1000);
                info["played"] = info["duration"] - remaining;
                if (info["state"] == "playing")
                    info["timeout_id"] = setTimeout(function() {
                        control("info");
                    }, remaining*1000);
            }
            else {
                /* We are playing a stream; update info again in one minute. */
                var played = getelem("played", data);
                var played_time = getelem("played_time", data);
                if (played && played_time) {
                    played = parseInt(played.text());
                    played_time = new Date(Date.parse(played_time.text()+" UTC"));
                    var now = new Date();
                    var corr_time = Math.floor((now - played_time)/1000);
                    played += corr_time;
                }
                else {
                    played = 0;
                }
                info["played"] = played;
                info["timeout_id"] = setTimeout(function() {
                    control("info");
                }, 60000);
            }
        }
    }
    else { /* Player is stopped. */
        $("#playing cite").html("").parent().hide();
        $("#title cite").html("Not Playing").parent().show();
    }
}

$(function() {
    $("#artist, #album, #stream").hide();
    control("info");

    $("#toolbar button").click(function() {
        control($(this).attr("value"));
    });
    $("#refresh").click(function() {control("info");});

    setInterval(update_playing_time, 1000);
});
