"""
Desafio Técnico - Envio de mensagens via WhatsApp (Z-API)
Lê contatos do Supabase e envia mensagem personalizada para até 3 contatos.
"""

import logging
import os
import sys

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuração de logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
MAX_CONTATOS = 3


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def carregar_variaveis_ambiente() -> dict:
    """Carrega e valida as variáveis de ambiente necessárias."""
    load_dotenv()

    variaveis = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
        "ZAPI_INSTANCE_ID": os.getenv("ZAPI_INSTANCE_ID"),
        "ZAPI_TOKEN": os.getenv("ZAPI_TOKEN"),
        "ZAPI_CLIENT_TOKEN": os.getenv("ZAPI_CLIENT_TOKEN"),
    }

    faltando = [chave for chave, valor in variaveis.items() if not valor]
    if faltando:
        logger.error("Variáveis de ambiente ausentes: %s", ", ".join(faltando))
        sys.exit(1)

    logger.info("Variáveis de ambiente carregadas com sucesso.")
    return variaveis


def buscar_contatos(url: str, key: str, limite: int = MAX_CONTATOS) -> list[dict]:
    """Busca até `limite` contatos na tabela 'contatos' via REST API do Supabase."""
    try:
        endpoint = f"{url}/rest/v1/contatos?select=nome,telefone&limit={limite}"
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
        }

        resposta = requests.get(endpoint, headers=headers, timeout=30)
        resposta.raise_for_status()
        contatos = resposta.json()

        if not contatos:
            logger.warning("Nenhum contato encontrado no banco de dados.")
            return []

        logger.info("Contatos encontrados: %d", len(contatos))
        return contatos
    except requests.exceptions.HTTPError as erro:
        logger.error("Erro HTTP ao buscar contatos: %s - %s", erro, resposta.text)
    except requests.exceptions.RequestException as erro:
        logger.error("Erro ao buscar contatos no Supabase: %s", erro)
    return []


def montar_mensagem(nome: str) -> str:
    """Retorna a mensagem personalizada para o contato."""
    return f"Olá, {nome} tudo bem com você?"


def enviar_mensagem_whatsapp(
    telefone: str,
    mensagem: str,
    instance_id: str,
    token: str,
    client_token: str,
) -> bool:
    """Envia uma mensagem de texto via Z-API. Retorna True se bem-sucedido."""
    url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/send-text"

    headers = {
        "Content-Type": "application/json",
        "Client-Token": client_token,
    }

    payload = {
        "phone": telefone,
        "message": mensagem,
    }

    try:
        resposta = requests.post(url, json=payload, headers=headers, timeout=30)
        resposta.raise_for_status()
        logger.info("Mensagem enviada com sucesso para %s.", telefone)
        return True
    except requests.exceptions.HTTPError as erro:
        logger.error("Erro HTTP ao enviar para %s: %s", telefone, erro)
    except requests.exceptions.ConnectionError as erro:
        logger.error("Erro de conexão ao enviar para %s: %s", telefone, erro)
    except requests.exceptions.Timeout as erro:
        logger.error("Timeout ao enviar para %s: %s", telefone, erro)
    except requests.exceptions.RequestException as erro:
        logger.error("Erro inesperado ao enviar para %s: %s", telefone, erro)

    return False


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------

def main() -> None:
    """Orquestra o fluxo: carrega config, busca contatos e envia mensagens."""
    logger.info("Início do processo de envio de mensagens.")

    # 1. Carregar variáveis de ambiente
    env = carregar_variaveis_ambiente()

    # 2. Buscar contatos (máximo 3)
    contatos = buscar_contatos(env["SUPABASE_URL"], env["SUPABASE_KEY"])
    if not contatos:
        logger.info("Processo encerrado — nenhum contato para enviar.")
        return

    # 3. Enviar mensagens
    enviados = 0
    for contato in contatos:
        nome = contato["nome"]
        telefone = contato["telefone"]
        mensagem = montar_mensagem(nome)

        sucesso = enviar_mensagem_whatsapp(
            telefone=telefone,
            mensagem=mensagem,
            instance_id=env["ZAPI_INSTANCE_ID"],
            token=env["ZAPI_TOKEN"],
            client_token=env["ZAPI_CLIENT_TOKEN"],
        )

        if sucesso:
            enviados += 1

    logger.info("Processo finalizado. Mensagens enviadas: %d/%d.", enviados, len(contatos))


if __name__ == "__main__":
    main()
