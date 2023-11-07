from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql
import uuid #gera um núme aleatório único para o nome das imagens

app = Flask(__name__)
app.secret_key = "quitandazezinho"

usuario = "usuario"
senha = "senha"
login = False

def verifica_sessao():
    if "login" in session and session["login"]:
        return True
    else:
        return False

def conecta_database():
    conexao = sql.connect("db_quitanda.db")
    conexao.row_factory = sql.Row 
    return conexao

def iniciar_db():
    conexao = conecta_database()
    with app.open_resource('esquema.sql', mode='r') as comandos:
        conexao.cursor().executescript(comandos.read())
    conexao.commit()
    conexao.close()

@app.route("/")
def index():
    iniciar_db()
    conexao = conecta_database()
    produtos = conexao.execute('SELECT * FROM produtos ORDER BY id_prod DESC').fetchall()
    conexao.close()
    title = "Home"
    return render_template("index.html", produtos=produtos, title=title)

#LOGIN
@app.route("/login")
def login():
    return render_template("login.html")

#ROTA PARA VERIFICAR O ACESSO
@app.route("/acesso", methods=['POST'])
def acesso():
    global login, senha
    usuario_informado = request.form["usuario"]
    senha_informada = request.form["senha"]
    if usuario == usuario_informado and senha == senha_informada:
        session["login"] = True
        return redirect('/') #homepage
    else:
        return render_template("login.html", msg="Usuário/Senha estão incorretos!")

@app.route("/logout")
def logout():
    global login
    login = False
    session.clear()
    return redirect('/')

app.run(debug=True)