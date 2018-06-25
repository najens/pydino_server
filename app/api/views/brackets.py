from app import app, db
from flask import request, jsonify, make_response
from app.models import Bracket, BracketSchema, User, UserSchema
from flask_jwt_extended import (
    jwt_required, jwt_optional, get_jwt_identity
)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.api import api
from datetime import timedelta, datetime


@api.route('/bracket', methods=['GET'])
def get_all_brackets():
    """
    This route gets all brackets from the database and returns
    the array as a json object.

    Returns {Object<json>} 200
            num_results: {string}
            success: {string}
            brackets: {Object<json>}

    Throws {Exception{Object<json>}}
            error: NoResultFound 404
                   SQLAlchemyError 400
    """
    # Try to get all brackets from database
    query = Bracket.query

    try:
        brackets = query.all()

        # # If query returns no brackets, return erorr
        # if len(brackets) == 0:
        #     return jsonify({'error': 'No results found!'}), 404

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400
    # Serialize array of brackets
    bracket_schema = BracketSchema(many=True)
    output = bracket_schema.dump(brackets).data

    # Return json response
    return jsonify(
        {
            'num_results': str(len(output)),
            'success': 'Successfully retrieved brackets!',
            'brackets': output,
        }
    ), 200


@api.route('/bracket/<id>', methods=['GET'])
def get_one_bracket(id):
    """
    This route gets a single bracket from the database
    and returns it as a json object.

    Args {string} id

    Returns {Object<json>} 200
            success: {string}
            bracket: {Object<json>}

    Throws {Exception{Object<json>}}
            error: NoResultFound 404
                   SQLAlchemyError 400
                   NotAuthorized 401
    """
    # Try to get bracket from database
    query = Bracket.query.filter_by(id=id)

    try:
        bracket = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Serialze the bracket object and return json response
    bracket_schema = BracketSchema()
    output = bracket_schema.dump(bracket).data

    return jsonify({
        'success': 'Successfully retrieved bracket.',
        'bracket': output
    }), 200


@api.route('/bracket', methods=['POST'])
@jwt_required
def create_bracket():
    """
    This route adds a new bracket to the database and
    returns a success message as a json object.

    Returns {Object<json>} 200
            success: {string}
            bracket: {Object<json>}

    Throws {Exception{Object<json>}}
            error: NotAuthorized 401
                   NoResultFound 404
                   SQLAlchemyError 400
    """
    # Get the user's id from access token
    uid = get_jwt_identity()

    # If no user id, return error
    if not uid:
        return make_response(
            jsonify({'error': 'Could not verify!'}),
            401,
            {'WWW-Authentication': 'Basic realm="Login required!"'})

    # Try to get user from database
    query = User.query.filter_by(public_id=uid)

    try:
        user = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 401

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Get bracket data from request
    data = request.get_json()

    # Verify that all required bracket data was sent
    bracket_columns = ['grp_a_1', 'grp_a_2', 'grp_b_1', 'grp_b_2',
        'grp_c_1', 'grp_c_2', 'grp_d_1', 'grp_d_2', 'grp_e_1', 'grp_e_2',
        'grp_f_1', 'grp_f_2', 'grp_g_1', 'grp_g_2', 'grp_h_1', 'grp_h_2']
    if not any(key in data for key in bracket_columns):
        return make_response(jsonify({'error': 'Missing data!'}), 400)

    # Create bracket object
    bracket = Bracket(
        uid=user.public_id,
        grp_a_1=data['grp_a_1'],
        grp_a_2=data['grp_a_2'],
        grp_b_1=data['grp_b_1'],
        grp_b_2=data['grp_b_2'],
        grp_c_1=data['grp_c_1'],
        grp_c_2=data['grp_c_2'],
        grp_d_1=data['grp_d_1'],
        grp_d_2=data['grp_d_2'],
        grp_e_1=data['grp_e_1'],
        grp_e_2=data['grp_e_2'],
        grp_f_1=data['grp_f_1'],
        grp_f_2=data['grp_f_2'],
        grp_g_1=data['grp_g_1'],
        grp_g_2=data['grp_g_2'],
        grp_h_1=data['grp_h_1'],
        grp_h_2=data['grp_h_2'])

    # Try to add bracket to database
    try:
        db.session.add(bracket)
        db.session.commit()

    # If bracket name already in database, return error
    except IntegrityError:
        return jsonify({
            'error': 'User with name or email already exists'
        }), 400

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Add the bracket to the user object
    user.bracket = bracket

    # Serialze the bracket and user objects and return json response
    bracket_schema = BracketSchema()
    b_output = bracket_schema.dump(bracket).data
    user_schema = UserSchema()
    u_output = user_schema.dump(user).data

    return jsonify({
        'success': 'Successfully retrieved bracket.',
        'bracket': b_output,
        'user': u_output,
    }), 200


