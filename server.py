from flask import Flask
from flask import render_template
import folium
from flask import request
import osmnx as ox
import pickle

from cars_interface import get_plot

app = Flask(__name__, template_folder='front')

@app.route('/')
@app.route('/index')
def index():
    address = request.args.get('address')
    folium_html = ''
    best_improvement = 0
    if address is not None:
        fplot, best_improvement = get_plot(address)
        folium_html = fplot._repr_html_()
    return render_template('index.html', title='Home', folium=folium_html, best_improvement=best_improvement * 100)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
