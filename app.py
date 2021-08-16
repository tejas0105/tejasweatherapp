import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisisasecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/weather'

db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=imperial&appid=8e647dac40bd61e65b4d80bb0496982a'
    response = requests.get(url).json()
    return response


@app.route('/')
def index_get():
    
    cities = City.query.all()
    # city = 'Dombivli'
    weather_data = []
    for city in cities:
        response = get_weather_data(city.name)
        # print(response)
        weather = {
            'city': city.name,
            'temperature': response['main']['temp'],
            'description': response['weather'][0]['description'],
            'icon': response['weather'][0]['icon'],
        }
    # print(weather)
        weather_data.append(weather)
    return render_template('weather.html',weather_data = weather_data)

@app.route('/', methods = ['POST'])
def index_post():
    err_msg = ''
    new_city = request.form.get('city')
    if new_city:
        
        existing_city = City.query.filter_by(name=new_city).first()
        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg = 'City does not exist in world!'
        else:
            err_msg = 'City already exists in the database!'

    if err_msg:
        flash(err_msg, 'error') #error is the category
    else:
        flash('City added successfully!')
    
    return redirect(url_for('index_get'))

@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name = name).first()
    db.session.delete(city)
    db.session.commit()

    flash(f'Successfully delete { city.name }', 'success')
    return redirect(url_for('index_get'))

if __name__ == '__main__':
    app.run(debug=True)