# Relatório Semanal Comercial & Marketing — Oases
**Período: 16/10/2026 00:01 a 22/10/2026 23:59 (BRT), sexta a quinta (7 dias)** · Pipeline: *Pipeline Owner* (`157611836`) · Fonte: HubSpot CRM

> **Versão corrigida** após retorno do João (comercial) sobre o relatório de 16–23/10. Três erros de metodologia foram corrigidos e passam a valer como padrão dos próximos relatórios — ver nota ao final. Números deste relatório: negócios novos e mix de origem conferem com o HubSpot, verificados linha a linha.

---

## Resumo executivo

- **78 negócios novos** criados na semana (sexta 16/10 a quinta 22/10), contra **94** na semana anterior (09–15/10) → **-17,0% (-16 negócios)**. Essa é a janela de 7 dias correta — a versão anterior comparava 8 dias com 7 e mostrava -5,3%, número errado.
- **94,9% dos novos leads** vieram de Social Pago/Facebook, campanha `[easy] [fundo] [loc.exatas] [leads] [13/07/26]`. Isso está dentro do padrão normal desde agosto (entre 80% e 97%) — não é um recorde, como o relatório anterior disse.
- **Casa Lunna** segue na liderança (26 leads, 33,3%), seguida de **Casa Piraquara** (22, 28,2%) e **Casa Laguna** (10, 12,8%).
- **Reunião qualificada concluída na semana: 1 (Romildo Júnior, Casa Laguna)**, confirmada pelo registro de reuniões da equipe comercial. As "4 reuniões" do relatório anterior eram falso-positivo do método (entrada no estágio por correção de cadastro/lote, não reunião real) — ver seção 1 para o detalhe de cada caso.
- **8 de 78 negócios novos (10,3%) avançaram de fato no funil** (chegaram a Apresentação agendada ou Reunião realizada). O número anterior (25,8%) estava inflado por contar "Contato realizado" como avanço.
- **Leads parados de verdade (mais de 21 dias no mesmo estágio, medido hoje 26/10): 36 em "Tentando contato" e 43 em "Contato realizado" = 79 no total** — não 235, como o relatório anterior somou (que contava todo o estoque do estágio, incluindo quem está dentro da cadência normal de mensagens).
- **Recomendação principal:** o crescimento do estoque em "Tentando contato" (74→150→184 nas últimas semanas) é majoritariamente volume saudável dentro da cadência de 21 dias — a causa raiz real é que **as mensagens 2 a 7 da cadência da Marina não estão rodando**, então ninguém sai para "Nunca respondeu" quando deveria. Corrigir isso é mais importante do que "reforçar atendimento" de forma genérica.

---

## 1. Reuniões qualificadas (correção principal desta edição)

O relatório anterior contou como "reunião realizada" qualquer negócio que **entrou no estágio "Reunião realizada"** na janela (`hs_v2_date_entered_1257274268`). O João mostrou que isso pega atualizações de cadastro e edições em lote, não reuniões reais. A contagem correta usa o **registro de reuniões** da equipe, não a data de entrada no estágio.

### O que os 4 "falsos positivos" do relatório anterior realmente eram

| Lead | O que o relatório anterior disse | O que realmente aconteceu |
|---|---|---|
| Cassio Simão | Reunião em 21/10, depois "Sem interesse" — "vale investigar" | A reunião foi em **09/12/2025**. A entrada no estágio em 21/10 veio da **mesclagem de duplicados** feita nesse dia. Uma hora depois o negócio foi corretamente para "Sem interesse" por "Não respondeu às tentativas de contato". Não há nada para investigar. |
| Gabriel Gil | Reunião em 20/10/2026 | A reunião foi em **07/10**, na semana anterior. O estágio só foi *atualizado* em 20/10 às 16h18 por uma sessão do Claude, no mesmo minuto que Gabriel Padula e Samuel Rollemberg (edição em lote). |
| Gabriel Padula | "9 meses parado, virou reunião em 20/10, R$ 3.318.000" | Atualizado no mesmo lote acima. **Não há reunião registrada** para esse negócio. E não ficou 9 meses em "Contato realizado": foi para "Nunca respondeu"/"Sem interesse" em março, voltou para "Contato realizado" em 02/09 e ficou lá 7 semanas — não 9 meses. |
| Ana Eliza Zanchet | Virou reunião em 19/10 | O estágio foi trocado manualmente, 21 minutos após ela entrar em "Contato realizado" — **sem reunião registrada**. Precisa confirmar com quem mudou o estágio se foi reunião ou ligação. |

