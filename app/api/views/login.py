from flask import make_response, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies, jwt_optional,
    get_jwt_identity, get_csrf_token
)
from app.api import api
from app.models import User, UserSchema, OAuth
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app import app, db
import json


@api.route('/login')
@jwt_optional
def login():
    """
    This route authenticates the user by checking the username and
    password if it exists or by decoding the jwt token if it exists.
    Each time a user logs in new jwt tokens cookies will be set in
    the response.

    Returns {Object<json>} 200
            success: {string}
            user: {Object<json>}

    Throws {Exception{Object<json}}:
            error: NoResultFound 401
                   SQLAlchemyError 400
                   InactiveUser 400
    """

    # If authorization header is present, try to authenticate the user
    if request.authorization:
        auth = request.authorization

        # If not username and password, return error
        if not auth.username or not auth.password:
            return not_authorized_error('Basic')

        # Find the user by username
        query = User.query.filter_by(username=auth.username)

        try:
            user = query.one()

        # If no user found, try by email or return error
        except NoResultFound:

            # Try to find the user by email
            query = User.query.filter_by(email=auth.username)

            try:
                user = query.one()

            # If no user found, try by email or return error
            except NoResultFound:
                return make_response(
                    jsonify({
                        'error': ('Sorry, your username or password was '
                                  'incorrect. Please try again.')
                    }), 401, {
                        'WWW-Authentication': 'Basic realm="Login required!"'
                    })
            # If some other sqlalchemy error is thrown, return error
            except SQLAlchemyError:
                return jsonify({'error': 'Some problem occurred!'}), 400

        # If some other sqlalchemy error is thrown, return error
        except SQLAlchemyError:
            return jsonify({'error': 'Some problem occurred!'}), 400

        # If provided password does not match user password, return error
        if not check_password_hash(user.password, auth.password + user.salt):
            return make_response(
                jsonify({
                    'error': ('Sorry, your username or password was '
                              'incorrect. Please try again.')
                }), 401, {
                    'WWW-Authentication': 'Basic realm="Login required!"'
                })

        # Serialize the user object
        user_schema = UserSchema()
        output = user_schema.dump(user).data

        # Create the tokens to be sent to the user
        expires = timedelta(seconds=1800)
        access_token = create_access_token(
            identity=user.public_id,
            expires_delta=expires
        )
        refresh_token = create_refresh_token(identity=user.public_id)

        # Get the csrf tokens so they can be set as headers in response
        csrf_access_token = get_csrf_token(access_token)
        csrf_refresh_token = get_csrf_token(refresh_token)

        # Create json response
        response = make_response(
            jsonify({
                'user': output,
                'success': 'Login successful!'
            }), 200)

        # Set JWT cookies and headers and return response
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        response.set_cookie('public_id', user.public_id)
        response.headers['access'] = csrf_access_token
        response.headers['refresh'] = csrf_refresh_token

        return response

    # If no authorization header present, check for jwt token cookies
    else:
        public_id = get_jwt_identity()

        # If there isn't a valid jwt token, return error
        if not public_id:
            return not_authorized_error('Cookie')

        # Find the user
        query = User.query.filter_by(public_id=public_id)

        try:
            user = query.first()

        # If no user found, return error
        except NoResultFound:
            return not_authorized_error('Cookie')

        # If some other sqlalchemy error is thrown, return error
        except SQLAlchemyError:
            return jsonify({'error': 'Some problem occurred!'}), 400

        # Serialize the user object
        user_schema = UserSchema()
        output = user_schema.dump(user).data

        # Create the tokens to be sent to the user
        expires = timedelta(seconds=1800)
        access_token = create_access_token(
            identity=user.public_id,
            expires_delta=expires
        )
        refresh_token = create_refresh_token(identity=user.public_id)

        # Get the csrf tokens so they can be set as headers in response
        csrf_access_token = get_csrf_token(access_token)
        csrf_refresh_token = get_csrf_token(refresh_token)

        # Create json response
        response = make_response(
            jsonify({
                'user': output,
                'success': 'Login successful!'
            }), 200)

        # Set JWT cookies and headers and return response
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        response.set_cookie('public_id', user.public_id)
        response.headers['access'] = csrf_access_token
        response.headers['refresh'] = csrf_refresh_token

        return response


