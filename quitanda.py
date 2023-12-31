from flask import Flask, render_template, request, redirect, session
import os
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
        return redirect('/adm') #homepage
    else:
        return render_template("login.html", msg="Usuário/Senha estão incorretos!")

#ROTA DE LOGOFF
@app.route("/logout")
def logout():
    global login
    login = False
    session.clear()
    return redirect('/')

#ROTA PARA PÁG ADM
@app.route("/adm")
def adm():
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        produtos = conexao.execute('SELECT * FROM produtos ORDER BY id_prod DESC').fetchall()
        conexao.close()
        title = "Administração"
        return render_template("adm.html", produtos=produtos, title=title)
    else:
        return redirect("/login")
    
#ROTA DA PÁGINA DE CADASTRO 
@app.route("/cadprodutos")
def cadprodutos():
    if verifica_sessao():
        title = "Cadastro de produto"
        return render_template("cadprodutos.html", title=title)
    else:
        return redirect("/login")
    
#ROTA DA PÁGINA DE CADASTRO NO BANCO
@app.route("/cadastro", methods=["post"])
def cadastro():
    if verifica_sessao():
        nome_prod=request.form['nome_prod']
        desc_prod=request.form['desc_prod']
        preco_prod=request.form['preco_prod']
        img_prod=request.files['img_prod']
        id_foto=str(uuid.uuid4().hex)
        filename=id_foto+nome_prod+'.png'
        img_prod.save("static/img/produtos/"+filename)
        conexao = conecta_database()
        conexao.execute('INSERT INTO produtos (nome_prod, desc_prod, preco_prod, img_prod) VALUES (?, ?, ?, ?)', (nome_prod, desc_prod, preco_prod, filename))
        conexao.commit()
        conexao.close()
        return redirect("/adm")
    else:
        return redirect("/login")
    
@app.route("/excluir/<id_prod>")
def excluir(id_prod):
    if verifica_sessao():
        id_prod = int(id_prod)
        conexao = conecta_database()
        produto = conexao.execute('SELECT * FROM produtos WHERE id_prod = ?', (id_prod,)).fetchall()
        filename_old = produto[0]['img_prod']
        excluir_arquivo = "static/img/produtos/"+filename_old
        os.remove(excluir_arquivo)
        conexao.execute('DELETE FROM produtos WHERE id_prod = ?', (id_prod,))
        conexao.commit()
        conexao.close()
        return redirect('/adm')
    else:
        return redirect("/login")

@app.route("/editprodutos/<id_prod>")
def editar(id_prod):
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        produtos = conexao.execute('SELECT * FROM produtos WHERE id_prod = ?', (id_prod,)).fetchall()
        conexao.close()
        title = "Edição de produtos"
        return render_template("editprodutos.html", produtos=produtos, title=title)
    else:
        return redirect("/login")

@app.route("/editarprodutos", methods=['POST'])
def editprod():
    id_prod = request.form['id_prod']
    nome_prod = request.form['nome_prod']
    desc_prod = request.form['desc_prod']
    preco_prod = request.form['preco_prod']
    img_prod = request.files['img_prod']
    conexao = conecta_database()
    if img_prod:
        produto = conexao.execute('SELECT * FROM produtos WHERE id_prod = ?', (id_prod,)).fetchall()
        filename = produto[0]['img_prod']
        img_prod.save("static/img/produtos"+filename)
    conexao.execute('UPDATE produtos SET nome_prod = ?, desc_prod = ?, preco_prod = ? WHERE id_prod = ?', (nome_prod, desc_prod,preco_prod, id_prod))
    conexao.commit()
    conexao.close()
    return redirect('/adm')

@app.route("/busca", methods=["post"])
def busca():
    busca=request.form['buscar']
    conexao = conecta_database()
    produtos = conexao.execute('SELECT * FROM produtos WHERE nome_prod LIKE "%" || ? || "%"',(busca,)).fetchall()
    title = "Home"
    return render_template("index.html", produtos=produtos, title=title)

app.run(debug=True)