### Reunião qualificada concluída nesta janela (pelo registro real)

| Lead | Casa | Data da reunião | Fonte da confirmação |
|---|---|---|---|
| **Romildo Júnior** | Casa Laguna | 21/10/2026 | Registro de reuniões da equipe comercial |

Houve também uma reunião concluída com **João Querino**, mas é relativa ao **Castelo** (captação de imóvel para o portfólio), não venda de cota — fora do escopo deste relatório comercial.

### Apresentações agendadas na semana — desfecho real (não "nenhuma virou reunião")
| Lead | Situação real |
|---|---|
| Samuel Rollemberg | Não compareceu |
| Felipe Borges | Cancelou; remarcada e feita por telefone |
| Van Vilela | Remarcada para hoje (26/10) às 15h30 |
| (lead com acompanhante) | Reunião ocorreu com o casal; devem ir para "Sem interesse" — gostaram, mas não têm perfil/condições |
| Lucas Silva, Joyce Campodonio, Marcia Gomes Villela, Joana Darc, e outros 3 negócios | Data da reunião já passou, desfecho ainda não preenchido no CRM |

**Leitura:** o funil de apresentações agendadas está ativo, mas o CRM está desatualizado quanto ao desfecho real de boa parte delas — recomenda-se cobrar o preenchimento do resultado da reunião (compareceu / não compareceu / proposta / sem interesse) como rotina, já que é esse campo que o relatório deveria usar.

---

## 2. Negócios novos da semana (78)

Janela corrigida: sexta 16/10 00:01 a quinta 22/10 23:59 (BRT). Os 11 negócios criados na sexta 23/10 pertencem à semana seguinte (23–29/10), não a esta.

*Valor (amount): sem dado para a totalidade dos 78 negócios novos.*

Lista completa disponível no artifact interativo (busca por lead/casa/campanha).

---

## 3. Distribuição no funil (dos 78 negócios novos)

| Estágio | Qtde | % |
|---|---|---|
| Tentando contato | 38 | 48,7% |
| Contato realizado | 13 | 16,7% |
| Sem interesse | 9 | 11,5% |
| Entrar em contato urgente | 8 | 10,3% |
| Apresentação agendada | 7 | 9,0% |
| INTERESSE FUTURO | 1 | 1,3% |
| Reunião realizada | 1 | 1,3% |
| Nunca respondeu | 1 | 1,3% |
| **Total** | **78** | **100%** |

**O que avançou (definição corrigida — só Apresentação agendada ou Reunião realizada contam como avanço real no funil, "Contato realizado" é etapa de triagem, não avanço):** **8 de 78 (10,3%)**. Descartados (Sem interesse + Nunca respondeu): 10 (12,8%). O restante (60, 76,9%) está em triagem/primeiro contato.

---

## 4. Leads parados — critério corrigido: mais de 21 dias no mesmo estágio

Medido hoje (26/10/2026). "Parado" agora significa **mais de 21 dias no estágio atual**, não "qualquer negócio no estágio" — a cadência de mensagens roda por 21 dias, então estar no estágio por menos que isso é normal, não um problema.

| Estágio | Total no estágio hoje | Dentro da cadência (≤21 dias) | **Parado de verdade (>21 dias)** | Dos quais há mais de 60 dias |
|---|---|---|---|---|
| Tentando contato | 184 | 148 | **36** | 3 |
| Contato realizado | 86 | 43 | **43** | 34 |
| **Total parado real** | | | **79** | 37 |

