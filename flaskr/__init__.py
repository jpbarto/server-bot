import os
import json
import socket
import requests

from flask import Flask, Response, request, jsonify

error_flag = False
BOT_VERSION = os.environ.get ('BOT_VERSION', '0.0.3')

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping()

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/stop')
    def fail_server ():
        global error_flag
        error_flag = True
        return server_response (None)

    @app.route('/start')
    def recover_server ():
        global error_flag
        error_flag = False
        return server_response (None)

    # a simple page that says hello
    @app.route('/', defaults={'rqst_path': ''})
    @app.route('/<path:rqst_path>')
    def server_response(rqst_path):

        # if this is an AWS EC2 instance get its metadata
        ec2_metadata = {}
        try:
            response = requests.get('http://169.254.169.254/latest/meta-data/instance-id', timeout = (0.5, 0.5))
            ec2_metadata['instance_id'] = response.text

            response = requests.get('http://169.254.169.254/latest/meta-data/local-hostname', timeout = (0.5, 0.5))
            ec2_metadata['local_hostname'] = response.text

            response = requests.get('http://169.254.169.254/latest/meta-data/local-ipv4', timeout = (0.5, 0.5))
            ec2_metadata['local_ipv4'] = response.text

            response = requests.get('http://169.254.169.254/latest/meta-data/public-hostname', timeout = (0.5, 0.5))
            ec2_metadata['public_hostname'] = response.text

            response = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4', timeout = (0.5, 0.5))
            ec2_metadata['public_ipv4'] = response.text

            response = requests.get('http://169.254.169.254/latest/meta-data/placement/region', timeout = (0.5, 0.5))
            ec2_metadata['region'] = response.text

            response = requests.get('http://169.254.169.254/latest/meta-data/placement/availability-zone', timeout = (0.5, 0.5))
            ec2_metadata['availability_zone'] = response.text
        except:
            print ("Request for EC2 metadata failed")

        response = {
                    "Request method": request.method,
                    "Request path": request.path,
                    "Request header keys": [],
                    "Server Bot Version": BOT_VERSION,
                    "os": os.name,
                    "uname": os.uname (),
                    "hostname": socket.gethostname (),
                    "EC2 metadata": ec2_metadata,
                    "Environment": dict(os.environ),
                    "error": error_flag}

        for header_key in request.headers.keys ():
            response['Request header keys'].append (header_key)

        accept_header = request.headers.get('Accept')

        if accept_header is not None and 'application/json' in accept_header:
            if error_flag:
                return jsonify (response), 500
            else:
                return jsonify (response), 200
        else:
            response_str = '<html><body><pre>' + json.dumps (response, indent=4) +'</pre></body></html>'
            if error_flag:
                return Response (response_str,
                             status = 500,
                             content_type='text/html')
            else:
                return Response (response_str,
                             status = 200,
                             content_type='text/html')


    return app
