from app import jwt, app
from flask import (
    make_response, request, jsonify, render_template)
from flask_jwt_extended import (
    create_access_token, jwt_refresh_token_required, get_jwt_identity,
    set_access_cookies, get_csrf_token)
from urllib.parse import urlsplit, unquote, urlunsplit
from app.auth import auth
from datetime import timedelta


@jwt.expired_token_loader
def my_expired_token_callback():
    """This function is called each time a user tries to access a
    jwt_required view with an expired access_token and returns the
    url path and method the user tried to execute.

    Returns {Object<json>} 200
            url: {string}
            method: {string}
    """
    # Make the url a safe url and return json response
    request_url = make_safe_url(unquote(request.url))
    method = request.method

    return jsonify({'url': request_url, 'method': method})


@auth.route('/', defaults={'path': ''})
@auth.route('/<path:path>')
def catch_all(path):
    """
    Catches all url and renders the dom.

    Arg {string} path

    Returns {file} index.html 200
    """
    return render_template('index.html'), 200


@auth.route('/token/refresh', methods=['GET'])
def get_tokens():
    """
    Gets a user's csrf token from cookies and
    returns it to the user as json object

    Returns {Object<json>} 200
            csrf_refresh_token: {string}
            success: {string}
    """
    csrf_refresh_token = request.cookies.get('csrf_refresh_token')
    if csrf_refresh_token:
        return jsonify({
            'success': 'Received user token',
            'csrf_refresh_token': csrf_refresh_token
        }), 200

    return jsonify({'error': 'User is missing csrf refresh token.'}), 400


@auth.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    '''
    Get the user's id from their refresh_token and create
    a new access token that will be returned in the response

    Returns {Object<json>} 200
            success: {string}
    '''
    # Get the user's id from refresh token cookie
    public_id = get_jwt_identity()

    # If no user id, return error
    if not public_id:
        return jsonify({'error': 'Invalid user request.'}), 400

    # Create access tokens
    expires = timedelta(seconds=1800)
    access_token = create_access_token(
        identity=public_id, expires_delta=expires)

    # Get newly created csrf access token to return as header
    csrf_access_token = get_csrf_token(access_token)

    # Create json response and return access cookies and header
    response = make_response(jsonify({
        'success': 'Access token has been refreshed.'
    }), 200)
    set_access_cookies(response, access_token)
    response.headers['access'] = csrf_access_token

    return response


def make_safe_url(url):
    '''Turns an unsafe absolute URL into a safe
    relative URL by removing the scheme and hostname

    Returns {string} safe_url 200
    '''
    parts = urlsplit(url)
    # Remove scheme and hostname from url
    safe_url = urlunsplit(('', '', parts.path, parts.query, parts.fragment))

    return safe_url


def _get_safe_next_param(param_name, default_endpoint):
    '''The next query parameter contains quoted URLs that may contain
    unsafe hostnames. Return the query parameter as a safe, unquoted URL

    Returns {string} safe_next 200
    '''
    if param_name in request.args:
        # Return safe unquoted query parameter value
        safe_next = make_safe_url(unquote(request.args[param_name]))
    else:
        # Return URL of default endpoint
        safe_next = _endpoint_url(default_endpoint)

    return safe_next


def _endpoint_url(endpoint):
    '''If default endpoint is not specified, return to home page

    Returns {string} url 200
    '''
    url = '/'
    if endpoint:
        url = '/'

    return url
