import os
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

import forms

basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)

app = Flask(__name__)

app.config["SECRET_KEY"] = "dfgsfdgsdfgsdfgsdf"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "vaikaitevai.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Tevas(db.Model):
    __tablename__ = "tevas"
    id = db.Column(db.Integer, primary_key=True)
    vardas = db.Column("Vardas", db.String)
    pavarde = db.Column("Pavardė", db.String)
    vaikas_id = db.Column(db.Integer, db.ForeignKey("vaikas.id"))
    vaikas = db.relationship("Vaikas", backref="tevai")

    def __init__(self, vardas, pavarde, vaikas_id) -> None:
        self.vardas = vardas
        self.pavarde = pavarde
        self.vaikas_id = vaikas_id


class Vaikas(db.Model):
    __tablename__ = "vaikas"
    id = db.Column(db.Integer, primary_key=True)
    vardas = db.Column("Vardas", db.String)
    pavarde = db.Column("Pavardė", db.String)

    def __init__(self, vardas, pavarde):
        self.vardas = vardas
        self.pavarde = pavarde


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/tevai")
def parents():
    try:
        all_parents = Tevas.query.all()
    except:
        all_parents = []
    print(all_parents)
    return render_template("tevai.html", parents=all_parents)


@app.route("/vaikai")
def children():
    try:
        all_children = Vaikas.query.all()
    except:
        all_children = []

    return render_template("vaikai.html", children=all_children)


@app.route("/naujas_tevas", methods=["GET", "POST"])
def new_parent():
    db.create_all()
    forma = forms.TevasForm()
    if forma.validate_on_submit():
        print(dir(forma.vaikas))
        if not forma.vaikas.data:
            vaikas_id = None
        else:
            vaikas_id = forma.vaikas.data.id
        naujas_tevas = Tevas(
            vardas=forma.vardas.data,
            pavarde=forma.pavarde.data,
            vaikas_id=vaikas_id,
        )
        db.session.add(naujas_tevas)
        db.session.commit()
        return redirect(url_for("parents"))
    return render_template("prideti_teva.html", form=forma)


@app.route("/delete/<int:id>")
def delete(id):
    uzklausa = Tevas.query.get(id)
    db.session.delete(uzklausa)
    db.session.commit()
    return redirect(url_for("parents"))


@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    form = forms.TevasForm()
    tevas = Tevas.query.get(id)
    if form.validate_on_submit():
        tevas.vardas = form.vardas.data
        tevas.pavarde = form.pavarde.data
        tevas.vaikas_id = form.vaikas.data.id
        db.session.commit()
        return redirect(url_for("parents"))
    return render_template("update.html", form=form, tevas=tevas)


@app.route("/naujas_vaikas", methods=["GET", "POST"])
def new_child():
    db.create_all()
    forma = forms.VaikasForm()
    if forma.validate_on_submit():
        naujas_vaikas = Vaikas(vardas=forma.vardas.data, pavarde=forma.pavarde.data)
        db.session.add(naujas_vaikas)
        db.session.commit()
        return redirect(url_for("children"))
    return render_template("prideti_vaika.html", form=forma)


@app.route("/vaikas_delete/<int:id>")
def vaikas_delete(id):
    uzklausa = Vaikas.query.get(id)
    db.session.delete(uzklausa)
    db.session.commit()
    return redirect(url_for("children"))


if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True)
