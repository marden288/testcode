"""
LIBRARY MANAGEMENT SYSTEM - WEB VERSION
Northwestern University - Ilocos Norte
Developed by: Jhasley Jay Corpuz
Theme: Maroon & Gold
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.secret_key = 'northwestern_university_library_system_2024'

# Data file paths
BOOKS_FILE = 'books.json'
MEMBERS_FILE = 'members.json'
TRANSACTIONS_FILE = 'transactions.json'

# Initialize data files if they don't exist
def init_data_files():
    if not os.path.exists(BOOKS_FILE):
        initial_books = {
            "B1001": {
                "book_id": "B1001",
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "isbn": "978-0-7432-7356-5",
                "copies": 3,
                "available_copies": 3,
                "category": "Fiction",
                "shelf_location": "A-1",
                "total_borrowed": 0
            },
            "B1002": {
                "book_id": "B1002",
                "title": "To Kill a Mockingbird",
                "author": "Harper Lee",
                "isbn": "978-0-06-112008-4",
                "copies": 2,
                "available_copies": 2,
                "category": "Classic",
                "shelf_location": "A-2",
                "total_borrowed": 0
            },
            "B1003": {
                "book_id": "B1003",
                "title": "Python Programming",
                "author": "John Smith",
                "isbn": "978-1-234-56789-0",
                "copies": 5,
                "available_copies": 5,
                "category": "Computer Science",
                "shelf_location": "B-1",
                "total_borrowed": 0
            }
        }
        with open(BOOKS_FILE, 'w') as f:
            json.dump(initial_books, f, indent=4)
    
    if not os.path.exists(MEMBERS_FILE):
        initial_members = {
            "M1001": {
                "member_id": "M1001",
                "name": "Juan Dela Cruz",
                "email": "juan@nwu.edu.ph",
                "phone": "09123456789",
                "address": "Ilocos Norte",
                "membership_type": "Regular",
                "borrowed_books": [],
                "total_borrowed": 0,
                "fine_balance": 0.0
            },
            "M1002": {
                "member_id": "M1002",
                "name": "Maria Santos",
                "email": "maria@nwu.edu.ph",
                "phone": "09123456790",
                "address": "Ilocos Norte",
                "membership_type": "Premium",
                "borrowed_books": [],
                "total_borrowed": 0,
                "fine_balance": 0.0
            }
        }
        with open(MEMBERS_FILE, 'w') as f:
            json.dump(initial_members, f, indent=4)
    
    if not os.path.exists(TRANSACTIONS_FILE):
        with open(TRANSACTIONS_FILE, 'w') as f:
            json.dump({}, f)

# Load data
def load_books():
    with open(BOOKS_FILE, 'r') as f:
        return json.load(f)

def load_members():
    with open(MEMBERS_FILE, 'r') as f:
        return json.load(f)

def load_transactions():
    with open(TRANSACTIONS_FILE, 'r') as f:
        return json.load(f)

# Save data
def save_books(books):
    with open(BOOKS_FILE, 'w') as f:
        json.dump(books, f, indent=4)

def save_members(members):
    with open(MEMBERS_FILE, 'w') as f:
        json.dump(members, f, indent=4)

def save_transactions(transactions):
    with open(TRANSACTIONS_FILE, 'w') as f:
        json.dump(transactions, f, indent=4)

# Helper functions
def generate_id(prefix):
    return f"{prefix}{random.randint(1000, 9999)}"

def calculate_fine(due_date):
    due = datetime.strptime(due_date, '%Y-%m-%d')
    today = datetime.now()
    if today > due:
        days_overdue = (today - due).days
        return days_overdue * 10
    return 0

# Routes
@app.route('/')
def index():
    books = load_books()
    members = load_members()
    transactions = load_transactions()
    
    total_books = len(books)
    total_members = len(members)
    active_loans = len([t for t in transactions.values() if t['status'] == 'Borrowed'])
    available_books = sum(book['available_copies'] for book in books.values())
    total_fines = sum(member['fine_balance'] for member in members.values())
    
    recent = sorted(transactions.values(), 
                   key=lambda x: x.get('borrow_date', ''), reverse=True)[:5]
    
    return render_template('index.html', 
                         total_books=total_books,
                         total_members=total_members,
                         active_loans=active_loans,
                         available_books=available_books,
                         total_fines=total_fines,
                         recent=recent)

@app.route('/books')
def books():
    books = load_books()
    return render_template('books.html', books=books)

@app.route('/add_book', methods=['POST'])
def add_book():
    try:
        books = load_books()
        book_id = generate_id('B')
        
        new_book = {
            'book_id': book_id,
            'title': request.form['title'],
            'author': request.form['author'],
            'isbn': request.form['isbn'],
            'copies': int(request.form['copies']),
            'available_copies': int(request.form['copies']),
            'category': request.form['category'],
            'shelf_location': request.form['shelf_location'],
            'total_borrowed': 0
        }
        
        books[book_id] = new_book
        save_books(books)
        flash(f'Book "{new_book["title"]}" added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding book: {str(e)}', 'danger')
    
    return redirect(url_for('books'))

@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    books = load_books()
    if book_id in books:
        del books[book_id]
        save_books(books)
        flash('Book deleted successfully!', 'success')
    else:
        flash('Book not found!', 'danger')
    
    return redirect(url_for('books'))

@app.route('/members')
def members():
    members = load_members()
    return render_template('members.html', members=members)

@app.route('/add_member', methods=['POST'])
def add_member():
    try:
        members = load_members()
        member_id = generate_id('M')
        
        new_member = {
            'member_id': member_id,
            'name': request.form['name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'address': request.form['address'],
            'membership_type': request.form['membership_type'],
            'borrowed_books': [],
            'total_borrowed': 0,
            'fine_balance': 0.0
        }
        
        members[member_id] = new_member
        save_members(members)
        flash(f'Member "{new_member["name"]}" added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding member: {str(e)}', 'danger')
    
    return redirect(url_for('members'))

@app.route('/delete_member/<member_id>')
def delete_member(member_id):
    members = load_members()
    if member_id in members:
        if len(members[member_id]['borrowed_books']) > 0:
            flash('Cannot delete member with borrowed books!', 'danger')
        else:
            del members[member_id]
            save_members(members)
            flash('Member deleted successfully!', 'success')
    else:
        flash('Member not found!', 'danger')
    
    return redirect(url_for('members'))

@app.route('/transactions')
def transactions():
    transactions = load_transactions()
    books = load_books()
    members = load_members()
    return render_template('transactions.html', 
                         transactions=transactions,
                         books=books,
                         members=members)

@app.route('/borrow', methods=['POST'])
def borrow():
    try:
        member_id = request.form['member_id']
        book_id = request.form['book_id']
        
        books = load_books()
        members = load_members()
        transactions = load_transactions()
        
        if member_id not in members:
            flash('Member not found!', 'danger')
            return redirect(url_for('transactions'))
        
        if book_id not in books:
            flash('Book not found!', 'danger')
            return redirect(url_for('transactions'))
        
        member = members[member_id]
        book = books[book_id]
        
        if member['fine_balance'] > 0:
            flash(f'Member has unpaid fine of ₱{member["fine_balance"]:.2f}!', 'danger')
            return redirect(url_for('transactions'))
        
        max_books = 5 if member['membership_type'] == 'Premium' else 3
        if len(member['borrowed_books']) >= max_books:
            flash(f'Borrowing limit reached! ({max_books} books max)', 'danger')
            return redirect(url_for('transactions'))
        
        if book['available_copies'] <= 0:
            flash('No available copies!', 'danger')
            return redirect(url_for('transactions'))
        
        trans_id = generate_id('T')
        borrow_date = datetime.now().strftime('%Y-%m-%d')
        due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        
        transaction = {
            'transaction_id': trans_id,
            'book_id': book_id,
            'member_id': member_id,
            'borrow_date': borrow_date,
            'due_date': due_date,
            'return_date': None,
            'fine': 0.0,
            'status': 'Borrowed'
        }
        
        transactions[trans_id] = transaction
        
        member['borrowed_books'].append(book_id)
        member['total_borrowed'] += 1
        book['available_copies'] -= 1
        book['total_borrowed'] += 1
        
        save_books(books)
        save_members(members)
        save_transactions(transactions)
        
        flash(f'Book borrowed successfully! Due date: {due_date}', 'success')
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('transactions'))

@app.route('/return_book', methods=['POST'])
def return_book():
    try:
        trans_id = request.form['transaction_id']
        
        transactions = load_transactions()
        books = load_books()
        members = load_members()
        
        if trans_id not in transactions:
            flash('Transaction not found!', 'danger')
            return redirect(url_for('transactions'))
        
        trans = transactions[trans_id]
        
        if trans['status'] == 'Returned':
            flash('Book already returned!', 'warning')
            return redirect(url_for('transactions'))
        
        book = books.get(trans['book_id'])
        member = members.get(trans['member_id'])
        
        if not book or not member:
            flash('Book or member not found!', 'danger')
            return redirect(url_for('transactions'))
        
        return_date = datetime.now()
        due_date = datetime.strptime(trans['due_date'], '%Y-%m-%d')
        fine = 0
        
        if return_date > due_date:
            days_overdue = (return_date - due_date).days
            fine = days_overdue * 10
            member['fine_balance'] += fine
        
        trans['return_date'] = return_date.strftime('%Y-%m-%d')
        trans['status'] = 'Returned'
        trans['fine'] = fine
        
        if trans['book_id'] in member['borrowed_books']:
            member['borrowed_books'].remove(trans['book_id'])
        book['available_copies'] += 1
        
        save_books(books)
        save_members(members)
        save_transactions(transactions)
        
        msg = 'Book returned successfully!'
        if fine > 0:
            msg += f' Fine charged: ₱{fine:.2f}'
        
        flash(msg, 'success')
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('transactions'))

@app.route('/fines')
def fines():
    members = load_members()
    members_with_fines = {k: v for k, v in members.items() if v['fine_balance'] > 0}
    return render_template('fines.html', members=members_with_fines)

@app.route('/pay_fine', methods=['POST'])
def pay_fine():
    try:
        member_id = request.form['member_id']
        amount = float(request.form['amount'])
        
        members = load_members()
        
        if member_id not in members:
            flash('Member not found!', 'danger')
            return redirect(url_for('fines'))
        
        member = members[member_id]
        
        if amount <= 0:
            flash('Amount must be greater than 0!', 'danger')
            return redirect(url_for('fines'))
        
        if amount > member['fine_balance']:
            flash('Amount exceeds fine balance!', 'danger')
            return redirect(url_for('fines'))
        
        member['fine_balance'] -= amount
        save_members(members)
        
        flash(f'Payment successful! Remaining fine: ₱{member["fine_balance"]:.2f}', 'success')
        
    except ValueError:
        flash('Invalid amount!', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('fines'))

@app.route('/reports')
def reports():
    books = load_books()
    members = load_members()
    transactions = load_transactions()
    
    popular_books = sorted(books.values(), 
                          key=lambda x: x['total_borrowed'], 
                          reverse=True)[:10]
    
    active_members = [m for m in members.values() if m['borrowed_books']]
    
    stats = {
        'total_books': len(books),
        'total_members': len(members),
        'active_members': len(active_members),
        'total_transactions': len(transactions),
        'active_loans': len([t for t in transactions.values() if t['status'] == 'Borrowed']),
        'total_fines': sum(m['fine_balance'] for m in members.values()),
        'total_borrowed_books': sum(b['total_borrowed'] for b in books.values())
    }
    
    return render_template('reports.html', 
                         popular_books=popular_books,
                         stats=stats,
                         members=members)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    search_type = request.args.get('type', 'books')
    
    if search_type == 'books':
        books = load_books()
        results = {k: v for k, v in books.items() 
                  if query in v['title'].lower() or 
                     query in v['author'].lower() or
                     query in v['category'].lower()}
        return render_template('search_results.html', results=results, query=query, type='books')
    else:
        members = load_members()
        results = {k: v for k, v in members.items() 
                  if query in v['name'].lower() or 
                     query in v['email'].lower()}
        return render_template('search_results.html', results=results, query=query, type='members')

# Initialize data files
init_data_files()

if __name__ == '__main__':
    app.run(debug=True)