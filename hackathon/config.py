import os

class Config:
    SECRET_KEY = os.urandom(24)  # Generates a random key for each session
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True  # Turn off in production

# You can define other configurations for different environments
class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_database.sqlite'

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = 'YOUR_SECRET_KEY_HERE'  # Set a permanent key for production
    # You might also use a different database for production
