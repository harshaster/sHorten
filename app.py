from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, BigInteger,Column
from sqlalchemy.exc import IntegrityError
import time

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///shorten.sqlite3"

db=SQLAlchemy()

HOST = "http://127.0.0.1:5000"
VALIDITY = (0)*3600 + (5)*60 + (0) 


class Mapping(db.Model):
    alias = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    created = Column(BigInteger, nullable=False)
    until = Column(BigInteger, nullable=False)

app.app_context().push()

db.init_app(app)

db.create_all()

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/")
def shorten():
    data = request.form.to_dict()
    og = data['url']
    alias = data['alias']
    if len(og.split("."))<2:
        return render_template("error.html", code=400)
    if not og.startswith("http://") or not og.startswith("https://"):
        og = "http://" + og
    try : 
        new = Mapping(
            alias = alias,
            url = og,
            created = time.time(),
            until = time.time() + VALIDITY
        )
        # print("here")
        db.session.add(new)
        db.session.commit()
    except IntegrityError:
        return render_template("index.html", duplicate=True, response=False, alias=alias, url=og)
    except:
        return render_template("error.html", code=500)
    return render_template("index.html", response=True, short_url=f"{HOST}/{data['alias']}")

@app.get("/<string:alias>")
def redir(alias):
    mapping = Mapping.query.get(alias)
    if not mapping:
        return render_template("error.html", code=404)
    url = mapping.url

    return redirect(f"{mapping.url}")


if __name__=="__main__":
    app.run(debug=True)