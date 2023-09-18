__author__ = 'mjw'
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask.ext.login import UserMixin, AnonymousUserMixin, current_user
from sqlalchemy.dialects.mysql import INTEGER, BLOB, DATETIME, TINYINT, TEXT, SMALLINT, VARCHAR
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from apiclient import discovery

from oauth2client import file
from oauth2client import client
from oauth2client import tools
from oauth2client.client import Credentials

import traceback
import sys
import os
import httplib2

from app.database import Base
from app import db, login_manager, DEBUG


#fixme move to config
ROLE_USER = 0
ROLE_SUBMITTER = 10
ROLE_APPROVER = 20
ROLE_ADMIN = 100
ROLE_GOD = 1000

#fixme move to config
PATH = os.environ.get('GAUDITPATH')
REDIRECT_URI = os.environ.get('REDIRECT_URI')
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), PATH + 'client_secrets.json')

if DEBUG:
    print "DEBUG: CLIENT_SECRETS=%s" % CLIENT_SECRETS
    print "DEBUG: redirect=%s" % REDIRECT_URI

FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS, scope=[
    'https://www.googleapis.com/auth/admin.reports.audit.readonly',
    'https://www.googleapis.com/auth/admin.reports.usage.readonly',
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://apps-apis.google.com/a/feeds/emailsettings/2.0/',
    'https://apps-apis.google.com/a/feeds/compliance/audit/',  # Email Audit API'
    'https://www.googleapis.com/auth/admin.directory.user.security',
    'https://www.googleapis.com/auth/admin.directory.userschema',
    'https://www.googleapis.com/auth/drive'  # needed for export of email to gdrive
], message=tools.message_if_missing(CLIENT_SECRETS), redirect_uri=REDIRECT_URI)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def isAnonymous(self):
        return True

    def isAuthenticated(self):
        return False

    def isSubmitter(self):
        return False

    def isApprover(self):
        return False

    def isAdmin(self):
        return False

    def isDisabled(self):
        false

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, Base):
    __tablename__ = 'users'
    __table_args__ = {
        'extend_existing': True
    }

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    role = db.Column(SMALLINT(), default=ROLE_USER)
    password_hash = db.Column(db.String(128))
    fName = db.Column(db.String(32), index=True)
    lName = db.Column(db.String(32), index=True)
    accountCreated = db.Column(DATETIME(), default=datetime.utcnow)
    lastLogin = db.Column(DATETIME(), index=True, default=datetime.utcnow)
    confirmed = db.Column(SMALLINT(), default=0, index=True)
    disabled = db.Column(SMALLINT(), default=0, index=True)
    # fixme typo
    acountApproved = db.Column(SMALLINT(), default=0, index=True)
    org = db.Column(db.String(32), index=True)
    googleAuth = db.Column(BLOB(), index=False)

    def approveAccount(self):
        self.acountApproved = 1
        db.session.merge(self)
        db.session.commit()

    def makeSubmitter(self, user):
        if self.role >= ROLE_ADMIN:
            user.role = ROLE_SUBMITTER
            db.session.merge(user)
            db.session.commit()
            return True

        return False

    def makeApprover(self, user):
        if self.role >= ROLE_ADMIN:
            user.role = ROLE_APPROVER
            db.session.merge(user)
            db.session.commit()

            return True

        return False

    def makeAdmin(self, user):
        if self.role >= ROLE_ADMIN:
            user.role = ROLE_ADMIN
            db.session.merge(user)
            db.session.commit()

            return True

        return False

    def disable(self, user):
        if self.role >= ROLE_ADMIN:
            user.disabled = 1
            db.session.merge(user)
            db.session.commit()

            return True

        return False

    @property
    def password(self):
        raise AttributeError("ERROR: Cannot read password")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha1', salt_length=8)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def isDisabled(self):
        if self.disabled == 0:
            return False

        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    def get_last_login(self):
        return self.lastLogin

    def isConfirmed(self):
        if self.confirmed == 1:
            return True

        return False

    def getRole(self):
        return self.role

    def isAdmin(self):
        return self.role >= ROLE_ADMIN

    def isApprover(self):
        return self.role >= ROLE_APPROVER

    def isSubmitter(self):
        return self.role >= ROLE_SUBMITTER

    def isAnonymous(self):
        return False

    def getAuthorizedDomains(self):
        # fixme eventually would like more than one domain
        pos = self.email.find("@")
        domain = self.email[pos + 1:]
        return [domain]

    def getGoogleAuthFile(self):
        pos = self.email.find("@")
        domain = self.email[pos + 1:]
        auth_file = PATH + "clients/" + domain + "/sample.dat"
        return auth_file

    def getDomain(self):
        # fixme eventually would like more than one domain
        pos = self.email.find("@")
        domain = self.email[pos + 1:]
        return domain

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            print "Token data = %s" % data

        except:
            traceback.print_exc(file=sys.stdout)
            return False

        if data.get('confirm') != self.id:
            print "ERROR: data.get confirm != self.id"
            return False

        self.confirmed = 1

        # fixme
        self.acountApproved = 1

        db.session.add(self)
        db.session.commit()

        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)

        except:
            traceback.print_exc(file=sys.stdout)
            return False

        if data.get('reset') != self.id:
            return False

        self.password = new_password
        db.session.add(self)
        db.session.flush()

        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token)

        except:
            traceback.print_exc(file=sys.stdout)
            return False

        if data.get('change_email') != self.id:
            return False

        new_email = data.get('new_email')

        if new_email is None:
            return False

        if self.query.filter_by(email=new_email).first() is not None:
            return False

        self.email = new_email
        db.session.add(self)
        db.session.flush()

        return True

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)

        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        print "in verify auth"
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token)

        except:
            traceback.print_exc(file=sys.stdout)
            return None

        return User.query.get(data['id'])

    def getEmail(self):
        return self.email

    def __unicode__(self):
        return self.email

    def hasGoogleAuth(self, domain=None):
        try:
            if domain is None:
                return len(self.getGoogleAuth()) > 16

            else:
                return len(self.query.filter_by(org=domain).first().getGoogleAuth()) > 16

        except TypeError:
            return False

    def getGoogleAuthByEmail(self, email):
        try:
            return self.query.filter_by(email=email).first().googleAuth

        except:
            return None

    def getGoogleAuthByDomain(self, domain):
        try:
            return self.query.filter_by(org=domain).first().googleAuth

        except AttributeError:
            return None

    def refreshGoogleAuth(self, domain=None):
        http = httplib2.Http()
        if domain:
            gauth = self.query.filter_by(org=domain).first().googleAuth

        else:
            gauth = self.googleAuth

        if gauth is None or len(gauth) < 16:
            if DEBUG:
                print "DEBUG: no gauth.. might be bad..."

            return None

        credentials = Credentials.new_from_json(gauth)
        credentials.refresh(http)
        jsonCreds = credentials.to_json()

        self.googleAuth = jsonCreds
        try:
            db.session.merge(self)
            db.session.commit()
            return jsonCreds

        except:
            traceback.print_exc(file=sys.stdout)
            db.session.rollback()
            return None

    def getGoogleAuth(self):
        return self.googleAuth

    def setGoogleAuthByEmail(self, email, data):
        user = self.query.filter_by(email=email).first()
        user.setGoogleAuth(data)

    def ingestLogins(self):
        gauth = self.getGoogleAuth()
        credentials = file.Credentials().new_from_json(gauth)
        http = httplib2.Http()
        credentials.refresh(http)
        http = credentials.authorize(http)

        service = discovery.build('admin', 'reports_v1', http=http)
        print "FiXME: ingestLogins"
        # gd = gDump(service)
        # data = gd.get_audit()
        # gd.load_audit(data)

    def setGoogleAuth(self, data):
        self.googleAuth = data

        try:
            db.session.merge(self)
            db.session.commit()
            return True

        except:
            print "FIXME: make except more specific"
            traceback.print_exc(file=sys.stdout)
            db.session.rollback()
            return False

    def getGoogleAuthorizeHTTP(self, domain=None):
        if domain is None:
            credentials = file.Credentials().new_from_json(self.googleAuth)

        else:
            auth = self.getGoogleAuthByDomain(domain)
            credentials = file.Credentials().new_from_json(auth)

        http = httplib2.Http()
        credentials.refresh(http)
        http = credentials.authorize(http)
        return http


def getGoogleAuthURL(clientAuthFile=''):
    auth_uri = FLOW.step1_get_authorize_url()
    print auth_uri
    return auth_uri


def getGoogleCredentials(auth_code):
    credentials = FLOW.step2_exchange(auth_code)
    http_auth = credentials.authorize(httplib2.Http())

    return credentials


def getGoogleCredentialsFromFile(clientAuthFile):
    storage = file.Storage(clientAuthFile)
    creds = storage.get()
    return str(creds.to_json())


# write credentials to a file
def writeGoogleCredentials(credentials, clientAuthFile):
    if DEBUG:
        print "DEBUG: Writing creds to %s" % clientAuthFile

    storage = file.Storage(clientAuthFile)
    storage.put(credentials)


def refreshGoogleFromFile(clientAuthFile):
    # credentials = Credentials.new_from_json(json)
    storage = file.Storage(clientAuthFile)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(FLOW, storage, flags)

    http = httplib2.Http()
    credentials.refresh(http)
    http = credentials.authorize(http)
