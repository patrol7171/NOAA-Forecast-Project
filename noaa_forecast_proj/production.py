from .settings import *
import os



SECRET_KEY = os.environ['APP_SECRET_KEY']
DEBUG = False
GOOGLE_MAPS_API_KEY = os.environ['GOOGLE_MAPS_API_KEY']
IPSTACK_API_KEY = os.environ['IPSTACK_API_KEY']

# Configure the domain name using the environment variable Azure automatically creates
ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []

# WhiteNoise configuration
MIDDLEWARE = [                                                                   
    'django.middleware.security.SecurityMiddleware',                            
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',                      
    'django.middleware.common.CommonMiddleware',                                 
    'django.middleware.csrf.CsrfViewMiddleware',                                 
    'django.contrib.auth.middleware.AuthenticationMiddleware',                   
    'django.contrib.messages.middleware.MessageMiddleware',                      
    'django.middleware.clickjacking.XFrameOptionsMiddleware',                    
]

#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  
#STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# DBHOST is only the server name, not the full URL
hostname = os.environ['DBHOST']
# Configure Postgres database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DBNAME'],
        'HOST': hostname + ".postgres.database.azure.com",
        'USER': os.environ['DBUSER'] + "@" + hostname,
        'PASSWORD': os.environ['DBPASS'] 
    }
}

