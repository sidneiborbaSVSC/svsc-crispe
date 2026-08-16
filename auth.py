# auth.py
import hashlib
import hmac
import secrets
import streamlit as st


def gerar_hash_senha(senha: str) -> str:
    """Gera um hash seguro para armazenar a senha."""
    salt = secrets.token_bytes(16)
    iteracoes = 310_000

    derivacao = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        iteracoes,
    )

    return (
        f"pbkdf2_sha256$"
        f"{iteracoes}$"
        f"{salt.hex()}$"
        f"{derivacao.hex()}"
    )


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Verifica uma senha contra um hash PBKDF2."""
    try:
        algoritmo, iteracoes, salt_hex, hash_hex = senha_hash.split("$")

        if algoritmo != "pbkdf2_sha256":
            return False

        derivacao = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iteracoes),
        )

        return hmac.compare_digest(
            derivacao,
            bytes.fromhex(hash_hex),
        )

    except (ValueError, TypeError):
        return False


def iniciar_sessao():
    """Inicializa a sessão do usuário."""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if "perfil" not in st.session_state:
        st.session_state.perfil = None

    if "cliente_id" not in st.session_state:
        st.session_state.cliente_id = None


def login_admin(senha: str, senha_configurada: str) -> bool:
    """Autentica o administrador."""
    if not senha_configurada:
        return False

    return hmac.compare_digest(
        senha,
        senha_configurada,
    )


def login_cliente(
    senha: str,
    senha_hash: str,
) -> bool:
    """Autentica um cliente."""
    if not senha_hash:
        return False

    return verificar_senha(
        senha,
        senha_hash,
    )


def autenticar_admin(senha: str, senha_configurada: str):
    """Faz login do administrador."""
    if login_admin(senha, senha_configurada):
        st.session_state.autenticado = True
        st.session_state.perfil = "admin"
        st.session_state.cliente_id = None
        return True

    return False


def autenticar_cliente(
    cliente_id: str,
    senha: str,
    senha_hash: str,
):
    """Faz login do cliente."""
    if login_cliente(senha, senha_hash):
        st.session_state.autenticado = True
        st.session_state.perfil = "cliente"
        st.session_state.cliente_id = cliente_id
        return True

    return False


def logout():
    """Encerra a sessão atual."""
    st.session_state.autenticado = False
    st.session_state.perfil = None
    st.session_state.cliente_id = None
    st.rerun()
