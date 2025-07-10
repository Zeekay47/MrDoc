import random
from datetime import datetime, timedelta
from flask import Flask, render_template, send_from_directory, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from models import db, User, BodyPart, Symptom, Rule, Diagnosis, UserSymptom, BodyPartSymptom, Article, Category
from functions import evaluate_symptoms, map_duration, map_severity

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:MySQL@localhost/healthcare_ddb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
CORS(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first() is not None:
        return jsonify({'message': 'Username already exists.'}), 400
    elif User.query.filter_by(email=data['email']).first() is not None:
        return jsonify({'message': 'Email already exists.'}), 400

    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_password, email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Login successful', 'user': {'username': user.username, 'email': user.email}})
    else:
        user = User.query.filter_by(email=data['username']).first()

    if user and check_password_hash(user.password, data['password']):
        if user and check_password_hash(user.password, data['password']):
            return jsonify({'message': 'Login successful', 'user': {'username': user.username, 'email': user.email}})
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


@app.route('/update-profile', methods=['POST'])
def update_profile():
    try:
        # Get JSON data from the request
        data = request.get_json()
        username = data.get('username')
        if not username:
            return jsonify({'success': False, 'message': 'Username is required'}), 400

        # Find the user by username
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        user.email = data.get('email')
        user.age = data.get('age')
        user.gender = data.get('gender')
        user.height = data.get('height')
        user.weight = data.get('weight')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully'}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred. Please try again.'}), 500


@app.route('/get_body_parts', methods=['GET'])
def get_body_parts():
    body_parts = BodyPart.query.all()
    body_part_list = [{'id': body_part.id, 'name': body_part.name} for body_part in body_parts]
    return jsonify({'body_parts': body_part_list})

@app.route('/getsymptoms', methods=['GET'])
def getsymptoms():
    try:
        symptoms = Symptom.query.all()
        if not symptoms:
            print(f"No symptoms found")
            return jsonify([])
        # Preparing the list of symptoms to be returned
        symptom_list = [{'id': symptom.id, 'name': symptom.name} for symptom in symptoms]
        return jsonify(symptom_list)
    except Exception as e:
        print(f"Error fetching symptoms: {str(e)}")
        return jsonify({'error': 'Failed to fetch symptoms'}), 500


