from app import app, db, Ticket
import sqlite3

def migrate_data():
    # Connect to the old database
    old_conn = sqlite3.connect('/home/zizekiando/rifa/old_rifa.db')
    old_cursor = old_conn.cursor()

    # Use Flask app context
    with app.app_context():
        # First, clear existing data
        Ticket.query.delete()
        db.session.commit()

        # Get data from old database
        old_cursor.execute('SELECT number, status FROM tickets')
        tickets = old_cursor.fetchall()

        # Migrate each ticket
        for number, status in tickets:
            print(f'Migrating ticket {number} with status {status}')
            ticket = Ticket(
                number=number,
                status=status  # Keep the English status names as they are
            )
            db.session.add(ticket)

        # Commit all changes
        db.session.commit()
        print("Migration completed successfully!")

    old_conn.close()

if __name__ == '__main__':
    migrate_data()
