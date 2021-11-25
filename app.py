import os.path
from sqlalchemy import create_engine,Column,Integer,String,Enum,ForeignKey
from flask_bcrypt import Bcrypt
from flask import Flask, jsonify, request , make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import IntegrityError
from flask import Flask, Response
from flask import jsonify
import json
from flask import make_response
from flask import request
from sqlalchemy.exc import IntegrityError
from sqlalchemy import insert, null
from flask_httpauth import HTTPBasicAuth


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


app = Flask(__name__)
auth = HTTPBasicAuth()
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@127.0.0.1/pythonbd"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#engine = create_engine("mysql+pymysql://root:root@127.0.0.1/pythonbd")
db = SQLAlchemy(app)
ma = Marshmallow(app)



class Bank(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), default=False)
    amountOfMoney = db.Column(db.Integer(), nullable=False)

    def __init__(self,name,amountOfMoney):
        self.name = name
        self.amountOfMoney =amountOfMoney

class BankSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'amountOfMoney', 'transactions')

class BankSchemaAmount(ma.Schema):
    class Meta:
        fields = ('name', 'amountOfMoney')

bank_schema = BankSchema()
bank_schema_amount = BankSchemaAmount()

@app.route('/bank', methods = ['POST'])
def add_createNewAccount():
    name = request.json['name']
    amountOfMoney = request.json['amountOfMoney']

    new_bank = Bank(name, amountOfMoney )

    try:
        db.session.add(new_bank)
        db.session.commit()
    except IntegrityError:
        print('Incorrect data')
        return make_response(jsonify({'error': 'Incorrect data'}), 404)


    return  bank_schema.jsonify(new_bank)

@app.route('/bank/<id>', methods = ['GET'])
@auth.login_required()
def get_bank(id):
    user1 = auth.current_user()
    fam_obj = Family.query.filter_by(BankId=id).first()
    if int(user1.FamilyId) != int(fam_obj.id):
        return make_response(jsonify({'error': 'Access denied'}), 406)
    # try:
    #     a = to_json(db.session.query(Bank).filter_by(id=id).one,Bank)
    #     return Response(response=a, status=200, mimetype="application/json")
    # except:
    #     return make_response(jsonify({'error': 'User not found'}), 404)

    bamk = Bank.query.get(id)
    return bank_schema.jsonify(bamk)


@app.route('/bank/<id>', methods = ['PUT'])
@auth.login_required()
def update_bank(id):
    user1 = auth.current_user()
    fam_obj = Family.query.filter_by(BankId=id).first()
    if int(user1.FamilyId) != int(fam_obj.id):
        return make_response(jsonify({'error': 'Access denied'}), 406)
    a = db.session.query(Bank).filter_by(id=id).one()
    if not a:
        return make_response(jsonify({'error': 'Not found'}), 404)

    bamk = Bank.query.get(id)

    name = request.json['name']
    amountOfMoney = request.json['amountOfMoney']

    bamk.name = name
    bamk.amountOfMoney = amountOfMoney

    db.session.commit()

    return  bank_schema.jsonify(bamk)

@app.route('/bank/<id>', methods = ['DELETE'])
@auth.login_required()
def delete_bank(id):
    user1 = auth.current_user()
    fam_obj = Family.query.filter_by(BankId=id).first()
    if int(user1.FamilyId) != int(fam_obj.id):
        return make_response(jsonify({'error': 'Access denied'}), 406)
    try:
        bamk = db.session.query(Bank).filter_by(id=id).first()
        db.session.delete(bamk)
        db.session.commit()
        return {
            "msg": "Bank deleted successfully",
            "id": id
        }
    except:
        return "User not found", 404




########################################################################


