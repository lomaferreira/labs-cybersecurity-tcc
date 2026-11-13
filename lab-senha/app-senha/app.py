#Laboratório de Cibersegurança Gamificado — Cenário: Quebra de Senha

from flask import Flask, request, render_template, jsonify
import hashlib
import secrets
import bcrypt

app = Flask(__name__)

usuarios = {
    "usuario_A": {"senha": "123456", "algoritmo": "md5"},
    "usuario_B": {"senha": "Trombone-Amarelo-47!Girassol", "algoritmo": "bcrypt"},
}


def calcular_hash(senha: str, algoritmo: str) -> str:
    if algoritmo == "md5":
        return hashlib.md5(senha.encode()).hexdigest() #retorna o calculo do hash com md5, após converte de bytes para hexadecimal
    if algoritmo == "bcrypt":
        return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode() #retorna o calculo do hash com bcrypt, o salt gerado também é armazenado junto com o resultado do bcrypt
    raise ValueError(f"algoritmo desconhecido: {algoritmo}")

#verifica se a senha digitada corresponde aos hash armazenados
def verificar_senha(senha: str, hash_armazenado: str, algoritmo: str) -> bool:
    if algoritmo == "md5":
        return hashlib.md5(senha.encode()).hexdigest() == hash_armazenado
    if algoritmo == "bcrypt":
        return bcrypt.checkpw(senha.encode(), hash_armazenado.encode())
    return False


#calcula o hash inicial de cada conta na inicialização da aplicação
for _conta in usuarios.values():
    _conta["hash"] = calcular_hash(_conta["senha"], _conta["algoritmo"])
    _conta["corrigido"] = False

@app.route("/", methods=["GET", "POST"])
def login():
    erro = None
    flag = None
  #verificar se o usuário informado na página existe no banco
    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        senha = request.form.get("senha", "")
        conta = usuarios.get(usuario)
        if conta and verificar_senha(senha, conta["hash"], conta["algoritmo"]):
            flag = f"SENHA_QUEBRADA_{usuario.upper()}"
        else:
            erro = "Usuário ou senha inválidos."
    return render_template("login.html", erro=erro, flag=flag)


#simula o vazamento do banco, expõe usuário:hash
@app.route("/leak")
def leak():
    linhas = []
    for u, c in usuarios.items():
        linha = f"{u}:{c['hash']}"
        linhas.append(linha)
    return "\n".join(linhas) + "\n", 200, {"Content-Type": "text/plain"}


@app.route("/admin/corrigir/<usuario>", methods=["POST"])
def corrigir(usuario):
    conta = usuarios.get(usuario)
    if not conta:
        return jsonify({"erro": "usuário não encontrado"}), 404
    nova_senha = secrets.token_urlsafe(16) #cria uma nova senha com com 16 bits e aleatoriedade
    conta["senha"] = nova_senha
    conta["algoritmo"] = "bcrypt" #mudança do algoritmo
    conta["hash"] = calcular_hash(nova_senha, "bcrypt") #calcula um novo hash com o novo algoritmo e nova senha
    conta["corrigido"] = True
    return jsonify({
        "usuario": usuario,
        "novo_algoritmo": "bcrypt",
        "nova_senha": nova_senha,
        "status": "corrigido",
    })

#retornar o resultado final das modificações com a flag de confirmação de defesa aplicada
@app.route("/admin/status")
def status():
    resultado = {}
    for usuario, conta in usuarios.items():
        resultado[usuario] = {
            "algoritmo": conta["algoritmo"],
            "corrigido": conta["corrigido"]
        }
    todos_seguros = True
    for conta in usuarios.values():
        if conta["algoritmo"] != "bcrypt":
            todos_seguros = False
            break
    if todos_seguros:
        flag = "DEFESA_APLICADA_COM_SUCESSO"
    else:
        flag = None
    return jsonify({
        "contas": resultado,
        "flag": flag
    })

#inicialização do servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