@api.route('/oauth/<provider>', methods=['POST'])
def oauth(provider):
    """
    This route authenticates the user by receiving a provider
    and oauth token and verifying a user exists. When a user logs
    in new jwt tokens cookies will be set in the response.

    Args {string} provider - facebook or google

    Returns {Object<json>} 200
            success: {string}
            user: {Object<json>}

    Throws {Exception{Object<json}}:
            error: Authorization 401
                   NoResultFound 401
                   SQLAlchemyError 400
                   MissingUser 400
                   InactiveUser 400
    """
    # If no authorization header, return error
    if not request.headers.get('Authorization'):
        return jsonify({'error': 'Not a valid request'}), 401

    # Get the token from authorization header and convert to dictionary
    token = request.headers.get('Authorization').split('Bearer ')[1]
    token = json.loads(token)

    # Try to find oauth user in database
    query = OAuth.query.filter_by(
        provider=provider,
        provider_uid=token['userID'],
    )

    try:
        oauth = query.first()

    # If no result found, return error
    except NoResultFound:
        return jsonify({
            'error': "The user doesn't exist. Sign up to create an account"
        }), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # If not oauth create a new user
    if not oauth:

        # Get user data from request
        data = request.get_json()

        # If name or email is missing, return error
        if not (data['name'] or not data['email'] or not data['picture']
        or not data['provider_user_id']):
            return make_response(jsonify({'error': 'Missing data!'}), 400)

        # Create user object
        user = User(
            name=data['name'],
            email=data['email'],
            picture=data['picture'],
            created_at=datetime.utcnow())

        user.generate_public_id()

        # Try to add user to database
        try:
            db.session.add(user)
            db.session.commit()

        # If username already in database, return error
        except IntegrityError:
            return jsonify({
                'error': 'User with name or email already exists'
            }), 400

        # If some other sqlalchemy error is thrown, return error
        except SQLAlchemyError:
            return jsonify({'error': 'Some problem occurred!'}), 400

        # Create new oauth token account for user
        oauth = OAuth(
            provider=provider,
            provider_uid=data['provider_user_id'],
            token=token,
        )

        # Associate the new local user account with the OAuth token
        oauth.user = user

        # Save and commit database models
        db.session.add(oauth)
        db.session.commit()

    # If there is no user relation, return error
    if not oauth.user:
        return jsonify({'error': 'Some problem occurred!'}), 400

    user = oauth.user

    # Serialze the user object
    user_schema = UserSchema()
    output = user_schema.dump(user).data

    # Create the tokens to be sent to the user
    expires = timedelta(seconds=1800)
    access_token = create_access_token(
        identity=user.public_id,
        expires_delta=expires
    )
    refresh_token = create_refresh_token(identity=user.public_id)

    # Get the csrf tokens so they can be set as headers in response
    csrf_access_token = get_csrf_token(access_token)
    csrf_refresh_token = get_csrf_token(refresh_token)

    # Create json response
    response = make_response(
        jsonify({
            'user': output,
            'success': 'Login successful!'
        }), 200)

    # Set JWT cookies and headers and return response
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    response.set_cookie('public_id', user.public_id)
    response.headers['access'] = csrf_access_token
    response.headers['refresh'] = csrf_refresh_token

    return response


@api.route('/logout', methods=['GET'])
def logout():
    """
    Logs out user and sends a response to clear access and refresh
    tokens, public_id cookie, and returns success message

    Returns {Object<json>} 200
            success: {string}
    """
    # Create json response
    response = make_response(
        jsonify({'success': 'The user has been logged out.'}),
        200
    )

    # Remove cookies from browser and return response
    response.delete_cookie('public_id')
    unset_jwt_cookies(response)

    return response


def not_authorized_error(type):
    """
    Creates a 401 Not Authorized response

    Arg {string} type - Basic or Cookie

    Returns {Object<json>} 200
            error: {string}
    """
    return make_response(
        jsonify({'error': 'Could not verify!'}), 401,
        {
            'WWW-Authentication': '%s realm="Login required!"' % (type)
        })
