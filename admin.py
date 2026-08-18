import streamlit as st
from clients import (
    carregar_clientes,
    criar_cliente,
    atualizar_cliente,
    ativar_cliente,
    desativar_cliente,
    excluir_cliente,
    gerar_link_cliente,
)

def mostrar_painel_admin(base_url=""):
    st.title("Painel Administrativo")
    st.success("Administrador autenticado")
    
    clientes = carregar_clientes() or {}
    st.write(f"Total de clientes: **{len(clientes)}**")
    st.divider()
    
    st.subheader("Cadastrar novo cliente")
    with st.form("form_novo_cliente"):
        nome = st.text_input("Nome da empresa")
        responsavel = st.text_input("Responsavel")
        email = st.text_input("E-mail")
        salvar = st.form_submit_button("Cadastrar cliente", type="primary")
        
        if salvar:
            if not nome.strip():
                st.error("Informe o nome da empresa")
            else:
                cliente = criar_cliente(
                    nome_empresa=nome,
                    responsavel=responsavel,
                    email=email
                )
                st.success(f"Cliente '{cliente['nome_empresa']}' cadastrado!")
                link = gerar_link_cliente(cliente["id"], base_url)
                st.info(f"ID: `{cliente['id']}`")
                st.code(link, language="text")
                st.rerun()
    
    st.divider()
    st.subheader("Clientes cadastrados")
    
    if not clientes:
        st.info("Nenhum cliente cadastrado ainda")
        return
    
    for cliente_id, cliente in clientes.items():
        nome = cliente.get("nome_empresa", "Sem nome")
        ativo = cliente.get("ativo", True)
        status = "Ativo" if ativo else "Inativo"
        
        with st.expander(f"{nome} - {status}"):
            st.write(f"**ID:** `{cliente_id}`")
            st.write(f"**Responsavel:** {cliente.get('responsavel', '')}")
            st.write(f"**E-mail:** {cliente.get('email', '')}")
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Salvar alteracoes", key=f"salvar_{cliente_id}"):
                    st.success("Salvo!")
            
            with col2:
                if ativo:
                    if st.button("Desativar", key=f"des_{cliente_id}"):
                        desativar_cliente(cliente_id)
                        st.rerun()
                else:
                    if st.button("Ativar", key=f"ativ_{cliente_id}"):
                        ativar_cliente(cliente_id)
                        st.rerun()
            
            st.divider()
            link = gerar_link_cliente(cliente_id, base_url)
            st.write("**Link do cliente:**")
            st.code(link, language="text")
            
            st.divider()
            if st.button("Excluir cliente", key=f"exc_{cliente_id}"):
                excluir_cliente(cliente_id)
                st.rerun()
