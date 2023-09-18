import traceback
import sys


from flask import render_template, redirect, session, url_for, request, g, Flask, make_response, jsonify
from flask.ext.login import current_user, login_required

from . import main
import reports
from app.models import domainAccountModel
from app.database import db
from app.main.auditModel import availableAuditFilesModel, emailExportAuditModel, authorizationFiles
from app import DEBUG
from app.auth.models import User


mydb = db(config_file="server.cfg")
myreports = reports.gAuditReports(mydb)


@main.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


@main.route('/', methods=['GET', 'POST'])
def index():
    data = []
    message = None

    if current_user.isAnonymous():
        return render_template('index.html')

    # FIXME: check google auth and refresh if necesses
    # elif current_user.isAdmin() and not current_user.hasGoogleAuth():
    #     message = "need to authorize google"
    #     return redirect(url_for('auth.authorizeGoogle'))

    return render_template('index.html')


@main.route('/mostActiveForeignIPs', methods=['GET', 'POST'])
@login_required
def mostActiveForeignIPs():
    authorizedDomain = current_user.getAuthorizedDomains()[0]
    message = "Most Active Foreign IPs"
    data = myreports.mostActiveForeignIPs(authorizedDomain)
    return render_template('ipTable.html', message=message, table=data)


@main.route('/mostActiveForeignCountries', methods=['GET', 'POST'])
@login_required
def mostActiveForeignCountries():
    authorizedDomain = current_user.getAuthorizedDomains()[0]
    message = "Most Active Foreign Countries"
    data = myreports.mostActiveForeignCountries(authorizedDomain)
    return render_template('mostActiveForeignCountries.html', message=message, table=data)


@main.route('/knownBad', methods=['GET', 'POST'])
@login_required
def knownBad():
    authorizedDomain = current_user.getAuthorizedDomains()[0]
    message = "Activity from known malicious addresses"
    data = []
    for (netid, domain, address) in myreports.knownBad(authorizedDomain):
        data.append([netid, domain, address])

    return render_template('editKnownBad.html', message=message, table=data)
    # return render_template('netidTable.html', message=message, table=data)


# fixme must be limited by user's domain
@main.route('/editKnownBad', methods=['GET', 'POST'])
@login_required
def editKnownBad():
    authorizedDomain = current_user.getAuthorizedDomains()[0]
    message = "Known Bad Addresses"
    data = []
    for (netid, domain, address) in myreports.knownBad(authorizedDomain):
        data.append([netid, domain, address])

    return render_template('editKnownBad.html', message=message, table=data)


# fixme must be limited by user's domain
@main.route('/mostDistinctCountries', methods=['GET', 'POST'])
@login_required
def mostDistinctCountries():
    authorizedDomain = current_user.getAuthorizedDomains()[0]
    message = "NetIDs with Logins from the Most Distinct Countries"
    data = myreports.mostDistinctCountries(authorizedDomain)
    return render_template('mostDistinctCountries.html', message=message, table=data)


# fixme must be limited by user's domain
@main.route('/emailForwards', methods=['GET', 'POST'])
@login_required
def emailForwards():
    authorizedDomain = current_user.getAuthorizedDomains()[0]
    message = "Email Forwards"
    data = []
    # data.append(myreports.mostDistinctCountries())
    return render_template('index.html', table=data)


# fixme must be limited by user's domain
@main.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    authorizedDomain = current_user.getAuthorizedDomains()[0]
    field = request.form['field']
    if field.find("NetID") == 0:
        message = "Results for "
        netid = request.form["search_value"].strip()
        message += " = %s" % netid
        data = myreports.searchNetID(str(netid), authorizedDomain)
        for line in data:
            print line
        return render_template('netidTable.html', message=message, table=data)

    elif field.find("IP") == 0:
        # FIXME Make it work for CIDR/range
        print "FIX ME: Add CIDR Range Option"
        message = "Results for IP "
        ip = request.form["search_value"].strip()
        message += " = %s" % ip
        data = myreports.searchIP(str(ip), authorizedDomain)
        return render_template('netidTable.html', message=message, table=data)

    elif field.find("countryCode") == 0:
        message = "Results for County Code (CC) "
        code = request.form["search_value"].strip()
        message += " = %s" % code
        data = myreports.searchCountryCode(str(code), authorizedDomain)
        return render_template('ccTable.html', message=message, table=data)


