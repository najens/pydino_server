from app import app, db
from flask import request, jsonify, make_response
from app.models import Match, MatchSchema, User, Team, TeamSchema
from flask_jwt_extended import (
    jwt_required, jwt_optional, get_jwt_identity
)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.api import api
from datetime import timedelta, datetime
from .utils import roles_required


@api.route('/match', methods=['GET'])
def get_all_matches():
    """
    This route gets all matches from the database and returns
    the array as a json object.

    Returns {Object<json>} 200
            num_results: {string}
            success: {string}
            matches: {Object<json>}

    Throws {Exception{Object<json>}}
            error: NoResultFound 404
                   SQLAlchemyError 400
    """
    # Try to get all matches from database
    query = Match.query

    try:
        matches = query.all()

        # # If query returns no matches, return erorr
        # if len(matches) == 0:
        #     return jsonify({'error': 'No results found!'}), 404

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Serialize array of matches
    match_schema = MatchSchema(many=True)
    output = match_schema.dump(matches).data

    # Return json response
    return jsonify(
        {
            'num_results': str(len(output)),
            'success': 'Successfully retrieved matches!',
            'Matches': output,
        }
    ), 200


@api.route('/match/<id>', methods=['GET'])
def get_one_match(id):
    """
    This route gets a single match from the database
    and returns it as a json object.

    Args {string} id

    Returns {Object<json>} 200
            success: {string}
            match: {Object<json>}

    Throws {Exception{Object<json>}}
            error: NoResultFound 404
                   SQLAlchemyError 400
                   NotAuthorized 401
    """
    # Try to get match from database
    query = Match.query.filter_by(id=id)

    try:
        match = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Serialze the match object and return json response
    match_schema = MatchSchema()
    output = match_schema.dump(match).data

    return jsonify({
        'success': 'Successfully retrieved match.',
        'Match': output
    }), 200


@api.route('/match', methods=['POST'])
@jwt_required
@roles_required('admin')
def create_match():
    """
    This route adds a new match to the database and
    returns a success message as a json object.

    Returns {Object<json>} 200
            success: {string}
            match: {Object<json>}

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

    # Get match data from request
    data = request.get_json()

    # Verify that all required match data was sent
    match_columns = ['Match', 'team1_id', 'team2_id', 'date', 'round', 'title']
    if not any(key in data for key in match_columns):
        return make_response(jsonify({'error': 'Missing data!'}), 400)

    # Create match object
    match = Match(
        match=data['Match'],
        team1_id=data['team1_id'],
        team2_id=data['team2_id'],
        date=data['date'],
        round=data['round'],
        title=data['title'])

    # Try to add match to database
    try:
        db.session.add(match)
        db.session.commit()

    # If match number already in database, return error
    except IntegrityError:
        return jsonify({
            'error': 'Match already exists'
        }), 400

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Serialze the match object and return json response
    match_schema = MatchSchema()
    output = match_schema.dump(match).data

    return jsonify({
        'success': 'Successfully retrieved match.',
        'Match': output
    }), 200


@api.route('/match/<id>', methods=['PUT'])
@jwt_required
@roles_required('admin')
def edit_match(id):
    """
    This route edits a match in the database and
    returns the updated match as a json object.

    Returns {Object<json>} 200
            success: {string}
            match: {Object<json>}

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

    # Try to get the match from the database
    query = Match.query.filter_by(id=id)

    try:
        match = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Get the match data from the request
    data = request.get_json()

    # Update match data if it was sent and save in database
    if 'match' in data:
        match.match = data['match']

    if 'team1_id' in data:
        match.team1_id = data['team1_id']

    if 'team2_id' in data:
        match.team2_id = data['team2_id']

    if 'date' in data:
        match.date = data['date']

    if 'round' in data:
        match.round = data['round']

    if 'title' in data:
        match.title = data['title']

    if 'team1_score' in data:
        match.team1_score = data['team1_score']

    if 'team2_score' in data:
        match.team2_score = data['team2_score']

    db.session.commit()

    # Try to get team1 from the database
    query = Team.query.filter_by(id=match.team1_id)

    try:
        team1 = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Try to get team2 from the database
    query = Team.query.filter_by(id=match.team2_id)

    try:
        team2 = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # if 'team1_score' in data:
    #     team1_score = int(data['team1_score'])
    #     team1.GF += team1_score
    #     if 'team2_score' in data:
    #         team2_score = int(data['team2_score'])
    #         team1.MP += 1
    #         team2.MP += 1
    #         team2.GF += team2_score
    #         team1.GA += team2_score
    #         team1.GD += (team1_score - team2_score)
    #         team2.GA += team1_score
    #         team2.GD += (team2_score - team1_score)
    #         if team1_score > team2_score:
    #             team1.W += 1
    #             team1.Pts += 3
    #             team2.L += 1
    #
    #         if team2_score > team1_score:
    #             team2.W += 1
    #             team2.Pts += 3
    #             team1.L += 1
    #
    #         if team1_score == team2_score:
    #             team1.D += 1
    #             team1.Pts += 1
    #             team2.D += 1
    #             team2.Pts += 1
    #
    # db.session.commit()

    # Serialize match
    match_schema = MatchSchema()
    team_schema = TeamSchema()
    m_output = match_schema.dump(match).data
    t1_output = team_schema.dump(team1).data
    t2_output = team_schema.dump(team2).data

    # Create json and return response
    return jsonify({
        'success': 'The match has been updated',
        'Match': m_output,
        'team1': t1_output,
        'team2': t2_output,
    })


@api.route('/match/<id>', methods=['DELETE'])
@jwt_required
@roles_required('admin')
def delete_match(id):
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

    # Try to get the match from the database
    query = Match.query.filter_by(id=id)

    try:
        match = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Delete the match from the database
    db.session.delete(match)
    db.session.commit()

    # Create json and return response
    return jsonify({'success': 'The match has been deleted!'})
