# clients.py

import json
import os
import secrets
from datetime import datetime


CLIENTS_FILE = "clients.json"


def carregar_clientes():
    """Carrega os clientes cadastrados."""
    if not os.path.exists(CLIENTS_FILE):
        return {}

    try:
        with open(CLIENTS_FILE, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        return dados if isinstance(dados, dict) else {}

    except (json.JSONDecodeError, OSError):
        return {}


def salvar_clientes(clientes):
    """Salva os clientes."""
    with open(
        CLIENTS_FILE,
        "w",
        encoding="utf-8",
    ) as arquivo:
        json.dump(
            clientes,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )


def gerar_id_cliente():
    """Gera um identificador único."""
    clientes = carregar_clientes()

    while True:
        cliente_id = secrets.token_hex(4)

        if cliente_id not in clientes:
            return cliente_id


def gerar_token_acesso():
    """Gera o token usado no link individual."""
    return secrets.token_urlsafe(32)


def criar_cliente(
    nome_empresa,
    responsavel="",
    email="",
):
    """Cria um novo cliente."""
    clientes = carregar_clientes()

    cliente_id = gerar_id_cliente()
    token = gerar_token_acesso()

    agora = datetime.now().isoformat()

    cliente = {
        "id": cliente_id,
        "nome_empresa": nome_empresa.strip(),
        "responsavel": responsavel.strip(),
        "email": email.strip(),
        "token_acesso": token,
        "ativo": True,
        "status": "novo",
        "criado_em": agora,
        "primeiro_acesso": None,
        "inicio_teste": None,
        "fim_teste": None,
        "provedor": None,
        "api_configurada": False,
    }

    clientes[cliente_id] = cliente
    salvar_clientes(clientes)

    return cliente


def buscar_cliente(cliente_id):
    """Busca um cliente pelo ID."""
    clientes = carregar_clientes()
    return clientes.get(cliente_id)


def atualizar_cliente(cliente_id, **alteracoes):
    """Atualiza os dados permitidos de um cliente."""
    clientes = carregar_clientes()

    if cliente_id not in clientes:
        return False

    campos_permitidos = {
        "nome_empresa",
        "responsavel",
        "email",
        "ativo",
        "status",
        "primeiro_acesso",
        "inicio_teste",
        "fim_teste",
        "provedor",
        "api_configurada",
    }

    for campo, valor in alteracoes.items():
        if campo in campos_permitidos:
            clientes[cliente_id][campo] = valor

    salvar_clientes(clientes)

    return True


def excluir_cliente(cliente_id):
    """Remove um cliente."""
    clientes = carregar_clientes()

    if cliente_id not in clientes:
        return False

    del clientes[cliente_id]
    salvar_clientes(clientes)

    return True


def ativar_cliente(cliente_id):
    """Ativa um cliente."""
    return atualizar_cliente(
        cliente_id,
        ativo=True,
        status="ativo",
    )


def desativar_cliente(cliente_id):
    """Desativa um cliente."""
    return atualizar_cliente(
        cliente_id,
        ativo=False,
        status="inativo",
    )


def cliente_por_token(token):
    """Localiza um cliente pelo token do link."""
    clientes = carregar_clientes()

    for cliente in clientes.values():
        if cliente.get("token_acesso") == token:
            return cliente

    return None


def gerar_link_cliente(
    cliente_id,
    base_url,
):
    """Gera o link individual do cliente."""
    cliente = buscar_cliente(cliente_id)

    if not cliente:
        return None

    token = cliente.get("token_acesso")

    if not token:
        return None

    separador = "&" if "?" in base_url else "?"

    return (
        f"{base_url}"
        f"{separador}"
        f"cliente={cliente_id}"
        f"&token={token}"
    )
