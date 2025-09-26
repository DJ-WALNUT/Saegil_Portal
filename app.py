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
DEPARTMENTS = ['컴퓨터공학과', '전자공학과', '기계공학과', '화학공학과', '신소재공학과']
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
    log_columns = ['이름', '전화번호', '학번', '학과', '대여물품', '대여담당자', '대여시각', '반납여부', '반납담당자', '반납시각']
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
    return render_template('borrow_main.html', items=available_items.to_dict('records'), departments=DEPARTMENTS)

@app.route('/borrow', methods=['POST'])
def borrow_process():
    name = request.form.get('name')
    student_id = request.form.get('student_id')
    department = request.form.get('department')
    phone = request.form.get('phone')
    auth_code = request.form.get('auth_code')
    handler_name = request.form.get('handler_name') # 대여 담당자 이름 추가
    selected_items_str = request.form.get('selected_items')

    if not all([name, student_id, department, phone, auth_code, handler_name, selected_items_str]):
        flash('모든 항목을 올바르게 입력해주세요.')
        return redirect(url_for('borrow_main'))

    if auth_code != AUTH_CODE:
        flash('인증번호가 일치하지 않습니다.')
        return redirect(url_for('borrow_main'))

    selected_items = selected_items_str.split(',')
    stock_df = load_stock()

    for item_name in selected_items:
        item_index = stock_df.index[stock_df['물품'] == item_name].tolist()
        if item_index:
            idx = item_index[0]
            current_stock = stock_df.loc[idx, '재고현황']
            if current_stock > 0:
                stock_df.loc[idx, '재고현황'] -= 1
    save_stock(stock_df)

    # 로그 기록 (새 양식에 맞춰 수정)
    log_entry = {
        '이름': name,
        '전화번호': phone,
        '학번': student_id,
        '학과': department,
        '대여물품': ', '.join(selected_items),
        '대여담당자': handler_name,
        '대여시각': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        '반납여부': 'X', # 대여 시 'X'로 초기화
        '반납담당자': '',
        '반납시각': ''
    }
    add_log_entry(log_entry)

    session['borrowed_items'] = selected_items
    return redirect(url_for('success_page'))

@app.route('/success')
def success_page():
    borrowed_items = session.pop('borrowed_items', [])
    if not borrowed_items:
        return redirect(url_for('borrow_main'))
    
    borrow_date = datetime.now().strftime('%Y-%m-%d')
    return_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    return render_template('borrow_success.html', 
                           items=borrowed_items, 
                           borrow_date=borrow_date, 
                           return_date=return_date)


# --- 관리자 페이지 라우트 ---

@app.route('/setting', methods=['GET', 'POST'])
def setting_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
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

# --- 신규/수정된 반납 관련 라우트 ---
@app.route('/setting/return')
def setting_return():
    """반납 현황 페이지 (미반납 건만 표시)"""
    if not session.get('logged_in'):
        return redirect(url_for('setting_login'))

    log_df = load_log()
    # '반납여부'가 'X'인 데이터만 필터링
    unreturned_df = log_df[log_df['반납여부'] == 'X'].copy()
    # 인덱스를 함께 전달하여 각 항목을 고유하게 식별
    unreturned_items = unreturned_df.reset_index().to_dict('records')

    return render_template('setting_return.html', items=unreturned_items)

@app.route('/setting/process_return', methods=['POST'])
def process_return():
    # 반납 처리 로직
    if not session.get('logged_in'):
        return redirect(url_for('setting_login'))

    log_index = int(request.form.get('log_index'))
    handler_name = request.form.get('return_handler_name')

    if handler_name:
        log_df = load_log()
        # 전달받은 인덱스로 해당 대여 건을 찾아 정보 업데이트
        if log_index < len(log_df):
            log_df.loc[log_index, '반납여부'] = 'O'
            log_df.loc[log_index, '반납담당자'] = handler_name
            log_df.loc[log_index, '반납시각'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            selected_items = [x.strip() for x in log_df.loc[log_index, '대여물품'].split(',')]
            stock_df = load_stock()

            for item_name in selected_items:
                item_index = stock_df.index[stock_df['물품'] == item_name].tolist()
                if item_index:
                    idx = item_index[0]
                    current_stock = stock_df.loc[idx, '재고현황']
                    if current_stock >= 0: # -1은 그대로 -1, 0 이상은 올리기
                        stock_df.loc[idx, '재고현황'] += 1
            save_stock(stock_df)
                
            # 엑셀 파일 저장
            log_df.to_excel(LOG_FILE, index=False)
            flash('반납 처리가 완료되었습니다.')
                
        else:
            flash('잘못된 요청입니다.')
    else:
        flash('반납 담당자 이름을 입력해주세요.')
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