# Flask- SQLAlchemy

# Context
To store and manage data, we need to integrate the Flask web application with a relational database. We need a solution that can seamlessly integrate Flask and provide ORM capabilities.

# Decision
We chose Flask-SQLAlchemy, a Flask extension that provides integration with SQLAlchemy, a powerful ORM (Object-Relational Mapper) for Python.

# Rationale
Database integration is facilitated by Flask-SQLAlchemy, which provides a Flask-friendly interface for working with databases. It provides object-relational mapping (ORM) features such as query building that simplify database operations and improve code maintainability. It also simplifies the complexity of raw SQL queries.

# Consequences
Pros:
*Flask-SQLAlchemy removes the complexity of database management, allowing developers to focus on application logic.
*SQLAlchemy's ORM features allow developers to manipulate database tables as Python objects, improving code readability and maintainability.
Cons:
*Developers unfamiliar with SQLAlchemy may need time to learn the ORM concepts and need practices.
*Flask-SQLAlchemy adds some overhead to the application, especially for complex database operations, compared to raw SQL queries.

# Sample code
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

class User(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   username = db.Column(db.String(80), unique=True, nullable=False)

if __name__ == '__main__':
   db.create_all()
   app.run(debug=True)


