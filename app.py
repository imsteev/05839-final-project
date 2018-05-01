from flask import Flask, render_template, url_for, request, redirect, Markup
import boto3

app = Flask(__name__, static_url_path='/static')
app.config['TEMPLATES_AUTO_RELOAD'] = True
s3 = boto3.resource('s3')
BUCKET_NAME = 'spchung-kediz-final-project'
KEY = "wildfires_1992.csv"

@app.route('/')
def homepage():
    # print(s3.Object(BUCKET_NAME, KEY).get())
    # s3.Bucket(BUCKET_NAME).download_file(KEY, KEY)
    s3.Bucket(BUCKET_NAME).download_file(KEY, KEY)
    return render_template("index.html",title="05839")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

if __name__ == '__main__':
    app.run(use_reloader=True)  