@api.route('/bracket/<id>', methods=['PUT'])
@jwt_required
def edit_bracket(id):
    """
    This route edits a bracket in the database and
    returns the updated bracket as a json object.

    Returns {Object<json>} 200
            success: {string}
            bracket: {Object<json>}

    Throws {Exception{Object<json>}}
            error: NotAuthorized 401
                   NoResultFound 404
                   SQLAlchemyError 400
    """
    # Get the user's id from access token
    uid = get_jwt_identity()

    # If no user id, return error
    if not uid:
        return make_response(
            jsonify({'error': 'Could not verify!'}),
            401,
            {'WWW-Authentication': 'Basic realm="Login required!"'})

    # Try to get user from database
    query = User.query.filter_by(public_id=uid)

    try:
        user = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 401

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Try to get the bracket from the database
    query = Bracket.query.filter_by(id=id)

    try:
        bracket = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Get the bracket data from the request
    data = request.get_json()

    # Update bracket data if it was sent and save in database
    if 'grp_a_1' in data:
        bracket.grp_a_1 = data['grp_a_1']

    if 'grp_a_2' in data:
        bracket.grp_a_2 = data['grp_a_2']

    if 'grp_b_1' in data:
        bracket.grp_b_1 = data['grp_b_1']

    if 'grp_b_2' in data:
        bracket.grp_b_2 = data['grp_b_2']

    if 'grp_c_1' in data:
        bracket.grp_c_1 = data['grp_c_1']

    if 'grp_c_2' in data:
        bracket.grp_c_2 = data['grp_c_2']

    if 'grp_d_1' in data:
        bracket.grp_d_1 = data['grp_d_1']

    if 'grp_d_2' in data:
        bracket.grp_d_2 = data['grp_d_2']

    if 'grp_e_1' in data:
        bracket.grp_e_1 = data['grp_e_1']

    if 'grp_e_2' in data:
        bracket.grp_e_2 = data['grp_e_2']

    if 'grp_f_1' in data:
        bracket.grp_f_1 = data['grp_f_1']

    if 'grp_f_2' in data:
        bracket.grp_f_2 = data['grp_f_2']

    if 'grp_g_1' in data:
        bracket.grp_g_1 = data['grp_g_1']

    if 'grp_g_2' in data:
        bracket.grp_g_2 = data['grp_g_2']

    if 'grp_h_1' in data:
        bracket.grp_h_1 = data['grp_h_1']

    if 'grp_h_2' in data:
        bracket.grp_h_2 = data['grp_h_2']

    if 'r16_1' in data:
        bracket.r16_1 = data['r16_1']

    if 'r16_2' in data:
        bracket.r16_2 = data['r16_2']

    if 'r16_3' in data:
        bracket.r16_3 = data['r16_3']

    if 'r16_4' in data:
        bracket.r16_4 = data['r16_4']

    if 'r16_5' in data:
        bracket.r16_5 = data['r16_5']

    if 'r16_6' in data:
        bracket.r16_6 = data['r16_6']

    if 'r16_7' in data:
        bracket.r16_7 = data['r16_7']

    if 'r16_8' in data:
        bracket.r16_8 = data['r16_8']

    if 'r8_1' in data:
        bracket.r8_1 = data['r8_1']

    if 'r8_2' in data:
        bracket.r8_2 = data['r8_2']

    if 'r8_3' in data:
        bracket.r8_3 = data['r8_3']

    if 'r8_4' in data:
        bracket.r8_4 = data['r8_4']

    if 'r4_1' in data:
        bracket.r4_1 = data['r4_1']

    if 'r4_2' in data:
        bracket.r4_2 = data['r4_2']

    if 'r2_1' in data:
        bracket.r2_1 = data['r2_1']

    if 'r2_2' in data:
        bracket.r2_1 = data['r2_2']

    db.session.commit()

    # Serialize bracket
    bracket_schema = BracketSchema()
    output = bracket_schema.dump(bracket).data

    # Create json and return response
    return jsonify({
        'success': 'The user has been updated',
        'bracket': output
    })


@api.route('/bracket/<id>', methods=['DELETE'])
@jwt_required
def delete_bracket(id):
    # Get the user's id from the jwt token cookie
    uid = get_jwt_identity()

    # Try to get the user from the database
    query = User.query.filter_by(public_id=uid)

    try:
        user = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 401

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Try to get the bracket from the database
    query = Bracket.query.filter_by(id=id)

    try:
        bracket = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Delete the bracket from the database
    db.session.delete(bracket)
    db.session.commit()

    # Create json and return response
    return jsonify({'success': 'The bracket has been deleted!'})
