from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import jwt
from functools import wraps
import pandas as pd
# Load the CSV file into a pandas DataFrame
seats = pd.read_csv("data.csv")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'
sample_users = {
    'username':"test",
    'password':"test"
}


@app.route('/token', methods=['POST'])
def generate_token():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': 'Username or password missing'}), 400
    # check the username and password (replace this with your own authentication logic)
    if username != sample_users['username'] or password != sample_users['password']:
        return jsonify({'message': 'Invalid username or password'}), 401
    # create a JWT token with a payload containing the username and expiration time
    payload = {
        'username': username,
        'password': password,
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload,app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token})

def verify_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # get the authorization header from the request
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Authorization header missing'}), 401
        # extract the token from the authorization header
        print(auth_header)
        print(type(auth_header))
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'message': 'Invalid Authorization header'}), 401
        token = parts[1]
        try:
            # decode the token and verify the signature
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.exceptions.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        # check the username and password
        if payload['username'] != sample_users['username'] or payload['password'] != sample_users['password']:
            return jsonify({'message': 'Invalid username or password'}), 401
        # check the expiration time
        if datetime.utcfromtimestamp(payload['exp']) < datetime.utcnow():
            return jsonify({'message': 'Token expired'}), 401
        return func(*args, **kwargs)
    return wrapper


@app.route('/seats', methods=['GET'])
@verify_token
def get_seats():
    return jsonify(seats.to_dict('records'))

@app.route('/seats/book', methods=['POST'])
@verify_token
def book_seats():
    selected_seat_nums = request.json.get('seats', [])

    # Find the seats that were selected
    selected_seats = seats[seats['number'].isin(selected_seat_nums)].to_dict('records')
    # Check if all selected seats are available
    for seat in selected_seats:
        if not seat['available']:
            return jsonify({'message': 'Seat {} is not available'.format(seat['number'])}), 400

    # Book the selected seats
    seats.loc[seats['number'].isin(selected_seat_nums), 'available'] = False

    # Count the number of available seats
    available_seats = dict()
    #available_seats['seat_numbers'] = [seat['number'] for seat in seats if seat['available']]
    available_seats['seat_numbers'] = seats.loc[seats['available'], 'number'].tolist()
    available_seats['total'] = len(available_seats['seat_numbers'])
    seats.to_csv("data.csv", index=False)
    return jsonify({'message': 'Successfully booked seats {}'.format(selected_seat_nums),
                    'available_seats': available_seats}), 200

if __name__ == '__main__':
    app.run(debug=True)