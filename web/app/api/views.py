from . import api
from flask import request, jsonify
import os
import sys
sys.path.append(os.path.realpath('..'))
from core.main import Spyder

spyder = None


@api.route('/login', methods=['POST'])
def login():
    """Login to the OJ account

    This route logs the user into the OJ.

    Returns:
        flask.Response: The login status is JSON format.
    """
    global spyder
    content = request.get_json()
    username = content['username']
    password = content['password']
    spyder = Spyder(username, password)
    status = spyder.login()
    return jsonify(status)


@api.route('/problems/get', methods=['GET'])
def get_problems():
    """Get problems by page
    
    This route gets the problem list and returns it.

    Returns:
        flask.Response: The problems list and status
    """
    content = request.get_json()
    page = content['page']
    result = spyder.get_problems(page)
    return jsonify(result)


@api.route('/problems/get/<int:pid>', methods=['GET'])
def get_problem(pid):
    """Get problem on OJ
    
    This route gets the problem and returns it.

    Args:
        pid (int): The problem id.

    Returns:
        flask.Response: The problem and status
    """
    result = spyder.get_problem(pid)
    return jsonify(result)


@api.route('/problems/submit/<int:pid>', methods=['POST'])
def submit_problem(pid):
    """Submit the problem
    
    This route submits the problem and returns the status of submitting.

    Args:
        pid (int): The problem id.

    Returns:
        flask.Response: The submitted status
    """    
    content = request.get_json()
    ans = content['ans']
    result = spyder.submit(pid, ans)
    return jsonify(result)


@api.route('/problems/status/<int:pid>', methods=['GET'])
def get_status(pid):
    """Get the problem status
    
    This route gets the problem status and returns it.

    Args:
        pid (int): The problem id.

    Returns:
        flask.Response: The status returned
    """    
    result = spyder.get_status(pid)
    return jsonify(result)


@api.app_errorhandler(500)
def internal_server_error(e):
    return jsonify({'status': 'error', 'msg': 'internal server error'}), 500


@api.app_errorhandler(404)
def not_found(e):
    return jsonify({'status': 'error', 'msg': 'not found'}), 404
