import numpy as np 
import pandas as pd 
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from flask import Flask, render_template, request, redirect, url_for
import pickle 
import datetime

app = Flask(__name__)

# Uncomment and load your models when ready
# model_xgb = pickle.load(open('model.pkl', 'rb'))
# model_anomaly = pickle.load(open('anomaly_model.pkl', 'rb'))

def prediction_function(transaction_amount, transaction_time, transaction_type):
    # Replace this with actual model prediction logic
    return "Prediction function is under process"

@app.route('/')
def home():
    """For Home page"""
    return render_template('index.html')

@app.route('/contact', methods=['GET', 'POST']) 
def contact():
    """For Contact Page"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        print(f"Received message from {name} ({email}): {message}")
        return redirect(url_for('home'))
    return render_template('contact.html')


@app.route('/ab')
def about():
    """For About Page"""
    print("Found")
    return render_template('about.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    print(f"Request method: {request.method}")
    if request.method == 'POST':
        try:
            transaction_amount = float(request.form['transaction_amount'])
            transaction_time = datetime.datetime.strptime(request.form['transaction_time'], '%Y-%m-%dT%H:%M')
            transaction_type = request.form['transaction_type']
            
            prediction = prediction_function(transaction_amount, transaction_time, transaction_type)
            
            return render_template('prediction_result.html', prediction=prediction)
        except Exception as e:
            return f"Error processing request: {str(e)}"
    
    return render_template('predict_form.html')

    

if __name__ == '__main__': 
    app.run(debug=True, port=5000, use_reloader=False)
