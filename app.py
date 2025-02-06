from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask application
app = Flask(__name__)

# Configure database URI for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rifa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model for raffle tickets
class Ticket(db.Model):
    # Stores ticket number (0-100) and payment status
    number = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='available')
    timestamp = db.Column(db.DateTime, default=db.func.now())

# CLI command for database initialization
@app.cli.command("init-db")
def init_db_command():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        if Ticket.query.count() == 0:
            for num in range(101):
                db.session.add(Ticket(number=num))
            db.session.commit()
    print("Database initialized successfully!")

# Public facing view showing available numbers
@app.route('/')
def public_view():
    # Retrieve all tickets from database
    tickets = Ticket.query.all()
    return render_template('public.html', tickets=tickets)

# Admin interface for updating payment status
@app.route('/admin', methods=['GET', 'POST'])
def admin_view():
    # Handle status updates from form submission
    if request.method == 'POST':
        # Get list of paid numbers from form data
        numbers = request.form.getlist('numbers')
        for number in numbers:
            ticket = Ticket.query.get(int(number))
            if ticket:
                ticket.status = 'paid'
        db.session.commit()
        return redirect('/admin')
    
    # Display all tickets in admin interface
    tickets = Ticket.query.all()
    return render_template('admin.html', tickets=tickets)

if __name__ == '__main__':
# 1. Create a GitHub repository
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git push -u origin main

# 2. Then sign up at pythonanywhere.com and:
- Create new web app
- Connect your GitHub repo
- Configure WSGI file:
  ```python
  import sys
  path = '/home/YOUR_USERNAME/YOUR_REPO'
  if path not in sys.path:
      sys.path.append(path)
  from app import app as application    app.run(debug=True)
