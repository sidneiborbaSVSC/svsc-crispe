# guard.py

"""
SVSC Guard

Camada inicial de proteção das solicitações antes
do envio ao provedor de IA.
"""

import re


# Padrões básicos para identificar informações sensíveis.
PADROES_SENSIVEIS = {
    "email": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),
    "telefone": re.compile(
        r"(?<!\d)(?:\+?55\s?)?"
        r"(?:\(?\d{2}\)?\s?)?"
        r"\d{4,5}[-.\s]?\d{4}(?!\d)"
    ),
    "cpf": re.compile(
        r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"
    ),
}


def detectar_dados_sensiveis(texto: str) -> list:
    """Identifica tipos básicos de dados sensíveis."""

    encontrados = []

    if not texto:
        return encontrados

    for tipo, padrao in PADROES_SENSIVEIS.items():
        if padrao.search(texto):
            encontrados.append(tipo)

    return encontrados


def anonimizar_dados(texto: str) -> str:
    """
    Substitui dados sensíveis encontrados por marcadores.
    """

    if not texto:
        return texto

    texto_protegido = texto

    texto_protegido = PADROES_SENSIVEIS["email"].sub(
        "[EMAIL_PROTEGIDO]",
        texto_protegido,
    )

    texto_protegido = PADROES_SENSIVEIS["telefone"].sub(
        "[TELEFONE_PROTEGIDO]",
        texto_protegido,
    )

    texto_protegido = PADROES_SENSIVEIS["cpf"].sub(
        "[CPF_PROTEGIDO]",
        texto_protegido,
    )

    return texto_protegido


def verificar_tamanho(
    texto: str,
    limite: int = 20000,
) -> bool:
    """Verifica se a solicitação está dentro do limite."""

    if not texto:
        return False

    return len(texto) <= limite


def proteger_solicitacao(
    texto: str,
    anonimizar: bool = True,
    limite: int = 20000,
) -> dict:
    """
    Executa as verificações básicas do SVSC Guard.
    """

    if not texto or not texto.strip():
        return {
            "permitido": False,
            "texto": "",
            "dados_detectados": [],
            "motivo": "Solicitação vazia.",
        }

    if not verificar_tamanho(texto, limite):
        return {
            "permitido": False,
            "texto": "",
            "dados_detectados": [],
            "motivo": (
                f"Solicitação excede o limite "
                f"de {limite} caracteres."
            ),
        }

    dados_detectados = detectar_dados_sensiveis(texto)

    texto_final = texto

    if anonimizar:
        texto_final = anonimizar_dados(texto)

    return {
        "permitido": True,
        "texto": texto_final,
        "dados_detectados": dados_detectados,
        "motivo": None,
    }


def pode_enviar(texto: str) -> bool:
    """Atalho para verificar se a solicitação pode prosseguir."""

    resultado = proteger_solicitacao(texto)

    return resultado["permitido"]
