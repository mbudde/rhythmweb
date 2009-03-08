$(function() {
    $("#playing").hide();

    function getelem(expr, context) {
        elem = $(expr, context);
        if (elem.length == 0) elem = null;
        return elem;
    }
        
    function update_info(data) {
        if (title = getelem("title", data))
            $("#playing > #title > cite").html(title.text());
        if (artist = getelem("artist", data))
            $("#playing > #artist > cite").html(artist.text()).show()
        else
            $("#playing > #artist").hide();
        if (album = getelem("album", data))
            $("#playing > #album > cite").html(album.text()).show()
        else
            $("#playing > #album").hide();
        $("#playing").show("slow");
    }

    $("#toolbar button").click(function(e) {
        $.post(
            "control",
            {action: $(this).attr("value")},
            update_info,
            "xml"
        );
    });
});
