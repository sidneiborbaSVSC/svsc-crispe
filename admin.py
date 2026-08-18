# admin.py

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
# admin.py

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


def mostrar_painel_admin(base_url):
    st.title("🛡️ SVSC-CRISPE")
    st.subheader("Painel Administrativo")

    clientes = carregar_clientes()

    st.write(f"Total de clientes: **{len(clientes)}**")

    st.divider()

    st.subheader("➕ Cadastrar novo cliente")

    with st.form("novo_cliente"):
        nome = st.text_input("Nome da empresa")
        responsavel = st.text_input("Responsável")
        email = st.text_input("E-mail")

        salvar = st.form_submit_button("Cadastrar cliente")

        if salvar:
            if not nome.strip():
                st.error("Informe o nome da empresa.")
            else:
                cliente = criar_cliente(
                    nome_empresa=nome,
                    responsavel=responsavel,
                    email=email,
                )

                st.success(
                    f"Cliente {cliente['nome_empresa']} cadastrado."
                )

                st.rerun()

    st.divider()

    st.subheader("👥 Clientes cadastrados")

    if not clientes:
        st.info("Nenhum cliente cadastrado ainda.")
        return

    for cliente_id, cliente in clientes.items():

        nome = cliente.get(
            "nome_empresa",
            "Sem nome",
        )

        status = cliente.get(
            "status",
            "novo",
        )

        ativo = cliente.get(
            "ativo",
            True,
        )

        with st.expander(
            f"{nome} — {status}"
        ):

            st.write(
                f"**ID:** {cliente_id}"
            )

            st.write(
                f"**Responsável:** "
                f"{cliente.get('responsavel', '')}"
            )

            st.write(
                f"**E-mail:** "
                f"{cliente.get('email', '')}"
            )

            st.write(
                f"**Status:** "
                f"{'🟢 Ativo' if ativo else '🔴 Inativo'}"
            )

            st.divider()

            novo_nome = st.text_input(
                "Nome da empresa",
                value=nome,
                key=f"nome_{cliente_id}",
            )

            novo_responsavel = st.text_input(
                "Responsável",
                value=cliente.get(
                    "responsavel",
                    "",
                ),
                key=f"resp_{cliente_id}",
            )

            novo_email = st.text_input(
                "E-mail",
                value=cliente.get(
                    "email",
                    "",
                ),
                key=f"email_{cliente_id}",
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 Salvar alterações",
                    key=f"salvar_{cliente_id}",
                ):
                    atualizar_cliente(
                        cliente_id,
                        nome_empresa=novo_nome,
                        responsavel=novo_responsavel,
                        email=novo_email,
                    )

                    st.success(
                        "Cliente atualizado."
                    )

                    st.rerun()

            with col2:
                if ativo:
                    if st.button(
                        "🔴 Desativar",
                        key=f"desativar_{cliente_id}",
                    ):
                        desativar_cliente(
                            cliente_id
                        )

                        st.success(
                            "Cliente desativado."
                        )

                        st.rerun()
                else:
                    if st.button(
                        "🟢 Ativar",
                        key=f"ativar_{cliente_id}",
                    ):
                        ativar_cliente(
                            cliente_id
                        )

                        st.success(
                            "Cliente ativado."
                        )

                        st.rerun()

            st.divider()

            link = gerar_link_cliente(
                cliente_id,
                base_url,
            )

            st.write("🔗 **Link do cliente**")

            st.code(
                link or "Link indisponível",
                language="text",
            )

            st.divider()

            if st.button(
                "🗑️ Excluir cliente",
                key=f"excluir_{cliente_id}",
            ):
                excluir_cliente(
                    cliente_id
                )

                st.success(
                    "Cliente excluído."
                )

                st.rerun()


def mostrar_painel_admin(base_url):
    st.title("🛡️ SVSC-CRISPE")
    st.subheader("Painel Administrativo")

    clientes = carregar_clientes()

    st.write(f"Total de clientes: **{len(clientes)}**")

    st.divider()

    st.subheader("➕ Cadastrar novo cliente")

    with st.form("novo_cliente"):
        nome = st.text_input("Nome da empresa")
        responsavel = st.text_input("Responsável")
        email = st.text_input("E-mail")

        salvar = st.form_submit_button("Cadastrar cliente")

        if salvar:
            if not nome.strip():
                st.error("Informe o nome da empresa.")
            else:
                cliente = criar_cliente(
                    nome_empresa=nome,
                    responsavel=responsavel,
                    email=email,
                )

                st.success(
                    f"Cliente {cliente['nome_empresa']} cadastrado."
                )

                st.rerun()

    st.divider()

    st.subheader("👥 Clientes cadastrados")

    if not clientes:
        st.info("Nenhum cliente cadastrado ainda.")
        return

    for cliente_id, cliente in clientes.items():

        nome = cliente.get(
            "nome_empresa",
            "Sem nome",
        )

        status = cliente.get(
            "status",
            "novo",
        )

        ativo = cliente.get(
            "ativo",
            True,
        )

        with st.expander(
            f"{nome} — {status}"
        ):

            st.write(
                f"**ID:** {cliente_id}"
            )

            st.write(
                f"**Responsável:** "
                f"{cliente.get('responsavel', '')}"
            )

            st.write(
                f"**E-mail:** "
                f"{cliente.get('email', '')}"
            )

            st.write(
                f"**Status:** "
                f"{'🟢 Ativo' if ativo else '🔴 Inativo'}"
            )

            st.divider()

            novo_nome = st.text_input(
                "Nome da empresa",
                value=nome,
                key=f"nome_{cliente_id}",
            )

            novo_responsavel = st.text_input(
                "Responsável",
                value=cliente.get(
                    "responsavel",
                    "",
                ),
                key=f"resp_{cliente_id}",
            )

            novo_email = st.text_input(
                "E-mail",
                value=cliente.get(
                    "email",
                    "",
                ),
                key=f"email_{cliente_id}",
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 Salvar alterações",
                    key=f"salvar_{cliente_id}",
                ):
                    atualizar_cliente(
                        cliente_id,
                        nome_empresa=novo_nome,
                        responsavel=novo_responsavel,
                        email=novo_email,
                    )

                    st.success(
                        "Cliente atualizado."
                    )

                    st.rerun()

            with col2:
                if ativo:
                    if st.button(
                        "🔴 Desativar",
                        key=f"desativar_{cliente_id}",
                    ):
                        desativar_cliente(
                            cliente_id
                        )

                        st.success(
                            "Cliente desativado."
                        )

                        st.rerun()
                else:
                    if st.button(
                        "🟢 Ativar",
                        key=f"ativar_{cliente_id}",
                    ):
                        ativar_cliente(
                            cliente_id
                        )

                        st.success(
                            "Cliente ativado."
                        )

                        st.rerun()

            st.divider()

            link = gerar_link_cliente(
                cliente_id,
                base_url,
            )

            st.write("🔗 **Link do cliente**")

            st.code(
                link or "Link indisponível",
                language="text",
            )

            st.divider()

            if st.button(
                "🗑️ Excluir cliente",
                key=f"excluir_{cliente_id}",
            ):
                excluir_cliente(
                    cliente_id
                )

                st.success(
                    "Cliente excluído."
                )

                st.rerun()
