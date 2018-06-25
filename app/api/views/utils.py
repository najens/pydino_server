from app.models import User, RoleSchema
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from functools import wraps
from flask import jsonify
from app import app


def roles_required(*role_names):
    """
    This decorator ensures that the current user has all of the
    required roles in order to access a protected endpoint. If
    user is missing any roles an error is thrown.

    Arg {Array<string>} role_names

    Returns {func} decorated_view
    """
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):

            # Get user id from jwt token
            public_id = get_jwt_identity()

            # Try to find user in database
            query = User.query.filter_by(public_id=public_id)

            try:
                user = query.first()

            # If no result found, return error
            except NoResultFound:
                return jsonify({'error': 'No result found!'}), 404

            # If some other sqlalchemy error is thrown, return error
            except SQLAlchemyError:
                return jsonify({'error': 'Some problem occurred!'}), 400

            # Create array of the user's roles
            role_schema = RoleSchema(many=True)
            output = role_schema.dump(user.roles).data
            app.logger.info(output)
            roles = []
            for role in output:
                roles.append(role['name'])

            app.logger.info(roles)
            app.logger.info(role_names)

            # Loop through the required roles, and return an error
            # if a required role is not found in the user's roles
            for role in role_names:
                if role not in roles:
                    return jsonify({'error': 'Not authorized'})

            # Call the actual view
            return func(*args, **kwargs)
        return decorated_view
    return wrapper


def roles_accepted(*role_names):
    """
    This decorator ensures that the user has at least one of the
    accpeted roles in order to access a protected endpoint. If user
    is doesn't have at least one of the accepted roles an error is thrown.

    Arg {Array<string>} role_names

    Returns {func} decorated_view
    """
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):

            # Get user id from jwt token
            public_id = get_jwt_identity()

            # Try to find user in the database
            query = User.query.filter_by(public_id=public_id)

            try:
                user = query.first()

            # If no result found, return error
            except NoResultFound:
                return jsonify({'error': 'No result found!'}), 404

            # If some other sqlalchemy error is thrown, return error
            except SQLAlchemyError:
                return jsonify({'error': 'Some problem occurred!'}), 400

            # Create array of the user's roles
            role_schema = RoleSchema(many=True)
            output = role_schema.dump(user.roles).data
            roles = []
            for role in output:
                roles.append(role['name'])

            # Loop through the required roles, and return an error
            # if not a single accepted role is found in the user's roles
            num = 0
            for role in roles:
                if role in role_names:
                    num += 1
            if num == 0:
                return jsonify({'error': 'Not authorized'})

            # Call the actual view
            return func(*args, **kwargs)
        return decorated_view
    return wrapper
