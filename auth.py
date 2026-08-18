import hashlib
import hmac
import secrets
import streamlit as st

ITERATIONS = 310000

def iniciar_sessao():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "perfil" not in st.session_state:
        st.session_state.perfil = None
    if "cliente_id" not in st.session_state:
        st.session_state.cliente_id = None

def autenticar_admin(senha):
    senha_correta = str(st.secrets.get("ADMIN_PASSWORD", ""))
    if not senha_correta:
        return False
    if not hmac.compare_digest(senha, senha_correta):
        return False
    st.session_state.autenticado = True
    st.session_state.perfil = "admin"
    st.session_state.cliente_id = None
    return True

def logout():
    st.session_state.autenticado = False
    st.session_state.perfil = None
    st.session_state.cliente_id = None
    st.rerun()
