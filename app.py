from flask import Flask, render_template, request, redirect, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta

# Initialize Flask application
app = Flask(__name__)

# Configure database URI for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/zizekiando/rifa/rifa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Required for session management

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database model for raffle tickets
class Ticket(db.Model):
    # Stores ticket number (1-100) and payment status
    number = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='available')
    timestamp = db.Column(db.DateTime, default=db.func.now())
    # New reservation fields
    reserved = db.Column(db.Boolean, default=False)
    reserved_until = db.Column(db.DateTime, nullable=True)
    reserved_by = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            'number': self.number,
            'status': self.status,
            'reserved': self.reserved,
            'reserved_until': self.reserved_until.isoformat() if self.reserved_until else None
        }

# CLI command for database initialization
@app.cli.command("init-db")
def init_db_command():
    """Inicializar la base de datos"""
    with app.app_context():
        db.create_all()
        if Ticket.query.count() == 0:
            for num in range(1, 101):
                db.session.add(Ticket(number=num))
            db.session.commit()
    print("¡Base de datos inicializada exitosamente!")

# Reservation routes
@app.route('/reserve/<int:number>', methods=['POST'])
def reserve_number(number):
    ticket = Ticket.query.get(number)
    if ticket and ticket.status == 'available' and not ticket.reserved:
        ticket.reserved = True
        ticket.reserved_until = datetime.utcnow() + timedelta(minutes=30)
        ticket.reserved_by = session.get('user_id', None)  # We'll generate this in a moment
        db.session.commit()
        return jsonify({'success': True, 'ticket': ticket.to_dict()})
    return jsonify({'success': False, 'message': 'Number not available'})

@app.route('/release/<int:number>', methods=['POST'])
def release_number(number):
    ticket = Ticket.query.get(number)
    if ticket and ticket.reserved and ticket.reserved_by == session.get('user_id', None):
        ticket.reserved = False
        ticket.reserved_until = None
        ticket.reserved_by = None
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'No se puede liberar el número'})

# Public facing view showing available numbers
@app.route('/')
def public_view():
    if 'user_id' not in session:
        import uuid
        session['user_id'] = str(uuid.uuid4())
    
    # Clean up expired reservations
    expired = Ticket.query.filter(
        Ticket.reserved == True,
        Ticket.reserved_until < datetime.utcnow()
    ).all()
    
    for ticket in expired:
        ticket.reserved = False
        ticket.reserved_until = None
        ticket.reserved_by = None
    
    if expired:
        db.session.commit()
    
    # Retrieve all tickets from database
    tickets = Ticket.query.all()
    return render_template('public.html', tickets=tickets)

# Admin interface for updating payment status
@app.route('/admin', methods=['GET', 'POST'])
def admin_view():
    # Handle status updates from form submission
    if request.method == 'POST':
        # Get list of all ticket numbers
        all_tickets = {str(ticket.number): 'available' for ticket in Ticket.query.all()}
        
        # Update status based on checked boxes
        checked_numbers = request.form.getlist('numbers')
        for number in checked_numbers:
            all_tickets[number] = 'paid'
        
        # Update database
        for number, status in all_tickets.items():
            ticket = Ticket.query.get(int(number))
            if ticket:
                ticket.status = status
                # Clear any reservations if marked as paid
                if status == 'paid':
                    ticket.reserved = False
                    ticket.reserved_until = None
                    ticket.reserved_by = None
        
        db.session.commit()
        return redirect('/admin')
    
    # Display all tickets in admin interface
    tickets = Ticket.query.all()
    return render_template('admin.html', tickets=tickets)

if __name__ == '__main__':
    app.run(debug=True)
