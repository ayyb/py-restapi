from flask import Flask, jsonify, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func #랜덤행을 가져오는


app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random")
def random():
    random_cafe = db.session.query(Cafe).order_by(func.random()).first() # 카페목록들에서 랜덤 초이스.

    return jsonify(cafe={ # json 직렬화
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        # Sub Group
        "amenities": {
            "seats": random_cafe.seats,
            "has_toilet": random_cafe.has_toilet,
            "has_wifi": random_cafe.has_wifi,
            "has_sockets": random_cafe.has_sockets,
            "can_take_calls": random_cafe.can_take_calls,
            "coffee_price": random_cafe.coffee_price,
        }
    })

#오브젝트 변환 함수 db모델 변환
def to_dict(self):
    # Method 1.
    dictionary = {}
    # Loop through each column in the data record
    for column in self.__table__.columns:
        # Create a new dictionary entry;
        # where the key is the name of the column
        # and the value is the value of the column
        dictionary[column.name] = getattr(self, column.name) # 속성값
    return dictionary

    # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
    # 컴프리헨션으로 한줄로 표현하기.
    return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route('/all')
def all():
    cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[to_dict(cafe) for cafe in cafes])

@app.route('/search', methods=['GET'])
def search():
    loc = request.args.get('loc')
    cafe = db.session.query(Cafe).filter_by(location=loc).first()
    if cafe :
        return jsonify(cafe=to_dict(cafe))
    else:
        return jsonify(error={"Not Found":"Sorry, we don't have a cafe at the location."})

@app.route('/add',methods=['POST'])
def add():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify({"response":{"success":"Successfully added the new cafe."}})

@app.route('/update-price/<cafe_id>',methods=["PATCH","GET"])
def update_price(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if cafe:
        cafe.coffee_price = request.args.get("new_price")
        db.session.commit()
        return jsonify({"response":{"success":"Successfully updated the price."}}) , 200
    else:
        return jsonify(error={"Not Found":"Sorry a cafe with that id was not found in the database."}), 404 # 상태코드값 보내기

@app.route('/report-closed/<cafe_id>',methods=["DELETE"])
def report_closed(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if cafe is None: # 카페아이디가 존재하지 않는다면
        return jsonify(error={"Not Found":"Sorry a cafe with that id was not found in the database."}), 404 # 상태코드값 보내기
    api_key = request.args.get("api-key")
    if api_key == 'TopSecretAPIKey':
        db.session.delete(cafe)
        db.session.commit() # 커밋읋 해야 db에 반영
        return "삭제되었습니다."
    else:
        return jsonify(error={"Not Found":"Sorry that's not allowd. Make sure you have the correct api_key"}), 403 # 삭제되어서? 보내기
## HTTP GET - Read Record

## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
