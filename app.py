import json

from flask import Flask, request, jsonify, render_template, make_response, Response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from sqlalchemy import String, Integer, ForeignKey,  Date, BOOLEAN
from sqlalchemy.exc import IntegrityError
from sqlalchemy.testing.schema import Column
from sqlalchemy.orm import relationship
from sqlalchemy import Column
import bcrypt
app=Flask(os.name)
basedir=os.path.abspath(os.path.dirname(os.file))

#+os.path.join(basedir, 'db.postgresql')

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:5528@localhost:5432/lll'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)

ma=Marshmallow(app)


def to_json(inst, cls):
    """
    Jsonify the sql alchemy query result.
    """
    convert = dict()
    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if c.type in convert.keys() and v is not None:
            try:
                d[c.name] = convert[c.type](v)
            except:
                d[c.name] = "Error:  Failed to covert using ", str(convert[c.type])
        elif v is None:
            d[c.name] = str()
        else:
            d[c.name] = v
    return json.dumps(d)
class Event(db.Model):
    tablename = "Event"
    event_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    data = db.Column(db.Date, nullable=False)

    def init(self,  name, data):
        self.name=name
        self.data=data
class Ticket(db.Model):
    tablename = "Ticket"
    ticket_id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    event_event_id = db.Column(db.Integer, ForeignKey("Event.event_id"))
    #Event = relationship("Event")

    def init(self, price, status, event_event_id):
        self.price=price
        self.status=status
        self.event_event_id=event_event_id
class User(db.Model):
    tablename = "User"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    firstName = db.Column(db.String(20), nullable=False)
    lastName = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    userStatus = db.Column(db.Integer, nullable=False)

    def init(self,  username, firstName, lastName, email, password, phone,userStatus):
        self.username=username
        self.firstName=firstName
        self.lastName=lastName
        self.email=email
        self.password=password
        self.phone=phone
        self.userStatus=userStatus
class Order(db.Model):
    tablename = "Order"
    order_id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    oredDate = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    complete = db.Column(db.BOOLEAN, nullable=False)
    ticket_ticket_id = db.Column(db.Integer, ForeignKey("Ticket.ticket_id"))
    user_user_id = db.Column(db.Integer, ForeignKey("User.user_id"))
    #Ticket = relationship("Ticket")
    #User = relationship("User")

    def init(self,  quantity, oredDate ,status, complete, ticket_ticket_id,user_user_id):
        self.quantity=quantity
        self.oredDate=oredDate
        self.status=status
        self.complete=complete
        self.ticket_ticket_id=ticket_ticket_id
        self.user_user_id=user_user_id
class ProductSchema(ma.Schema):
    class Meta:
        fields=('id', 'name', 'description', 'price', 'qty')
class EventSchema(ma.Schema):
    class Meta:
        fields=('event_id', 'name', 'data')


event_schema=EventSchema()
events_schema=EventSchema(many=True)

class TicketSchema(ma.Schema):
    class Meta:
        fields=('ticket_id', 'price', 'status','event_event_id')

ticket_schema=TicketSchema()
tickets_schema=TicketSchema(many=True)

class UserSchema(ma.Schema):
    class Meta:
        fields=('user_id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone','userStatus')

user_schema=UserSchema()
users_schema=UserSchema(many=True)

class OrderSchema(ma.Schema):
    class Meta:
        fields=('order_id', 'quantity', 'oredDate' ,'status', 'complete', 'ticket_ticket_id', 'user_user_id')


order_schema=OrderSchema()
orders_schema=OrderSchema(many=True)

#методи для івенту
@app.route('/event', methods=['POST'])
def add_event():
    name=request.json['name']
    data = request.json['data']
    new_event = Event(name, data)

    try:
        db.session.add(new_event)
        db.session.commit()
    except IntegrityError:
        print('Incorrect data')
        return make_response(jsonify({'error': 'Incorrect data'}), 409)


    # db.session.add(new_event)
    # db.session.commit()
    #
    # return event_schema.jsonify(new_event)


@app.route('/event', methods=['GET'])
def get_events():
    all_events = Event.query.all()
    result = events_schema.dump(all_events)
    return jsonify(result)


@app.route('/event/<id>', methods=['GET'])
def get_event(id):
    try:
        a = to_json(db.ession.query(Event).filter_by(id=id).one(), Event)
        return Response(response=a, status=200, mimetype="application/json")
    except:
        return make_response(jsonify({'error': 'User not found'}), 404)
    # event = Event.query.get(id)
    # return event_schema.jsonify(event)


@app.route('/event/<id>', methods=['DELETE'])
def delete_event(id):
    try:
        event = db.session.query(Event).filter_by(id=id).first()
        db.session.delete(event)
        db.session.commit()
        return {
            "msg": "User deleted successfully",
            "id": id
        }
    except:
        return "User not found", 404
    # event = Event.query.get(id)
    # db.session.delete(event)
    # db.session.commit()

    # return event_schema.jsonify(event)


# методи для тікету
@app.route('/ticket', methods=['POST'])
def add_ticket():
    price = request.json['price']
    status = request.json['status']
    event_event_id = request.json['event_event_id']

    new_ticket = Ticket(price, status, event_event_id)

    try:
        db.session.add(new_ticket)
        db.session.commit()
    except IntegrityError:
        print('Incorrect data')
        return make_response(jsonify({'error': 'Incorrect data'}), 409)
        # tasks.append(task)
    a = to_json(new_ticket, Ticket)
    return Response(response=a, status=200, mimetype="application/json")

    # db.session.add(new_ticket)
    # db.session.commit()
    #
    # return ticket_schema.jsonify(new_ticket)


