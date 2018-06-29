from flask_mail import Message
from app import app, mail
from flask import render_template, current_app


def _render_email(filename, **kwargs):
    '''Renders an email using a flask html template

    Arg {string} filename
    Arg {Array} **kwargs

    Returns {string} subject
            {string} html_message
            {string} text_message
    '''
    # Render subject
    subject = render_template(filename+'_subject.txt', **kwargs)
    # Make sure that subject lines do not contain newlines
    subject = subject.replace('\n', ' ')
    subject = subject.replace('\r', ' ')
    # Render HTML message
    html_message = render_template(filename+'_message.html', **kwargs)
    # Render text message
    text_message = render_template(filename+'_message.txt', **kwargs)

    return (subject, html_message, text_message)


def send_email(recipient, subject, html_message, text_message):
    '''Send email from default sender to recipient

    Arg {string} recipient
        {string} subject
        {string} html_message
        {string} text_message
    '''

    # Disable email sending when testing
    if current_app.testing:
        return

    class SendEmailError(Exception):
        pass

    # Make sure that Flask-Mail has been installed
    try:
        from flask_mail import Message

    except Exception as ex:
        raise SendEmailError(
            ("Flask-Mail has not been installed. Use "
             "'pip install Flask-Mail' to install Flask-Mail."))

    # Make sure that Flask-Mail has been initialized
    mail_engine = current_app.extensions.get('mail', None)
    if not mail_engine:
        raise SendEmailError(
            ('Flask-Mail has not been initialized. Initialize Flask-Mail '
             'or disable USER_SEND_PASSWORD_CHANGED_EMAIL, '
             'USER_SEND_REGISTERED_EMAIL and '
             'USER_SEND_USERNAME_CHANGED_EMAIL'))

    # Try to send email to recipient
    try:

        # Construct Flash-Mail message
        message = Message(
                subject,
                recipients=[recipient],
                html=html_message,
                body=text_message)

        mail_engine.send(message)

    # Print helpful error messages on exceptions
    except (socket.gaierror, socket.error) as e:
        raise SendEmailError(
            ('SMTP Connection error: Check your MAIL_SERVER '
             'and MAIL_PORT settings.'))
    except smtplib.SMTPAuthenticationError:
        raise SendEmailError(
            ('SMTP Authentication error: Check your MAIL_USERNAME '
             'and MAIL_PASSWORD settings.'))


def send_confirm_email_email(user, user_email, confirm_email_link):
    '''Sends a confirmation email link to recipient

    Arg {Object} user
        {string} email
        {string} confirm_email_link
    '''
    # Retrieve email address from User or UserEmail object
    email = user_email if user_email else user.email
    assert(email)

    # Render subject, html message and text message
    subject, html_message, text_message = _render_email(
            '/confirm_email',
            user=user,
            app_name=app.config.get('APP_NAME'),
            confirm_email_link=confirm_email_link)

    # Send email message using Flask-Mail
    send_email(email, subject, html_message, text_message)


def send_forgot_password_email(user, user_email, reset_password_link):
    '''Sends a forgot password email link to recipient

    Arg {Object} user
        {string} user_email
        {string} reset_password_link
    '''
    # Retrieve email address from User or UserEmail object
    email = user_email if user_email else user.email
    assert(email)

    # Render subject, html message and text message
    subject, html_message, text_message = _render_email(
            '/forgot_password',
            user=user,
            app_name=app.config.get('APP_NAME'),
            reset_password_link=reset_password_link)

    # Send email message using Flask-Mail
    send_email(email, subject, html_message, text_message)


def send_contact_email(user, message):
    '''Sends a contact email to support@pydino.com

    Arg {object} user - name, email
        {string} message
    '''
    # Retrieve email address from User or UserEmail object
    email = app.config.get('MAIL_USERNAME')
    assert(email)

    # Render subject, html message and text message
    subject, html_message, text_message = _render_email(
            '/contact',
            user=user,
            message=message)

    # Send email message using Flask-Mail
    send_email(email, subject, html_message, text_message)


def send_thank_you_email(user):
    '''Sends a thank you email to the recipient

    Arg {object} user - name, email
    '''
    # Retrieve email address from user
    email = user['email']
    assert(email)

    # Render subject, html message and text message
    subject, html_message, text_message = _render_email(
            '/thank_you',
            user=user,
            app_name=app.config.get('APP_NAME'))

    # Send email message using Flask-Mail
    send_email(email, subject, html_message, text_message)


def send_all_email(user, subj, message):
    '''Sends a thank you email to the recipient

    Arg {object} user - name, email
    '''
    # Retrieve email address from user
    email = user.email
    assert(email)

    # Render subject, html message and text message
    subject, html_message, text_message = _render_email(
            '/email',
            user=user,
            subj=subj,
            message=message,
            app_name=app.config.get('APP_NAME'))

    # Send email message using Flask-Mail
    send_email(email, subject, html_message, text_message)
