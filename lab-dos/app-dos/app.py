#Laboratório de Cibersegurança Gamificado — Cenário: Negação de Serviço (DoS)

import os
import time

from flask import Flask, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

#latência artificial simulando trabalho real de backend 
LATENCIA_SEGUNDOS = float(os.environ.get("LATENCIA_SEGUNDOS", "0.2"))

#limitador de requisições por IP, inicialmente sem limite, só entra em vigor quando a defesa é ativada
limiter = Limiter(get_remote_address, app=app, default_limits=[])

estado = {"defesa_ativa": False}

#verifica se a defesa está desativad
def defesa_desativada() -> bool:
    return not estado["defesa_ativa"]

#atende quem acessa a página inicial
@app.route("/")
@limiter.limit("10 per minute", exempt_when=defesa_desativada)
def home():
    time.sleep(LATENCIA_SEGUNDOS)
    return render_template("home.html")

#rota para ativar a defesa de rate limiting por IP na rota alvo
@app.route("/admin/ativar_defesa", methods=["POST"])
def ativar_defesa():
    estado["defesa_ativa"] = True
    return jsonify({
        "status": "defesa ativada",
        "regra": "10 request/min por IP na rota '/'",
    })

#rota para ativar a defesa
@app.route("/admin/desativar_defesa", methods=["POST"])
def desativar_defesa():
    estado["defesa_ativa"] = False
    return jsonify({"status": "defesa desativada"})


@app.route("/admin/status")
def status():
    if estado["defesa_ativa"]:
        flag = "FLAG{DEFESA_APLICADA_COM_SUCESSO}"
    else:
        flag = None
    return jsonify({"defesa_ativa": estado["defesa_ativa"], "flag": flag})


if __name__ == "__main__":
    # threaded=False desativa o atendimento de requisições em múltiplas threads
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=False)
