import nltk
from flask import Flask, request, render_template,flash,redirect,session,abort,jsonify
from models import Model
from stress_detection_tweets import DepressionDetection
from TweetModel import process_message
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
import pandas as pd
import numpy as np

nltk.download('stopwords')

set(stopwords.words('english'))

# Configure Flask to use the correct template and static folders
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'HTML'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)


@app.route('/')
def root():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')


@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'admin' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else :
        flash('wrong password!')
    return root()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return root()

@app.route('/upload')
def upload():
    return render_template('upload.html')  

@app.route('/prediction1')
def prediction1():
    return render_template('index.html')  

@app.route('/chart')
def chart():
    return render_template('chart.html') 

@app.route('/preview', methods=["POST"])
def preview():
    dataset = request.files.get('datasetfile')
    if dataset is None:
        return render_template("upload.html", error="Please choose a dataset file.")
    try:
        df = pd.read_csv(dataset, encoding='unicode_escape')
    except Exception as e:
        return render_template("upload.html", error=f"Unable to read dataset file: {e}")
    df.set_index('Id', inplace=True)
    return render_template("preview.html", df_view=df)


@app.route("/sentiment")
def sentiment():
    return render_template("sentiment.html")




@app.route("/predictSentiment", methods=["POST"])
def predictSentiment():
    stop_words = stopwords.words('english')
    message = request.form.get('form10', '').strip()
    if not message:
        return render_template("sentiment.html", error="Please enter text for sentiment analysis.")

    text_final = ''.join(c for c in message if not c.isdigit())
    processed_doc1 = ' '.join([word for word in text_final.split() if word not in stop_words])

    sa = SentimentIntensityAnalyzer()
    dd = sa.polarity_scores(text=processed_doc1)
    compound = round((1 + dd['compound']) / 2, 2)
    return render_template("tweetresult.html", result=compound, text1=text_final, text2=dd['pos'], text5=dd['neg'], text4=compound, text3=dd['neu'])


@app.route('/predict', methods=["POST"])
def predict():
    values = []
    for i in range(1, 11):
        value = request.form.get(f'a{i}')
        if value is None:
            return render_template("index.html", error="Please answer all questions before submitting.")
        values.append(int(value))

    model = Model()
    classifier = model.svm_classifier()
    prediction = classifier.predict([values])
    if prediction[0] == 0:
        result = 'Your Gadget Addiction test result: No Impact of Addiction.'
    elif prediction[0] == 1:
        result = 'Your Gadget Addiction test result : Moderate Usage with Minor Impact'
    elif prediction[0] == 2:
        result = 'Your Gadget Addiction test result : Frequent Usage with Noticeable Impact'
    elif prediction[0] == 3:
        result = 'Your Gadget Addiction test result : High Usage with Significant Impact'
    else:
        result = 'Your Gadget Addiction test result : Severe Dependency with Major Impact'
    return render_template("result.html", result=result)

app.secret_key = os.urandom(12)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port, host='0.0.0.0', debug=True)