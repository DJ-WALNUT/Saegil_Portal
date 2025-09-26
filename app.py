import os
import sys
import io
import random
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from datetime import datetime, timedelta

# --- 기본 설정 ---
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
os.environ["PYTHONIOENCODING"] = "utf-8"

app = Flask(__name__)
app.secret_key = 'saegil-portal-secret-key-!@#$' 


# --- 상수 정의 ---
DATA_DIR = 'data'
STOCK_FILE = os.path.join(DATA_DIR, 'stuff_ongoing.xlsx')
LOG_FILE = os.path.join(DATA_DIR, 'borrow_log.xlsx')
MAJOR_FILE = os.path.join(DATA_DIR, 'major.xlsx')
AUTH_CODE = '0924'
ADMIN_PASSWORD = 'saegil0924'

# --- 헬퍼 함수 (데이터 처리) ---
def load_stock():
    if not os.path.exists(STOCK_FILE):
        df = pd.DataFrame({'물품': [], '재고현황': []})
        df.to_excel(STOCK_FILE, index=False)
    return pd.read_excel(STOCK_FILE)

def save_stock(df):
    df.to_excel(STOCK_FILE, index=False)

def load_log():
    # 새 양식의 컬럼 정의
    log_columns = ['이름', '전화번호', '학번', '학과', '대여물품', '대여담당자', '대여시각', '대여현황', '반납담당자', '반납시각']
    if not os.path.exists(LOG_FILE):
        df = pd.DataFrame(columns=log_columns)
        df.to_excel(LOG_FILE, index=False)
        return df
    
    df = pd.read_excel(LOG_FILE, dtype=str)
    df.fillna('', inplace=True)
    # 기존 파일에 새 컬럼이 없을 경우 추가 (호환성 유지)
    for col in log_columns:
        if col not in df.columns:
            df[col] = ''
    return df

def save_log(df):
    df = load_log()
    new_df = pd.concat([df, pd.DataFrame([df])], ignore_index=True)
    new_df.to_excel(LOG_FILE, index=False)

def load_majors(): # 학과 목록을 불러오는 함수 새로 추가
    """학과 엑셀 파일을 읽어 리스트로 반환합니다."""
    if not os.path.exists(MAJOR_FILE):
        # 파일이 없으면 기본값으로 비어있는 데이터프레임 생성
        df = pd.DataFrame({'학과명': []})
        df.to_excel(MAJOR_FILE, index=False)
    
    df = pd.read_excel(MAJOR_FILE)
    # '학과명' 컬럼의 모든 값을 리스트로 변환하여 반환
    return df['학과명'].tolist()

def add_log_entry(entry):
    df = load_log()
    new_df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    new_df.to_excel(LOG_FILE, index=False)

# --- 사용자 페이지 라우트 ---
@app.route('/')
def index():
    """메인 랜딩 페이지를 렌더링합니다."""
    image_folder = os.path.join(app.static_folder, 'files/img/main_scroll')
    images = []
    
    if os.path.exists(image_folder):
        all_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        # 사진이 5개 이상이면 5개만 랜덤으로 고르고, 아니면 있는대로 섞기
        if len(all_files) > 5:
            images = random.sample(all_files, 5) # 전체 목록에서 중복 없이 5개를 뽑음
        else:
            images = all_files
            random.shuffle(images) # 5개 이하일 경우 순서만 섞음
            
    return render_template('index.html', images=images)

@app.route('/borrow')
def borrow_main():
    stock_df = load_stock()
    available_items = stock_df[stock_df['재고현황'] >= -1] # -1, 0, 있음 모두 표시
    majors = load_majors()
    
    return render_template('borrow_main.html', items=available_items.to_dict('records'), departments=majors)

@app.route('/borrow/request', methods=['POST'])
def borrow_request():
    name = request.form.get('name')
    student_id = request.form.get('student_id')
    department = request.form.get('department')
    phone = request.form.get('phone')
    selected_items_str = request.form.get('selected_items')

    if not all([name, student_id, department, phone, selected_items_str]):
        flash('모든 항목을 올바르게 입력해주세요.')
        return redirect(url_for('borrow_main'))

    selected_items = selected_items_str.split(',')
    log_df = load_log()
    log_entry = {
        '이름': name, '전화번호': phone, '학번': student_id, '학과': department,
        '대여물품': ', '.join(selected_items),
        '대여담당자': '',
        '대여시각': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        '대여현황': '신청', # ✨ 상태를 '신청'으로 저장
        '반납담당자': '', '반납시각': ''
    }
    new_log_df = pd.concat([log_df, pd.DataFrame([log_entry])], ignore_index=True)
    save_log(new_log_df)
    session['requested_items'] = selected_items
    
    return redirect(url_for('success_page'))