@app.route('/get_symptoms/<int:body_part_id>', methods=['GET'])
def get_symptoms(body_part_id):
    try:
        symptoms = Symptom.query.join(BodyPartSymptom).filter(BodyPartSymptom.body_part_id == body_part_id).all()
        if not symptoms:
            print(f"No symptoms found for body part ID: {body_part_id}")
            return jsonify([])
        # Preparing the list of symptoms to be returned
        symptom_list = [{'id': symptom.id, 'name': symptom.name} for symptom in symptoms]
        return jsonify(symptom_list)

    except Exception as e:
        print(f"Error fetching symptoms for body part ID {body_part_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch symptoms'}), 500


@app.route('/symptom_description', methods=['GET'])
def symptom_description():
    symptom_name = request.args.get('name')
    symptom = Symptom.query.filter_by(name=symptom_name).first()
    if not symptom:
        return jsonify({'message': 'Symptom not found'}), 404

    return jsonify({'description': symptom.description})


# Route to fetch user data
@app.route('/api/user-data', methods=['GET'])
def get_user_data():
    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    response_data = {
        'username': user.username,
        'email': user.email,
        'age': user.age,
        'gender': user.gender,
        'height': user.height,
        'weight': user.weight,
    }
    return jsonify(response_data)


@app.route('/diagnose', methods=['POST'])
def diagnose():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400

        username = data.get('username')
        if not username:
            return jsonify({'error': 'Username is required'}), 400

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        symptoms_data = data.get('symptoms', [])
        if not isinstance(symptoms_data, list):
            return jsonify({'error': 'Symptoms should be a list'}), 400

        symptom_ids = [symptom_data.get('symptom') for symptom_data in symptoms_data]
        if not symptom_ids:
            return jsonify({'error': 'No symptoms provided'}), 400

        # Get diagnosis (returns numpy array)
        diagnosis = evaluate_symptoms(symptom_ids)

        # Convert numpy array to list for JSON serialization
        diagnosis_list = diagnosis.tolist() if hasattr(diagnosis, 'tolist') else list(diagnosis)

        return jsonify({
            'diagnosis': diagnosis_list,
            'status': 'success'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_diagnosis', methods=['POST'])
def save_diagnosis():
    try:
        data = request.get_json()
        username = data.get('username')
        diagnoses = data.get('diagnosis')  # Expecting a list of diagnoses
        if not username or not diagnoses:
            return jsonify({'error': 'Missing username or diagnoses'}), 400
        # Fetch the user by username
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        # Get the user ID from the user object
        user_id = user.id
        # Track existing diagnoses to prevent duplicates
        existing_diagnoses = {d.diagnosis for d in Diagnosis.query.filter_by(user_id=user_id).all()}

        # Add each diagnosis to the database if not already present
        for diagnosis in diagnoses:
            if diagnosis not in existing_diagnoses:
                new_diagnosis = Diagnosis(user_id=user_id, diagnosis=diagnosis)
                db.session.add(new_diagnosis)
                existing_diagnoses.add(diagnosis)  # Update existing diagnoses set
                db.session.commit()
        return jsonify({'message': 'Diagnoses saved successfully'}), 200

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"An error occurred while saving the diagnoses: {str(e)}")
        return jsonify({'error': 'Failed to save diagnoses', 'details': str(e)}), 500

@app.route('/api/get_diagnoses', methods=['GET'])
def get_diagnoses():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Missing username'}), 400

    user = User.query.filter_by(username=username).first()
    user_id = user.id

    diagnoses = Diagnosis.query.filter_by(user_id=user_id).all()
    diagnosis_data = []
    for diagnosis in diagnoses:
        rule = Rule.query.filter_by(disease_name=diagnosis.diagnosis).first()
        if rule:
            precautions = [p.precaution for p in rule.precautions]
        else:
            precautions = ["No precautions available"]

        diagnosis_info = {
            'diagnosis': diagnosis.diagnosis,
            'date': diagnosis.date,
            'description': rule.description if rule else "No description available",
            'precautions': precautions
        }
        diagnosis_data.append(diagnosis_info)

    return jsonify(diagnosis_data), 200

@app.route('/api/delete_old_diagnoses', methods=['POST'])
def trigger_delete_old_diagnoses():
    delete_old_diagnoses()
    return jsonify({'message': 'Old diagnoses deleted successfully'}), 200

def delete_old_diagnoses():
    with app.app_context():
        try:
            ten_days_ago = datetime.now() - timedelta(days=10)
            Diagnosis.query.filter(Diagnosis.date < ten_days_ago).delete()
            db.session.commit()
            print("Old diagnoses deleted successfully")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"An error occurred while deleting old diagnoses: {str(e)}")


@app.route('/api/featured_article', methods=['GET'])
def get_featured_article():
    articles = Article.query.filter_by(is_featured=True).all()
    if not articles:
        return jsonify({'error': 'No articles found'}), 404
    article = random.choice(articles)
    print(article.id, article.title)
    return jsonify({
        'id': article.id,
        'title': article.title,
        'content': article.content
    })


@app.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': category.id,
        'name': category.name
    } for category in categories])


@app.route('/articles/category/<int:category_id>', methods=['GET'])
def get_articles_by_category(category_id):
    articles = Article.query.filter_by(category_id=category_id).all()
    return jsonify([{
        'id': article.id,
        'title': article.title,
        'content': article.content
    } for article in articles])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    delete_old_diagnoses()
    return render_template('index.html')


@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory(app.template_folder, path)


# Create the tables in the database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
