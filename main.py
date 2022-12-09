from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# #Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

cafes_query = {}
TopSecretKey = "Test"


# # Cafe TABLE Configuration
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

    def to_dict(self):
        # Loop through each column in the data record,
        # create a new dictionary entry,
        # where the key is the name of the column,
        # and the value is the value of the column
        # with dictionary comprehension
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


# # HTTP GET - Read Record

# Method GET is allowed by default on all routes, so you don't have to add it
@app.route("/random")
def get_random_cafe():
    cafes = Cafe.query.all()
    # cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    # return jsonify({
    #     "cafe": {
    #         "can_take_calls": random_cafe.can_take_calls,
    #         "coffee_price": random_cafe.coffee_price,
    #         "has_sockets": random_cafe.has_sockets,
    #         "has_toilet": random_cafe.has_toilet,
    #         "has_wifi": random_cafe.has_wifi,
    #         "id": random_cafe.id,
    #         "img_url": random_cafe.img_url,
    #         "location": random_cafe.location,
    #         "map_url": random_cafe.map_url,
    #         "name": random_cafe.name,
    #         "seats": random_cafe.seats
    #     }
    # })
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafes():
    cafes = Cafe.query.all()
    for cafe in cafes:
        cafes_query[cafe.name] = cafe.to_dict()
    return jsonify(cafes=[cafes_query])


@app.route("/search")
def get_search_at_location_cafe():
    query_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry,we don't have a cafe at that location."})


# # HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_new_cafe():
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
    return jsonify(response={"success": "Successfully added the new cafe."})


# # HTTP PUT/PATCH - Update Record
@app.route("/update-price", methods=["PATCH"])
def update_coffee_price():
    query_id = request.args.get("id")
    selected_id = db.session.query(Cafe).filter_by(id=query_id).first()
    if selected_id:
        new_price = request.args.get("new_price")
        selected_id.coffee_price = new_price
        db.session.commit()
        return jsonify(success={"success": "Successfully updated the price."})
    else:
        return jsonify(error={"error": "Sorry a cafe with that id was not found in the database."})


# # HTTP DELETE - Delete Record
@app.route("/report-closed", methods=["DELETE"])
def delete_cafe():
    query_id = request.args.get("id")
    selected_id = db.session.query(Cafe).filter_by(id=query_id).first()
    if selected_id:
        api_key = request.args.get("api-key")
        if api_key == TopSecretKey:
            db.session.query(Cafe).filter_by(id=query_id).delete()
            db.session.commit()
            return jsonify(success={"success": "Successfully deleted the cafe."})
        else:
            return jsonify(error={"error": "Sorry wrong api key."})
    else:
        return jsonify(error={"error": "Sorry a cafe with that id was not found in the database."})


if __name__ == '__main__':
    app.run(debug=True)
