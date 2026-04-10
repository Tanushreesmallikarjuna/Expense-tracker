from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.models import Expense
from app import db


tasks_bp = Blueprint('tasks', __name__)

CATEGORIES = ['Food', 'Transport', 'Shopping', 'Health', 'Bills', 'Entertainment', 'General']

@tasks_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    tasks = Expense.query.filter_by(user_id=session['user_id']).order_by(Expense.date.desc()).all()

    # ✅ Total
    total = sum(t.amount for t in tasks)

    # ✅ Per-category breakdown
    category_totals = {}
    for t in tasks:
        category_totals[t.category] = category_totals.get(t.category, 0) + t.amount

    return render_template('dashboard.html', tasks=tasks, total=total,
                           category_totals=category_totals, categories=CATEGORIES)


@tasks_bp.route('/add', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    title = request.form['title']
    amount = float(request.form.get('amount', 0))
    category = request.form.get('category', 'General')           # ✅ New
 
    new_task = Expense(title=title, amount=amount, category=category, user_id=session['user_id'])
    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for('tasks.dashboard'))


# ✅ New: Edit route
@tasks_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    task = db.session.get(Expense, id)

    if not task or task.user_id != session['user_id']:
        flash("Expense not found.")
        return redirect(url_for('tasks.dashboard'))

    if request.method == 'POST':
        task.title = request.form['title']
        task.amount = float(request.form['amount'])
        task.category = request.form.get('category', 'General')
        db.session.commit()
        flash("Expense updated!")
        return redirect(url_for('tasks.dashboard'))

    return render_template('edit.html', task=task, categories=CATEGORIES)


@tasks_bp.route('/delete/<int:id>')
def delete_task(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    task = db.session.get(Expense, id)

    if task and task.user_id == session['user_id']:
        db.session.delete(task)
        db.session.commit()

    return redirect(url_for('tasks.dashboard'))