# Laboratório de Cibersegurança Gamificado — Cenário: XSS Refletido

import secrets
from datetime import datetime
from urllib.parse import parse_qs #transforma uma sequência de parâmetros em um dicionário


from flask import Flask, jsonify, make_response, render_template, request, session

app = Flask(__name__)


estado = {"corrigido": False}

#chave utilizada para assinar os cookies de sessão
app.secret_key = secrets.token_hex(32)

#permite que JavaScript leia o cookie
app.config["SESSION_COOKIE_HTTPONLY"] = False

# dados capturados pelo atacante
capturados = []


@app.route("/", methods=["GET", "POST"])
def login():
    aviso = request.args.get("aviso")  
    mensagem = None

    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        senha = request.form.get("senha", "")
        if usuario == "ana" and senha == "ana2026":
            session["usuario"] = usuario
            mensagem = f"Bem-vindo(a), {usuario}!"
        else:
            mensagem = "Usuário ou senha inválidos."

    #transforma o conteudo em uma resposta HTTP
    resp = make_response(
        render_template(
            "login.html", aviso=aviso, mensagem=mensagem, corrigido=estado["corrigido"]
        )
    )

    return resp


@app.route("/analytics/evento", methods=["POST"])
def analytics_evento():
    #lê o corpo da requisição HTTP como texto puro, no formato "chave=valor&chave=valor"
    corpo = request.get_data(as_text=True)
    campos = parse_qs(corpo)

    #armazena os dados capturados pelo atacante (usuário, senha e cookie)
    capturados.append(
        {
        "usuario": campos.get("usuario", [""])[0],
        "senha": campos.get("senha", [""])[0],
        "cookie": campos.get("cookie", [""])[0],
        }
    )
    return ("", 204)

#exibe os dados capturados pelo atacante e a flag
@app.route("/painel")
def painel():
    if capturados:
        flag = "FLAG{CREDENCIAIS_ROUBADAS}"
    else:
        flag = None

    return render_template(
        "painel.html", capturados=list(reversed(capturados)), flag=flag
    )


@app.route("/admin/corrigir", methods=["POST"])
def corrigir():
    estado["corrigido"] = True
    return jsonify(
        {"status": "corrigido"}
    )


@app.route("/admin/status")
def status():
    if estado["corrigido"]:
         flag = "FLAG{DEFESA_APLICADA_COM_SUCESSO}"
    else:
        flag= None

    return jsonify({"corrigido": estado["corrigido"], "flag": flag})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
