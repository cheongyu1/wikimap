#myproject1/app/__init__.py
from flask import Flask, jsonify, request, render_template, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.models import db
from app import main_views
from geopy.geocoders import Nominatim
from bs4 import BeautifulSoup
from googletrans import Translator
import os
import traceback
import re
import requests  # requests 모듈 추가


def create_app():
    app = Flask(__name__)
    
    # 이 부분을 추가하여 favicon.ico 요청을 무시
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

    # 임의의 시크릿 키 설정
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'user.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # instance 폴더가 존재하는지 확인
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 데이터베이스 초기화
    db.init_app(app)

    # 마이그레이션 설정
    migrate = Migrate(app, db)

    # 모델 클래스 import
    from app.models import User  # models.py에서 User import

    # 블루프린트 등록
    from app.main_views import bp as main_bp
    app.register_blueprint(main_bp)

    # 블루프린트 등록
    # app.register_blueprint(main_views.bp, url_prefix='/main')


    @app.errorhandler(Exception)
    def handle_error(e):
        traceback.print_exc()  # 추가: 전체 오류 추적을 출력합니다.
        return f"An error occurred: {str(e)}", 500

    @app.route('/reverse_geocode', methods=['GET'])
    def reverse_geocode():
        latitude = float(request.args.get('lat'))
        longitude = float(request.args.get('lng'))

        geolocator = Nominatim(user_agent="reverse_geocoding")
        location = geolocator.reverse((latitude, longitude), language='en')

        city_name = location.raw['address'].get('city', None)
        
        if city_name is None:
            return jsonify({'error': '위치 정보가 정확하지 않습니다.'})
        else:
            return jsonify({'address': city_name})

    @app.route('/wikipedia_info', methods=['POST'])
    def wikipedia_info():
        keyword = request.form['keyword']

        # Wikipedia API를 사용하여 키워드 검색
        search_url = "https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={}".format(keyword)
        response = requests.get(search_url)
        search_results = response.json()

        # 검색 결과 중 첫 번째 문서에 접근
        if 'query' in search_results and 'search' in search_results['query'] and search_results['query']['search']:
            first_result_title = search_results['query']['search'][0]['title']

            # 해당 문서의 HTML 가져오기
            article_url = "https://en.wikipedia.org/wiki/{}".format(first_result_title)
            article_response = requests.get(article_url)
            article_html = article_response.text

            # HTML에서 <table class="infobox">에 해당하는 요소 저장
            soup = BeautifulSoup(article_html, 'html.parser')
            infobox_table = soup.find('table', {'class': 'infobox'})

            if infobox_table:
                # <p> 태그 내용 추출
                first_paragraph = infobox_table.find_next('p').get_text()

                # 첫 번째 이미지 URL 추출
                first_image = infobox_table.find('img')['src'] if infobox_table.find('img') else None

                # 검색 결과와 번역된 내용
                search_result = get_search_result_info(first_result_title)
                translated_description = translate_to_korean(first_paragraph)

                # information.html로 이동하며 정보를 렌더링
                return render_template('information.html', search_result=search_result, description=translated_description, first_image_url=first_image)

        # 검색 결과가 없을 경우 홈페이지로 리다이렉트
        return redirect('/select_map')

    def translate_to_korean(text):
        translator = Translator()
        translated_text = translator.translate(text, src='en', dest='ko').text

        # 대괄호와 그 안의 숫자를 정규 표현식을 사용하여 제거
        cleaned_text = re.sub(r'\[\d+\]', '', translated_text)

        return cleaned_text

    def get_search_result_info(title):
        search_url = "https://en.wikipedia.org/w/api.php?action=query&format=json&titles={}".format(title)
        response = requests.get(search_url)
        search_results = response.json()

        if 'query' in search_results and 'pages' in search_results['query']:
            page_id = next(iter(search_results['query']['pages']))
            search_result = {'title': search_results['query']['pages'][page_id]['title']}
            return search_result

        return {'title': '검색 결과 없음'}  # 검색 결과가 없을 경우의 기본 값
      
    return app

