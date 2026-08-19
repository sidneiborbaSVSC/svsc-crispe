import json
import os
import secrets
import sqlite3
from datetime import datetime
from typing import Dict, Optional

DB_FILE = "clients.db"
JSON_FILE = "clients.json"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS clients (
    id TEXT PRIMARY KEY,
    nome_empresa TEXT,
    responsavel TEXT,
    email TEXT,
    token_acesso TEXT,
    ativo INTEGER,
    status TEXT,
    criado_em TEXT,
    inicio_teste TEXT
);
"""


def _get_conn():
    conn = sqlite3.connect(DB_FILE, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_db():
    conn = _get_conn()
    with conn:
        conn.execute(CREATE_TABLE_SQL)
    conn.close()


def _import_json_if_present():
    if not os.path.exists(JSON_FILE):
        return
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return
    if not isinstance(data, dict) or not data:
        return
    _ensure_db()
    conn = _get_conn()
    with conn:
        for cid, cliente in data.items():
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO clients (id, nome_empresa, responsavel, email, token_acesso, ativo, status, criado_em, inicio_teste) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        cliente.get("id"),
                        cliente.get("nome_empresa"),
                        cliente.get("responsavel"),
                        cliente.get("email"),
                        cliente.get("token_acesso"),
                        1 if cliente.get("ativo", True) else 0,
                        cliente.get("status", "trial"),
                        cliente.get("criado_em"),
                        cliente.get("inicio_teste"),
                    ),
                )
            except Exception:
                # skip malformed entries
                continue
    conn.close()


# Initialize DB and import if needed
_ensure_db()
_import_json_if_present()


def carregar_clientes() -> Dict[str, dict]:
    _ensure_db()
    conn = _get_conn()
    clientes = {}
    try:
        cur = conn.execute("SELECT * FROM clients")
        rows = cur.fetchall()
        for row in rows:
            clientes[row["id"]] = {
                "id": row["id"],
                "nome_empresa": row["nome_empresa"],
                "responsavel": row["responsavel"],
                "email": row["email"],
                "token_acesso": row["token_acesso"],
                "ativo": bool(row["ativo"]),
                "status": row["status"],
                "criado_em": row["criado_em"],
                "inicio_teste": row["inicio_teste"],
            }
    finally:
        conn.close()
    return clientes


def salvar_clientes(clientes: Dict[str, dict]):
    # convenience function to replace entire clients set
    _ensure_db()
    conn = _get_conn()
    with conn:
        conn.execute("DELETE FROM clients")
        for cid, c in clientes.items():
            conn.execute(
                "INSERT INTO clients (id, nome_empresa, responsavel, email, token_acesso, ativo, status, criado_em, inicio_teste) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    c.get("id"),
                    c.get("nome_empresa"),
                    c.get("responsavel"),
                    c.get("email"),
                    c.get("token_acesso"),
                    1 if c.get("ativo", True) else 0,
                    c.get("status", "trial"),
                    c.get("criado_em"),
                    c.get("inicio_teste"),
                ),
            )
    conn.close()


def criar_cliente(nome_empresa, responsavel="", email="") -> dict:
    _ensure_db()
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
        "inicio_teste": agora,
    }

    conn = _get_conn()
    with conn:
        conn.execute(
            "INSERT INTO clients (id, nome_empresa, responsavel, email, token_acesso, ativo, status, criado_em, inicio_teste) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                cliente["id"],
                cliente["nome_empresa"],
                cliente["responsavel"],
                cliente["email"],
                cliente["token_acesso"],
                1,
                cliente["status"],
                cliente["criado_em"],
                cliente["inicio_teste"],
            ),
        )
    conn.close()
    return cliente


def buscar_cliente(cliente_id) -> Optional[dict]:
    _ensure_db()
    conn = _get_conn()
    try:
        cur = conn.execute("SELECT * FROM clients WHERE id = ?", (cliente_id,))
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "nome_empresa": row["nome_empresa"],
            "responsavel": row["responsavel"],
            "email": row["email"],
            "token_acesso": row["token_acesso"],
            "ativo": bool(row["ativo"]),
            "status": row["status"],
            "criado_em": row["criado_em"],
            "inicio_teste": row["inicio_teste"],
        }
    finally:
        conn.close()


def atualizar_cliente(cliente_id, **alteracoes) -> bool:
    _ensure_db()
    clientes = carregar_clientes()
    if cliente_id not in clientes:
        return False
    cliente = clientes[cliente_id]
    for campo, valor in alteracoes.items():
        cliente[campo] = valor
    conn = _get_conn()
    with conn:
        conn.execute(
            "UPDATE clients SET nome_empresa = ?, responsavel = ?, email = ?, token_acesso = ?, ativo = ?, status = ?, criado_em = ?, inicio_teste = ? WHERE id = ?",
            (
                cliente.get("nome_empresa"),
                cliente.get("responsavel"),
                cliente.get("email"),
                cliente.get("token_acesso"),
                1 if cliente.get("ativo", True) else 0,
                cliente.get("status"),
                cliente.get("criado_em"),
                cliente.get("inicio_teste"),
                cliente_id,
            ),
        )
    conn.close()
    return True


def excluir_cliente(cliente_id) -> bool:
    _ensure_db()
    conn = _get_conn()
    with conn:
        cur = conn.execute("DELETE FROM clients WHERE id = ?", (cliente_id,))
        deleted = cur.rowcount
    conn.close()
    return deleted > 0


def ativar_cliente(cliente_id) -> bool:
    return atualizar_cliente(cliente_id, ativo=True, status="ativo")


def desativar_cliente(cliente_id) -> bool:
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
