from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://okunsydryzqwqw:c513df721a5ae23ebd8ecd5e6a7fdf3e3f4c3e424972f8c7530744f8eb99a7dc@ec2-34-227-120-79.compute-1.amazonaws.com:5432/d51d1a3nbf48gq'

db = SQLAlchemy(app)
ma = Marshmallow(app)

CORS(app)


# ____________________    
# | Class Definitions |    
# V                   V

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), unique=False)
    last_name = db.Column(db.String(30), unique=False)
    email = db.Column(db.String(45), unique=True, nullable=False)
    address = db.Column(db.String(240), unique=False)
    city = db.Column(db.String(30), unique=False)
    state = db.Column(db.String(2), unique=False)
    zip_code = db.Column(db.String(20), unique=False)
    selected_painting = db.Column(db.String(45))
    

    def __init__(self, first_name, last_name, email, address, city, state, zip_code, selected_painting):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.selected_painting = selected_painting

class OrderSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'city', 'state', 'zip_code', 'selected_painting')


order_schema = OrderSchema()
multi_order_schema = OrderSchema(many=True)

class Painting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String, unique=False)
    price = db.Column(db.Integer, unique=False, nullable=False)
    name = db.Column(db.String(45), unique=False, nullable=False)
    color = db.Column(db.String(30), unique=False)
    medium = db.Column(db.String(30), unique=False, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=False)
    

    def __init__(self, image_url, price, name, color, medium, description):
        self.image_url = image_url
        self.price = price
        self.name = name
        self.color = color
        self.medium = medium
        self.description = description

class PaintingSchema(ma.Schema):
    class Meta:
        fields = ('id', 'image_url', 'price', 'name', 'color', 'medium', 'description')


painting_schema = PaintingSchema()
multi_painting_schema = PaintingSchema(many=True)

# __________    
# | Routes |    
# V        V

# Endpoint to submit an order
@app.route('/order', methods=['POST'])
def new_order():
    if request.content_type != 'application/json':
        return jsonify('Error: data MUST be sent as JSON!')

    post_data = request.get_json()
    first_name = post_data.get('first_name')
    last_name = post_data.get('last_name')
    email = post_data.get('email')
    address = post_data.get('address')
    city = post_data.get('city')
    state = post_data.get('state')
    zip_code = post_data.get('zip_code')
    selected_painting = post_data.get('selected_painting')
    
    if first_name == None:
        return jsonify('Error: What do you think this is? You must provide a first name!')
    if last_name == None:
        return jsonify('Error: What do you think this is? You must provide a last name!')
    if address == None:
        return jsonify('Error: What do you think this is? You must provide an address!')
    if city == None:
        return jsonify('Error: What do you think this is? You do live in a city, dont ya?')
    if state == None:
        return jsonify('Error: What do you think this is? You must claim your state of residence!')
    if zip_code == None:
        return jsonify('Error: We can\'t read minds...You must provide a valid zip code!')
    if selected_painting == None:
        return jsonify('Error: We can\'t read minds...You must choose a painting!')


    new_order = Order(first_name, last_name, email, address, city, state, zip_code, selected_painting)
    db.session.add(new_order)
    db.session.commit()

    return jsonify("Order Submitted Successfully!")

# Endpoint to query all orders
@app.route('/orders/get', methods=['GET'])
def get_all_orders():
    all_orders = db.session.query(Order).all()
    return jsonify(multi_order_schema.dump(all_orders))

# Endpoint to query one order
@app.route('/order/get/<id>', methods=['GET'])
def get_order_id(id):
    one_order = db.session.query(Order).filter(Order.id == id).first()
    return jsonify(order_schema.dump(one_order))

# Endpoint to delete an order
@app.route('/order/delete/<id>', methods=['DELETE'])
def order_to_delete(id):
    delete_order = db.session.query(Order).filter(Order.id == id).first()
    db.session.delete(delete_order)
    db.session.commit()
    return jsonify("The order you chose is POOF! Gone, done, DELETED!")

