"""
Sofia — concierge virtual da Oases Luxury Homes
------------------------------------------------
Co-ownership (propriedade fracionada) de casas de alto padrão em destinos
brasileiros. Atende Instagram (comentários + direct) e WhatsApp.

Precisão em primeiro lugar: sempre que o lead perguntar sobre suítes, capacidade,
destinos, preço da fração ou uma casa específica, o agente consulta os DADOS REAIS
ao vivo (tool consultar_casas → /api/comercial do dashboard) — nunca inventa números.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import anthropic
import httpx

logger = logging.getLogger(__name__)

client = anthropic.Anthropic()
MODEL = "claude-opus-4-6"

# API do dashboard de gestão (fonte da verdade das casas: suítes, capacidade, preço)
DASHBOARD_API = os.getenv(
    "OASES_DASHBOARD_API",
    "https://web-production-49eedb.up.railway.app/analytics",
).rstrip("/")

# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

_BASE = """Você é a Sofia, concierge virtual da Oases Luxury Homes.

## O que é a Oases
Vendemos FRAÇÕES (cotas de 1/8) de casas de luxo mobiliadas e geridas, em destinos
brasileiros (Trancoso, Praia do Forte, Angra dos Reis, Escarpas do Lago, Península de
Maraú, Copacabana, Mangaratiba). O coproprietário usa a casa por temporadas e conta com
gestão profissional completa (limpeza, manutenção, reservas). Cada casa tem configuração
própria de suítes e capacidade de hóspedes.

## PRECISÃO — regra mais importante
- Sempre que perguntarem sobre suítes, capacidade/hóspedes, destinos, preço da fração
  (share ⅛), disponibilidade ou uma casa específica, use a tool `consultar_casas` e
  responda com os NÚMEROS REAIS. NUNCA responda genérico ("varia conforme o projeto")
  sem antes trazer o dado.
- Se não souber a qual casa a pessoa se refere, traga a FAIXA real (ex.: "de 4 a 8 suítes,
  até 24 hóspedes, conforme a casa") e pergunte o destino/casa de interesse.
- Nunca invente valores. Se a tool falhar, seja honesta e diga que confirma e retorna.

## Estilo
- Calorosa, sofisticada e CONCISA (Instagram/WhatsApp). No máximo 1–2 emojis.
- Termine sempre com UMA pergunta ou próximo passo claro.
- Não peça dados que a pessoa já forneceu."""

# Direct/WhatsApp: conversa contínua e precisa, qualificando o lead
SYSTEM_PROMPT = _BASE + """

## Objetivo no direct/WhatsApp
Responder com precisão e conduzir a uma conversa qualificada. Ao longo da conversa,
capte de forma natural: nome, destino/casa de interesse e melhor forma de contato.
Se a pessoa veio de um comentário, RETOME exatamente o que ela perguntou (ex.: a
capacidade de hóspedes) e responda de imediato com os números reais — sem repetir
saudações genéricas."""

# Resposta PÚBLICA ao comentário: curta, precisa, convida ao direct
PUBLIC_COMMENT_PROMPT = _BASE + """

## Objetivo na resposta PÚBLICA ao comentário
Escreva UMA resposta curta (1–2 frases), calorosa e PRECISA ao comentário, e convide a
pessoa a seguir no direct. Se a pergunta for sobre suítes/capacidade/preço/destino, dê o
dado real de forma resumida (ex.: a faixa) já na resposta pública — não empurre para o
direct sem nenhuma informação. Não use saudação longa. Não repita o texto do comentário."""

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

TOOLS: list[dict] = [
    {
        "name": "consultar_casas",
        "description": (
            "Consulta a lista ATUAL das casas Oases com destino, número de suítes, "
            "capacidade de hóspedes, preço da fração (share ⅛) e disponibilidade, além "
            "dos totais do portfólio. Use SEMPRE que o lead perguntar sobre capacidade, "
            "suítes, hóspedes, destinos, preços ou uma casa específica — nunca invente."
        ),
        "input_schema": {"type": "object", "properties": {}},
    }
]

_casas_cache: dict = {"ts": 0, "data": None}


def _fetch_casas() -> dict:
    """Dados reais das casas, do dashboard de gestão (cache leve de 5 min)."""
    import time

    if _casas_cache["data"] and time.time() - _casas_cache["ts"] < 300:
        return _casas_cache["data"]
    try:
        r = httpx.get(f"{DASHBOARD_API}/api/comercial", timeout=15)
        r.raise_for_status()
        d = r.json()
        k = d.get("kpis", {})
        out = {
            "portfolio": {
                "casas": k.get("casas"),
                "suites_total": k.get("capacidade_suites"),
                "hospedes_total": k.get("capacidade_hospedes"),
                "destinos": k.get("regioes"),
            },
            "casas": [
                {
                    "nome": c.get("nome"),
                    "destino": f"{c.get('regiao')}/{c.get('uf')}",
                    "suites": c.get("suites"),
                    "hospedes": c.get("hospedes"),
                    "preco_fracao_1_8": c.get("share8"),
                    "shares_disponiveis": c.get("disp"),
                    "status": c.get("status"),
                }
                for c in d.get("casas", [])
            ],
        }
        _casas_cache["ts"], _casas_cache["data"] = time.time(), out
        return out
    except Exception as exc:  # noqa: BLE001
        logger.warning("consultar_casas falhou: %s", exc)
        return {"erro": "não consegui consultar as casas agora"}


def execute_tool(name: str, inputs: dict[str, Any]) -> str:
    if name == "consultar_casas":
        return json.dumps(_fetch_casas(), ensure_ascii=False)
    return json.dumps({"erro": f"Tool desconhecida: {name}"}, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Session state — em memória (usar Redis/DB em produção)
# ---------------------------------------------------------------------------

_sessions: dict[str, list[dict]] = {}


def get_session(session_id: str) -> list[dict]:
    return _sessions.setdefault(session_id, [])


def clear_session(session_id: str):
    _sessions.pop(session_id, None)


# ---------------------------------------------------------------------------
# Loop agêntico (com tools)
# ---------------------------------------------------------------------------

def _run(messages: list[dict], system: str) -> str:
    """Roda o loop até stop_reason != tool_use e devolve o texto final.
    `messages` é mutado in-place (mantém histórico da sessão quando aplicável)."""
    for _ in range(6):  # trava de segurança contra loop infinito de tools
        response = client.messages.create(
            model=MODEL, max_tokens=1024, system=system, tools=TOOLS, messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if getattr(block, "type", None) == "tool_use":
                    logger.info("Tool: %s | %s", block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": execute_tool(block.name, block.input),
                    })
            messages.append({"role": "user", "content": tool_results})
            continue

        text = next((b.text for b in response.content if hasattr(b, "text")), "")
        return text.strip()
    return "Já te respondo com os detalhes! 😊"


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def chat(session_id: str, user_message: str, canal: str = "whatsapp", user_name: str = "") -> str:
    """Turno de conversa com estado (direct/WhatsApp)."""
    messages = get_session(session_id)
    if user_name and not messages:
        user_message = f"[Nome do contato: {user_name}]\n{user_message}"
    messages.append({"role": "user", "content": user_message})
    return _run(messages, SYSTEM_PROMPT)


def comment_public_reply(comment_text: str) -> str:
    """Resposta pública (stateless) a um comentário — curta, precisa, convida ao direct."""
    return _run([{"role": "user", "content": comment_text}], PUBLIC_COMMENT_PROMPT)
