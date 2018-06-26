from app import app, db
from flask import request, jsonify, make_response
from app.models import Project, ProjectSchema, ProjectTopics, User
from flask_jwt_extended import (
    jwt_required, jwt_optional, get_jwt_identity
)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.api import api
from datetime import timedelta, datetime
from .utils import roles_required


@api.route('/project', methods=['GET'])
def get_all_projects():
    """
    This route gets all projects from the database and returns
    the array as a json object.

    Returns {Object<json>} 200
            num_results: {string}
            success: {string}
            projects: {Object<json>}

    Throws {Exception{Object<json>}}
            error: NoResultFound 404
                   SQLAlchemyError 400
    """
    # Try to get all projects from database
    query = Project.query

    try:
        projects = query.all()

        # # If query returns no projects, return erorr
        # if len(projects) == 0:
        #     return jsonify({'error': 'No results found!'}), 404

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Serialize array of projects
    project_schema = ProjectSchema(many=True)
    output = project_schema.dump(projects).data

    # Return json response
    return jsonify(
        {
            'num_results': str(len(output)),
            'success': 'Successfully retrieved users!',
            'projects': output,
        }
    ), 200


@api.route('/project/<id>', methods=['GET'])
def get_one_project(id):
    """
    This route gets a single project from the database
    and returns it as a json object.

    Args {string} id

    Returns {Object<json>} 200
            success: {string}
            project: {Object<json>}

    Throws {Exception{Object<json>}}
            error: NoResultFound 404
                   SQLAlchemyError 400
                   NotAuthorized 401
    """
    # Try to get project from database
    query = Project.query.filter_by(id=id)

    try:
        project = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Serialze the project object and return json response
    project_schema = ProjectSchema()
    output = project_schema.dump(project).data

    return jsonify({
        'success': 'Successfully retrieved project.',
        'project': output
    }), 200


@api.route('/project', methods=['POST'])
@jwt_required
@roles_required('admin')
def create_project():
    """
    This route adds a new project to the database and
    returns a success message as a json object.

    Returns {Object<json>} 200
            success: {string}
            project: {Object<json>}

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

    # Get project data from request
    data = request.get_json()

    # Verify that all required project data was sent
    # TODO: Add topics as required. Do I have to post directly to
    # topics table or can I post to relationship table???
    if not data['title'] or not data['description']:
        return make_response(jsonify({'error': 'Missing data!'}), 400)

    # Create project object
    project = Project(
        title=data['title'],
        description=data['description'],
        created_at=datetime.utcnow())

    # Add additional non-required project data if it was sent
    if 'img_url' in data:
        project.img_url = data['img_url']

    if 'alt' in data:
        project.alt = data['alt']

    if 'site_url' in data:
        project.site_url = data['site_url']

    if 'github_url' in data:
        project.github_url = data['github_url']

    if 'read_me' in data:
        project.read_me = data['read_me'].encode()

    if 'topic_main' in data:
        project.topic_main = data['topic_main']

    # Try to add project to database
    try:
        db.session.add(project)
        db.session.commit()

    # If project name already in database, return error
    except IntegrityError:
        return jsonify({
            'error': 'User with name or email already exists'
        }), 400

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    if 'topics' in data:
        for id in data['topics']:

            # Create project topics object
            project_topics = ProjectTopics(
                project_id=project.id,
                topic_id=id)

            # Try to add project_topics to database
            try:
                db.session.add(project_topics)
                db.session.commit()

            # If project name already in database, return error
            except IntegrityError:
                return jsonify({
                    'error': 'User with name or email already exists'
                }), 400

            # If some other sqlalchemy error is thrown, return error
            except SQLAlchemyError:
                return jsonify({'error': 'Some problem occurred!'}), 400

    # Serialze the project object and return json response
    project_schema = ProjectSchema()
    output = project_schema.dump(project).data

    return jsonify({
        'success': 'Successfully retrieved project.',
        'project': output
    }), 200


@api.route('/project/<id>', methods=['PUT'])
@jwt_required
@roles_required('admin')
def edit_project(id):
    """
    This route edits a project in the database and
    returns the updated project asa json object.

    Returns {Object<json>} 200
            success: {string}
            project: {Object<json>}

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

    # Try to get the project from the database
    query = Project.query.filter_by(id=id)

    try:
        project = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Get the project data from the request
    data = request.get_json()

    # Update project data if it was sent and save in database
    if 'title' in data:
        project.title = data['title']

    if 'description' in data:
        project.description = data['description']

    if 'img_url' in data:
        project.img_url = data['img_url']

    if 'alt' in data:
        project.alt = data['alt']

    if 'site_url' in data:
        project.site_url = data['site_url']

    if 'github_url' in data:
        project.github_url = data['github_url']

    if 'read_me' in data:
        project.read_me = data['read_me'].encode()

    if 'topic_main' in data:
        project.topic_main = data['topic_main']

    db.session.commit()

    # Try to get the project topics from the database
    query = ProjectTopics.query.filter_by(project_id=project.id)

    try:
        topics = query.all()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    topicIds = []

    # topicIds = [1, 2]
    # data['topics'] = [1, 2, 3, 4, 5] 3, 4, 5 added, 1,2 deleted
    for topic in topics:
        topicIds.append(topic.topic_id)

    app.logger.info(topicIds)

    if 'topics' in data:
        for id in data['topics']:
            app.logger.info(id)
            if id not in topicIds:
                # Create project topics object
                project_topics = ProjectTopics(
                    project_id=project.id,
                    topic_id=id)

                # Try to add project_topics to database
                try:
                    db.session.add(project_topics)
                    db.session.commit()

                # If project name already in database, return error
                except IntegrityError:
                    return jsonify({
                        'error': 'User with name or email already exists'
                    }), 400

                # If some other sqlalchemy error is thrown, return error
                except SQLAlchemyError:
                    return jsonify({'error': 'Some problem occurred!'}), 400

        for id in topicIds:
            if id not in data['topics']:
                index = topicIds.index(id)
                topic = topics[index]

                db.session.delete(topic)
                db.session.commit()

    # Serialize project
    project_schema = ProjectSchema()
    output = project_schema.dump(project).data

    # Create json and return response
    return jsonify({
        'success': 'The user has been updated',
        'project': output
    })


@api.route('/project/<id>', methods=['DELETE'])
@jwt_required
@roles_required('admin')
def delete_project(id):
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

    # Try to get the project from the database
    query = Project.query.filter_by(id=id)

    try:
        project = query.one()

    # If no result found, return error
    except NoResultFound:
        return jsonify({'error': 'No result found!'}), 404

    # If some other sqlalchemy error is thrown, return error
    except SQLAlchemyError:
        return jsonify({'error': 'Some problem occurred!'}), 400

    # Delete the project from the database
    db.session.delete(project)
    db.session.commit()

    # Create json and return response
    return jsonify({
        'success': 'The project has been deleted!',
        'id': str(project.id)
    })
