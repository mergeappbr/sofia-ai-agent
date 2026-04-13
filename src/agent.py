"""
Agente Virtual — Clínica Saúde Integral
----------------------------------------
Powered by Claude Opus 4.6 with tool use.

Fluxo de coleta de dados (via conversa natural):
  1. Nome completo
  2. CPF
  3. E-mail
  4. Procedimento desejado
  5. Preferência de horário → busca disponibilidade → confirma agendamento

Tools disponíveis para o agente:
  - listar_procedimentos      : Lista os procedimentos disponíveis
  - verificar_disponibilidade : Consulta horários disponíveis
  - buscar_paciente           : Verifica se o paciente já existe no CRM
  - salvar_paciente           : Cria/atualiza cadastro do paciente no CRM
  - confirmar_agendamento     : Finaliza o agendamento e salva no CRM
"""

from __future__ import annotations

import json
import logging
from typing import Any

import anthropic

from .crm import crm

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cliente Anthropic
# ---------------------------------------------------------------------------

client = anthropic.Anthropic()
MODEL = "claude-opus-4-6"

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Você é a assistente virtual da Clínica Saúde Integral. Seu nome é Sofia.
Seu tom é acolhedor, profissional e paciente. Você atende pelo WhatsApp e Instagram.

## Seu objetivo
Tirar dúvidas sobre procedimentos e realizar agendamentos de consultas e exames.

## Regras absolutas
- NUNCA dê diagnósticos médicos, nem sugestões diagnósticas.
- Se o paciente relatar sintomas graves (dor no peito, falta de ar, desmaio), oriente-o a buscar pronto-socorro imediatamente.
- Não mencione preços sem antes o paciente perguntar.
- Seja concisa: mensagens curtas, amigáveis e objetivas (adequadas para WhatsApp/Instagram).
- Nunca peça informações que você já possui na conversa.

## Fluxo de agendamento
Para agendar, colete SEQUENCIALMENTE e de forma natural:
1. Nome completo
2. CPF (formato: 000.000.000-00)
3. E-mail
4. Procedimento desejado (use a tool listar_procedimentos se o paciente não souber)
5. Preferência de data/horário → use verificar_disponibilidade → apresente opções → confirme

Após coletar todos os dados, use as tools nesta ordem:
  buscar_paciente → salvar_paciente (se novo) → confirmar_agendamento

