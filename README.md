# Agente Virtual — Clínica Saúde Integral

Assistente de IA para clínicas médicas com integração WhatsApp, Instagram e CRM.
Powered by **Claude Opus 4.6** (Anthropic).

---

## Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| Atendimento humanizado | Tom acolhedor, profissional, sem diagnósticos |
| Agendamento completo | Coleta nome, CPF, e-mail, procedimento e horário |
| Verificação de disponibilidade | Consulta slots em tempo real no CRM |
| Cadastro automático | Cria/atualiza paciente no CRM ao agendar |
| WhatsApp | Via Twilio Sandbox ou número aprovado |
| Instagram DM | Via Meta Graph API |
| REST direto | Endpoint `/chat` para testes e integrações |
| Multi-sessão | Cada usuário tem seu histórico independente |

---

## Arquitetura

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────────┐
│   WhatsApp      │────▶│              │     │                  │
│   (Twilio)      │     │  FastAPI     │────▶│  Claude Opus 4.6 │
├─────────────────┤     │  Webhook     │     │  (Anthropic API) │
│   Instagram DM  │────▶│  Server      │     │                  │
│   (Meta API)    │     │  server.py   │     └────────┬─────────┘
└─────────────────┘     └──────┬───────┘              │ tool_use
                               │                      ▼
                               │             ┌──────────────────┐
                               │             │   CRM Layer      │
                               └────────────▶│   crm.py         │
                                             │  (Mock → Real)   │
                                             └──────────────────┘
```

---

## Setup Rápido

### 1. Instalar dependências

```bash
cd "Claude Doctors"
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite .env com suas chaves
```

### 3. Rodar localmente

```bash
python main.py
# Servidor em http://localhost:8000
```

### 4. Testar via REST

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "teste123", "message": "Olá, quero agendar uma consulta"}'
```

---

## Integração WhatsApp (Twilio)

1. Crie conta em [twilio.com](https://twilio.com) e ative o **WhatsApp Sandbox**
2. Exponha o servidor com [ngrok](https://ngrok.com):
   ```bash
   ngrok http 8000
   ```
3. No painel Twilio, configure o Webhook URL:
   ```
   https://SEU_NGROK.ngrok.io/webhook/whatsapp
   ```
4. Envie mensagem para o número Twilio Sandbox pelo WhatsApp

---

## Integração Instagram (Meta Graph API)

1. Crie um App em [developers.facebook.com](https://developers.facebook.com)
2. Adicione o produto **Messenger** ao app
3. Configure o Webhook:
   - URL: `https://SEU_DOMINIO/webhook/instagram`
   - Verify Token: o valor de `META_VERIFY_TOKEN` no seu `.env`
   - Assine o campo: `messages`
4. Obtenha o **Page Access Token** e salve no `.env`
5. Conecte a Página do Instagram ao App

---

## Substituir o CRM Mock por CRM Real

Implemente a interface `BaseCRM` em `src/crm.py`:

```python
class HubSpotCRM(BaseCRM):
    def find_patient(self, cpf: str): ...
    def create_patient(self, nome, cpf, email, telefone, canal): ...
    def list_procedures(self): ...
    def check_availability(self, procedure, preferred_date): ...
    def create_appointment(self, patient_id, procedure, date, time, doctor, notes): ...

# Troque o singleton:
crm: BaseCRM = HubSpotCRM()
```

CRMs populares para clínicas: **Doctoralia**, **iClinic**, **Nuvem**, **Salesforce Health Cloud**, **HubSpot**.

---

## Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/webhook/whatsapp` | Twilio WhatsApp webhook |
| `GET` | `/webhook/instagram` | Verificação do webhook Meta |
| `POST` | `/webhook/instagram` | Instagram DM webhook |
| `POST` | `/chat` | Endpoint direto (testes) |
| `DELETE` | `/chat/{session_id}` | Limpa histórico da sessão |

Documentação interativa: `http://localhost:8000/docs`

---

## Estrutura do Projeto

```
Claude Doctors/
├── main.py                 # Ponto de entrada
├── requirements.txt
├── .env.example
├── data/
│   └── crm_data.json       # Dados do CRM mock (gerado automaticamente)
└── src/
    ├── __init__.py
    ├── agent.py            # Agente Claude + tools + gerenciamento de sessões
    ├── crm.py              # Interface CRM + implementação mock
    └── server.py           # Webhooks FastAPI (WhatsApp + Instagram)
```

---

## Segurança em Produção

- Use variáveis de ambiente — nunca comite chaves no código
- Valide a assinatura `X-Hub-Signature-256` do Meta (já implementado)
- Use HTTPS em produção (obrigatório para Meta webhooks)
- Implemente rate limiting por `session_id` para evitar abuso
- Armazene sessões no Redis em vez de memória para escalabilidade
- Adicione autenticação no endpoint `/chat` se exposto externamente
