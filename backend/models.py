from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Define models
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    articles = db.relationship('Article', backref='category', lazy=True)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    is_featured = db.Column(db.Boolean, default=False)


class BodyPart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Symptom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    body_part_symptoms = db.relationship('BodyPartSymptom', backref='symptom', lazy=True)
    user_symptoms = db.relationship('UserSymptom', backref='symptom', lazy=True)
    conditions = db.relationship('Condition', backref='symptom', lazy=True)


class BodyPartSymptom(db.Model):
    body_part_id = db.Column(db.Integer, db.ForeignKey('body_part.id'), primary_key=True)
    symptom_id = db.Column(db.Integer, db.ForeignKey('symptom.id'), primary_key=True)


class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disease_name = db.Column(db.String(100))
    required_count = db.Column(db.Integer)
    description = db.Column(db.Text)
    conditions = db.relationship('Condition', backref='rule', lazy=True)
    precautions = db.relationship('Precaution', backref='rule', lazy=True)


class Precaution(db.Model):
    __tablename__ = 'precautions'
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id'), nullable=False)
    precaution = db.Column(db.String(255), nullable=False)


class Condition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id'))
    symptom_id = db.Column(db.Integer, db.ForeignKey('symptom.id'))
    condition_value = db.Column(db.String(50))
    severity = db.Column(db.Integer, nullable=True)
    duration = db.Column(db.Integer, nullable=True)


class UserSymptom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    symptom_id = db.Column(db.Integer, db.ForeignKey('symptom.id'))
    severity = db.Column(db.Integer)
    duration = db.Column(db.Integer)


class PreExistingCondition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    condition = db.Column(db.String(100))


class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    medication = db.Column(db.String(100))


class Diagnosis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    diagnosis = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    pre_existing_conditions = db.relationship('PreExistingCondition', backref='user', lazy=True)
    medications = db.relationship('Medication', backref='user', lazy=True)
    diagnoses = db.relationship('Diagnosis', backref='user', lazy=True)
    symptoms = db.relationship('UserSymptom', backref='user', lazy=True)
