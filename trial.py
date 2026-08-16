# trial.py

from datetime import datetime, timedelta


DIAS_TESTE = 7


def iniciar_teste(cliente):
    """
    Inicia o período de teste do cliente.
    Só inicia se ainda não houver data de início.
    """

    if cliente.get("inicio_teste"):
        return cliente

    agora = datetime.now()

    cliente["inicio_teste"] = agora.isoformat()
    cliente["fim_teste"] = (
        agora + timedelta(days=DIAS_TESTE)
    ).isoformat()

    cliente["status"] = "teste"

    return cliente


def obter_datas_teste(cliente):
    """Retorna as datas de início e fim do teste."""

    inicio = cliente.get("inicio_teste")
    fim = cliente.get("fim_teste")

    if not inicio or not fim:
        return None, None

    try:
        inicio = datetime.fromisoformat(inicio)
        fim = datetime.fromisoformat(fim)

        return inicio, fim

    except ValueError:
        return None, None


def teste_expirou(cliente):
    """Verifica se os 7 dias já terminaram."""

    if cliente.get("status") == "ativo":
        return False

    _, fim = obter_datas_teste(cliente)

    if not fim:
        return False

    return datetime.now() >= fim


def dias_restantes(cliente):
    """Calcula quantos dias faltam para terminar o teste."""

    _, fim = obter_datas_teste(cliente)

    if not fim:
        return None

    restante = fim - datetime.now()

    if restante.total_seconds() <= 0:
        return 0

    return restante.days + 1


def atualizar_status_teste(cliente):
    """
    Atualiza automaticamente o status do cliente.
    """

    if cliente.get("status") == "ativo":
        return cliente

    if teste_expirou(cliente):
        cliente["status"] = "expirado"
        return cliente

    cliente["status"] = "teste"

    return cliente


def pode_usar_sistema(cliente):
    """
    Verifica se o cliente pode utilizar o sistema.
    """

    if not cliente.get("ativo", True):
        return False

    if cliente.get("status") == "ativo":
        return True

    if teste_expirou(cliente):
        return False

    return True


def mensagem_teste(cliente):
    """Gera a mensagem exibida ao cliente durante o teste."""

    if cliente.get("status") == "ativo":
        return "Licença ativa."

    restantes = dias_restantes(cliente)

    if restantes is None:
        return "Período de avaliação ainda não iniciado."

    if restantes <= 0:
        return "Seu período de avaliação terminou."

    if restantes == 1:
        return "⚠️ Seu período de avaliação termina hoje."

    if restantes <= 2:
        return (
            f"⚠️ Seu período de avaliação "
            f"termina em {restantes} dias."
        )

    return (
        f"🟢 Você está no período de avaliação. "
        f"Restam {restantes} dias."
    )
