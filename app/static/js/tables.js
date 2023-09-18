/**
 * Created by mjw on 10/3/14.
 */

$(document).ready(function () {
    function CopyToClipboard(text) {
        var Copied = text.createTextRange();
        Copied.execCommand("Copy");
        alert("after copied " + text);
    }

    $('#example').dataTable(
        { "lengthMenu": [  100, 500, 1000 ],
           "stateSave": false,
            "ordering": true,
            "order": [[ 2, "desc" ]],
            "paging": true,
           "dom": '<"container" <"row" <"top" <"span2 pull-left"<"toolbar">> <"span4 pull-right"  f>>>>rt<"bottom"><"span2 pull-right" p><"clear">'
    });

    //for netid table
    $('#netidTable').dataTable(
        { "lengthMenu": [  100, 500, 1000 ],
            "stateSave": false,
            "ordering": true,
            "order": [[ 2, "desc" ]],
            "paging": true,
            "dom": '<"container" <"row" <"top" <"span2 pull-left"<"toolbar">> <"span4 pull-right"  f>>>>rt<"bottom"><"span2 pull-right" p><"clear">'
    });

    //mostActiveForeignCountriesTable
    $('#mostActiveForeignCountriesTable').dataTable(
        { "lengthMenu": [  100, 500, 1000 ],
            "stateSave": false,
            "ordering": true,
            "order": [[ 1, "desc" ]],
            "paging": true,
            "dom": '<"container" <"row" <"top" <"span2 pull-left"<"toolbar">> <"span4 pull-right"  f>>>>rt<"bottom"><"span2 pull-right" p><"clear">'
    });

    $('#mostDistinctTable').dataTable(
        { "lengthMenu": [  100, 500, 1000 ],
            "stateSave": false,
            "ordering": true,
            "order": [[ 2, "desc" ]],
            "paging": true,
            "dom": '<"container" <"row" <"top" <"span2 pull-left"<"toolbar">> <"span4 pull-right"  f>>>>rt<"bottom"><"span2 pull-right" p><"clear">'
    });

    $('#ipTable').dataTable(
        { "lengthMenu": [  100, 500, 1000 ],
            "stateSave": false,
            "ordering": true,
            "order": [[ 2, "desc" ]],
            "paging": true,
            "dom": '<"container" <"row" <"top" <"span2 pull-left"<"toolbar">> <"span4 pull-right"  f>>>>rt<"bottom"><"span2 pull-right" p><"clear">'
    });

    //this might be too general
    $(".dropdown-menu a").on('click', function (ev) {
        var actionObject = $(this).attr("actionObject");
        var action = $(this).text();
        var msg = "";

        if (actionObject.indexOf("netid") >= 0) {
            var netid = $(this).attr("netid");
            msg = action + ": " + netid;

            if(action.indexOf("Search") >= 0){
                $("#field").val("NetID");
                $("#search_value").val(netid);
                $("#navSearch").submit();
            }

        } else if (actionObject.indexOf("IP") >= 0) {
            var ip = $(this).attr("IP");

            if(action.indexOf("Search") >= 0){
                $("#field").val("IP");
                $("#search_value").val(ip);
                $("#navSearch").submit();
            }

        } else if (actionObject.indexOf("countryCode") >= 0) {
            alert("meh");
            var code = $(this).attr("countryCode");
            if(action.indexOf("Search") >= 0){
                $("#field").val("Country Code");
                $("#search_value").val(code);
                $("#navSearch").submit();
            }

        } else
            alert("You fucked up");

    });




});
