import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from flask import Flask, render_template, request, redirect, url_for
import pickle
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        
        # Email server configuration
        sender_email = 'tecnocracy.nitrr@gmail.com'
        sender_password = 'jnca hltp hfuk yutb'
        receiver_email = email  # Use the email address provided in the form
        
        # Email to the user
        msg_to_user = MIMEMultipart()
        msg_to_user['From'] = sender_email
        msg_to_user['To'] = receiver_email
        msg_to_user['Subject'] = 'We Received Your Message'
        
        body_to_user = f"Hello {name},\n\nThank you for reaching out to us. We have received your message and will get back to you soon.\n\nYour Message:\n{message}\n\nBest regards,\nYour Company"
        msg_to_user.attach(MIMEText(body_to_user, 'plain'))
        
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            
            # Send email to the user
            text_to_user = msg_to_user.as_string()
            server.sendmail(sender_email, receiver_email, text_to_user)
            print('Email to user sent successfully')
            
            server.quit()
        except Exception as e:
            print(f"Failed to send email: {e}")
        
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

            if not user_id.startswith('U') or not merchant_id.startswith('M'):
                raise ValueError("Invalid user or merchant ID format")

            prediction = prediction_conversion_function(transaction_amount, transaction_type, user_id, merchant_id, old_balance_merchant, old_balance_user)
            
            return render_template('prediction_result.html', prediction=prediction)
        except Exception as e:
            print(f"Error processing request: {e}")
            return f"Error processing request: {str(e)}"
    
    return render_template('predict_form.html')

if __name__ == '__main__': 
    app.run(debug=True, port=5000, use_reloader=False)
