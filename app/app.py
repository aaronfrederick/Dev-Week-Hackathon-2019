from flask import Flask, render_template, session, redirect, url_for, session
import numpy as np
from flask_wtf import FlaskForm
from wtforms import (StringField, RadioField, DecimalField, SubmitField)
from wtforms.validators import DataRequired
from clarifai.rest import ClarifaiApp

from takeImage import takeImage
from face_comparison import intruder

import pickle

with open('data/user_pass.pkl', 'rb') as f:
    user_pass_df = pickle.load(f)

#Load Api Keys
with open('data/api_keys.pickle', 'rb') as handle:
    api_keys = pickle.load(handle)

def confirm_login(username,password):

    final_dict = {}
    temp_list = []
    counter = 0

    result = user_pass_df.loc[(user_pass_df['user']==str(username)) & (user_pass_df['password']==str(password)),]
    if len(result) > 0:
        final_dict['valid'] = 1
    else:
        final_dict['valid'] = 0
    return final_dict

# we import the Twilio client from the dependency we just installed
from twilio.rest import Client

#Change the intruder_demo to include send_sms_intruder
def send_sms_intruder(safety=False, n_people=0):
    if safety:
        if n_people == 1:
            body = f"You are Safe! There is {n_people} person in this picture."
        else:
            body = f"You are Safe! There are {n_people} people in this picture."
    if not safety:
        if n_people == 1:
            body = f"Intruder Alert! There is someone we do not know in your home."
        else:
            body = f"Intruder Alert! We count {n_people} people that we do not know."


    # the following line needs your Twilio Account SID and Auth Token
    client = Client("TWILIO API KEY", api_keys['twilio'])
    if safety:
        media_url = "http://www.stickpng.com/assets/images/586aac1f1fdce414493f50fd.png"
    else:
        media_url = 'https://www.crosstimbersgazette.com/crosstimbersgazette/wp-content/uploads/2015/07/intruder.jpg'

    # change the "from_" number to your Twilio number and the "to" number
    # to the phone number you signed up for Twilio with, or upgrade your
    # account to send SMS to any phone number
    client.messages.create(to="YOUR PHONE NUMBER", from_="+15167011855", body=body, media_url= media_url) # if you need to attach multimedia to your message, else remove this parameter.
    return (True)

def send_sms_baby(lists):
    danger_low_list = lists[1]
    danger_high_list = lists[2]
    if len(lists[0]) == 0:
        body = f"Baby is missing!"
        media_url = "https://www.babycenter.com/ims/2015/04/720x365x177344571_wide.jpg.pagespeed.ic.nXNn-WGsN8.jpg"
    """
    elif len(lists[2]) != 0:
        body = f"High Danger Alert! These types of danger may be present: "
        for i, danger in enumerate(danger_high_list):
            if i == len(danger_high_list) - 1:
                body += f'{danger}.'
            else:
                body += f'{danger}, '
        media_url = "https://i.ytimg.com/vi/5B-YOjkPzJ4/maxresdefault.jpg"

    elif len(lists[1]) != 0:
        body = f"Potential Danger Alert! These potential dangers may be present: "
        for i, danger in enumerate(danger_low_list):
            if i == len(danger_high_list) - 1:
                body += f'{danger}.'
            else:
                body += f'{danger}, '
        media_url = "https://i.ytimg.com/vi/5B-YOjkPzJ4/maxresdefault.jpg"
        # the following line needs your Twilio Account SID and Auth Token
    """
    client = Client("TWILIO API KEY", api_keys['twilio'])
    # change the "from_" number to your Twilio number and the "to" number
    # to the phone number you signed up for Twilio with, or upgrade your
    # account to send SMS to any phone number
    client.messages.create(to="YOUR PHONE NUMBER", from_="+15167011855", body=body, media_url= media_url) # if you need to attach multimedia to your message, else remove this parameter.
    return (True)

