import streamlit as st
import hmac
from auth import iniciar_sessao, autenticar_admin, logout
from clients import buscar_cliente
from admin import mostrar_painel_admin

st.set_page_config(page_title="SVSC-CRISPE", page_icon="🧠", layout="centered")
iniciar_sessao()

def cabecalho():
    st.markdown("<h1>🧠 SVSC-CRISPE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='opacity:0.7'>Sistema de Governanca e IA</p>", unsafe_allow_html=True)

def obter_dados_link():
    params = st.query_params
    cliente_id = str(params.get("cliente", "")).strip()
    token = str(params.get("token", "")).strip()
    if not cliente_id or not token:
        return None
    cliente = buscar_cliente(cliente_id)
    if not cliente:
        return None
    token_salvo = str(cliente.get("token_acesso", "")).strip()
    if token_salvo and hmac.compare_digest(token_salvo, token):
        if cliente.get("ativo", True):
            return cliente
    return None

if st.session_state.get("autenticado"):
    if st.session_state.get("perfil") == "admin":
        cabecalho()
        if st.button("Sair"):
            logout()
        base_url = str(st.secrets.get("APP", {}).get("base_url", "")).strip()
        if not base_url:
            base_url = "https://svsc-crispe-pjqdpgd7.streamlit.app"
        mostrar_painel_admin(base_url=base_url)
    else:
        cabecalho()
        st.write("Painel do Cliente")
        if st.button("Sair"):
            logout()
else:
    cliente_link = obter_dados_link()
    if cliente_link:
        cabecalho()
        st.success(f"Bem-vindo, {cliente_link.get('nome_empresa', 'Cliente')}!")
        st.write("Voce esta logado automaticamente pelo link.")
        texto = st.text_area("Digite sua solicitacao", height=150)
        if st.button("Processar", type="primary"):
            if texto.strip():
                st.info("Solicitacao recebida pelo nucleo SVSC-CRISPE")
            else:
                st.warning("Digite uma solicitacao")
    else:
        cabecalho()
        st.subheader("Area administrativa")
        senha = st.text_input("Senha do administrador", type="password")
        if st.button("Entrar", type="primary"):
            if autenticar_admin(senha):
                st.rerun()
            else:
                st.error("Senha incorreta")
