from app import app, db
from flask import request, jsonify, make_response
from app.models import Topic, TopicSchema, User, UserSchema
from flask_jwt_extended import (
    jwt_required, jwt_optional, get_jwt_identity
)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.api import api
from datetime import timedelta, datetime
from .utils import roles_required


@api.route('/topic', methods=['GET'])
def get_all_topics():
    """
    This route gets all topics from the database and returns
    the array as a json object.

    Returns {Object<json>} 200
            num_results: {string}
            success: {string}
            topics: {Object<json>}

    Throws {Exception{Object<json>}}
            error: NoResultFound 404
                   SQLAlchemyError 400
    """
    # Try to get all topics from database
    query = Topic.query

    try:
        topics = query.all()

        # # If query returns no topics, return erorr
        # if len(topics) == 0:
        #     return jsonify({'error': 'No results found!'}), 404

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400
    # Serialize array of topics
    topic_schema = TopicSchema(many=True)
    output = topic_schema.dump(topics).data

    # Return json response
    return jsonify(
        {
            'num_results': str(len(output)),
            'success': 'Successfully retrieved topics!',
            'topics': output,
        }
    ), 200


@api.route('/topic/<id>', methods=['GET'])
def get_one_topic(id):
    """
    This route gets a single topic from the database
    and returns it as a json object.

    Args {string} id

    Returns {Object<json>} 200
            success: {string}
            topic: {Object<json>}

    Throws {Exception{Object<json>}}
            error: NoResultFound 404
                   SQLAlchemyError 400
                   NotAuthorized 401
    """
    # Try to get topic from database
    query = Topic.filter_by(id=id)

    try:
        topic = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Serialze the topic object and return json response
    topic_schema = TopicSchema()
    output = topic_schema.dump(topic).data

    return jsonify({
        'success': 'Successfully retrieved topic.',
        'topic': output
    }), 200


@api.route('/topic', methods=['POST'])
@jwt_required
@roles_required('admin')
def create_topic():
    """
    This route adds a new topic to the database and
    returns a success message as a json object.

    Returns {Object<json>} 200
            success: {string}
            topic: {Object<json>}

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

    # Get topic data from request
    data = request.get_json()

    # Verify that all required topic data was sent
    topic_columns = ['name', 'profeciency']
    if not any(key in data for key in topic_columns):
        return make_response(jsonify({'error': 'Missing data!'}), 400)

    # Create topic object
    topic = Topic(
        name=data['name'],
        profeciency=data['profeciency'])

    # Try to add topic to database
    try:
        db.session.add(topic)
        db.session.commit()

    # If topic name already in database, return error
    except IntegrityError:
        return jsonify({
            'error': 'Topic with name already exists'
        }), 400

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Serialze the topic object and return json response
    topic_schema = TopicSchema()
    output = topic_schema.dump(topic).data

    return jsonify({
        'success': 'Successfully retrieved topic.',
        'topic': output,
    }), 200


@api.route('/topic/<id>', methods=['PUT'])
@jwt_required
@roles_required('admin')
def edit_topic(id):
    """
    This route edits a topic in the database and
    returns the updated topic as a json object.

    Returns {Object<json>} 200
            success: {string}
            topic: {Object<json>}

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

    # Try to get the topic from the database
    query = Topic.query.filter_by(id=id)

    try:
        topic = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Get the topic data from the request
    data = request.get_json()

    # Update topic data if it was sent and save in database
    if data['name']:
        topic.name = data['name']

    if data['profeciency']:
        topic.profeciency = data['profeciency']

    db.session.commit()

    # Serialize topic
    topic_schema = TopicSchema()
    output = topic_schema.dump(topic).data

    # Create json and return response
    return jsonify({
        'success': 'The topic has been updated',
        'topic': output
    })


@api.route('/topic/<id>', methods=['DELETE'])
@jwt_required
@roles_required('admin')
def delete_topic(id):
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

    # Try to get the topic from the database
    query = Topic.query.filter_by(id=id)

    try:
        topic = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Delete the topic from the database
    db.session.delete(topic)
    db.session.commit()

    # Create json and return response
    return jsonify({'success': 'The topic has been deleted!'})
