from app.mail import mail
from app.mail.utils.emails import send_contact_email, send_thank_you_email
from flask import request, jsonify
from app import app


@mail.route('/contact', methods=['POST'])
def contact():
    '''This path takes in contact info and sends an email to
    support@pydino.com as well as an email to the contact user

    Returns {Object<json>} 200
            success: {string}
    '''
    # Get the contact info from the request
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing username or email'}), 400

    user = {
        'name': data['name'],
        'email': data['email'],
    }

    message = data['message']

    # Send contact email to support@pydno.com
    send_contact_email(user, message)

    # Send thank you email to user
    send_thank_you_email(user)

    # Return json response with success message
    success = ('Your message has been sent to %s. '
               'Our team will get back to you shortly.') % (app.config.get('MAIL_USERNAME'))

    return jsonify({'success': success}), 200
