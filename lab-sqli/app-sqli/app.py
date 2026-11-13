# Laboratório de Cibersegurança Gamificado — Cenário: SQL Injection

from flask import Flask, request, render_template, jsonify
import sqlite3
import hashlib

app = Flask(__name__)

estado = {"corrigido": False}

#calcular hash sem salt
def calcular_hash(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


#banco SQLite em memória, criado na inicialização da aplicação
db = sqlite3.connect(":memory:", check_same_thread=False)
db.executescript("""
CREATE TABLE usuarios (id INTEGER PRIMARY KEY, usuario TEXT, senha_hash TEXT, perfil TEXT);
CREATE TABLE funcionarios (id INTEGER PRIMARY KEY, nome TEXT, cargo TEXT, departamento TEXT);
CREATE TABLE segredos (id INTEGER PRIMARY KEY, descricao TEXT, flag TEXT);

INSERT INTO funcionarios (nome, cargo, departamento) VALUES
    ('Ana Souza',      'Perito', 'Sinistros'),
    ('Bruno Lima',     'Gerente Comercial',         'Vendas'),
    ('Carla Mendes',   'Gerente de RH',         'RH'),
    ('Diego Alves',    'Contador',              'Financeiro');

INSERT INTO segredos (descricao, flag) VALUES
    ('Chave do cofre da B&B Seguros', 'FLAG{MINHA_SENHA_SUPER_SECRETA}');
""")

#contas inseridas no banco: admin e ana
db.execute("INSERT INTO usuarios (usuario, senha_hash, perfil) VALUES (?, ?, ?)",
          ("admin", calcular_hash("Zx9!kQ-trueSecurity-2291"), "admin"))
db.execute("INSERT INTO usuarios (usuario, senha_hash, perfil) VALUES (?, ?, ?)",
          ("Ana", calcular_hash("ana2026"), "comum"))
db.commit()

#faz login de usuários 
@app.route("/", methods=["GET", "POST"])
def login():
    erro = None
    flag = None
    mensagem = None

    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        senha = request.form.get("senha", "")
        senha_hash = calcular_hash(senha)

        try:
            if estado["corrigido"]:
                #os valores são enviados separados da query (parâmetros "?")
                consulta = "SELECT * FROM usuarios WHERE usuario = ? AND senha_hash = ?"
                linha = db.execute(consulta, (usuario, senha_hash)).fetchone()
            else:
                # a entrada do usuário é concatenada direto na query
                consulta = f"SELECT * FROM usuarios WHERE usuario = '{usuario}' AND senha_hash = '{senha_hash}'"
                linha = db.execute(consulta).fetchone()

            if linha and linha[3] == "admin":
                flag = "FLAG{LOGIN_ADMIN}"
            elif linha:
                mensagem = f"Bem-vindo(a), {linha[1]}! Seu login foi realizado com sucesso!"
            else:
                erro = "Usuário ou senha inválidos."
        except sqlite3.Error as e:
            #o erro do banco aparece na tela, é esse comportamento que entrega a pista
            erro = f"Erro no servidor: {e}"

    return render_template("login.html", erro=erro, flag=flag, mensagem=mensagem)

#busca de funcionários 
@app.route("/busca")
def busca():
    nome = request.args.get("nome", "")
    resultados = None
    erro = None

    if "nome" in request.args:
        try:
            if estado["corrigido"]:
                # SEGURO
                consulta = "SELECT nome, cargo, departamento FROM funcionarios WHERE nome LIKE ?"
                resultados = db.execute(consulta, (f"%{nome}%",)).fetchall()
            else:
                # VULNERÁVEL
                consulta = f"SELECT nome, cargo, departamento FROM funcionarios WHERE nome LIKE '%{nome}%'"
                resultados = db.execute(consulta).fetchall()
        except sqlite3.Error as e:
            erro = f"Erro no servidor: {e}"

    return render_template("busca.html", nome=nome, resultados=resultados, erro=erro)


#aplica e verifica a defesa
@app.route("/admin/corrigir", methods=["POST"])
def corrigir():
    estado["corrigido"] = True
    return jsonify({"status": "corrigido", "defesa": "consultas parametrizadas ativadas"})


@app.route("/admin/status")
def status():
    if estado["corrigido"]:
        flag = "FLAG{DEFESA_APLICADA_COM_SUCESSO}"
    else:
        flag = None
    return jsonify({"corrigido": estado["corrigido"], "flag": flag})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
