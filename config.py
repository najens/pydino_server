# Configure app
DEBUG = True
APP_NAME = 'PyDino'
SECRET_KEY = 'REPLACE THIS WITH SOMETHING SUPER SECRET FOR PRODUCTION'
DOMAIN = 'localhost:3000'

# DB Configurations
POSTGRES_USER = 'najens'
POSTGRES_PW = 'n2T13j88'
POSTGRES_URL = 'pydino.com'
POSTGRES_PORT = '5432'
POSTGRES_DB = 'fantasy_wc'
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}:{port}/{db}'.format(
    user=POSTGRES_USER, pw=POSTGRES_PW, url=POSTGRES_URL,
    port=POSTGRES_PORT, db=POSTGRES_DB)
SQLALCHEMY_DATABASE_URI = DB_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False
JSON_SORT_KEYS = False

# JWT Cookie Configurations
JWT_TOKEN_LOCATION = ['cookies']
JWT_COOKIE_SECURE = False  # Set to True in production
JWT_ACCESS_COOKIE_PATH = '/api/'
JWT_ACCESS_CSRF_COOKIE_PATH = '/api/'
JWT_REFRESH_COOKIE_PATH = '/token/refresh'
JWT_REFRESH_CSRF_COOKIE_PATH = '/token/refresh'
JWT_COOKIE_SAMESITE = 'Strict'
# JWT_COOKIE_DOMAIN = 'localhost'
JWT_COOKIE_CSRF_PROTECT = True
JWT_SECRET_KEY = 'REPLACE THIS WITH SOMETHING SUPER SECRET FOR PRODUCTION'

# Flask-Mail settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USE_TLS = False
MAIL_USERNAME = 'support@pydino.com'
MAIL_PASSWORD = 'n2T13j88!'
MAIL_DEFAULT_SENDER = '<PyDino support@pydino.com>'
