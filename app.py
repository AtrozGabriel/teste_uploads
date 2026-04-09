import os
import psycopg2
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from uuid import uuid4

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def conectar():
    return psycopg2.connect(
        host="aws-0-us-west-2.pooler.supabase.com",
        port=6543,
        dbname="postgres",
        user="postgres.gyzqfnxwnnxwzqtzodmu",
        password="senhadobanco",
        sslmode="require"
    )

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":
        nome = request.form["nome"]
        foto = request.files["foto"]

        if foto and allowed_file(foto.filename):

            extensao = foto.filename.rsplit(".", 1)[1].lower()
            novo_nome = f"{uuid4().hex}.{extensao}"

            caminho = os.path.join(app.config["UPLOAD_FOLDER"], novo_nome)
            foto.save(caminho)

            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO teste_fotos (nome, foto) VALUES (%s, %s)",
                (nome, caminho)
            )
            conn.commit()
            cursor.close()
            conn.close()

            return redirect("/listar")

    return render_template("upload.html")


@app.route("/listar")
def listar():
    pagina = request.args.get("page", 1, type=int)
    limite = 12
    offset = (pagina - 1) * limite

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT nome, foto FROM teste_fotos ORDER BY id DESC LIMIT %s OFFSET %s",
        (limite, offset)
    )
    fotos = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM teste_fotos")
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    total_paginas = (total // limite) + (1 if total % limite > 0 else 0)

    return render_template(
        "listar.html",
        fotos=fotos,
        pagina=pagina,
        total_paginas=total_paginas
    )


if __name__ == "__main__":
    app.run(debug=True)