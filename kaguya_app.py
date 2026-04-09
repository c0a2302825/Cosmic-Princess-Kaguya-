from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import SessionLocal, init_db
from kaguya_models import Goods, Possession
from datetime import datetime, date, timedelta
import calendar
import os
import logging
import traceback

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# ロギング設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# データベース初期化
init_db()

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Unhandled Error: {str(error)}")
    logger.error(traceback.format_exc())
    return jsonify({"error": str(error), "traceback": traceback.format_exc()}), 500

@app.route('/')
def index():
    # 現在の年月を取得（デフォルトは今月）
    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', datetime.now().month))
    
    # カレンダー生成（日本カレンダー：日曜日から開始）
    calendar.setfirstweekday(calendar.SUNDAY)
    cal = calendar.monthcalendar(year, month)
    
    # 発売日のグッズをカレンダーに表示
    day_goods = {}
    session = SessionLocal()
    
    # 月の最初の日から最後の日までのデータを取得
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    # 発売日が指定されているグッズを取得
    release_goods = session.query(Goods).filter(
        Goods.release_date >= start_date,
        Goods.release_date <= end_date
    ).all()
    
    # 日付ごとにグッズをまとめる
    for goods in release_goods:
        day = goods.release_date.day
        if day not in day_goods:
            day_goods[day] = []
        day_goods[day].append(goods)
    
    session.close()
    
    # 前月・次月の計算
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    return render_template('calendar.html', 
                         year=year, month=month, cal=cal,
                         day_goods=day_goods,
                         prev_year=prev_year, prev_month=prev_month,
                         next_year=next_year, next_month=next_month,
                         month_name=calendar.month_name[month])

@app.route('/goods')
def goods_list():
    session = SessionLocal()
    goods = session.query(Goods).all()
    session.close()
    return render_template('goods_list.html', goods=goods)
@app.route('/day/<int:year>/<int:month>/<int:day>', methods=['GET', 'POST'])
def day_detail(year, month, day):
    target_date = date(year, month, day)
    
    session = SessionLocal()
    
    if request.method == 'POST':
        possession_type = request.form.get('possession_type', 'current')
        
        # 既存の同じタイプの所持データを削除
        session.query(Possession).filter(
            Possession.date == target_date,
            Possession.status == possession_type
        ).delete()
        
        # 新しい所持データを追加
        selected_goods_ids = request.form.getlist('goods_ids')
        for goods_id in selected_goods_ids:
            quantity = int(request.form.get(f'quantity_{goods_id}', 1))
            if quantity > 0:
                possession = Possession(
                    date=target_date,
                    goods_id=int(goods_id),
                    quantity=quantity,
                    status=possession_type
                )
                session.add(possession)
        
        session.commit()
        type_display = '購入予定' if possession_type == 'planned' else '所持アイテム'
        flash(f'{year}年{month}月{day}日の{type_display}を更新しました！')
        return redirect(url_for('index'))
    
    # 現在の所持状況を取得（current と placed に分ける）
    possessions = session.query(Possession).filter(Possession.date == target_date).all()
    current_possessions = {p.goods_id: p.quantity for p in possessions if p.status == 'current'}
    planned_possessions = {p.goods_id: p.quantity for p in possessions if p.status == 'planned'}
    
    # すべてのグッズを取得
    all_goods = session.query(Goods).all()
    
    session.close()
    
    return render_template('day_detail.html', 
                         year=year, month=month, day=day,
                         all_goods=all_goods,
                         current_possessions=current_possessions,
                         planned_possessions=planned_possessions)
@app.route('/goods/add', methods=['GET', 'POST'])
def add_goods():
    if request.method == 'POST':
        session = SessionLocal()
        release_date_str = request.form.get('release_date', '')
        release_date = None
        if release_date_str:
            release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
        
        new_goods = Goods(
            name=request.form['name'],
            category=request.form['category'],
            description=request.form.get('description', ''),
            price=float(request.form['price']),
            stock=int(request.form['stock']),
            image_url=request.form.get('image_url', ''),
            release_date=release_date
        )
        session.add(new_goods)
        session.commit()
        session.close()
        flash('グッズを追加しました！')
        return redirect(url_for('goods_list'))
    return render_template('add_goods.html')

@app.route('/goods/edit/<int:id>', methods=['GET', 'POST'])
def edit_goods(id):
    session = SessionLocal()
    goods = session.query(Goods).filter(Goods.id == id).first()
    if not goods:
        session.close()
        flash('グッズが見つかりません')
        return redirect(url_for('goods_list'))

    if request.method == 'POST':
        goods.name = request.form['name']
        goods.category = request.form['category']
        goods.description = request.form.get('description', '')
        goods.price = float(request.form['price'])
        goods.stock = int(request.form['stock'])
        goods.image_url = request.form.get('image_url', '')
        
        release_date_str = request.form.get('release_date', '')
        if release_date_str:
            goods.release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
        else:
            goods.release_date = None
        
        session.commit()
        session.close()
        flash('グッズを更新しました！')
        return redirect(url_for('goods_list'))

    session.close()
    
    # カテゴリの選択状態を事前に設定
    categories = {
        'フィギュア': 'selected' if goods.category == 'フィギュア' else '',
        'ポスター': 'selected' if goods.category == 'ポスター' else '',
        'Tシャツ': 'selected' if goods.category == 'Tシャツ' else '',
        'アクセサリー': 'selected' if goods.category == 'アクセサリー' else '',
        'その他': 'selected' if goods.category == 'その他' else ''
    }
    
    return render_template('edit_goods.html', goods=goods, categories=categories)

@app.route('/goods/delete/<int:id>')
def delete_goods(id):
    session = SessionLocal()
    goods = session.query(Goods).filter(Goods.id == id).first()
    if goods:
        session.delete(goods)
        session.commit()
        flash('グッズを削除しました！')
    session.close()
    return redirect(url_for('goods_list'))

@app.route('/search')
def search_goods():
    query = request.args.get('q', '').strip()
    session = SessionLocal()
    
    if query:
        # 名前またはカテゴリで検索
        goods = session.query(Goods).filter(
            (Goods.name.contains(query)) | 
            (Goods.category.contains(query)) | 
            (Goods.description.contains(query))
        ).all()
    else:
        goods = []
    
    session.close()
    return render_template('search_results.html', query=query, goods=goods)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=True, use_reloader=False)