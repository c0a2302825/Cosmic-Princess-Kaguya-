from flask import Flask, render_template, request, redirect, url_for, flash
from database import SessionLocal, init_db
from kaguya_models import Goods
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# データベース初期化
init_db()

@app.route('/')
def index():
    session = SessionLocal()
    goods = session.query(Goods).all()
    session.close()
    return render_template('kaguya_index.html', goods=goods)

@app.route('/add', methods=['GET', 'POST'])
def add_goods():
    if request.method == 'POST':
        session = SessionLocal()
        new_goods = Goods(
            name=request.form['name'],
            category=request.form['category'],
            description=request.form.get('description', ''),
            price=float(request.form['price']),
            stock=int(request.form['stock']),
            image_url=request.form.get('image_url', '')
        )
        session.add(new_goods)
        session.commit()
        session.close()
        flash('グッズを追加しました！')
        return redirect(url_for('index'))
    return render_template('add_goods.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_goods(id):
    session = SessionLocal()
    goods = session.query(Goods).filter(Goods.id == id).first()
    if not goods:
        session.close()
        flash('グッズが見つかりません')
        return redirect(url_for('index'))

    if request.method == 'POST':
        goods.name = request.form['name']
        goods.category = request.form['category']
        goods.description = request.form.get('description', '')
        goods.price = float(request.form['price'])
        goods.stock = int(request.form['stock'])
        goods.image_url = request.form.get('image_url', '')
        session.commit()
        session.close()
        flash('グッズを更新しました！')
        return redirect(url_for('index'))

    session.close()
    return render_template('edit_goods.html', goods=goods)

@app.route('/delete/<int:id>')
def delete_goods(id):
    session = SessionLocal()
    goods = session.query(Goods).filter(Goods.id == id).first()
    if goods:
        session.delete(goods)
        session.commit()
        flash('グッズを削除しました！')
    session.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)