@main.route('/viewUserInfo', methods=['GET', 'POST'])
@login_required
def viewUserInfo():
    if current_user.isDisabled() or not current_user.isConfirmed():
        return render_template('index.html')

    # fixme
    # https://developers.google.com/admin-sdk/directory/v1/quickstart/quickstart-python
    return jsonify({"data": current_user.email})


@main.route('/viewUsers', methods=['GET', 'POST'])
@login_required
def viewUsers():
    if current_user.isDisabled() or not current_user.isConfirmed():
        return render_template('index.html')

    uList = []
    users = domainAccountModel().listAccounts(current_user)
    for u in users:
        uList.append(
            {
                "firstName": u.fName,
                "lastName": u.lName,
                "email": u.emailAddress,
                "lastLogin": u.lastLogin,
                "isSuspended": u.isSuspended,
                "isMailboxSetup": u.isMailboxSetup,
                "recordUpdated": u.recordUpdated
            }
        )

    return jsonify({"data": {"users": uList}})


@main.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')


@main.route('/uploadGPG', methods=['GET', 'POST'])
@login_required
def uploadGPG():
    # fixme
    print "Todo"


@main.route('/generateGPG', methods=['GET', 'POST'])
@login_required
def generateGPG():
    # fixme
    print "Todo"


# fixme must be limited by user's domain
@main.route('/viewAudits', methods=['GET', 'POST'])
@login_required
def viewAudits():
    authorizedDomain = current_user.getAuthorizedDomains()[0]
    if current_user.isDisabled() or not current_user.isConfirmed():
        # fixme - prod logout!
        return render_template('index.html')

    # fixme - need to add context menus.

    return render_template('emailTable.html')


@main.route('/viewAuditDownloads', methods=['GET', 'POST'])
@login_required
def viewAuditDownloads():
    print "Todo"


@main.route('/viewAuditRequests', methods=['GET', 'POST'])
@login_required
def viewAuditRequests():
    data = []

    if current_user.isDisabled() or not current_user.isConfirmed():
        return jsonify({"data": data})

    else:
        domain = current_user.getDomain()
        adminEmail = current_user.getEmail()
        print "creating emailexportaudit object for %s" % (adminEmail)

        myEmailAudits = emailExportAuditModel(domain, adminEmail, current_user)
        data = myEmailAudits.listAudits()

    return jsonify({"data": data})


@main.route('/viewAuditDetails', methods=['GET', 'POST'])
@login_required
def viewAuditDetails():
    data = []
    requestID = request.args.get("RequestID")
    if current_user.isDisabled() or not current_user.isConfirmed() or requestID is None:
        return jsonify({"data": data})

    else:
        domain = current_user.getDomain()
        adminEmail = current_user.getEmail()

        myEmailAudits = emailExportAuditModel(domain, adminEmail, current_user)
        data = myEmailAudits.listAuditDetails(requestID)

    return jsonify({"data": data})


@main.route('/viewAuditLinks', methods=['GET', 'POST'])
@login_required
def viewAuditLinks():
    data = []
    requestID = request.args.get("RequestID")
    if current_user.isDisabled() or not current_user.isConfirmed() or requestID is None:
        return jsonify({"data": data})

    else:
        domain = current_user.getDomain()
        adminEmail = current_user.getEmail()

        myEmailAudits = emailExportAuditModel(domain, adminEmail, current_user)
        data = myEmailAudits.getGoogleLinks(requestID)

    return jsonify({"data": data})