def save_log(df):
    df.to_excel(LOG_FILE, index=False)

@app.route('/success')
def success_page():    
    requested_items = session.pop('requested_items', [])
    if not requested_items:
        return redirect(url_for('borrow_main'))
    
    borrow_date = datetime.now().strftime('%Y-%m-%d')
    return_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    return render_template('borrow_success.html', 
                           items=requested_items, 
                           borrow_date=borrow_date, 
                           return_date=return_date)

@app.route('/check', methods=['GET', 'POST'])
def check_rental_status():
    if request.method == 'POST':
        name = request.form.get('name')
        student_id = request.form.get('student_id')
        
        log_df = load_log()
        # 학번을 문자열로 변환하여 비교 (엑셀에서 숫자로 읽힐 수 있음)
        log_df['학번'] = log_df['학번'].astype(str)
        
        results = log_df[(log_df['이름'] == name) & (log_df['학번'] == student_id)]
        
        if not results.empty:
            user_info = results.iloc[0].to_dict()
            records = results.sort_values(by='대여시각', ascending=False).to_dict('records')
            # 반납기한 계산 (대여시각이 문자열이므로 datetime으로 변환 필요)
            for record in records:
                if record.get('대여현황') == '미반납' and record.get('대여시각'):
                    borrow_time = datetime.strptime(record['대여시각'], '%Y-%m-%d %H:%M:%S')
                    record['반납기한'] = (borrow_time + timedelta(days=7)).strftime('%Y-%m-%d')
                else:
                    record['반납기한'] = '-'
            return render_template('borrow_check.html', user_info=user_info, records=records)
        else:
            return render_template('borrow_check.html', no_records=True, search_name=name)
            
    return render_template('borrow_check.html')


# --- 관리자 페이지 라우트 ---

@app.route('/setting', methods=['GET', 'POST'])
def setting_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('setting_main'))
        else:
            flash('비밀번호가 틀렸습니다.')
    return render_template('setting_login.html')

@app.route('/setting/logout')
def setting_logout():
    session.pop('logged_in', None)
    return redirect(url_for('setting_login'))

@app.route('/setting/main')
def setting_main():
    if not session.get('logged_in'):
        return redirect(url_for('setting_login'))
    
    log_df = load_log()
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    if not log_df.empty and '대여시각' in log_df.columns:
        log_df['대여일'] = pd.to_datetime(log_df['대여시각']).dt.strftime('%Y-%m-%d')
        today_rentals = log_df[log_df['대여일'] == today_str].shape[0]
        recent_logs = log_df.tail(5).to_dict('records')[::-1]
    else:
        today_rentals = 0
        recent_logs = []

    return render_template('setting_main.html', today_rentals=today_rentals, recent_logs=recent_logs)

@app.route('/setting/ongoing', methods=['GET', 'POST'])
def setting_ongoing():
    if not session.get('logged_in'):
        return redirect(url_for('setting_login'))

    if request.method == 'POST':
        stock_df = load_stock()
        action = request.form.get('action')

        if action == 'update':
            for index, row in stock_df.iterrows():
                new_stock = request.form.get(f'stock_{index}')
                if new_stock is not None and new_stock.strip() != '':
                    stock_df.loc[index, '재고현황'] = int(new_stock)
        
        elif action == 'add':
            new_item_name = request.form.get('new_item_name').strip()
            new_item_stock = request.form.get('new_item_stock')
            if new_item_name and new_item_stock is not None and new_item_stock.strip() != '':
                if new_item_name not in stock_df['물품'].values:
                    new_row = pd.DataFrame([{'물품': new_item_name, '재고현황': int(new_item_stock)}])
                    stock_df = pd.concat([stock_df, new_row], ignore_index=True)
                else:
                    flash(f"'{new_item_name}'은(는) 이미 존재하는 물품입니다.")
        
        save_stock(stock_df)
        flash('재고 정보가 성공적으로 업데이트되었습니다.')
        return redirect(url_for('setting_ongoing'))
    
    stock_df = load_stock()
    return render_template('setting_ongoing.html', items=stock_df.to_dict('records'))

@app.route('/setting/log')
def setting_log():
    if not session.get('logged_in'):
        return redirect(url_for('setting_login'))
    
    log_df = load_log()
    logs = log_df.sort_values(by='대여시각', ascending=False).to_dict('records')
    return render_template('setting_log.html', logs=logs)

