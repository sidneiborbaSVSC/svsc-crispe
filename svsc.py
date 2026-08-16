# svsc.py

"""
Núcleo do SVSC-CRISPE.

O cliente escreve normalmente.
Este módulo organiza a solicitação antes de enviá-la
ao provedor de IA.
"""


def montar_contexto(
    solicitacao: str,
    contexto: str = "",
    objetivo: str = "",
    perfil: str = "",
):
    """Organiza os dados básicos da solicitação."""

    return {
        "contexto": contexto.strip(),
        "solicitacao": solicitacao.strip(),
        "objetivo": objetivo.strip(),
        "perfil": perfil.strip(),
    }


def aplicar_crispe(dados: dict) -> dict:
    """
    Estrutura internamente a solicitação no formato CRISPE.

    O cliente não precisa preencher os campos.
    """

    solicitacao = dados.get("solicitacao", "").strip()

    if not solicitacao:
        raise ValueError("A solicitação não foi informada.")

    return {
        "contexto": dados.get("contexto", ""),
        "papel": (
            "Atue como um assistente profissional, "
            "analítico e orientado a resultados."
        ),
        "instrução": solicitacao,
        "etapas": [
            "Compreender a solicitação.",
            "Identificar informações relevantes.",
            "Organizar a resposta.",
            "Apresentar uma solução prática.",
        ],
        "perfil": dados.get("perfil", ""),
        "objetivo": dados.get("objetivo", ""),
    }


def gerar_prompt_crispe(estrutura: dict) -> str:
    """Transforma a estrutura CRISPE em um prompt interno."""

    partes = [
        "Você está operando dentro do SVSC-CRISPE.",
        "",
        "CONTEXTO:",
        estrutura.get("contexto", ""),
        "",
        "PAPEL:",
        estrutura.get("papel", ""),
        "",
        "INSTRUÇÃO:",
        estrutura.get("instrução", ""),
        "",
        "OBJETIVO:",
        estrutura.get("objetivo", ""),
        "",
        "PERFIL:",
        estrutura.get("perfil", ""),
        "",
        "ETAPAS:",
    ]

    for etapa in estrutura.get("etapas", []):
        partes.append(f"- {etapa}")

    partes.extend(
        [
            "",
            "Produza uma resposta clara, objetiva, "
            "profissional e adequada ao contexto informado.",
        ]
    )

    return "\n".join(partes)


def processar_solicitacao(
    solicitacao: str,
    contexto: str = "",
    objetivo: str = "",
    perfil: str = "",
) -> dict:
    """Executa o processamento interno do SVSC-CRISPE."""

    dados = montar_contexto(
        solicitacao=solicitacao,
        contexto=contexto,
        objetivo=objetivo,
        perfil=perfil,
    )

    estrutura = aplicar_crispe(dados)

    prompt = gerar_prompt_crispe(estrutura)

    return {
        "dados": dados,
        "estrutura": estrutura,
        "prompt": prompt,
    }
