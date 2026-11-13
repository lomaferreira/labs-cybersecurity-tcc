# Laboratório de Cibersegurança — Cenário: IDOR

from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import hashlib
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

estado = {"corrigido": False}

#gera o hash de uma senha usando SHA256
def hash(s):
    return hashlib.sha256(s.encode()).hexdigest()

USUARIOS = {
    "ana":    {"senha": hash("ana2026"),    "nome": "Ana Souza",    "cargo": "Analista de Segurança"},
    "bruno":  {"senha": hash("bruno2026"),  "nome": "Bruno Lima",   "cargo": "Desenvolvedor"},
    "carla":  {"senha": hash("carla2026"),  "nome": "Carla Mendes", "cargo": "Gerente de RH"},
    "diego":  {"senha": hash("diego2026"),  "nome": "Diego Alves",  "cargo": "Contador"},
}

# contracheques, cada um pertence a um funcionário
CONTRACHEQUES = {
    1: {"dono": "ana",   "mes": "Outubro/2026", "salario": "R$ 5.200,00",  "bonus": "R$ 400,00",  "liquido": "R$ 4.891,50"},
    2: {"dono": "bruno", "mes": "Outubro/2026", "salario": "R$ 7.800,00",  "bonus": "R$ 600,00",  "liquido": "R$ 7.254,00"},
    3: {"dono": "carla", "mes": "Outubro/2026", "salario": "R$ 12.500,00", "bonus": "R$ 1.500,00","liquido": "R$ 11.200,00"},
    4: {"dono": "diego", "mes": "Outubro/2026", "salario": "R$ 6.100,00",  "bonus": "R$ 300,00",  "liquido": "R$ 5.620,00"},
}

#mapa de funcionário para contracheque
ID_DO_USUARIO = {}

for id, dados in CONTRACHEQUES.items():
    nome = dados["dono"]
    ID_DO_USUARIO[nome] = id



@app.route("/", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        senha = request.form.get("senha", "")
        nome = USUARIOS.get(usuario)
        if nome and nome["senha"] == hash(senha):
            session["usuario"] = usuario #se o login estiver correto, registra o nome do funcionário na sessão
            return redirect(url_for("home"))
        erro = "Usuário ou senha inválidos."
    return render_template("login.html", erro=erro)

#encerra a sessão do usuário e redireciona para a página de login
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



@app.route("/home")
def home():
    if "usuario" not in session:
        return redirect(url_for("login"))
    #quando o usuário existe, recupera os dados e o id do contracheque, com base nisso carrega a página correpondente
    usuario = session["usuario"]
    dados = USUARIOS[usuario]
    meu_id = ID_DO_USUARIO[usuario]
    return render_template("home.html", usuario=usuario, nome=dados["nome"],
    cargo=dados["cargo"], meu_id=meu_id)


@app.route("/contracheque/<int:cid>")
def contracheque(cid):
    if "usuario" not in session:
        return redirect(url_for("login"))

    contrCh = CONTRACHEQUES.get(cid)
    #quando o id não existe, retorna uma página de erro 404
    if not contrCh:
        return render_template("erro.html", msg="Contracheque não encontrado."), 404

    usuario = session["usuario"]
    
    #quando a defesa está ativada, verifica se o dono do contracheque é o mesmo que está logado, caso contrário retorna uma página de erro 403
    if estado["corrigido"] and contrCh["dono"] != usuario:
        return render_template("erro.html", msg="Acesso negado: este contracheque não pertence a você."), 403

    dono = USUARIOS[contrCh["dono"]]
    flag = None
    if contrCh["dono"] != usuario:
        flag = "FLAG{CONTRACHEQUE_ACESSADO}"

    return render_template("contracheque.html", contrCh=contrCh, dono=dono,
    proprio=(contrCh["dono"] == usuario), flag=flag)


@app.route("/admin/corrigir", methods=["POST"])
def corrigir():
    estado["corrigido"] = True
    return jsonify({"status": "corrigido", "defesa": "verificacao de dono ativada"})

@app.route("/admin/status")
def status():
    if estado["corrigido"]:
        flag = "FLAG{DEFESA_APLICADA_COM_SUCESSO}"
    else:
        flag = None
    return jsonify({"corrigido": estado["corrigido"], "flag": flag})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