# ✨ 신규: 대여 수락 관리 페이지
@app.route('/setting/approve', methods=['GET', 'POST'])
def setting_approve():
    if not session.get('logged_in'): return redirect(url_for('setting_login'))
    
    log_df = load_log()
    requests_df = log_df[log_df['대여현황'] == '신청'].copy()
    
    search_name = request.form.get('search_name', '')
    if search_name:
        requests_df = requests_df[requests_df['이름'].str.contains(search_name, na=False)]
        
    requests = requests_df.sort_values(by='대여시각', ascending=False).reset_index().to_dict('records')
    return render_template('setting_approve.html', items=requests, search_name=search_name)

# ✨ 신규: 대여 수락 처리
@app.route('/setting/process_approval', methods=['POST'])
def process_approval():
    if not session.get('logged_in'): return redirect(url_for('setting_login'))

    log_index = int(request.form.get('log_index'))
    handler_name = request.form.get('handler_name')

    log_df = load_log()
    stock_df = load_stock()

    if log_index < len(log_df) and handler_name:
        items_to_borrow = log_df.loc[log_index, '대여물품'].split(', ')
        
        # 재고 확인
        can_borrow = True
        for item_name in items_to_borrow:
            stock_row = stock_df[stock_df['물품'] == item_name]
            if not stock_row.empty and stock_row.iloc[0]['재고현황'] <= 0:
                flash(f"'{item_name}'의 재고가 부족하여 대여를 수락할 수 없습니다.")
                can_borrow = False
                break
        
        if can_borrow:
            # 재고 차감
            for item_name in items_to_borrow:
                stock_idx = stock_df.index[stock_df['물품'] == item_name].tolist()[0]
                stock_df.loc[stock_idx, '재고현황'] -= 1
            save_stock(stock_df)

            # 로그 업데이트
            log_df.loc[log_index, '대여현황'] = '미반납'
            log_df.loc[log_index, '대여담당자'] = handler_name
            log_df.loc[log_index, '대여시각'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_log(log_df)
            flash('대여 신청을 수락했습니다.')
        
    return redirect(url_for('setting_approve'))

# ✨ 신규: 대여 신청 초기화
@app.route('/setting/reset_requests', methods=['POST'])
def reset_requests():
    if not session.get('logged_in'): return redirect(url_for('setting_login'))
    
    log_df = load_log()
    # '신청' 상태가 아닌 기록만 남김
    remaining_logs = log_df[log_df['대여현황'] != '신청']
    save_log(remaining_logs)
    flash('대기 중인 모든 대여 신청을 초기화했습니다.')
    return redirect(url_for('setting_approve'))

# ✨ 수정: 반납 현황 페이지에 검색 기능 추가
@app.route('/setting/return', methods=['GET', 'POST'])
def setting_return():
    if not session.get('logged_in'): return redirect(url_for('setting_login'))
    
    log_df = load_log()
    unreturned_df = log_df[log_df['대여현황'] == '미반납'].copy()
    
    search_name = request.form.get('search_name', '')
    if search_name:
        unreturned_df = unreturned_df[unreturned_df['이름'].str.contains(search_name, na=False)]
        
    unreturned_items = unreturned_df.sort_values(by='대여시각', ascending=False).reset_index().to_dict('records')
    return render_template('setting_return.html', items=unreturned_items, search_name=search_name)

# ✨ 수정: 반납 처리 로직
@app.route('/setting/process_return', methods=['POST'])
def process_return():
    if not session.get('logged_in'): return redirect(url_for('setting_login'))

    log_index = int(request.form.get('log_index'))
    handler_name = request.form.get('return_handler_name')
    
    if handler_name:
        log_df = load_log()
        
        if log_index < len(log_df):
            stock_df = load_stock()
            
            items_returned_str = log_df.loc[log_index, '대여물품']
            items_returned_list = items_returned_str.split(', ')
            
            for item_name in items_returned_list:
                item_indices = stock_df.index[stock_df['물품'] == item_name].tolist()
                if item_indices:
                    stock_idx = item_indices[0]
                    # 재고가 -1(확인중)이 아닌 경우에만 수량을 1 늘립니다.
                    if stock_df.loc[stock_idx, '재고현황'] != -1:
                        stock_df.loc[stock_idx, '재고현황'] += 1

            save_stock(stock_df)

            log_df.loc[log_index, '대여현황'] = '반납완료'
            log_df.loc[log_index, '반납담당자'] = handler_name
            log_df.loc[log_index, '반납시각'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_log(log_df)
            
            flash('반납 처리가 완료되었고, 재고가 업데이트되었습니다.')
            
    return redirect(url_for('setting_return'))

@app.route('/download/log')
def download_log_file():
    if not session.get('logged_in'):
        return redirect(url_for('setting_login'))
    return send_from_directory(DATA_DIR, 'borrow_log.xlsx', as_attachment=True)

# --- 애플리케이션 실행 ---
if __name__ == '__main__':
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    app.run(debug=True)