# myproject1/run.py
from app import create_app, db
from flask import send_from_directory
from flask_migrate import Migrate
import os

app = create_app()

app.static_folder = 'static'

# 데이터베이스 초기화
with app.app_context():
    # 데이터베이스 마이그레이션 설정
    migrate = Migrate(app, db)

@app.route('/static/www/.well-known/pki-validation/<filename>')
def download_file(filename):
    return send_from_directory(os.path.join(app.static_folder, 'www/.well-known/pki-validation'), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8801)
