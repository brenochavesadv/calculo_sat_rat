import os

class Config:
    # Database URL - set via environment or fallback to local MySQL
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:Bj150181@127.0.0.1:3306/sat_rat_paracuru"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 64 * 1024 * 1024
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
    REPORT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "static/reports"))

    # JWT secret key - set via environment or fallback to a stable long default for development.
    # Prefer setting the environment variable `JWT_SECRET_KEY` (or `SECRET_KEY`) to a long secret (>=32 bytes).
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or os.environ.get('SECRET_KEY') or 'super-secret-key-change-me-please-32-bytes-min'
    
    # JWT expirations (em minutos)
    JWT_ACCESS_TOKEN_EXPIRES_MIN = 1440
    JWT_REFRESH_TOKEN_EXPIRES_MIN = 43200  # 30 dias
    
    # Use cookies to send/store JWTs so standard browser navigation includes the token
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/auth/refresh'

## migrations:
## delete migrations folder and database if you want to reset everything
## flask db init
## flask db migrate -m "migration description"
## flask db upgrade
## para criar usuario admin: /login/createadmin