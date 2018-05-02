from flask import Flask, render_template, url_for, request, redirect, Markup
import boto3
import os
import sys
from wildfires.wildfire_classifier import WildfireClassifier

app = Flask(__name__, static_url_path='/static')
app.config['TEMPLATES_AUTO_RELOAD'] = True
s3 = boto3.resource('s3')
BUCKET_NAME = 'spchung-kediz-final-project'
KEY = "trimmed_wildfires_%d.csv"
classifiers = {}

@app.route('/')
def homepage():
    return render_template("index.html",title="05839")

@app.route('/classify/<year>')
def classify_fire_size(year):
    try:
        year = int(year)
        if year in classifiers:
            print("cached")
            clf = classifiers[year]
            test_value = clf.test(.7)
        else:
            valid_year_start = 1992
            valid_year_end = 2015
            if not (valid_year_start <= year <= valid_year_end): return url_for('homepage')
            fname = './%s' % (KEY % year)
            if not os.path.isfile(fname):
                print("not downloaded")
                s3.Bucket(BUCKET_NAME).download_file(KEY % year, KEY % year)
            else:
                print("downloaded")
            clf = WildfireClassifier(fname,year,cleaned=True)
            classifiers[year] = clf
            test_value = clf.test(0.7)
        return render_template("index.html", year=year, test_results=test_value)
    except Exception as e:
        print("couldn't load", e)
        return url_for('homepage')

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

if __name__ == '__main__':
    app.run(use_reloader=True)  