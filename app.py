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
ranges = {
    'A' : "0 to 0.25",
    'B' : '0.26 to 9.9',
    'C' : '10.0 to 99.9',
    'D' : '100 to 299',
    'E' : '300 to 999',
    'F' : '1000 to 4999',
    'G' : '5000+'
}
years = list(range(1992,2016))
causes = [
    'Lightning',
    'Equipment Use',
    'Smoking',
    'Campfire',
    'Debris Burning',
    'Railroad',
    'Arson',
    'Children',
    'Miscellaneous',
    'Fireworks',
    'Powerline',
    'Structure',
    'Missing/Undefined'
]
seasons = WildfireClassifier.SEASONS
regions = WildfireClassifier.REGIONS.keys()

@app.route('/')
def homepage():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html", title="About")

@app.route('/data')
def data():
    return render_template("data.html", title="Data")

@app.route('/classification')
def classification():
    prediction = request.args.get('prediction')
    year = request.args.get('year')
    season = request.args.get('season')
    region = request.args.get('region')
    cause = request.args.get('cause')
    return render_template("classification.html", 
                            title="Classification", 
                            years=years, 
                            causes=causes, 
                            regions=regions, 
                            seasons=seasons,
                            year=year, 
                            season=season, 
                            region=region, 
                            cause=cause,
                            prediction=prediction,
                            ranges=ranges)

@app.route('/classify', methods=['POST'])
def classify():
    print(request.form)
    try:
        year = int(request.form['year'])
        season = request.form['season']
        region = request.form['region']
        cause = request.form['cause']
        if year in classifiers:
            print("cached")
            clf = classifiers[year]
            size_class = clf.predict(season,region,cause)
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
            clf.train()
            classifiers[year] = clf
            size_class = clf.predict(season,region,cause)
        return redirect(url_for('classification', year=year, season=season, region=region, cause=cause, prediction=size_class))
    except Exception as e:
        print("couldn't load", e)
        return url_for('homepage')

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

if __name__ == '__main__':
    app.run(use_reloader=True)  