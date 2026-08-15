import json
import hashlib
import hmac
import secrets
from urllib.parse import urlencode
import streamlit as st

APP_NAME = "SVSC-CRISPE"
APP_VERSION = "1.0.0"

st.set_page_config(page_title=APP_NAME, page_icon="🧠", layout="centered")

st.markdown("""
<style>
.block-container{max-width:900px;padding-top:2rem}
.hero{padding:1.4rem;border-radius:18px;border:1px solid rgba(128,128,128,.25);margin-bottom:1rem}
.small{opacity:.7;font-size:.9rem}
</style>
""", unsafe_allow_html=True)

def gerar_hash_senha(senha: str) -> str:
    salt = secrets.token_bytes(16)
    n = 310_000
    h = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, n)
    return f"pbkdf2_sha256${n}${salt.hex()}${h.hex()}"

def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        algoritmo, n, salt_hex, hash_hex = senha_hash.split("$")
        if algoritmo != "pbkdf2_sha256":
            return False
        h = hashlib.pbkdf2_hmac(
            "sha256", senha.encode(), bytes.fromhex(salt_hex), int(n)
        )
        return hmac.compare_digest(h, bytes.fromhex(hash_hex))
    except Exception:
        return False

def carregar_config():
    try:
        auth = st.secrets.get("auth", {})
    except Exception:
        auth = {}
    admin_hash = str(auth.get("admin_password_hash", "")).strip()
    admin_password = str(auth.get("admin_password", "")).strip()
    raw = str(auth.get("clients_json", "")).strip()
    clientes = {}
    if raw:
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                clientes = data
        except Exception:
            pass
    return admin_hash, admin_password, clientes

ADMIN_HASH, ADMIN_PASSWORD, CLIENTES = carregar_config()

for key, default in {
    "autenticado": False,
    "perfil": None,
    "cliente_id": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

q = st.query_params
empresa_url = str(q.get("empresa", "")).strip()
acesso_url = str(q.get("acesso", "")).strip()

def cliente_do_link():
    if not empresa_url or not acesso_url:
        return None, None
    c = CLIENTES.get(empresa_url)
    if not isinstance(c, dict):
        return None, None
    token = str(c.get("acesso", "")).strip()
    if token and hmac.compare_digest(token, acesso_url):
        return empresa_url, c
    return None, None

cliente_id_url, cliente_url = cliente_do_link()

def cabecalho():
    st.markdown(
        f'<div class="hero"><h1>🧠 {APP_NAME}</h1>'
        f'<div class="small">Sistema de Governança e IA · versão {APP_VERSION}</div></div>',
        unsafe_allow_html=True,
    )

def sair():
    st.session_state.autenticado = False
    st.session_state.perfil = None
    st.session_state.cliente_id = None
    st.rerun()

def login_admin():
    cabecalho()
    st.subheader("Área administrativa")
    if not ADMIN_HASH and not ADMIN_PASSWORD:
        st.error("Administrador não configurado. Configure ADMIN_PASSWORD ou ADMIN_PASSWORD_HASH em Streamlit Secrets.")
        return
    with st.form("login_admin"):
        senha = st.text_input("Senha do administrador", type="password")
        entrar = st.form_submit_button("Entrar", use_container_width=True)
    if entrar:
        ok = verificar_senha(senha, ADMIN_HASH) if ADMIN_HASH else hmac.compare_digest(senha, ADMIN_PASSWORD)
        if ok:
            st.session_state.autenticado = True
            st.session_state.perfil = "admin"
            st.rerun()
        else:
            st.error("Senha incorreta.")

def painel_admin():
    cabecalho()
    a, b = st.columns([4, 1])
    with a:
        st.subheader("Painel do administrador")
    with b:
        if st.button("Sair"):
            sair()
    st.success("Administrador autenticado.")
    st.markdown("### Clientes cadastrados")
    if not CLIENTES:
        st.info("Nenhum cliente configurado ainda. Os clientes serão adicionados pelo Streamlit Secrets.")
    else:
        for cid, c in CLIENTES.items():
            if not isinstance(c, dict):
                continue
            nome = c.get("nome", cid)
            with st.container(border=True):
                st.markdown(f"**{nome}**")
                st.caption(f"Empresa: {cid}")
                token = str(c.get("acesso", "")).strip()
                if token:
                    st.code("?" + urlencode({"empresa": cid, "acesso": token}), language="text")
    st.divider()
    st.markdown("### Núcleo SVSC-CRISPE")
    st.write("O protocolo funciona internamente. O administrador não precisa preencher C/R/I/S/P/E manualmente.")
    st.markdown("**C** Contexto · **R** Papel · **I** Instrução · **S** Etapas · **P** Parâmetros · **E** Exemplos")
    st.caption("As credenciais e configurações não precisam ficar no código do GitHub.")

def login_cliente():
    cabecalho()
    st.subheader("Acesso do cliente")
    if not cliente_id_url or not cliente_url:
        st.info("Use o link de acesso fornecido pelo administrador.")
        return
    nome = cliente_url.get("nome", cliente_id_url)
    st.success(f"Cliente identificado: {nome}")
    with st.form("login_cliente"):
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar", use_container_width=True)
    if entrar:
        senha_hash = str(cliente_url.get("senha_hash", "")).strip()
        senha_salva = str(cliente_url.get("senha", "")).strip()
        ok = verificar_senha(senha, senha_hash) if senha_hash else (
            bool(senha_salva) and hmac.compare_digest(senha, senha_salva)
        )
        if ok:
            st.session_state.autenticado = True
            st.session_state.perfil = "cliente"
            st.session_state.cliente_id = cliente_id_url
            st.rerun()
        else:
            st.error("Senha incorreta.")

def painel_cliente():
    cid = st.session_state.cliente_id
    c = CLIENTES.get(cid, {})
    cabecalho()
    a, b = st.columns([4, 1])
    with a:
        st.subheader(f"Olá, {c.get('nome', cid)}")
    with b:
        if st.button("Sair"):
            sair()
    st.success("Acesso autorizado.")
    texto = st.text_area("Digite sua solicitação", height=160, placeholder="Escreva aqui o que deseja processar...")
    if st.button("Processar solicitação", type="primary", use_container_width=True):
        if texto.strip():
            st.info("Solicitação recebida pelo núcleo SVSC-CRISPE. A integração com o provedor de IA será ativada na próxima etapa.")
        else:
            st.warning("Digite uma solicitação antes de processar.")

if st.session_state.autenticado:
    if st.session_state.perfil == "admin":
        painel_admin()
    elif st.session_state.perfil == "cliente":
        painel_cliente()
else:
    if cliente_id_url and cliente_url:
        login_cliente()
    else:
        cabecalho()
        st.write("Sistema de governança, organização e processamento inteligente de solicitações.")
        st.divider()
        opcao = st.radio("Escolha o acesso", ["Cliente", "Administrador"], horizontal=True)
        if opcao == "Administrador":
            login_admin()
        else:
            login_cliente()
        st.divider()
        st.caption("SVSC-CRISPE · Sistema de Governança e IA")
