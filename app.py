from flask import Flask,render_template, request
import requests
import folium
from flask_sqlalchemy import SQLAlchemy
from flask_alembic import Alembic

app = Flask(__name__)
db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"
db.init_app(app)

class Places(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String, nullable=False)
    street_number = db.Column(db.Integer, nullable=False)
    number_of_places = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return f'{self.street} / {self.street_number} / {self.number_of_places} '
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String, nullable=False)
    street_number = db.Column(db.Integer, nullable=False)
    number_of_places = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return f'{self.street} / {self.street_number} / {self.number_of_places} '

with app.app_context():
    db.create_all()

def load_parking_places ():
    lista=[]
    ApiKey = "7909a2f5-dd04-4c9b-b0c4-07e7a3bbe7a1"
    url = f"https://api.um.warszawa.pl/api/action/disabled_parking_spaces/?apikey={ApiKey}"
    resp = requests.get(url)
    print(resp.ok)
    print(resp.status_code)
    if resp.ok:
        places = (resp.json()["result"])
        for p in places:
            miejsca = {"ulica": p["street"],"numer_ulicy": p["street_number"], "liczba_miejsc": p["number_of_places"]}
            lista.append(miejsca)
            p1 =db.session.query(Places).filter(Places.street==p["street"],Places.street_number== p["street_number"],Places.number_of_places==p["number_of_places"]).first()
            if not p1:
                p = Places(street=p["street"], street_number=p["street_number"], number_of_places=p["number_of_places"])
                db.session.add(p)
        db.session.commit()
    else:
        print("błąd zapytania)")
    return lista

def verified_street(veryfied_street, lista):
    lista_miejsc =[]
    lista_miejsc_gps = []
    for miejsce in lista:
        ulica = miejsce["ulica"]
        numer_ulicy = miejsce["numer_ulicy"]
        liczba_miejsc = miejsce["liczba_miejsc"]
        if ulica  == veryfied_street:
            a = {f"ulica: {ulica}, numer_ulicy: {numer_ulicy}, liczba_miejsc: {liczba_miejsc}"}
            adress = f"{ulica}+{numer_ulicy}+Warsaw"
            h1 = db.session.query(History).filter(History.street == ulica,
                                                 History.street_number == numer_ulicy,
                                                 History.number_of_places == liczba_miejsc).first()
            if not h1:
                hp = History(street=ulica, street_number=numer_ulicy, number_of_places=liczba_miejsc)
                db.session.add(hp)
            db.session.commit()
            lista_miejsc.append(a)
            lista_miejsc_gps.append((adress, liczba_miejsc))
    return  lista_miejsc, lista_miejsc_gps

def gps(lista_miejsc_gps):
    if lista_miejsc_gps:
        print("*********************")
        print(f"Lista z funkcji gps{lista_miejsc_gps}")
        print("*********************")
    my_map = folium.Map(location=[52.22975703411665, 21.011760261431466], zoom_start=16, )
    tooltip = 'Hej! Naciśnij mnie jeśli chcesz zobaczyć to miejsce parkingowe'
    for place, liczba_miejsc in lista_miejsc_gps:
        url = f"https://nominatim.openstreetmap.org/"
        adress = place
        params = {
            "addressdetails": 1,
            "q": adress,
            "format": "json",
            "limit": 1
        }
        resp = requests.get(url, params=params)
        if resp.ok:
            place_gps = resp.json()
        if place_gps:
            lat =(place_gps[0]["lat"])
            lon = (place_gps[0]["lon"])

            folium.Marker([lat, lon],
                          popup=f'{place}-liczba miejsc parkingowych:{liczba_miejsc}',
                          tooltip=tooltip).add_to(my_map)
    my_map.save('templates/warszawa.html')

@app.route("/", methods=['POST', 'GET'])
def main_page():
    title = "Miejsca parkingowe dla niepełnosprawnych w Warszawie - strona główna"
    veryfied_street = request.form.get("veryfied_street")
    lista = load_parking_places ()
    ulice, kody = verified_street(veryfied_street, lista)
    gps(kody)
    context = {
        "szukana_ulica": (ulice,kody),
    }
    return render_template("index.html", context = context)

@app.route("/wszystkie miejsca", methods=['POST', 'GET'])
def all_places():
    places = db.session.query(Places).order_by(Places.street.asc()).all()
    title = "Wszystkie miejsca pargingowe dla niepełnosprawnych w Warszawie"
    context = {"places": places
    }
    return render_template("places.html", context = context)

@app.route("/mapa", methods=['POST', 'GET'])
def map():
    return render_template("mapa.html" )

@app.route("/mapa2", methods=['POST', 'GET'])
def mapa():
    return render_template("warszawa.html" )

@app.route("/historia", methods=['POST', 'GET'])
def historia():
    history = db.session.query(History).all()
    context = {"history": history
    }
    return render_template("history.html", context = context)

alembic = Alembic()
alembic.init_app(app)