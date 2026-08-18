import streamlit as st
import hmac
from auth import iniciar_sessao, autenticar_admin, logout
from clients import buscar_cliente
from admin import mostrar_painel_admin

st.set_page_config(page_title="SVSC-CRISPE", page_icon="🧠", layout="centered")
iniciar_sessao()

def cabecalho():
    st.markdown("<h1>🧠 SVSC-CRISPE</h1><p style='opacity:0.7'>Sistema de Governança e IA</p>", unsafe_allow_html=True)

def obter_dados_link():
    params = st.query_params
    cliente_id = str(params.get("cliente", "")).strip()
    token = str(params.get("token", "")).strip()
    if not cliente_id or not token: return None
    cliente = buscar_cliente(cliente_id)
    if not cliente: return None
    token_salvo = str(cliente.get("token_acesso", "")).strip()
    if token_salvo and hmac.compare_digest(token_salvo, token) and cliente.get("ativo", True):
        return cliente
    return None

if st.session_state.get("autenticado"):
    if st.session_state.get("perfil") == "admin":
        cabecalho()
        if st.button("Sair do Admin"): logout()
        mostrar_painel_admin(base_url=st.get_option("server.baseUrlPath") or "")
    else:
        cabecalho()
        st.write("Painel do Cliente")
        if st.button("Sair"): logout()
else:
    cliente_link = obter_dados_link()
    if cliente_link:
        cabecalho()
        st.subheader(f"🔐 Acesso de {cliente_link.get('nome_empresa', 'Cliente')}")
        if st.button("Entrar (Demo)"): st.write("Login do cliente")
    else:
        cabecalho()
        st.subheader("🛡️ Área administrativa")
        senha_admin = st.text_input("Senha do administrador", type="password")
        if st.button("Entrar", type="primary"):
            if autenticar_admin(senha_admin):
                st.rerun()
            else:
                st.error("Senha incorreta.")
