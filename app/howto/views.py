__author__ = 'mjw'

from flask import render_template, redirect, request, url_for, flash, jsonify
from flask.ext.login import login_user, logout_user, login_required, current_user

from app import DEBUG
from . import howto

@howto.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html", current_user=current_user)


@howto.route('/signup', methods=['GET', 'POST'])
@howto.route('/register', methods=['GET', 'POST'])
def register():
    return render_template("index.html", current_user=current_user)


@howto.route('/unconfirmed', methods=['GET', 'POST'])
def unconfirmed():
    return render_template("index.html", current_user=current_user)


@howto.route('/google', methods=['GET', 'POST'])
@howto.route('/authorize', methods=['GET', 'POST'])
@howto.route('/authorizeGoogle', methods=['GET', 'POST'])
def authorizeGoogle():
    return render_template("index.html", current_user=current_user)


@howto.route('/contact', methods=['GET', 'POST'])
@howto.route('/email', methods=['GET', 'POST'])
def contact():
    return render_template("index.html", current_user=current_user)

@howto.route('/knownBad', methods=['GET', 'POST'])
def knownBad():
    return render_template("index.html", current_user=current_user)


@howto.route('/mostActiveForeignIPs', methods=['GET', 'POST'])
def mostActiveForeignIPs():
    return render_template("index.html", current_user=current_user)


@howto.route('/mostActiveForeignCountries', methods=['GET', 'POST'])
def mostActiveForeignCountries():
    return render_template("index.html", current_user=current_user)


@howto.route('/mostDistinctCountries', methods=['GET', 'POST'])
def mostDistinctCountries():
    return render_template("index.html", current_user=current_user)