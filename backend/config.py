import os

API_PREFIX = '/api'
FRONTEND_ORIGINS = [x.strip() for x in os.getenv('FRONTEND_ORIGINS','http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000').split(',') if x.strip()]
