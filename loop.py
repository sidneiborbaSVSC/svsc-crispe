# loop.py

"""
SVSC-LOOP

Camada de execução iterativa do SVSC-CRISPE.

O Loop recebe:
- objetivo;
- critério de sucesso;
- limite de tentativas.

Ele gera uma resposta, avalia contra os critérios
e, quando necessário, solicita uma nova tentativa.

A integração com o provedor de IA é feita externamente.
"""

from typing import Callable, Dict, List, Optional


STATUS_APROVADO = "aprovado"
STATUS_REVISANDO = "revisando"
STATUS_LIMITE_ATINGIDO = "limite_atingido"


def validar_configuracao(
    objetivo: str,
    criterios: List[str],
    max_tentativas: int,
):
    if not objetivo or not objetivo.strip():
        raise ValueError("O objetivo não foi informado.")

    if not criterios:
        raise ValueError(
            "Pelo menos um critério de sucesso deve ser informado."
        )

    if max_tentativas < 1:
        raise ValueError(
            "O limite de tentativas deve ser maior que zero."
        )


def montar_prompt_inicial(
    objetivo: str,
    criterios: List[str],
    prompt_crispe: str,
) -> str:

    criterios_texto = "\n".join(
        f"- {criterio}"
        for criterio in criterios
    )

    return f"""
Você está operando dentro do SVSC-CRISPE em MODO LOOP.

OBJETIVO:
{objetivo}

CRITÉRIOS DE SUCESSO:
{criterios_texto}

INSTRUÇÃO CRISPE:
{prompt_crispe}

Produza uma resposta que atenda ao objetivo
e cumpra todos os critérios de sucesso.

Não explique o processo interno.
Entregue somente o resultado solicitado.
""".strip()


def montar_prompt_revisao(
    objetivo: str,
    criterios: List[str],
    resposta_anterior: str,
    falhas: List[str],
) -> str:

    criterios_texto = "\n".join(
        f"- {criterio}"
        for criterio in criterios
    )

    falhas_texto = "\n".join(
        f"- {falha}"
        for falha in falhas
    )

    return f"""
Você está operando dentro do SVSC-CRISPE em MODO LOOP.

OBJETIVO:
{objetivo}

CRITÉRIOS DE SUCESSO:
{criterios_texto}

RESPOSTA ANTERIOR:
{resposta_anterior}

PROBLEMAS IDENTIFICADOS:
{falhas_texto}

Gere uma nova versão da resposta.

Corrija os problemas identificados.
Preserve o que já estiver correto.
Atenda novamente a todos os critérios.

Entregue somente a nova resposta.
""".strip()


def montar_prompt_avaliacao(
    objetivo: str,
    criterios: List[str],
    resposta: str,
) -> str:

    criterios_texto = "\n".join(
        f"- {criterio}"
        for criterio in criterios
    )

    return f"""
Você é o avaliador do SVSC-LOOP.

OBJETIVO:
{objetivo}

CRITÉRIOS DE SUCESSO:
{criterios_texto}

RESPOSTA AVALIADA:
{resposta}

Avalie a resposta exclusivamente com base no objetivo
e nos critérios fornecidos.

Responda obrigatoriamente neste formato:

APROVADO: SIM ou NÃO

FALHAS:
- liste cada critério que não foi atendido

Se todos os critérios forem atendidos, escreva:

APROVADO: SIM

FALHAS:
- nenhuma
""".strip()


def interpretar_avaliacao(
    avaliacao: str,
) -> Dict:

    texto = (avaliacao or "").strip()

    aprovado = "APROVADO: SIM" in texto.upper()

    falhas = []

    if "FALHAS:" in texto.upper():
        parte = texto.upper().split(
            "FALHAS:",
            1,
        )[1]

        for linha in parte.splitlines():
            linha = linha.strip()

            if linha.startswith("-"):
                falha = linha[1:].strip()

                if falha and falha.lower() != "nenhuma":
                    falhas.append(falha)

    return {
        "aprovado": aprovado,
        "falhas": falhas,
        "avaliacao_bruta": texto,
    }


def executar_loop(
    objetivo: str,
    criterios: List[str],
    prompt_crispe: str,
    chamar_ia: Callable[[str], str],
    max_tentativas: int = 3,
) -> Dict:

    validar_configuracao(
        objetivo=objetivo,
        criterios=criterios,
        max_tentativas=max_tentativas,
    )

    historico = []

    prompt = montar_prompt_inicial(
        objetivo=objetivo,
        criterios=criterios,
        prompt_crispe=prompt_crispe,
    )

    melhor_resposta: Optional[str] = None

    for tentativa in range(
        1,
        max_tentativas + 1,
    ):

        resposta = chamar_ia(prompt)

        melhor_resposta = resposta

        prompt_avaliacao = montar_prompt_avaliacao(
            objetivo=objetivo,
            criterios=criterios,
            resposta=resposta,
        )

        avaliacao_bruta = chamar_ia(
            prompt_avaliacao
        )

        avaliacao = interpretar_avaliacao(
            avaliacao_bruta
        )

        historico.append(
            {
                "tentativa": tentativa,
                "resposta": resposta,
                "avaliacao": avaliacao,
            }
        )

        if avaliacao["aprovado"]:

            return {
                "status": STATUS_APROVADO,
                "aprovado": True,
                "tentativas": tentativa,
                "resposta": resposta,
                "historico": historico,
            }

        if tentativa < max_tentativas:

            prompt = montar_prompt_revisao(
                objetivo=objetivo,
                criterios=criterios,
                resposta_anterior=resposta,
                falhas=avaliacao["falhas"],
            )

    return {
        "status": STATUS_LIMITE_ATINGIDO,
        "aprovado": False,
        "tentativas": max_tentativas,
        "resposta": melhor_resposta or "",
        "historico": historico,
    }
