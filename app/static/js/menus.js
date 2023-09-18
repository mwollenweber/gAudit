$(document).ready(function () {
    $(".dropdown-menu a").on('click', function (ev) {
        var actionObject = $(this).attr("actionObject");
        var action = $(this).text();
        var msg = "";

        if (actionObject.indexOf("netid") >= 0) {
            var netid = $(this).attr("netid");
            msg = action + ": " + netid;

            //switch on netid actions

        } else if (actionObject.indexOf("ip") >= 0) {
            var ip = $(this).attr("ip");
            alert("ici");
            msg = action + ": " + ip;

            //switch on ip actions

        } else
            alert("You fucked up");

        //alert(msg);
        console.write(msg);

    });
});