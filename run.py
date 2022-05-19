import os
from app import app

if __name__ == '__main__':
    if os.environ.get('FLASK_DEBUG', False):
        app.run()
    else:
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))