# Endpoint to update/edit an order
@app.route('/order/update/<id>', methods=['PUT'])
def update_order_id(id):
    if request.content_type != 'application/json':
        return jsonify('Error: data must be sent as JSON!')

    put_data = request.get_json()
    
    first_name = put_data.get('first_name')
    last_name = put_data.get('last_name')
    email = put_data.get('email')
    address = put_data.get('address')
    city = put_data.get('city')
    state = put_data.get('state')
    zip_code = put_data.get('zip_code')
    selected_painting = put_data.get('selected_painting')

    order_to_update = db.session.query(Order).filter(Order.id == id).first()

    if first_name != None:
        order_to_update.first_name = first_name
    if last_name != None:
        order_to_update.last_name = last_name
    if email != None:
        order_to_update.email = email
    if address != None:
        order_to_update.address = address
    if city != None:
        order_to_update.city = city
    if state != None:
        order_to_update.state = state
    if zip_code != None:
        order_to_update.zip_code = zip_code
    if selected_painting != None:
        order_to_update.selected_painting = selected_painting

    db.session.commit()

    return jsonify(order_schema.dump(order_to_update))

# Endpoint to add a painting
@app.route('/painting/add', methods=['POST'])
def add_painting():
    if request.content_type != 'application/json':
        return jsonify('Error: data MUST be sent as JSON!')

    post_data = request.get_json()
    image_url = post_data.get('image_url')
    price = post_data.get('price')
    name = post_data.get('name')
    color = post_data.get('color')
    medium = post_data.get('medium')
    description = post_data.get('description')

    new_painting = Painting(image_url, price, name, color, medium, description)
    db.session.add(new_painting)
    db.session.commit()

    return jsonify(painting_schema.dump(new_painting))

# Endpoint to add multiple paintings
@app.route('/painting/add-multi', methods=['POST'])
def add_multiple_paintings():
    if request.content_type != 'application/json':
        return jsonify('Error: You are kind of a putz...the data MUST be sent as JSON!')

    post_data = request.get_json()
    data = post_data.get("data")

    new_paintings = []

    for painting in data:
        image_url = painting.get("image_url")
        price = painting.get("price")
        name = painting.get("name")
        color = painting.get("color")
        medium = painting.get("medium")
        description = painting.get("description")

        existing_painting_check = db.session.query(Painting).filter(Painting.name == name).filter(Painting.name == name).first()
        if existing_painting_check is not None:
            return jsonify("Error: STOP trying to add stuff that's already there...")
        else:
            new_painting = Painting(image_url, price, name, color, medium, description)
            db.session.add(new_painting)
            db.session.commit()
            new_paintings.append(new_painting)

    return jsonify(multi_painting_schema.dump(new_paintings))

# Endpoint to query all paintings
@app.route('/paintings/get', methods=['GET'])
def get_all_paintings():
    all_paintings = db.session.query(Painting).all()
    return jsonify(multi_painting_schema.dump(all_paintings))

# Endpoint to query one painting
@app.route('/painting/get/<id>', methods=['GET'])
def get_painting_id(id):
    one_painting = db.session.query(Painting).filter(Painting.id == id).first()
    return jsonify(painting_schema.dump(one_painting))

# Endpoint to delete a painting
@app.route('/painting/delete/<id>', methods=['DELETE'])
def painting_to_delete(id):
    delete_painting = db.session.query(Painting).filter(Painting.id == id).first()
    db.session.delete(delete_painting)
    db.session.commit()
    return jsonify("The painting you chose is POOF! Gone, done, DELETED!")

# Endpoint to update/edit a painting
@app.route('/painting/update/<id>', methods=['PUT'])
def update_painting_id(id):
    if request.content_type != 'application/json':
        return jsonify('Error: data must be sent as JSON!')

    put_data = request.get_json()
    id = put_data.get('id')
    image_url = put_data.get('image_url')
    price = put_data.get('price')
    name = put_data.get('name')
    color = put_data.get('color')
    medium = put_data.get('medium')
    description = put_data.get('description')

    painting_to_update = db.session.query(Painting).filter(Painting.id == id).first()

    id = id

    if image_url != None:
        painting_to_update.image_url = image_url
    if price != None:
        painting_to_update.price = price
    if name != None:
        painting_to_update.name = name
    if color != None:
        painting_to_update.color = color
    if medium != None:
        painting_to_update.medium = medium
    if description != None:
        painting_to_update.description = description

    db.session.commit()

    return jsonify(painting_schema.dump(painting_to_update))

if __name__ == '__main__':
    app.run(debug=True)