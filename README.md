MrDoc: Symptom-Based Disease Diagnosis Web App

Overview

MrDoc is a responsive web application that utilizes machine learning to diagnose expected diseases based on user-provided symptoms. Powered by a RandomForestClassifier model, this app provides an interactive interface for users to input their symptoms and receive potential disease diagnoses.

Features

- Symptom-based disease diagnosis using machine learning (RandomForestClassifier)
- Responsive web design for seamless user experience
- Interactive interface for easy symptom input and diagnosis

Technologies Used

- Machine Learning: RandomForestClassifier
- Front-end: HTML, CSS, JavaScript, Bootstrap
- Back-end: Python(Flask), SQL
- Database: MySQL

Installation

1. Clone the repository: git clone https://github.com/Zeekay47/MrDoc.git
2. Open 'backend' folder
3. Install required dependencies: pip install -r requirements.txt
4. Run the application: 'python app.py' or 'flask run'

Usage

1. Open the web application in your browser: http://localhost:5000
2. Input your symptoms in the provided form
3. Receive potential disease diagnoses based on your symptoms

Model Details

- The RandomForestClassifier model is trained on a dataset of symptoms and diseases
- The model uses 17 features to predict disease diagnoses

Contributing

Contributions are welcome! If you'd like to contribute to MrDoc, please fork the repository and submit a pull request.

Acknowledgments

- Dataset from kaggle.com
- Flask backend framework with MySQL database
