from app.mail import mail
from app.mail.utils.emails import send_all_emaill
from flask import request, jsonify
from app import app


@mail.route('/email', methods=['POST'])
def email():
    '''This path sends an email to all users from support@pydino.com

    Returns {Object<json>} 200
            success: {string}
    '''
    # Get the contact info from the request
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing subject or message'}), 400

    subj = data['subject']
    message = data['message']

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

    for user in users:
        app.logger.info(user)
        # Send email to all users
        # send_all_email(user, subj, message)

    user = {
        'name': 'Nate',
        'email': 'najens@gmail.com',
    }

    send_all_email(user, subj, message)

    # Return json response with success message
    success = 'Your message has been sent to all users'

    return jsonify({'success': success}), 200