## Formato das respostas
- Use emojis com moderação (1-2 por mensagem) para manter tom amigável
- Quebre mensagens longas em parágrafos curtos
- Listas curtas quando apresentar opções
- Sempre termine com uma pergunta ou próxima ação clara"""

# ---------------------------------------------------------------------------
# Definições das tools
# ---------------------------------------------------------------------------

TOOLS: list[dict] = [
    {
        "name": "listar_procedimentos",
        "description": "Lista todos os procedimentos, consultas e exames disponíveis na clínica com nome, duração e preço.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "verificar_disponibilidade",
        "description": "Verifica horários disponíveis para um procedimento específico. Retorna uma lista de datas e horários.",
        "input_schema": {
            "type": "object",
            "properties": {
                "procedimento": {
                    "type": "string",
                    "description": "Nome exato do procedimento (ex: 'Consulta Cardiologia')",
                },
                "data_preferida": {
                    "type": "string",
                    "description": "Data preferida pelo paciente no formato YYYY-MM-DD (opcional)",
                },
            },
            "required": ["procedimento"],
        },
    },
    {
        "name": "buscar_paciente",
        "description": "Verifica se o paciente já existe no CRM pelo CPF.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cpf": {
                    "type": "string",
                    "description": "CPF do paciente (somente números ou formatado)",
                }
            },
            "required": ["cpf"],
        },
    },
    {
        "name": "salvar_paciente",
        "description": "Cadastra um novo paciente no CRM ou atualiza se já existir.",
        "input_schema": {
            "type": "object",
            "properties": {
                "nome": {"type": "string", "description": "Nome completo do paciente"},
                "cpf": {"type": "string", "description": "CPF do paciente"},
                "email": {"type": "string", "description": "E-mail do paciente"},
                "telefone": {"type": "string", "description": "Telefone/WhatsApp (opcional)"},
                "canal": {
                    "type": "string",
                    "enum": ["whatsapp", "instagram", "telefone", "site"],
                    "description": "Canal de atendimento de origem",
                },
            },
            "required": ["nome", "cpf", "email"],
        },
    },
    {
        "name": "confirmar_agendamento",
        "description": "Finaliza e salva o agendamento no CRM após confirmação do paciente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "patient_id": {"type": "string", "description": "ID do paciente no CRM"},
                "procedimento": {"type": "string", "description": "Nome do procedimento"},
                "data": {
                    "type": "string",
                    "description": "Data do agendamento (YYYY-MM-DD)",
                },
                "horario": {"type": "string", "description": "Horário (HH:MM)"},
                "medico": {"type": "string", "description": "Nome do médico/profissional"},
                "observacoes": {
                    "type": "string",
                    "description": "Observações adicionais (opcional)",
                },
            },
            "required": ["patient_id", "procedimento", "data", "horario", "medico"],
        },
    },
]

# ---------------------------------------------------------------------------
# Execução das tools
# ---------------------------------------------------------------------------

def execute_tool(name: str, inputs: dict[str, Any]) -> str:
    """Dispatch tool calls to the CRM layer and return a JSON string result."""
    try:
        if name == "listar_procedimentos":
            procedures = crm.list_procedures()
            return json.dumps({"procedimentos": procedures}, ensure_ascii=False)

        elif name == "verificar_disponibilidade":
            slots = crm.check_availability(
                procedure=inputs["procedimento"],
                preferred_date=inputs.get("data_preferida"),
            )
            return json.dumps({"slots_disponiveis": slots}, ensure_ascii=False)

        elif name == "buscar_paciente":
            patient = crm.find_patient(cpf=inputs["cpf"])
            if patient:
                return json.dumps(
                    {"encontrado": True, "paciente": patient}, ensure_ascii=False
                )
            return json.dumps({"encontrado": False}, ensure_ascii=False)

        elif name == "salvar_paciente":
            patient = crm.find_patient(cpf=inputs["cpf"])
            if not patient:
                patient = crm.create_patient(
                    nome=inputs["nome"],
                    cpf=inputs["cpf"],
                    email=inputs["email"],
                    telefone=inputs.get("telefone", ""),
                    canal=inputs.get("canal", "whatsapp"),
                )
                return json.dumps(
                    {"sucesso": True, "novo": True, "paciente": patient},
                    ensure_ascii=False,
                )
            return json.dumps(
                {"sucesso": True, "novo": False, "paciente": patient},
                ensure_ascii=False,
            )

        elif name == "confirmar_agendamento":
            appt = crm.create_appointment(
                patient_id=inputs["patient_id"],
                procedure=inputs["procedimento"],
                date=inputs["data"],
                time=inputs["horario"],
                doctor=inputs["medico"],
                notes=inputs.get("observacoes", ""),
            )
            return json.dumps({"sucesso": True, "agendamento": appt}, ensure_ascii=False)

        else:
            return json.dumps({"erro": f"Tool desconhecida: {name}"})

    except Exception as exc:
        logger.exception("Tool execution error: %s", name)
        return json.dumps({"erro": str(exc)})


# ---------------------------------------------------------------------------
# Session state — in-memory (use Redis/DB for production)
# ---------------------------------------------------------------------------

# sessions: { session_id: [ {"role": ..., "content": ...}, ... ] }
_sessions: dict[str, list[dict]] = {}


def get_session(session_id: str) -> list[dict]:
    return _sessions.setdefault(session_id, [])


def clear_session(session_id: str):
    _sessions.pop(session_id, None)


# ---------------------------------------------------------------------------
# Core agent function
# ---------------------------------------------------------------------------

def chat(session_id: str, user_message: str, canal: str = "whatsapp") -> str:
    """
    Process one user message turn and return the agent's response string.

    Args:
        session_id: Unique identifier for this conversation (e.g., WhatsApp phone number).
        user_message: The raw text sent by the user.
        canal: Channel of origin ('whatsapp', 'instagram', etc.).

    Returns:
        The agent's text reply.
    """
    messages = get_session(session_id)
    messages.append({"role": "user", "content": user_message})

    # Agentic loop: keep calling Claude until stop_reason != "tool_use"
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Append assistant turn to history
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Extract final text reply
            text = next(
                (b.text for b in response.content if hasattr(b, "text")), ""
            )
            return text

        if response.stop_reason == "tool_use":
            # Execute all requested tools and collect results
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    logger.info("Tool called: %s | inputs: %s", block.name, block.input)
                    result = execute_tool(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )

            # Feed results back as a user turn
            messages.append({"role": "user", "content": tool_results})
            continue  # loop → next Claude call

        # Unexpected stop reason — return whatever text is available
        text = next(
            (b.text for b in response.content if hasattr(b, "text")),
            "Desculpe, ocorreu um erro. Por favor, tente novamente."
        )
        return text