**Por que "Tentando contato" saltou de 74 → 150 → 184 nas últimas semanas, e por que isso não é o alarme que os relatórios anteriores descreveram:**
1. **Volume de leads novos subiu** (89–94/semana agora, contra 37–45/semana antes) — mais entrada natural no estágio.
2. **Hoje (26/10) 34 negócios foram movidos em lote** de "Entrar em contato urgente" para "Tentando contato" — eles vão aparecer como "novos" em "Tentando contato" no próximo relatório, mas não são acúmulo, é reclassificação.
3. **As mensagens 2 a 7 da cadência da Marina não estão rodando** — por isso quase ninguém sai do estágio para "Nunca respondeu" quando a cadência deveria terminar. Esse é o problema real a corrigir, não o volume em si.

Dos 79 parados de verdade, os 37 com mais de 60 dias (34 deles em "Contato realizado") são os que merecem triagem manual prioritária — candidatos a reativação (como o caso real de Romildo) ou a desqualificação.

---

## 5. Origem do tráfego & campanha

### 5.1 Canal — 78 negócios novos
| Canal | Qtde | % |
|---|---|---|
| Social Pago (Meta/Facebook Ads) | 75 | 96,2% |
| Social orgânico (Instagram) | 2 | 2,6% |
| Offline (CRM manual) | 1 | 1,3% |

### 5.2 Campanha dominante
`[easy] [fundo] [loc.exatas] [leads] [13/07/26]`: **74 de 78 (94,9%)**. Dentro da faixa normal desde agosto/2026 (80%–97% das semanas) — **não é um recorde**, correção do relatório anterior, que havia comparado com uma base histórica incompleta. O pico já registrado foi 94,7% (semana de 07–13/08).

### 5.3 Comparação com a semana anterior (corrigida)
- **Negócios novos:** 94 (09–15/10) → **78** (16–22/10) = **-17,0%**.
- **Mix de origem:** estável, dentro do padrão de concentração em Social Pago/Facebook das últimas 11 semanas.

---

## Alertas & próximos passos

1. **Corrigir a cadência da Marina (mensagens 2–7):** é a causa raiz do acúmulo visual em "Tentando contato" — sem isso, leads sem resposta nunca saem do estágio.
2. **Cobrar o preenchimento do desfecho das reuniões no CRM:** várias apresentações já ocorreram (Lucas, Joyce, Marcia, Joana e outras) sem resultado registrado — isso é o que torna o relatório de reuniões não confiável sem checagem manual.
3. **Triagem dos 37 negócios parados há mais de 60 dias** (34 em "Contato realizado"): candidatos a reativação (replicar o padrão do caso real de Romildo) ou desqualificação.
4. **Dedupe:** a mesclagem de duplicados (caso Cassio Simão) é rotina saudável, mas horários de edição em lote (caso Gabriel Gil/Padula/Rollemberg) merecem registrar a mudança como "atualização de cadastro", não deixar o `hs_v2_date_entered` do estágio sugerir uma reunião que não houve.
5. **Padrão de relatório atualizado** (ver nota abaixo): janela sexta–quinta (7 dias), reunião pelo registro real, parado = >21 dias.

---

## Nota: ajustes de metodologia aplicados a partir deste relatório

A pedido do João (comercial), três regras passam a valer em todos os próximos relatórios semanais:

1. **Janela de 7 dias, sexta a quinta** (não sexta a sexta, que gera 8 dias e contagem dupla do dia de corte).
2. **Reunião qualificada = registro de reunião concluída**, não a data de entrada no estágio "Reunião realizada" (que pega correções de cadastro e edições em lote).
3. **"Parado" = mais de 21 dias no mesmo estágio** — não "qualquer negócio no estágio", já que a cadência normal de mensagens dura 21 dias.

Assim como da última vez, não consigo editar a rotina agendada diretamente (foi criada fora desta sessão) — o texto atualizado do prompt, com essas três regras, será entregue separadamente para colar na rotina.

---
*Relatório gerado a partir do HubSpot CRM (portal 47638395), corrigido com apoio da equipe comercial. Conforme LGPD, não foram expostos CPF, RG, dados bancários, contratos ou identidade de proprietários/sócios. Não invento dados: campos ausentes aparecem como "sem dado".*
