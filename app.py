import psycopg2
from flask import Flask, render_template, request, redirect
from uuid import uuid4
from supabase import create_client

app = Flask(__name__)

# 🔥 SUPABASE CONFIG
SUPABASE_URL = "https://gyzqfnxwnnxwzqtzodmu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5enFmbnh3bm54d3pxdHpvZG11Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ0NzQyMDcsImV4cCI6MjA5MDA1MDIwN30.U2A381bsMsvEjqlgT9X--Y-4nhCHW9eJXQv9kxoTDRg"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🔥 BANCO
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


# 🔥 FUNÇÃO DE UPLOAD (CORRIGIDA)
def upload_supabase(file, filename):
    file_bytes = file.read()  # 🔥 CORREÇÃO AQUI

    supabase.storage.from_("uploads").upload(
        path=filename,
        file=file_bytes
    )

    return f"{SUPABASE_URL}/storage/v1/object/public/uploads/{filename}"


# 🏠 INDEX
@app.route("/")
def index():
    return render_template("index.html")


# 📤 UPLOAD
@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":
        nome = request.form["nome"]
        foto = request.files["foto"]

        if foto and allowed_file(foto.filename):

            extensao = foto.filename.rsplit(".", 1)[1].lower()
            novo_nome = f"{uuid4().hex}.{extensao}"

            # 🔥 ENVIA PRO SUPABASE
            url_imagem = upload_supabase(foto, novo_nome)

            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO teste_fotos (nome, foto) VALUES (%s, %s)",
                (nome, url_imagem)
            )
            conn.commit()
            cursor.close()
            conn.close()

            return redirect("/listar")

    return render_template("upload.html")


# 📋 LISTAGEM COM PAGINAÇÃO
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