@app.route('/ticket/<id>', methods=['DELETE'])
def delete_ticket(id):
    try:
        ticket = db.session.query(Ticket).filter_by(id=id).first()
        db.session.delete(ticket)
        db.session.commit()
        return {
            "msg": "Ticket deleted successfully",
            "id": id
        }
    except:
        return "Ticket not found", 404
    # ticket = Ticket.query.get(id)
    # db.session.delete(ticket)
    # db.session.commit()
    #
    # return ticket_schema.jsonify(ticket)


@app.route('/ticket', methods=['GET'])
def get_tickets():

    all_tickets = Ticket.query.all()
    result = tickets_schema.dump(all_tickets)
    return jsonify(result)


@app.route('/ticket/<id>', methods=['GET'])
def get_ticket(id):
    try:
        a = to_json(db.session.query(Ticket).filter_by(id=id).one(), Ticket)
        return Response(response=a, status=200, mimetype="application/json")
    except:
        return make_response(jsonify({'error': 'Event not found'}), 404)
    # ticket = Ticket.query.get(id)
    # return ticket_schema.jsonify(ticket)


# get single


# все для юзера
@app.route('/users', methods = ['POST'])
def add_user():
    username = request.json['username']
    firstName = request.json['firstName']
    lastName = request.json['lastName']
    email = request.json['email']
    password = request.json['password']
    phone = request.json['phone']
    FamilyId = request.json['FamilyId']
    userStatus = request.json['userStatus']

    hashed=bcrypt.hashpw(password.encode('utf-8','ignore'), bcrypt.gensalt())

    new_users = User(username, firstName , lastName , email , hashed , phone , FamilyId, userStatus )

    tvins = (db.session.query(User).filter_by(username=new_users.username).all())


    if tvins != []:
        return make_response(jsonify({'error': 'Username is busy'}), 404)
    try:
        db.session.add(new_users)
        db.session.commit()
    except IntegrityError:
        print('Incorrect data')
        return make_response(jsonify({'error': 'Incorrect data'}), 404)
    # tasks.append(task)


   # return Response(users_schema.jsonify(new_users),status=200)
    return  users_schema.jsonify(new_users)

@app.route('/users/<id>', methods = ['GET'])
def get_users(id):
    try:
        a = to_json(db.session.query(User).filter_by(id=id).one(), User)
        return Response(response=a, status=200, mimetype="application/json")
    except:
        return make_response(jsonify({'error': 'User not found'}), 404)


@app.route('/users/<id>', methods = ['PUT'])
def update_users(id):
    u = db.session.query(User).filter_by(id=id).one()
    if not u:
        return make_response(jsonify({'error': 'Not found'}), 404)
    if request.json.get('username'):
        tvins = (db.session.query(User).filter_by(username=request.json.get('username')).all())
        if tvins != []:
            return make_response(jsonify({'error': 'username is busy'}), 409)

    users = User.query.get(id)

    firstName = request.json['firstName']
    lastName = request.json['lastName']
    email = request.json['email']
    password = request.json['password']
    phone = request.json['phone']
    FamilyId = request.json['FamilyId']
    userStatus = request.json['userStatus']

    users.firstName = firstName
    users.lastName = lastName
    users.email = email
    users.password = password
    users.phone = phone
    users.FamilyId = FamilyId
    users.userStatus = userStatus

    db.session.commit()

    return  users_schema.jsonify(users)

@app.route('/users/<id>', methods = ['DELETE'])
def delete_users(id):
    try:
        users = db.session.query(User).filter_by(id=id).first()
        db.session.delete(users)
        db.session.commit()
        return {
            "msg": "User deleted successfully",
            "id": id
        }
    except:
        return "User not found", 404


# вся для ордера
@app.route('/order', methods=['POST'])
def add_order():
    quantity = request.json['quantity']
    oredDate = request.json['oredDate']
    status = request.json['status']
    complete = request.json['complete']
    ticket_ticket_id = request.json['ticket_ticket_id']
    user_user_id = request.json['user_user_id']

    new_order = Order(quantity, oredDate, status, complete, ticket_ticket_id, user_user_id)

    try:
        db.session.add(new_order)
        db.session.commit()
    except IntegrityError:
        print('Incorrect data')
        return make_response(jsonify({'error': 'Incorrect data'}), 409)
        # tasks.append(task)
    a = to_json(new_order, Order)
    return Response(response=a, status=200, mimetype="application/json")

    # db.session.add(new_order)
    # db.session.commit()
    #
    # return order_schema.jsonify(new_order)


@app.route('/order', methods=['GET'])
def get_orders():

    all_orders = Order.query.all()
    result = orders_schema.dump(all_orders)
    return jsonify(result)


@app.route('/order/<id>', methods=['GET'])
def get_order(id):
    try:
        a = to_json(db.session.query(Order).filter_by(id=id).one(), Order)
        return Response(response=a, status=200, mimetype="application/json")
    except:
        return make_response(jsonify({'error': 'Order not found'}), 404)
    # order = Order.query.get(id)
    # return order_schema.jsonify(order)