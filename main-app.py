import json
import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__, template_folder='templates-web', static_folder='styles-web')
app.secret_key = 'super-secret-rockport-key'

DATA_FILE = os.path.join(os.path.dirname(__file__), 'blacklisted-data', 'cars.json')
RACER_FILE = os.path.join(os.path.dirname(__file__), 'blacklisted-data', 'racers.json')

# Admin Credentials
ADMIN_USER = "CROSS"
ADMIN_PASS = "BTYHNTR"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def load_cars():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def save_cars(cars):
    with open(DATA_FILE, 'w') as f:
        json.dump(cars, f, indent=2)


def load_racers():
    if not os.path.exists(RACER_FILE):
        return []
    with open(RACER_FILE, 'r') as f:
        return json.load(f)


def save_racers(racers):
    with open(RACER_FILE, 'w') as f:
        json.dump(racers, f, indent=2)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid Credentials')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))


@app.route('/')
def index():
    cars = load_cars()
    return render_template('index.html', cars=cars)


@app.route('/racers')
def racers():
    racers_list = load_racers()
    return render_template('racers.html', racers=racers_list)


@app.route('/racer/<int:rank>')
def racer_detail(rank):
    racers_list = load_racers()
    racer = next((r for r in racers_list if r['rank'] == rank), None)
    if racer is None:
        return redirect(url_for('racers'))
    return render_template('racer_detail.html', racer=racer)


@app.route('/database')
def database():
    cars = load_cars()
    return render_template('database.html', cars=cars)


@app.route('/car/<int:car_id>')
def car_detail(car_id):
    cars = load_cars()
    car = next((c for c in cars if c['id'] == car_id), None)
    if car is None:
        return redirect(url_for('index'))
    return render_template('detail.html', car=car)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_car():
    if request.method == 'POST':
        cars = load_cars()
        new_id = max((c['id'] for c in cars), default=-1) + 1
        new_car = {
            'id': new_id,
            'model': request.form.get('model', ''),
            'make': request.form.get('make', ''),
            'chassis': request.form.get('chassis', ''),
            'year': request.form.get('year', ''),
            'engine': request.form.get('engine', ''),
            'aspiration': request.form.get('aspiration', ''),
            'transmission': request.form.get('transmission', ''),
            'top_speed': request.form.get('top_speed', ''),
            'acceleration': request.form.get('acceleration', ''),
            'power': request.form.get('power', ''),
            'torque': request.form.get('torque', ''),
            'weight': request.form.get('weight', ''),
            'speed_rating': int(request.form.get('speed_rating', 50)),
            'accel_rating': int(request.form.get('accel_rating', 50)),
            'handl_rating': int(request.form.get('handl_rating', 50)),
            'car_cost': int(request.form.get('car_cost', 0)),
            'country_origin': request.form.get('country_origin', ''),
            'description': request.form.get('description', ''),
            'is_blacklist_car': request.form.get('is_blacklist_car') == 'on',
            'blacklist_rank': int(request.form.get('blacklist_rank', 0)) if request.form.get('blacklist_rank') else None
        }
        cars.append(new_car)
        save_cars(cars)
        return redirect(url_for('database'))
    return render_template('add.html')


@app.route('/add_racer', methods=['GET', 'POST'])
@login_required
def add_racer():
    if request.method == 'POST':
        racers_list = load_racers()
        new_racer = {
            'rank': int(request.form.get('rank', 0)),
            'alias': request.form.get('alias', '').upper(),
            'real_name': request.form.get('real_name', ''),
            'strength': request.form.get('strength', ''),
            'suspected_vehicles': [v.strip() for v in request.form.get('suspected_vehicles', '').split(',') if v.strip()],
            'bio': request.form.get('bio', '')
        }
        # Overwrite or append based on rank
        racers_list = [r for r in racers_list if r['rank'] != new_racer['rank']]
        racers_list.append(new_racer)
        racers_list.sort(key=lambda x: x['rank'])
        save_racers(racers_list)
        return redirect(url_for('racers'))
    return render_template('add_racer.html')


@app.route('/delete_racer/<int:rank>')
@login_required
def delete_racer(rank):
    racers_list = load_racers()
    racers_list = [r for r in racers_list if r['rank'] != rank]
    save_racers(racers_list)
    return redirect(url_for('racers'))


@app.route('/delete/<int:car_id>')
@login_required
def delete_car(car_id):
    cars = load_cars()
    cars = [c for c in cars if c['id'] != car_id]
    save_cars(cars)
    return redirect(url_for('database'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)