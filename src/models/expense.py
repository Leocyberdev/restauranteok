from src.database import db

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    expense_type = db.Column(db.String(50), nullable=False)  # Changed from 'type' to 'expense_type'
    date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<Expense {self.description} - {self.amount}>'


