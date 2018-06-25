from app import app, db
from os import urandom
from base64 import b64encode
from flask import request, jsonify, make_response
from app.models import User, UserSchema, RoleSchema, OAuth
from flask_jwt_extended import (
        jwt_required, jwt_optional, get_jwt_identity,
        create_access_token, create_refresh_token,
        set_access_cookies, set_refresh_cookies,
        get_csrf_token
)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.api import api
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import timedelta, datetime
from app.mail.utils.emails import send_confirm_email_email
from .utils import roles_required, roles_accepted


@api.route('/user', methods=['GET'])
def get_all_users():
    """
    This route gets all users from the database and returns
    the array as a json object.

    Returns {Object<json>} 200
            num_results: {string}
            success: {string}
            users: {Object<json>}

    Throws {Exception{Object<json>}}
            error: NoResultFound 404
                   SQLAlchemyError 400
    """
    # Try to get all users from database
    query = User.query

    try:
        users = query.all()

        # If query returns no users, return erorr
        if len(users) == 0:
            return jsonify({'error': 'No results found!'}), 404

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Serialize array of users
    user_schema = UserSchema(many=True)
    output = user_schema.dump(users).data

    # Return json response
    return jsonify(
        {
            'num_results': str(len(output)),
            'success': 'Successfully retrieved users!',
            'users': output,
        }
    ), 200


@api.route('/user/<public_id>', methods=['GET'])
@jwt_required
def get_one_user(public_id):
    """
    This route gets a single user from the database
    and returns it as a json object.

    Args {string} public_id

    Returns {Object<json>} 200
            success: {string}
            user: {Object<json>}

    Throws {Exception{Object<json>}}
            error: NoResultFound 404
                   SQLAlchemyError 400
                   NotAuthorized 401
    """
    # Get the user's id from access token
    uid = get_jwt_identity()

    # If user's public_id doesn't equal public id in url, return error
    if user.public_id != public_id:
        return jsonify({'error': 'Not authorized!'}), 401

    # Try to get user from database
    query = User.query.filter_by(public_id=uid)

    try:
        user = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Serialze the user object and return json response
    user_schema = UserSchema()
    output = user_schema.dump(user).data

    return jsonify({
        'success': 'Successfully retrieved user.',
        'user': output
    }), 200


@api.route('/user', methods=['POST'])
def create_user():
    """
    This route adds a new user to the database, sends a
    confirmation link to the user's email and returns a
    success message aa a json object.

    Returns {Object<json>} 200
            success: {string}

    Throws {Exception{Object<json>}}
            error: NotAuthorized 401
                   NoResultFound 404
                   SQLAlchemyError 400
    """
    # Get user's authorization credentials
    auth = request.authorization

    # If no authorization credentials, return error
    if not auth or not auth.username or not auth.password:
        return make_response(
            jsonify({'error': 'Could not verify!'}),
            401,
            {'WWW-Authentication': 'Basic realm="Login required!"'})

    # Get user data from request
    data = request.get_json()

    # If name or email is missing, return error
    if not data['name'] or not data['email']:
        return make_response(jsonify({'error': 'Missing data!'}), 400)

    # Create a salted password
    random_bytes = urandom(24)
    salt = b64encode(random_bytes).decode('utf-8')
    salted_password = auth['password'] + salt

    # Hash the salted password
    hashed_password = generate_password_hash(
        salted_password,
        method='pbkdf2:sha512:80000',
        salt_length=20)

    # Create user object
    user = User(
        name=data['name'],
        email=data['email'],
        username=auth['username'],
        password=hashed_password,
        salt=salt,
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


@api.route('/user/<id>', methods=['PUT'])
@jwt_optional
def edit_user(id):
    """
    This route edits a user in the database and
    returns the updated user aa a json object.

    Returns {Object<json>} 200
            success: {string}
            user: {Object<json>}

    Throws {Exception{Object<json>}}
            error: NotAuthorized 401
                   ExpiredSignatureError 400
                   DecodeJWTError 400
                   NoResultFound 404
                   SQLAlchemyError 400
    """
    auth = {}

    # Get the user data from the request
    data = request.get_json()

    # If there is no authorization header, get
    # the user's id from the access token cookie
    if not request.headers.get('Authorization'):
        public_id = get_jwt_identity()

        # If user's id doesn't match url id, return error
        if public_id != id:
            return jsonify({'error': 'Not authorized!'}), 401

    # If basic authorization, get the user's
    # id from the authorization username
    elif request.authorization:

        auth = request.authorization

        # If authorization credentials missing, return error
        if not auth or not auth.username or not auth.password:
            return make_response(
                jsonify({
                    'error': 'Could not verify'
                }),
                401,
                {'WWW-Authentication': 'Basic realm="Login required!"'})

        public_id = auth.username

        # If the user's public id doesn't match url id, return error
        if public_id != id:
            return jsonify({'error': 'Not authorized!'}), 401

    else:
        # Get the user's token from the authorization header
        token = request.headers.get('Authorization').split(' ')[1]

        # If there is no token, return error
        if not token:
            return jsonify({'error': 'Missing token!'}), 401

        token = token.encode("utf-8")

        # Decode the jwt token
        try:
            jwt_data = jwt.decode(
                token, app.config.get('SECRET_KEY'), algorithm='HS256')

        # If the token has expired, return error
        except jwt.ExpiredSignatureError:
            # Signature has expired
            return jsonify({
                'error': 'Reset token is expired. Please try again.'
            }), 400

        # If failed to decode jwt, return error
        if not jwt_data:
            return jsonify({'error': 'Failed to decode jwt token.'}), 400

        # Get the user's id from the decoded jwt
        public_id = jwt_data['public_id']

        # If the user's id doesn't match the url id, return error
        if public_id != id:
            return jsonify({'error': 'Not authorized!'}), 401

    # Try to get the user from the database
    query = User.query.filter_by(public_id=public_id)

    try:
        user = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # If password provided but can't be verified, return error
    if 'password' in auth:

        if not check_password_hash(user.password, auth.password + user.salt):
            return jsonify({
                'error': ('The password you provided could '
                          'not be found for this user.')
            }), 401

    # If new password provided, create salt and hash it
    if 'password' in data:
        random_bytes = urandom(24)
        salt = b64encode(random_bytes).decode('utf-8')
        salted_password = data['password'] + salt

        hashed_password = generate_password_hash(
            salted_password, method='pbkdf2:sha512:80000', salt_length=20)
        user.password = hashed_password
        user.salt = salt

    # If other user attributes provided, add
    # them to user and save in database
    if 'name' in data:
        user.name = data['name']

    if 'username' in data:
        user.username = data['username']

    if 'email' in data:
        user.email = data['email']

    if 'picture' in data:
        user.picture = data['picture']

    db.session.commit()

    # Serialize user
    user_schema = UserSchema()
    output = user_schema.dump(user).data

    # Create json and return response
    return jsonify({
        'success': 'The user has been updated',
        'user': output
    })


@api.route('/user/<public_id>', methods=['DELETE'])
@jwt_required
def delete_user(public_id):
    # Get the user's id from the jwt token cookie
    uid = get_jwt_identity()

    # Try to get the user from the database
    query = User.query.filter_by(public_id=uid)

    try:
        user = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Find the user's OAuth data if it exists
    oauth = OAuth.query.filter_by(uid=uid).first()

    # Delete the user from the database
    db.session.delete(oauth)
    db.session.delete(user)
    db.session.commit()

    # Create json and return response
    return jsonify({'message': 'The user has been deleted!'})
