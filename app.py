import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from flask import Flask, render_template, request, redirect, url_for
import pickle
import datetime


app = Flask(__name__)

# Load your models
model_xgb = pickle.load(open('xgb_model.pkl', 'rb'))
standard_scaler_for_data = pickle.load(open('standered_scaler_for_X.pkl', 'rb'))
label_encoder_for_type = pickle.load(open('label_encoder_for_type.pkl', 'rb'))
label_encoder_for_nameDest = pickle.load(open('label_encoder_for_nameDest_C_M.pkl', 'rb'))

def prediction_conversion_function(transaction_amount, transaction_type, user_id, merchant_id, old_balance_merchant, old_balance_user):
    new_balance_user = old_balance_user - transaction_amount
    new_balance_merchant = old_balance_merchant + transaction_amount

    type_encoded = label_encoder_for_type.transform([transaction_type])[0]
    user_id_num = int(user_id[1:])
    merchant_id_num = int(merchant_id[1:])
    merchant_id_cat = merchant_id[:1]
    merchant_id_cat_encoded = label_encoder_for_nameDest.transform([merchant_id_cat])[0]

    data = pd.DataFrame({
        'type': [type_encoded],
        'Amount': [transaction_amount],
        'nameDest_num': [merchant_id_num],
        'oldbalanceOrg': [old_balance_user],
        'newbalanceOrg': [new_balance_user],
        'oldbalanceDest': [old_balance_merchant],
        'newbalanceDest': [new_balance_merchant],
        'nameDest_Cat': [merchant_id_cat_encoded]
    })

    scaler_data = standard_scaler_for_data.transform(data)

    # Replace this with actual model prediction logic
    prediction = model_xgb.predict(scaler_data)
    return prediction

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
            print("Received form data:", request.form)
            transaction_amount = float(request.form['transaction_amount'])
            transaction_time = datetime.datetime.strptime(request.form['transaction_time'], '%Y-%m-%dT%H:%M')
            transaction_type = request.form['transaction_type']
            old_balance_merchant = float(request.form['old_balance_merchant'])
            old_balance_user = float(request.form['old_balance_user'])
            user_id = request.form['user_id']
            merchant_id = request.form['merchant_id']

            

            prediction = prediction_conversion_function(transaction_amount, transaction_type, user_id, merchant_id, old_balance_merchant, old_balance_user)
            
            return render_template('prediction_result.html', prediction=prediction)
        except Exception as e:
            print(f"Error processing request: {e}")
            return f"Error processing request: {str(e)}"
    
    return render_template('predict_form.html')

if __name__ == '__main__': 
    app.run(debug=True, port=5000, use_reloader=False)
