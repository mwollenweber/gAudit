import tempfile

from flask import render_template, redirect, request, url_for, flash, jsonify
from flask.ext.login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import LoginForm, RegistrationForm, ChangeEmailForm, PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm, ChangePasswordForm
from models import db, User, getGoogleAuthURL, getGoogleCredentials, writeGoogleCredentials, FLOW, getGoogleCredentialsFromFile, refreshGoogleFromFile

from app import DEBUG
from app.myEmail import send_email


#fixme
@auth.before_app_request
def before_request():
    if current_user.is_authenticated():
        if not current_user.isConfirmed() \
                and request.endpoint[:5] != 'auth.':

            db.session.flush()
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and user.verify_password(form.password.data) and user.isDisabled() is False:
            login_user(user, form.remember_me.data)
            current_user.refreshGoogleAuth()
            return redirect(request.args.get('next') or url_for('main.index'))

        flash("Invalid username or password")

    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data, lName = form.lName.data,
                    fName = form.fName.data, confirmed= 0)
        db.session.merge(user)
        db.session.flush()
        db.session.commit()

        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        #fixme - Need a note saying wait for the email
        return redirect('auth/postRegister')

    return render_template('auth/register.html', form=form)


@auth.route('/postRegister')
def postRegister():
    return render_template('auth/postRegister.html')


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.isConfirmed() == True:
        return redirect(url_for('main.index'))

    if current_user.confirm(token):
        print "You have confirmed your account. Thanks!"
        flash('You have confirmed your account. Thanks!')

    else:
        print "The confirmation link is invalid or has expired."
        flash('The confirmation link is invalid or has expired.')

    return redirect(url_for('auth.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return render_template('auth/postRegister.html')


@auth.route('/logout')
@login_required
def logout():
    current_user.refreshGoogleAuth()
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))

        else:
            flash('Invalid password.')

    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))

    form = PasswordResetRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))

    form = PasswordResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))

        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))

        else:
            return redirect(url_for('main.index'))

    return render_template('auth/reset_password.html', form=form)

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous():
        print "User is anonymous"
        return redirect(url_for('main.index'))

    elif current_user.isConfirmed():
        print "user is confirmed"
        return redirect(url_for('main.index'))

    return render_template('auth/unconfirmed.html')


@auth.route('/authorize', methods=['GET', 'POST'])
@auth.route('/authorizeGoogle', methods=['GET', 'POST'])
@login_required
def authorizeGoogle():
    auth_uri = getGoogleAuthURL()
    return render_template('gauth.html', auth_uri=auth_uri)


@auth.route('/callback', methods=['GET', 'POST'])
@auth.route('/oauth2callback', methods=['GET', 'POST'])
@login_required
def oauth2callback():
    authorizedDomain = current_user.getAuthorizedDomains()[0]
    auth_code = str(request.args.get("code")).strip()
    creds = getGoogleCredentials(auth_code)

    #it's stupid to write the file but i can't get the auth to work otherwise
    file = tempfile.NamedTemporaryFile(delete=False)

    writeGoogleCredentials(creds, file.name)
    auth_data = getGoogleCredentialsFromFile(file.name)
    current_user.setGoogleAuth(auth_data)
    print auth_data

    return redirect(url_for('main.index'))

@auth.route('/refreshGoogleAuth', methods=['GET'])
@login_required
def refreshGoogleAuth():
    # gauth = User().getGoogleAuthByDomain(current_user.getDomain())
    # f = tempfile.NamedTemporaryFile(delete=False)
    # filename = f.name
    # f.write(gauth)
    # f.close()
    #
    # refreshGoogleFromFile(filename)
    return jsonify({"data": current_user.refreshGoogleAuth()})









