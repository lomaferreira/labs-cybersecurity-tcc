import time
import requests
#import urllib3

#rllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SERVIDOR_HTTP = "http://servidor:5000"
SERVIDOR_HTTPS = "https://servidor:5443"

CREDENCIAIS = {"usuario": "Ana", "senha": "anAdoTI2026"}

#simula um funcionário que acessa o portal periodicamente a cada 6 segundos
while True:
    try:
        resp = requests.get(f"{SERVIDOR_HTTP}/admin/modo", timeout=5) #requisição ao servidor para saber se o canal é HTTP ou HTTPS
        modo = resp.json().get("modo", "http")
    except Exception as e:
        print(f"[vitima] erro ao consultar modo do servidor: {e}", flush=True)
        time.sleep(5)
        continue

    try:
        if modo == "http":
            requests.post(f"{SERVIDOR_HTTP}", data=CREDENCIAIS, timeout=5) #requisição HTTP POST para login
        else:
            requests.post(f"{SERVIDOR_HTTPS}", data=CREDENCIAIS, timeout=5, verify=False) #verify=False desativa a validação do certificado TLS do servidor
        print(f"[vitima] login enviado via {modo}", flush=True)
    except Exception as e:
        print(f"[vitima] erro ao enviar login: {e}", flush=True)

    time.sleep(6)
