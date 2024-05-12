#myproject1/app/main_views.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import db, User

bp = Blueprint('main', __name__, url_prefix='/')

# 메인 화면
@bp.route('/')
def index():
    # 사용자가 로그인한 경우 확인
    user_name = session.get('user_name', None)

    return render_template('main_page.html', user_name=user_name)

# 클러스터링 함수 추가
@bp.route('/map_with_clusters')
def map_with_clusters():
    return render_template('map_with_clusters.html')

# 회원가입 이벤트
@bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']

        new_user = User(username=username, password=password, name=name)
        db.session.add(new_user)
        db.session.commit()

        flash('회원가입이 완료되었습니다.', 'success')

        # URL 변경
        return redirect(url_for('main.login_page'))

    return render_template('add_user.html')

# 로그인 이벤트
@bp.route('/login_page', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            flash('로그인 성공!', 'success')
            print(f"User ID: {user.id}, User Name: {user.name}, User Username: {user.username}")

            # 세션에 사용자 이름 저장
            session['user_name'] = user.name

            # 로그인 성공 후 리다이렉트할 페이지를 'select_map'으로 설정
            return redirect(url_for('main.select_map'))
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'danger')

    # 세션 값 확인 (디버깅 목적)
    print(session.get('user_name'))
    print(session.get('user_username'))
    print(session.get('user_password'))

    return render_template('login_page.html')

@bp.route('/logout')
def logout():
    # 세션에서 사용자 이름 제거
    session.pop('user_name', None)

    # 로그아웃 후 리다이렉트할 페이지를 'main_page'로 설정
    return redirect(url_for('main.index'))


#지도 선택 화면 이동
@bp.route('/select_map')
def select_map():
    return render_template('select_map.html')

# 지도 선택 이벤트
@bp.route('/Asia_Clustering')
def Asia_Clustering():
    return render_template('/clustering/Asia_Clustering.html')
@bp.route('/Africa_Clustering')
def Africa_Clustering():
    return render_template('/clustering/Africa_Clustering.html')
@bp.route('/EU_Clustering')
def EU_Clustering():
    return render_template('/clustering/EU_Clustering.html')
@bp.route('/NA_Clustering')
def NA_Clustering():
    return render_template('/clustering/NA_Clustering.html')
@bp.route('/Oceania_Clustering')
def Oceania_Clustering():
    return render_template('/clustering/Oceania_Clustering.html')
@bp.route('/SA_Clustering')
def SA_Clustering():
    return render_template('/clustering/SA_Clustering.html')

@bp.route('/information')
def information():
    address = request.args.get('address')
    return render_template('information.html', address=address)