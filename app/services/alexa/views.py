from flask import render_template, flash, redirect, session, url_for, request, g, make_response, jsonify
from . import alexa
from .models import alexaModel, ip2int, int2ip


@alexa.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('index.html')    


@alexa.route('/getInfo', methods = ['GET', 'POST'])
def getInfo(ip_str = None):
    response = {"record": None}
    
    if ip_str == None:
        data = request.get_json()
        if data != None:
            ip_str = data['ip']
            
        if ip_str == None:
            ip_str = request.args.get("ip")
        
    if ip_str != None:
        ip = ip2int(ip_str)
        topIP = alexaModel.query.filter_by(ip=ip).first()
        isTop = (topIP != None)
    else:
        isTop = None
        
    if isTop: 
        response = {"record": {"found":True}}

    
    return jsonify({"alexa":response})
        
    
