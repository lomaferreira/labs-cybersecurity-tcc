# Laboratório de Cibersegurança Gamificado — Cenário: Man-in-the-Middle (ARP Spoofing)

from flask import Flask, request, render_template, jsonify
import threading

app = Flask(__name__)

CREDENCIAIS = {"usuario": "Ana", "senha": "anAdoTI2026"}

#estado compartilhado entre as threads HTTP e HTTPS
estado = {"modo": "http", "defesa_aplicada": False}

# rota de login, que recebe as credenciais enviadas pelo container vitima
@app.route("/", methods=["GET", "POST"])
def login():
    erro = None
    flag = None
    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        senha = request.form.get("senha", "")
        if usuario == CREDENCIAIS["usuario"] and senha == CREDENCIAIS["senha"]:
            flag = "CREDENCIAIS_INTERCEPTADAS"
        else:
            erro = "Usuário ou senha inválidos."
    return render_template("login.html", erro=erro, flag=flag)


#mostra em qual modo o servidor está operando (consultado pelo container vitima
#a cada ciclo, e pelo aluno para confirmar se a defesa foi aplicada)
@app.route("/admin/modo")
def modo():
    flag = None
    if estado["defesa_aplicada"]:
        flag = "DEFESA_APLICADA_COM_SUCESSO"
    return jsonify({
        "modo": estado["modo"],
        "defesa_aplicada": estado["defesa_aplicada"],
        "flag": flag,
    })


# aplica a correção: a vitima passa a enviar as credenciais apenas pelo canal HTTPS
@app.route("/admin/ativar-https", methods=["POST"])
def ativar_https():
    estado["modo"] = "https"
    estado["defesa_aplicada"] = True
    return jsonify({"modo": estado["modo"]})


def run_http():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


def run_https():
    #adhoc gera um certificado autoassinado automaticamente na inicialização,
    app.run(host="0.0.0.0", port=5443, ssl_context="adhoc", debug=False, use_reloader=False)


if __name__ == "__main__":
    thread_https = threading.Thread(target=run_https, daemon=True)
    thread_https.start()
    run_http()