class Family(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    BankId = db.Column(db.Integer(),db.ForeignKey(Bank.id), nullable=False)

    def __init__(self,name,BankId):
        self.name = name
        self.BankId =BankId

class FamilySchema(ma.Schema):
    class Meta:
        fields = ('id','name','BankId')

family_schema = FamilySchema()

@app.route('/family', methods = ['POST'])
def add_family():

    name = request.json['name']
    BankId = request.json['BankId']

    new_family = Family(name, BankId )

    try:
        db.session.add(new_family)
        db.session.commit()
    except IntegrityError:
        print('Incorrect data')
        return make_response(jsonify({'error': 'Incorrect data'}), 409)


    return  family_schema.jsonify(new_family)

@app.route('/family/<id>', methods = ['GET'])
def get_family(id):

    try:
        a = to_json(db.session.query(Family).filter_by(id=id).one,Family)
        return Response(response=a, status=200, mimetype="application/json")
    except:
        return make_response(jsonify({'error': 'Family not found'}), 404)


@app.route('/family/<id>', methods = ['PUT'])
@auth.login_required()
def update_family(id):
    user1 = auth.current_user()
    if int(user1.FamilyId) != int(id):
        return make_response(jsonify({'error': 'Access denied'}), 406)
    a = db.session.query(Family).filter_by(id=id).one()
    if not a:
        return make_response(jsonify({'error': 'Not found'}), 404)
    family = Family.query.get(id)

    name = request.json['name']
    BankId = request.json['BankId']

    family.name = name
    family.BankId = BankId

    db.session.commit()

    return  family_schema.jsonify(family)

@app.route('/family/<id>', methods = ['DELETE'])
@auth.login_required()
def delete_family(id):
    user1 = auth.current_user()
    if int(user1.FamilyId) != int(id):
        return make_response(jsonify({'error': 'Access denied'}), 406)
    try:
        a = db.session.query(Family).filter_by(id=id).first()
        db.session.delete(a)
        db.session.commit()
        return {
            "msg": "Family deleted successfully",
            "id": id
        }
    except:
        return "Family not found", 404



#########################################################################


class Users(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(1000), nullable=False)
    phone = db.Column(db.String(100), nullable=True)
    FamilyId = db.Column(db.Integer(),db.ForeignKey(Family.id), nullable=False)
    userStatus = db.Column(db.Integer(), nullable=False)

    def __init__(self, username, firstName, lastName, email, password, phone, FamilyId, userStatus):
        self.username = username
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.password = password
        self.phone = phone
        self.FamilyId = FamilyId
        self.userStatus = userStatus

class UsersSchema(ma.Schema):
    class Meta:
        fields = ('id','username','firstName','lastName','email', 'phone','FamilyId','userStatus','Family')

users_schema = UsersSchema()

@auth.verify_password
def verify_password(username, password):
    user = db.session.query(Users).filter_by(username = username).first()
    if not user:
        return False
    if not bcrypt.check_password_hash(user.password.encode("utf-8"),password.encode("utf-8")):
        return False
    if user:
        return user


@app.route('/users', methods = ['POST'])
def add_user():
    username = request.json['username']
    firstName = request.json['firstName']
    lastName = request.json['lastName']
    email = request.json['email']
    password = bcrypt.generate_password_hash(str(request.json.get('password'))).decode('utf-8'),
    phone = request.json['phone']
    FamilyId = request.json['FamilyId']
    userStatus = request.json['userStatus']


    new_users = Users(username, firstName , lastName , email , password , phone , FamilyId, userStatus )

    tvins = (db.session.query(Users).filter_by(username=new_users.username).all())


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
        a = to_json(db.session.query(Users).filter_by(id=id).one(), Users)
        return Response(response=a, status=200, mimetype="application/json")
    except:
        return make_response(jsonify({'error': 'User not found'}), 404)


@app.route('/users/<id>', methods = ['PUT'])
@auth.login_required()
def update_users(id):
    user1 = auth.current_user()
    if int(user1.id) != int(id):
        return make_response(jsonify({'error': 'Access denied'}), 406)
    u = db.session.query(Users).filter_by(id=id).one()
    if not u:
        return make_response(jsonify({'error': 'Not found'}), 404)
    if request.json.get('username'):
        tvins = (db.session.query(Users).filter_by(username=request.json.get('username')).all())
        if tvins != []:
            return make_response(jsonify({'error': 'username is busy'}), 409)

    users = Users.query.get(id)

    firstName = request.json['firstName']
    lastName = request.json['lastName']
    email = request.json['email']
    password = bcrypt.generate_password_hash(str(request.json.get('password'))).decode('utf-8'),
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
@auth.login_required()
def delete_users(id):
    user1 = auth.current_user()
    if int(user1.id) != int(id):
        return make_response(jsonify({'error': 'Access denied'}), 406)
    try:
        users = db.session.query(Users).filter_by(id=id).first()
        db.session.delete(users)
        db.session.commit()
        return {
            "msg": "User deleted successfully",
            "id": id
        }
    except:
        return "User not found", 404



#########################################################################


class Transaction(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    UsersId = db.Column(db.Integer(), db.ForeignKey(Users.id), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer(), nullable=False)
    ExtraInfo = db.Column(db.String(100), nullable=False)
    BankId = db.Column(db.Integer(), db.ForeignKey(Bank.id), nullable=False)

    def __init__(self, UsersId , date, amount, ExtraInfo, BankId):
        self.UsersId = UsersId
        self.date = date
        self.amount = amount
        self.ExtraInfo = ExtraInfo
        self.BankId = BankId

class TransactionSchema(ma.Schema):
    class Meta:
        fields = ('id','UsersId','date','amount','ExtraInfo','BankId')

transaction_schema = TransactionSchema()
transaction_schemas = TransactionSchema(many=True)

@app.route('/TransactionList', methods = ['POST'])
def add_transaction():

    UsersId = request.json['UsersId']
    date = request.json['date']
    amount = request.json['amount']
    ExtraInfo = request.json['ExtraInfo']
    BankId = request.json['BankId']

    bamk = Bank.query.get(BankId)

    try:
        check = (db.session.query(Bank).get(BankId))
        check2 = check.amountOfMoney
        bamk.amountOfMoney = int(check2) - int(amount)
    except:
        return make_response(jsonify({'error': 'Bank not found'}), 404)

    # check = (db.session.query(Bank).get(BankId))
    # check2 = check.amountOfMoney
    # bamk.amountOfMoney = check2 - amount


    new_transaction = Transaction(UsersId, date, amount, ExtraInfo, BankId )
    try:
        if(int(check2) <= int(amount)):
            print(check2)
            print(amount)
            return Response(response="not enough money", status=200, mimetype="application/json")
        db.session.add(new_transaction)
        db.session.commit()
    except IntegrityError:
        print('Incorrect data')
        return make_response(jsonify({'error': 'Incorrect data'}), 404)
        # tasks.append(task)
    a = to_json(new_transaction, Transaction)
    return Response(response=a, status=200, mimetype="application/json")


    #return  transaction_schema.jsonify(new_transaction)



@app.route('/TransactionList/<id>', methods = ['GET'])
@auth.login_required()
def get_transaction(id):
    trans_obj = Transaction.query.filter_by(id=id).first()
    fam_obj = Family.query.filter_by(BankId=trans_obj.BankId).first()
    user1 = auth.current_user()
    if int(user1.FamilyId) != int(fam_obj.id):
        return make_response(jsonify({'error': 'Access denied'}), 406)
    try:
        a = to_json(db.session.query(Transaction).filter_by(id=id).one(), Transaction)
        return Response(response=a, status=200, mimetype="application/json")
    except:
        return make_response(jsonify({'error': 'Transaction not found'}), 404)


# @app.route('/TransactionList/<id>', methods = ['PUT'])
# def update_transaction(id):
#     transaction = Transaction.query.get(id)
#
#     UsersId = request.json['UsersId']
#     date = request.json['date']
#     amount = request.json['amount']
#     ExtraInfo = request.json['ExtraInfo']
#     BankId = request.json['BankId']
#
#     transaction.UsersId = UsersId
#     transaction.date = date
#     transaction.amount = amount
#     transaction.ExtraInfo = ExtraInfo
#     transaction.BankId = BankId
#
#     db.session.commit()
#
#     return  transaction_schema.jsonify(transaction)

@app.route('/TransactionList/<id>', methods = ['DELETE'])
@auth.login_required()
def delete_transaction(id):
    trans_obj = Transaction.query.filter_by(id=id).first()
    fam_obj = Family.query.filter_by(BankId=trans_obj.BankId).first()
    user1 = auth.current_user()
    if int(user1.FamilyId) != int(fam_obj.id):
        return make_response(jsonify({'error': 'Access denied'}), 406)
    try:
        a = db.session.query(Transaction).filter_by(id=id).first()
        db.session.delete(a)
        db.session.commit()
        return {
            "msg": "Transaction deleted successfully",
            "id": id
        }
    except:
        return "Transaction not found", 404



@app.route('/TransactionListF/<id>', methods = ['GET'])
@auth.login_required()
def get_all_transaction(id):
    user1 = auth.current_user()
    fam_obj = Family.query.filter_by(id=id).first()
    if int(user1.FamilyId) != int(id):
        return make_response(jsonify({'error': 'Access denied'}), 406)
    a = db.session.query(Transaction).filter_by(BankId=fam_obj.BankId).all()

    json_data = []
    for i in a:
        json_data.append(to_json(i, Transaction))
    try:
        db.session.commit()
    except:
        return make_response(jsonify({'error': 'Not found'}), 404)

    return Response(response=str(json_data),
                    status=200,
                    mimetype="application/json")


#########################################################################


# @app.errorhandler(400)
# def handle_400_error(error):
#     return make_response(jsonify({'error' : 'Bad  request'}),400)
#
# @app.errorhandler(404)
# def handle_404_error(error):
#     return make_response(jsonify({'error' : 'Not found'}),404)





if __name__ == '__main__':
    app.run(debug=True)

