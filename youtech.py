from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql 
import uuid 
import os

app= Flask(__name__)
app.secret_key = "youtechzinho"

#Reformulando a questão do usuário para envolver o RH 
usuario = "adm"
senha = "123"
login = False

#Função para sessão RH 
def verifica_sessao():
    if "login" in session and session["login"]:
        return True
    else:
        return False
    
#Estabelecendo conexão com Banco de dados 
def conecta_database():
    conexao = sql.connect("db_youtech.db")
    conexao.row_factory = sql.Row
    return conexao

#Iniciando baco de dados 
def iniciar_db():
    conexao = conecta_database()
    with app.open_resource('esquema.sql', mode='r') as comandos:
        conexao.cursor().executescript(comandos.read())
    conexao.commit()
    conexao.close()

#Rota da página inicial 
@app.route("/")
def index():
    iniciar_db()
    conexao = conecta_database()
    vagas = conexao.execute('SELECT * FROM vagas ORDER BY id_vaga DESC').fetchall()
    conexao.close()
    title = "Home"
    return render_template("home.html", vagas=vagas, title=title)

# Rota login 
@app.route("/login")
def login():
    title ="Login"
    return render_template("login.html",title=title)

#Rota da página acesso 
@app.route("/acesso", methods=['post'])
def acesso():
    global usuario, senha
    usuario_informado = request.form["usuario"]
    senha_informada = request.form["senha"]
    if usuario == usuario_informado and senha==senha_informada:
        session["login"] = True
        return redirect('/admrh')
    else:
        return render_template("login.html", msg="Usuário/Senha estão incorretos!")
    
#Rota para a página de administração do RH 
@app.route("/admrh")
def adm():
    if verifica_sessao():
        conexao = conecta_database()
        vagas = conexao.execute('SELECT * FROM vagas ORDER BY id_vaga DESC').fetchall()
        conexao.close()
        title = "Administração RH"
        return render_template("admrh.html" , vagas=vagas, title=title)
    else:
        return redirect("/login")
    
#código do logout
@app.route("/logout")
def logout():
    global login
    login = False
    session.clear()
    return redirect('/')

#Rota da página de cadastro de vagas
@app.route("/cadvagas")
def cadvagas():
    if verifica_sessao():
        title = "Cadastro de Vagas"
        return render_template("cadvagas.html", title=title)
    else:
        return redirect("/login")
    
#Rota da página de cadastro de vagas no banco
@app.route("/cadastro",methods=["post"])
def cadastro():
    if verifica_sessao():
        cargo_vaga=request.form['cargo_vaga'] 
        requi_vaga=request.form['requi_vaga']
        img_vaga=request.files['img_vaga']
        salario_vaga= request.form['salario_vaga']
        local_vaga= request.form['local_vaga']
        email_vaga = request.form['email_vaga']
        tipo_vaga = request.form['tipo_vaga']
        id_foto=str(uuid.uuid4().hex)
        filename=id_foto+cargo_vaga+'.png'
        img_vaga.save("static/img/vagas/"+filename)
        conexao = conecta_database()
        conexao.execute('INSERT INTO vagas (cargo_vaga, requi_vaga, salario_vaga, local_vaga, email_vaga, tipo_vaga, img_vaga) VALUES (?, ?, ?, ?, ?, ?, ?)', (cargo_vaga, requi_vaga, salario_vaga, local_vaga, email_vaga, tipo_vaga, filename))

        conexao.close()
        return redirect("/admrh")
    else:
        return redirect("/login")
    
#Rota de exclusão
@app.route("/excluir/<id_vaga>")
def excluir(id_vaga):
    if verifica_sessao():
        id_vaga = int(id_vaga)
        conexao = conecta_database()
        vaga = conexao.execute('SELECT * FROM vagas WHERE id_vaga = ?', (id_vaga,)).fetchall()
        
        if vaga:
            filename_old = vaga[0]['img_vaga']
            excluir_arquivo = "static/img/vagas/" + filename_old
            os.remove(excluir_arquivo)
            
            conexao.execute('DELETE FROM vagas WHERE id_vaga = ?', (id_vaga,))
            conexao.commit()
            conexao.close()
            return redirect('/admrh')
        else:
            return "Vaga não encontrada."
    else:
        return redirect('/login')

      
#Criar rota de edição
@app.route("/editvagas/<id_vaga>")
def editar(id_vaga):
    if verifica_sessao():
        id_vaga = int(id_vaga)
        conexao = conecta_database()
        vagas = conexao.execute('SELECT * FROM vagas WHERE id_vaga = ?',(id_vaga,)).fetchall()
        conexao.close()
        title = "Edição de Vagas"
        return render_template("editvagas.html",vagas=vagas,title=title)
    else:
        return redirect("/login")
    
#Rota para tratar edição
@app.route("/editarvagas", methods=['POST'])
def editvaga():
    id_vaga= request.form['id_vaga']
    cargo_vaga=request.form['cargo_vaga'] 
    requi_vaga=request.form['requi_vaga']
    img_vaga=request.files['img_vaga']
    salario_vaga= request.form['salario_vaga']
    local_vaga= request.form['local_vaga']
    conexao = conecta_database()
    if img_vaga:
        vaga = conexao.execute('SELECT * FROM vagas WHERE id_vaga = ? ', (id_vaga,)).fetchall()
        filename = vaga[0]['img_vaga']
        img_vaga.save("static/img/vagas/"+filename)
    conexao.execute('UPDATE vagas SET cargo_vaga = ?, requi_vaga = ?, salario_vaga = ?, local_vaga = ?  WHERE id_vaga = ?', (cargo_vaga, requi_vaga, salario_vaga, local_vaga, id_vaga))
    conexao.commit()
    conexao.close()
    return redirect('/admrh')

#Rota para a busca de vagas 
@app.route("/busca", methods=["post"])
def busca():
    busca = request.form['buscar']
    conexao = conecta_database()
    vagas = conexao.execute('SELECT * FROM vagas WHERE cargo_vaga LIKE "%" || ? || "%"',(busca,)).fetchall()
    title= "Home"
    return render_template("home.html", vagas=vagas, title=title)

#Rota para página individual das vagas 
@app.route("/vagaindi/<id_vaga>",methods=['GET'])
def vaga_especifica(id_vaga):
    id_vaga = int(id_vaga)
    conexao = conecta_database()
    vagas = conexao.execute('SELECT * FROM vagas WHERE id_vaga = ?',(id_vaga,)).fetchall()
    conexao.close()
    title = "Vaga Especificada"
    return render_template("vagaindi.html",vagas=vagas,title=title)


#Final do código - Executando o servidor
app.run(debug=True)