app = Flask(__name__,static_url_path='/static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.config['SECRET_KEY'] = 'mysecretkey'

class InfoForm(FlaskForm):

    username = StringField("Username")
    password = StringField("Password")
    submit = SubmitField('Submit')

class DemosForm(FlaskForm):

    demo_selection = RadioField('Choose a demo', choices=[('intruder','intruder'),('baby','baby')])
    submit = SubmitField('Submit')

class TakeImageForm(FlaskForm):
    take_image_selection = RadioField('Take Image', choices=[('Yes','Yes'),('No','No')])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET','POST'])
def index():
    form = InfoForm()

    if form.validate_on_submit():

        # Grab the data from the breed on the form.
        session['Username'] = form.username.data;
        session['Password'] = form.password.data;

        results = confirm_login(session['Username'],session['Password'])
        print(results)

        if results['valid'] == 1:
            return redirect(url_for("main"))

    return render_template('index.html', form=form)

@app.route('/main', methods=['GET','POST'])
def main():

    demo_form = DemosForm()

    if demo_form.validate_on_submit():

        session['Demos Form'] = demo_form.demo_selection.data;

        if demo_form.demo_selection.data == 'intruder':
            return redirect(url_for("intruder_demo"))

        elif demo_form.demo_selection.data == 'baby':
            return redirect(url_for("baby_demo"))

    return render_template('main.html',demo_form=demo_form)

#First intruder alert page
@app.route('/intruder_demo', methods=['GET','POST'])
def intruder_demo():

    image_form = TakeImageForm()

    if image_form.validate_on_submit():

        session['Demos Form'] = image_form.take_image_selection.data;
        print(image_form.take_image_selection.data)

        if image_form.take_image_selection.data == 'Yes':
            takeImage()
            return redirect(url_for("intruder_results"))

    return render_template('intruder_demo.html',image_form=image_form)

#Results page
@app.route('/intruder_results', methods=['GET','POST'])
def intruder_results():

    n_people, safe = intruder('static/image.png',api_key=api_keys['clarifai'])
    results = [n_people,safe]

    if safe == True:
        send_sms_intruder(safety=safe, n_people=n_people)

    return render_template('intruder_results.html',results=results, safe=safe, n_people=n_people)

'''
Baby Functionality
'''
def is_something(parameters):

    [api_key,image_filepath,string_list,threshold] = parameters


    # Instantiate a new Clarifai app by passing in your API key.
    app = ClarifaiApp(api_key=api_key)

    # Choose one of the public models.
    model = app.public_models.general_model

    # Predict the contents of an image by passing in a URL.
    response = model.predict_by_filename(image_filepath, max_concepts=200)

    #Interate through response to find baby or child percentage
    relevant = []

    for result in response['outputs'][0]['data']['concepts']:
        if result['name'] in string_list and result['value'] > threshold:
                relevant.append(result['name'])

    return relevant

photo_counter = 130
general = lambda x: is_something(x)

@app.route("/baby_demo", methods=['POST','GET'])
def baby_demo():
    # placeholders
    global photo_counter
    try:
        if photo_counter >= 130:
                photo_counter = photo_counter - 130 + 10
        else:
            photo_counter += 20
    except:
        photo_counter = 0
    string = 23 + photo_counter
    print(string)
    if string <= 99:
        string = '0' + str(string)
    else:
        string = str(string)
    image = 'static/photo_data/frame00' + string + '.png'
    my_key = api_keys['clarifai']
    danger_low_list = ['toy','stand']
    danger_high_list = ['knife', 'drink', 'flame']
    missing_list = ['child','baby']
    isBaby = general([my_key, image, missing_list,0.8])
    detectLowDanger = general([my_key, image, danger_low_list,0])
    detectHighDanger = general([my_key, image,danger_high_list,0.1])
    if len(isBaby) == 0:
        send_sms_baby([isBaby,detectLowDanger,detectHighDanger])

    if len(isBaby) == 0:
        babyMissing = True
    else:
        babyMissing = False
    if babyMissing == True:
        # needs to be made different than intruder one
        # send_sms_intruder()
        print("True")
    return render_template('baby_demo.html', image = image, babyMissing = babyMissing, detectLowDanger = detectLowDanger, detectHighDanger = detectHighDanger)

if __name__ == "__main__":
    app.run(debug=True)
