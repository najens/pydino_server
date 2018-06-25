from app.mail import mail
from app.mail.utils.emails import send_forgot_password_email
from flask import request, make_response, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, set_access_cookies,
    set_refresh_cookies, get_csrf_token)
from datetime import datetime, timedelta
from app import app, db
from app.models import User, UserSchema
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
import jwt


@mail.route('/confirm/email/<token>', methods=['GET'])
def confirm_email(token):
    '''This route takes in a token from the confirmation email
    link to authenticate the user. It returns the user json object
    as well as access and refresh token cookies and csrf headers

    Arg {string} token

    Returns {Object<json>} 200
            success: {string}
            user: {Object<json>}
    '''
    # Try to decode the jwt token
    token = token.encode("utf-8")
    try:
        data = jwt.decode(
            token, app.config.get('SECRET_KEY'), algorithm='HS256')

    # If the token is expired, return error
    except jwt.ExpiredSignatureError:
        # Signature has expired
        return jsonify({
            'error': 'Reset token is expired. Please try again.'
        }), 400

    # Get the user's id from the token
    public_id = data['public_id']

    # Try to get the user from the database
    query = User.query.filter_by(public_id=public_id)

    try:
        user = query.one()

    # If no user found, return error
    except NoResultFound:
        return jsonify({
            'error': ('Could not identify the user. '
                      ' Please try again.')
        }),
        404,
        {'WWW-Authentication': 'Basic realm="Login required!"'}

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Add a confirmation date to user and make status active
    user.confirmed_at = datetime.utcnow()
    user.is_active = True

    # Try to add updated user to database
    try:
        db.session.commit()

    # If username already in database, return error
    except IntegrityError:
        return jsonify({
            'error': 'Could not confirm user. Please try again.'
        }), 400

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Serialize the user
    user_schema = UserSchema()
    output = user_schema.dump(user).data

    # Create the tokens to be sent to the user
    expires = timedelta(seconds=1800)
    access_token = create_access_token(
        identity=user.public_id,
        expires_delta=expires
    )
    refresh_token = create_refresh_token(identity=user.public_id)

    # Get the new csrf tokens to be sent as headers
    csrf_access_token = get_csrf_token(access_token)
    csrf_refresh_token = get_csrf_token(refresh_token)

    # Create json response
    response = make_response(
        jsonify({
            'user': output,
            'success': 'Login successful!'
        }), 200)

    # Set access and refresh cookies and headers and return response
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    response.set_cookie('public_id', user.public_id)
    response.headers['access'] = csrf_access_token
    response.headers['refresh'] = csrf_refresh_token

    return response


@mail.route('/password/forgot', methods=['POST'])
def forgot_password():
    '''This path takes in a username or email and sends a
    reset password link to the user's email if the user exists.

    Returns {Object<json>} 200
            success: {string}
    '''
    # Get the username or email from the request
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing username or email'}), 400
    username = data['username']

    # Try to find the user in the database
    query = User.query.filter_by(username=username)

    try:
        user = query.one()

    # If no user found, try to find the user by email or return error
    except NoResultFound:

        # Try to find the user by email
        query = User.query.filter_by(email=username)

        try:
            user = query.one()

        # If no user found, return error
        except NoResultFound:
            return make_response(
                jsonify({
                    'error': ('Sorry, your username or email was incorrect. '
                              ' Please try again.')
                }),
                404,
                {'WWW-Authentication': 'Basic realm="Login required!"'})

        # If some other sqlalchemy error is thrown, return error
        except SQLAlchemyError:
            return jsonify({'error': 'Some problem occurred!'}), 400

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    email = user.email

    # Create an encoded token to add to reset password link
    token = jwt.encode(
        {
            'public_id': user.public_id,
            'exp': datetime.utcnow() + timedelta(seconds=500)
        },
        app.config.get('SECRET_KEY'),
        algorithm='HS256')

    token = token.decode("utf-8")

    # Create reset password link
    reset_password_link = (
        '%spassword/reset?token=%s&public_id=%s' % (
            app.config.get('DOMAIN'), token, user.public_id))

    # Send reset password email to user
    send_forgot_password_email(user, email, reset_password_link)

    # Return json response with success message
    success = ('A reset password email has been sent to %s. '
               'Open the email and follow the instructions to '
               'reset your password.') % (email)

    return jsonify({'success': success}), 200
