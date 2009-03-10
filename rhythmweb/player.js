/*
 Rhythmweb - a web site for your Rhythmbox.
 Copyright (C) 2009 Michael Budde

 See COPYING for license information.
*/

info = {};
info["played"] = null;
info["duration"] = null;
info["state"] = null;
info["timeout_id"] = null;

function getelem(expr, context) {
    var elem = $(expr, context);
    if (elem.length == 0) elem = null;
    return elem;
}

function secs2str(s) {
    var hours = Math.floor(s/60/60);
    var mins = Math.floor(s/60-hours*60);
    var secs = Math.floor(s-hours*60-mins*60);
    var secs = (secs < 10) ? "0"+secs : secs;
    if (hours > 0)
        return [hours, mins, secs].join(":")
    else
        return [mins, secs].join(":");
}

function update_playing_time() {
    if (info["state"] == "stopped")
        $("#playingtime").html("")
    else {
        if (info["played"] <= info["duration"])
            $("#playingtime").html(
                secs2str(info["played"]) + " of " +
                secs2str(info["duration"])
            );
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
        if (title = getelem("title", data))
            $("#title > cite").html(title.text());
        if (artist = getelem("artist", data))
            $("#artist > cite").html(artist.text()).parent().show()
        else
            $("#artist").hide();
        if (album = getelem("album", data))
            $("#album > cite").html(album.text()).parent().show()
        else
            $("#album").hide();
        if (stream = getelem("stream", data))
            $("#stream > cite").html("("+stream.text()+")").parent().show()
        else
            $("#stream").hide();
    } else {
        $("#playing cite").html("").parent().hide();
        $("#title cite").html("Not Playing").parent().show();
    }
    if (duration = getelem("duration", data))
        info["duration"] = parseInt(duration.text());
    if (finish_time = getelem("finish_time", data)) {
        var finish = new Date(Date.parse(finish_time.text()+" UTC"));
        var now = new Date();
        var remaining = Math.floor((finish - now)/1000);
        info["played"] = info["duration"] - remaining;
        if (info["timeout_id"])
            clearTimeout(info["timeout_id"]);
        if (info["state"] == "playing")
            info["timeout_id"] = setTimeout(function() {
                $.post("control", {action: "info"}, update_info, "xml");
            }, remaining*1000);
    }
}

$(function() {
    $("#artist, #album, #stream").hide();
    $.post("control", {action: "info"}, update_info, "xml");

    $("#toolbar button").click(function(e) {
        $.post(
            "control",
            {action: $(this).attr("value")},
            update_info,
            "xml"
        );
    });

    setInterval(update_playing_time, 1000);
});
