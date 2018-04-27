from flask import Flask, render_template, url_for, request, redirect, Markup

app = Flask(__name__, static_url_path='/static')
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def homepage():
    return "Hello, 05839 Final Project"

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

if __name__ == '__main__':
    app.run(use_reloader=True)  