@main.route('/viewAuditRequestsByAdminAddress', methods=['GET', 'POST'])
@login_required
def viewAuditRequestsByAdminAddress(targetAdminEmail=None):
    data = []
    if current_user.isDisabled() or not current_user.isConfirmed() or request.args.get("targetAdminEmail") is None:
        return jsonify({"data": data})

    else:
        targetAdminEmail = str(request.args.get("targetAdminEmail")).strip()
        print "targetAdminEmail = %s" % targetAdminEmail

        domain = current_user.getDomain()
        adminEmail = current_user.getEmail()

        myEmailAudits = emailExportAuditModel(domain, adminEmail)
        data = myEmailAudits.listAuditsByAdminAddress(targetAdminEmail)

    return jsonify({"data": data})


@main.route('/viewAuditRequestsByEmailAddress', methods=['GET', 'POST'])
@login_required
def viewAuditRequestsByEmailAddress(targetEmail=None):
    data = []

    if current_user.isDisabled() or not current_user.isConfirmed() or request.args.get("targetEmail") is None:
        return jsonify({"data": data})

    else:
        targetEmail = str(request.args.get("targetEmail")).strip()
        domain = current_user.getDomain()
        adminEmail = current_user.getEmail()

        myEmailAudits = emailExportAuditModel(domain, adminEmail)
        data = myEmailAudits.listAuditsByAddress(targetEmail)

    return jsonify({"data": data})


@main.route('/retainEmail', methods=['GET', 'POST'])
@login_required
def retainEmail():
    if current_user.isDisabled() or not current_user.isConfirmed():
        # fixme: prod logout
        return render_template('index.html')

    if request.method == 'POST':
        # print "request Data = %s" % request.get_data()
        data = request.values
        domain = current_user.getDomain()
        adminEmail = current_user.getEmail()

        myEmailAudits = emailExportAuditModel(domain, adminEmail)

        try:
            username = startDate = endDate = query = None
            headersOnly = includeDeleted = False
            emailAddress = data["emailAddress"]
            username = emailAddress[:emailAddress.find("@")]
            startDate = data["startDate"]
            endDate = data["endDate"]

            # configure the dates to be the full and complete date with time
            if len(startDate) > 4:
                startDate = startDate + " 00:00"

            else:
                startDate = None

            if len(endDate) > 4:
                endDate = endDate + " 23:59"

            else:
                endDate = None

            # fixme what if includeDeleted is false?
            if data.has_key("includeDeleted") is True:
                includeDeleted = True

            else:
                if data.has_key("query") is True:
                    query = data['query']

            if data.has_key("headersOnly") is True:
                headersOnly = data["headersOnly"]
                if headersOnly is not None:
                    headersOnly = True
                else:
                    headersOnly = False

            print "Creating Audit for %s, %s, %s, %s, %s, %s" % \
                  (username, startDate, endDate, query, includeDeleted, headersOnly)
            myEmailAudits.exportUserMailbox(username, startDate, endDate, query, includeDeleted, headersOnly)
            redirect("/viewAudits")

        except:
            traceback.print_exc(file=sys.stderr)

    return render_template('retainEmail.html')


@main.route('/getEmailAccounts', methods=['GET', 'POST'])
@login_required
def getEmailAccounts():
    if current_user.isDisabled() or not current_user.isConfirmed():
        return render_template('index.html')

    myDomainAccounts = domainAccountModel()
    if request.args.get("searchField") == "NetID":
        targetUser = str(request.args.get("searchValue")).strip()
        data = myDomainAccounts.getAccountByUsername(current_user, targetUser)
        r = {"data": data}
        print r
        return jsonify(r)

    elif request.args.get("searchField") == "lName":
        targetFamily = str(request.args.get("searchValue")).strip()
        data = myDomainAccounts.getAccountByFamilyName(current_user, targetFamily)
        r = {"data": data}
        print r
        return jsonify(r)

    else:
        return jsonify({"data": []})


@main.route('/ingestLogins', methods=['GET', 'POST'])
@login_required
def ingestLogins():
    domain = current_user.getDomain()
    gauth = User().getGoogleAuthByDomain(domain=domain)
    if gauth is None:
        return jsonify({"Status": "Error"})

    else:
        current_user.ingestLogins()

        return jsonify({"Status": "Success"})

















