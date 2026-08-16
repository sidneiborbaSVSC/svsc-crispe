import requests


PROVIDERS = {
    "openai": {
        "nome": "OpenAI",
        "modelos": [
            "gpt-4o-mini",
        ],
    },
    "gemini": {
        "nome": "Google Gemini",
        "modelos": [
            "gemini-2.0-flash",
        ],
    },
    "anthropic": {
        "nome": "Anthropic Claude",
        "modelos": [
            "claude-3-5-haiku-latest",
        ],
    },
    "mistral": {
        "nome": "Mistral",
        "modelos": [
            "mistral-small-latest",
        ],
    },
    "groq": {
        "nome": "Groq",
        "modelos": [
            "llama-3.3-70b-versatile",
        ],
    },
    "deepseek": {
        "nome": "DeepSeek",
        "modelos": [
            "deepseek-chat",
        ],
    },
}


def listar_provedores():
    return PROVIDERS


def nomes_provedores():
    return {
        chave: dados["nome"]
        for chave, dados in PROVIDERS.items()
    }


def modelos_do_provedor(provedor):
    dados = PROVIDERS.get(provedor)

    if not dados:
        return []

    return dados["modelos"]


def provedor_existe(provedor):
    return provedor in PROVIDERS


def chamar_provedor(
    provedor,
    api_key,
    modelo,
    prompt,
):
    if not api_key:
        raise ValueError(
            "API não configurada."
        )

    if provedor == "openai":
        return _openai(
            api_key,
            modelo,
            prompt,
        )

    if provedor == "anthropic":
        return _anthropic(
            api_key,
            modelo,
            prompt,
        )

    if provedor == "gemini":
        return _gemini(
            api_key,
            modelo,
            prompt,
        )

    if provedor in {
        "mistral",
        "groq",
        "deepseek",
    }:
        return _openai_compatível(
            provedor,
            api_key,
            modelo,
            prompt,
        )

    raise ValueError(
        "Provedor não suportado."
    )


def _openai(
    api_key,
    modelo,
    prompt,
):
    resposta = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": modelo,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        },
        timeout=60,
    )

    resposta.raise_for_status()

    dados = resposta.json()

    return dados["choices"][0]["message"]["content"]


def _openai_compatível(
    provedor,
    api_key,
    modelo,
    prompt,
):
    endpoints = {
        "groq": (
            "https://api.groq.com/openai/v1/"
            "chat/completions"
        ),
        "deepseek": (
            "https://api.deepseek.com/v1/"
            "chat/completions"
        ),
        "mistral": (
            "https://api.mistral.ai/v1/"
            "chat/completions"
        ),
    }

    endpoint = endpoints[provedor]

    resposta = requests.post(
        endpoint,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": modelo,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        },
        timeout=60,
    )

    resposta.raise_for_status()

    dados = resposta.json()

    return dados["choices"][0]["message"]["content"]


def _anthropic(
    api_key,
    modelo,
    prompt,
):
    resposta = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json={
            "model": modelo,
            "max_tokens": 2048,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        },
        timeout=60,
    )

    resposta.raise_for_status()

    dados = resposta.json()

    return dados["content"][0]["text"]


def _gemini(
    api_key,
    modelo,
    prompt,
):
    endpoint = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{modelo}:generateContent"
    )

    resposta = requests.post(
        endpoint,
        params={
            "key": api_key,
        },
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt,
                        }
                    ]
                }
            ]
        },
        timeout=60,
    )

    resposta.raise_for_status()

    dados = resposta.json()

    return (
        dados["candidates"][0]
        ["content"]["parts"][0]["text"]
    )
