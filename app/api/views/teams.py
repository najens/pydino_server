from app import app, db
from flask import request, jsonify, make_response
from app.models import Team, TeamSchema, User
from flask_jwt_extended import (
    jwt_required, jwt_optional, get_jwt_identity
)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.api import api
from datetime import timedelta, datetime
from .utils import roles_required


@api.route('/team', methods=['GET'])
def get_all_teams():
    """
    This route gets all teams from the database and returns
    the array as a json object.

    Returns {Object<json>} 200
            num_results: {string}
            success: {string}
            teams: {Object<json>}

    Throws {Exception{Object<json>}}
            error: NoResultFound 404
                   SQLAlchemyError 400
    """
    # Try to get all teams from database
    query = Team.query

    try:
        teams = query.all()

        # If query returns no teams, return erorr
        if len(teams) == 0:
            return jsonify({'error': 'No results found!'}), 404

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Serialize array of teams
    team_schema = TeamSchema(many=True)
    output = team_schema.dump(teams).data

    # Return json response
    return jsonify(
        {
            'num_results': str(len(output)),
            'success': 'Successfully retrieved teams!',
            'teams': output,
        }
    ), 200



@api.route('/team/<id>', methods=['GET'])
def get_one_team(id):
    """
    This route gets a single team from the database
    and returns it as a json object.

    Args {string} id

    Returns {Object<json>} 200
            success: {string}
            team: {Object<json>}

    Throws {Exception{Object<json>}}
            error: NoResultFound 404
                   SQLAlchemyError 400
                   NotAuthorized 401
    """
    # Try to get team from database
    query = Team.query.filter_by(id=id)

    try:
        team = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Serialze the team object and return json response
    team_schema = TeamSchema()
    output = team_schema.dump(team).data

    return jsonify({
        'success': 'Successfully retrieved team.',
        'team': output
    }), 200


@api.route('/team', methods=['POST'])
@jwt_required
@roles_required('admin')
def create_team():
    """
    This route adds a new team to the database and
    returns a success message as a json object.

    Returns {Object<json>} 200
            success: {string}
            team: {Object<json>}

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

    # Get team data from request
    data = request.get_json()

    # Verify that all required team data was sent
    if not data['name'] or not data['group']:
        return make_response(jsonify({'error': 'Missing data!'}), 400)

    # Create team object
    team = Team(
        name=data['name'],
        iso_2=data['iso_2'],
        group=data['group'])

    # Try to add team to database
    try:
        db.session.add(team)
        db.session.commit()

    # If team name already in database, return error
    except IntegrityError:
        return jsonify({
            'error': 'Team with name already exists'
        }), 400

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Serialze the team object and return json response
    team_schema = TeamSchema()
    output = team_schema.dump(team).data

    return jsonify({
        'success': 'Successfully retrieved team.',
        'team': output
    }), 200


@api.route('/team/<id>', methods=['PUT'])
@jwt_required
@roles_required('admin')
def edit_team(id):
    """
    This route edits a team in the database and
    returns the updated team as a json object.

    Returns {Object<json>} 200
            success: {string}
            team: {Object<json>}

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

    # Try to get the team from the database
    query = Team.query.filter_by(id=id)

    try:
        team = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Get the team data from the request
    data = request.get_json()

    # Update team data if it was sent and save in database
    if data['name']:
        team.name = data['name']

    if data['iso_2']:
        team.iso_2 = data['iso_2']

    if data['MP']:
        team.MP = data['MP']

    if data['W']:
        team.W = data['W']

    if data['D']:
        team.D = data['D']

    if data['L']:
        team.L = data['L']

    if data['GF']:
        team.GF = data['GF']

    if data['GA']:
        team.GA = data['GA']

    if data['GD']:
        team.GD = data['GD']

    if data['Pts']:
        team.Pts = data['Pts']

    db.session.commit()

    # Serialize team
    team_schema = TeamSchema()
    output = team_schema.dump(team).data

    # Create json and return response
    return jsonify({
        'success': 'The team has been updated',
        'team': output
    })


@api.route('/team/<id>', methods=['DELETE'])
@jwt_required
@roles_required('admin')
def delete_team(id):
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

    # Try to get the team from the database
    query = Team.query.filter_by(id=id)

    try:
        team = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Delete the team from the database
    db.session.delete(team)
    db.session.commit()

    # Create json and return response
    return jsonify({'success': 'The team has been deleted!'})
