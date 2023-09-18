/**
 * Created by mjw on 2/5/15.
 */
$(document).ready(function () {
    $('.retainSearch').on('submit', function () {
        var searchField = $('#searchField').val();
        var searchValue = $('#searchValue').val();

        //destroy the table if it already exists
        var oTable = $('#emailRetentionTable').dataTable();
        if (oTable != null)
            oTable.fnDestroy();

        $('#emailRetentionTable').dataTable({
            // "order": [[1, 'asc']]
            "fnInitComplete": function () {
                var rows = this.fnGetNodes();
                for (var i = 0; i < rows.length; i++) {
                    //create magical buttons
                    var emailAddr = rows[i].cells[0].innerHTML;
                    var pre = "<div class=\"btn-group\"><button type=\"button\" data-content=\"" + emailAddr + "\"" +
                        " class=\"btn btn-default\"data-toggle=\"dropdown\"> ";
                    var post = " </button><ul class=\"dropdown-menu\" role=\"menu\">" +
                        "<li><a actionObject=\"view\" id=\"viewRequests\" href=\"#\">View Requests</a></li>" +
                        "<li><a actionObject=\"create\" id=\"createRequest\" href=\"#\">Retain Email</a></li>" +
                        "<li class=\"disabled\"><a actionObject=\"viewMonitors\" id=\"viewMonitors\" " +
                        "href=\"#\">View Monitors</a></li><li class=\"disabled\">" +
                        "<a actionObject=\"createMonitor\" id=\"createMonitor\" href=\"#\">Create Monitor</a>" +
                        "</li></ul></div></td> ";

                    rows[i].cells[0].innerHTML = pre + emailAddr + post;
                    rows[i].cells[0].data = emailAddr;

                    $(".dropdown-menu").on('click', function (ev) {
                        //fixme
                        //alert($(this).html());
                    });

                    $(".dropdown-menu").on('mouseover', function (ev) {
                        emailAddr = $(this).parent().children(".btn").html();
                    });

                    $(".dropdown-menu a").on('click', function (ev) {
                        var actionObject = $(this).attr("actionObject");
                        var msg = "";

                        if (actionObject.indexOf("view") >= 0) {
                            msg = "fixme"
                            //switch on netid actions

                        } else if (actionObject.indexOf("create") >= 0) {
                            $("#username").val(emailAddr).text(emailAddr);
                            $("#emailAddress").val(emailAddr).text(emailAddr);
                            $("#myModal").modal("show");

                        } else
                            alert("You fucked up");
                    });
                } //end of for each row
            },
            "info": false,
            "dom": '<"container" <"row" <"top" <"span2 pull-left"<"toolbar">> <"span4 pull-right"  ' +
            'f>>>>rt<"bottom"><"span2 pull-right" p><"clear">',
            "search": true,
            "ajax": "/getEmailAccounts?searchField=" + searchField + "&searchValue=" + searchValue,
            "columns": [
                {"data": "email"},
                {"data": "fName"},
                {"data": "lName"},
                {"data": "isMailboxSetup", visible: false},
                {"data": "isSuspended", visible: false},
                {"data": "lastLogin"}]
        });
        $('#searchResults').removeClass("hidden").addClass("show");
        return false;
    });

    $('#myButton').on('click', function () {
        var data = $("#retainEmailForm").serialize();
        $.post("/retainEmail", data);
        $("#myModal").hide();
        $(location).attr('href', "/viewAudits");
    });

    $('#emailAuditTable').dataTable( {
        "search":   true,
        "ajax": "/viewAuditRequests",
        "pageLength": 100,
        "ordering": true,
        "order": [[ 0, "desc" ]],
        //fixme: add name
        "columns": [
            { "data": "requestID", visible: true },
            { "data": "requestDate", visible: true },
            { "data": "fName" },
            { "data": "lName" },
            { "data": "requestor", visible: false},
            { "data": "emailAddress" },
            { "data": "beginDate", visible: false },
            { "data": "endDate", visible: false },
            { "data": "completedDate", visible: false},
            { "data": "status"},
            { "data": "contentType", visible: false},
            { "data": "includeDeleted", visible: false}],
        "fnInitComplete": function () {
            var rows = this.fnGetNodes();
            for (var i = 0; i < rows.length; i++) {
                //create magical buttons
                var original = rows[i].cells[0].innerHTML;
                var pre = "<div class='btn-group'><button type='button' data-content='" + original +
                    "' class='btn btn-default idButton' data-toggle='dropdown'> ";
                var post = " <span class='caret'> </span></button><ul class='dropdown-menu' role='menu'>" +
                    "<li><a actionObject='view' id='' href='/viewAuditDetails?RequestID=" + original +
                    "'>View Details</a></li><li  class='disabled'><a actionObject='create' id='downloadAudit' href='#'>"+
                    "Download</a></li><li  class='disabled'><a href='#'>View Google Links</a></li> " +
                    "<li class='disabled'><a href='#'>Export to gDrive</a></li></ul></div></td> ";

                rows[i].cells[0].innerHTML = pre + original + post;
                rows[i].cells[0].data = original;
            }
        }
    });

    $(".idButton").on('mouseover', function () {
        //var id = this.text();
        alert("idButton");
        return false;

        $.get( "viewAuditDetails?RequestID=" + id, function( data ) {
            $(".result").html(data);
            var str = JSON.stringify(data, undefined, 2); // indentation level = 2
            alert(str);
        });
    });

    $('#emailAuditTable tbody').on('mouseover', 'tr', function () {
        var id = $('td', this).eq(0).text();
        var status = $('td', this).eq(5).text();
        //alert( "HOVER: Request " + id + " has status " + status );
        //$.get( "viewAuditDetails?RequestID=" + id, function( data ) {
            //$( ".result" ).html( data );
          //  alert($( ".result" ).html( data ));
        //});

    });


    $('a.yourlink').click(function(e) {
        e.preventDefault();
        var requestID= "1234";
        var baseURL = "/viewAuditLinks?RequestID=";
        var links = [];

        $.get(baseURL + requestID, function( data ) {
            $.parseJSON(data);
            //append links

        });

        //for(x in links){
            //window.open('mysite.com/file1');
        //}

    });


    $('#emailAuditTable tbody').on('click', 'tr', function () {
        var id = $('td', this).eq(0).text();
        var status =  $('td', this).eq(5).text();

        //alert( "Request " + id + " has status " + status );

        //if status is COMPLETE - want to be able to download
        //
    });

});