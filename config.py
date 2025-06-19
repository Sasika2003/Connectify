# config.py

class Config:
   SECRET_KEY = 'your_secret_key'

    # Remote MySQL Configuration (InfinityFree)
    MYSQL_HOST = os.getenv('DB_HOST', 'sql210.infinityfree.com')
    MYSQL_USER = os.getenv('DB_USER', 'if0_39273264')
    MYSQL_PASSWORD = os.getenv('DB_PASSWORD', 'your_password_here')
    MYSQL_DB = os.getenv('DB_NAME', 'if0_39273264_connectify')
    MYSQL_PORT = int(os.getenv('DB_PORT', 3306))
UPLOAD_FOLDER = '/path/to/upload/folder'
