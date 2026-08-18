import json
import os
import secrets
from datetime import datetime

CLIENTS_FILE = "clients.json"

def carregar_clientes():
    if not os.path.exists(CLIENTS_FILE):
        return {}
    try:
        with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def salvar_clientes(clientes):
    with open(CLIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(clientes, f, indent=2, ensure_ascii=False)

def criar_cliente(nome_empresa, responsavel="", email=""):
    clientes = carregar_clientes()
    cliente_id = secrets.token_hex(4)
    token = secrets.token_urlsafe(32)
    agora = datetime.now().isoformat()
    
    cliente = {
        "id": cliente_id,
        "nome_empresa": nome_empresa.strip(),
        "responsavel": responsavel.strip(),
        "email": email.strip(),
        "token_acesso": token,
        "ativo": True,
        "status": "trial",
        "criado_em": agora,
        "inicio_teste": agora
    }
    
    clientes[cliente_id] = cliente
    salvar_clientes(clientes)
    return cliente

def buscar_cliente(cliente_id):
    clientes = carregar_clientes()
    return clientes.get(cliente_id)

def atualizar_cliente(cliente_id, **alteracoes):
    clientes = carregar_clientes()
    if cliente_id not in clientes:
        return False
    for campo, valor in alteracoes.items():
        clientes[cliente_id][campo] = valor
    salvar_clientes(clientes)
    return True

def excluir_cliente(cliente_id):
    clientes = carregar_clientes()
    if cliente_id not in clientes:
        return False
    del clientes[cliente_id]
    salvar_clientes(clientes)
    return True

def ativar_cliente(cliente_id):
    return atualizar_cliente(cliente_id, ativo=True, status="ativo")

def desativar_cliente(cliente_id):
    return atualizar_cliente(cliente_id, ativo=False, status="inativo")

def gerar_link_cliente(cliente_id, base_url):
    cliente = buscar_cliente(cliente_id)
    if not cliente:
        return None
    token = cliente.get("token_acesso")
    if not token:
        return None
    separador = "&" if "?" in base_url else "?"
    return f"{base_url}{separador}cliente={cliente_id}&token={token}"
