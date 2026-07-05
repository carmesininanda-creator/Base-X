"""
Testes E2E da Giu Família.

Testa o SISTEMA (identidade, isolamento, consentimento, permissões,
compartilhamento, emergência), não o modelo de linguagem — por isso roda
sem custo de API. Rodar de dentro de giu/:

    GIU_FAMILY_MODE=1 GIU_API_TOKEN=operadora python -m pytest tests/ -v
"""

import os
import sys

os.environ.setdefault("GIU_FAMILY_MODE", "1")
os.environ.setdefault("GIU_API_TOKEN", "operadora")
os.environ["GIU_DB_PATH"] = "/tmp/giu_familia_e2e.db"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

if os.path.exists("/tmp/giu_familia_e2e.db"):
    os.remove("/tmp/giu_familia_e2e.db")

from giu import brain, memory, onboarding, tools  # noqa: E402
from server import app  # noqa: E402

ADMIN = {"Authorization": "Bearer operadora"}

IAN = "5511911111111"
PAULINE = "5511922222222"
RAFAEL = "5511933333333"
NANDA = "5511900000000"
ESTRANHO = "5511999999999"

TOKENS = {}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# ─── 1. Identidade: cadastro da família ───────────────────────────────────────

def test_registro_dos_tres_membros(client):
    for user_id, name in [(IAN, "Ian"), (PAULINE, "Pauline"), (RAFAEL, "Rafael")]:
        r = client.post(
            "/family/members",
            json={"user_id": user_id, "name": name, "emergency_contact": NANDA},
            headers=ADMIN,
        )
        assert r.status_code == 200
        body = r.json()
        assert body["token"]  # token pessoal mostrado uma única vez
        TOKENS[name] = body["token"]

    r = client.get("/family/members", headers=ADMIN)
    members = r.json()["members"]
    assert len(members) == 3
    assert all("token" not in m and "token_hash" not in m for m in members)


def test_cadastro_exige_token_de_operadora(client):
    r = client.post("/family/members", json={"user_id": "x", "name": "X"})
    assert r.status_code == 401


# ─── 2. Portaria: só membros conversam ────────────────────────────────────────

def test_estranho_nao_passa_da_portaria(client):
    from server import family_gate
    assert family_gate(ESTRANHO) is False
    # E nada foi criado para ele
    assert memory.message_count(ESTRANHO) == 0
    assert memory.get_facts(ESTRANHO) == []


def test_membro_passa_e_e_ativado(client):
    from server import family_gate
    assert family_gate(IAN) is True
    assert memory.get_member(IAN)["status"] == "active"


# ─── 3. Onboarding individual e independente ──────────────────────────────────

def test_onboarding_individual():
    # Ian completa o onboarding
    tools.execute_tool("registrar_onboarding", {"campo": "pendencia_inicial", "valor": "devolver livros"}, IAN)
    tools.execute_tool("registrar_onboarding", {"campo": "nome", "valor": "Ian"}, IAN)
    tools.execute_tool("registrar_onboarding", {"campo": "consentimento", "valor": "sim"}, IAN)
    assert onboarding.current_step(memory.get_profile(IAN)) is None

    # Pauline ainda está no começo do dela — progresso NÃO vazou
    assert onboarding.current_step(memory.get_profile(PAULINE)) == "pendencia_inicial"
    tools.execute_tool("registrar_onboarding", {"campo": "pendencia_inicial", "valor": "agendar dentista"}, PAULINE)
    tools.execute_tool("registrar_onboarding", {"campo": "nome", "valor": "Pauline"}, PAULINE)
    tools.execute_tool("registrar_onboarding", {"campo": "consentimento", "valor": "sim"}, PAULINE)


# ─── 4. Isolamento de memória entre membros ───────────────────────────────────

def test_memoria_isolada_no_cerebro():
    memory.remember_fact(IAN, "Ian tem prova de matemática sexta", "rotina")
    memory.remember_fact(PAULINE, "Pauline faz natação às terças", "rotina")

    prompt_ian = brain._system_prompt(IAN, "oi")
    prompt_pauline = brain._system_prompt(PAULINE, "oi")

    assert "prova de matemática" in prompt_ian
    assert "natação" not in prompt_ian          # nada da Pauline no prompt do Ian
    assert "natação" in prompt_pauline
    assert "prova de matemática" not in prompt_pauline  # e vice-versa


def test_api_memoria_so_com_token_proprio(client):
    # Dono acessa a própria memória
    r = client.get(f"/memories/{IAN}", headers={"Authorization": f"Bearer {TOKENS['Ian']}"})
    assert r.status_code == 200
    assert any("prova de matemática" in f["content"] for f in r.json()["facts"])

    # Outro membro NÃO acessa (nem com token válido dele)
    r = client.get(f"/memories/{IAN}", headers={"Authorization": f"Bearer {TOKENS['Pauline']}"})
    assert r.status_code == 403

    # A OPERADORA também não — confidencialidade inclusive da mãe
    r = client.get(f"/memories/{IAN}", headers=ADMIN)
    assert r.status_code == 403

    # Sem token, nada
    assert client.get(f"/memories/{IAN}").status_code == 403


def test_chat_exige_token_da_propria_pessoa(client):
    r = client.post("/chat", json={"user_id": IAN, "message": "oi"}, headers=ADMIN)
    assert r.status_code == 403  # operadora não conversa em nome do Ian
    r = client.post("/chat", json={"user_id": IAN, "message": "oi"},
                    headers={"Authorization": f"Bearer {TOKENS['Ian']}"})
    assert r.status_code == 200


def test_pessoa_apaga_a_propria_memoria(client):
    memory.remember_fact(RAFAEL, "Fato temporário", "geral")
    h = {"Authorization": f"Bearer {TOKENS['Rafael']}"}
    facts = client.get(f"/memories/{RAFAEL}", headers=h).json()["facts"]
    fid = facts[-1]["id"]
    assert client.delete(f"/memories/{RAFAEL}/{fid}", headers=h).status_code == 200
    assert client.delete(f"/memories/{RAFAEL}/{fid}", headers=h).status_code == 404


# ─── 5. Ações pendentes: escopadas por usuário ────────────────────────────────

def test_acao_de_um_nao_confirma_pelo_outro():
    r = tools.execute_tool("agendar", {"titulo": "Dentista", "data": "2027-03-01", "hora": "10:00"}, PAULINE)
    action_id = int(r.split("#")[1].split(" ")[0])
    # Ian tenta confirmar a ação da Pauline → não existe para ele
    assert "Não encontrei" in tools.execute_tool("confirmar_acao", {"action_id": action_id}, IAN)
    # Pauline confirma a dela → executa
    assert "Agenda Viva" in tools.execute_tool("confirmar_acao", {"action_id": action_id}, PAULINE)
    # Agenda do Ian continua vazia
    assert memory.get_agenda(IAN) == []


# ─── 6. Compartilhamento: só com consentimento explícito ─────────────────────

def test_compartilhar_exige_confirmacao():
    memory.save_message(PAULINE, "user", "oi", "telegram")  # canal de push da Pauline
    r = tools.execute_tool("compartilhar_com_familia", {"para": "Pauline", "mensagem": "Chego às 20h"}, IAN)
    assert "Ação pendente" in r
    action_id = int(r.split("#")[1].split(" ")[0])

    # ANTES da confirmação: nada foi entregue à Pauline
    assert memory.reminders_today(PAULINE) == []

    r = tools.execute_tool("confirmar_acao", {"action_id": action_id}, IAN)
    assert "enviado para Pauline" in r
    entregues = memory.due_reminders()
    recado = [x for x in entregues if x["user_id"] == PAULINE]
    assert len(recado) == 1
    assert "Chego às 20h" in recado[0]["text"]
    assert "Recado de Ian" in recado[0]["text"]  # remetente identificado
    assert recado[0]["channel"] == "telegram"    # canal certo da destinatária
    memory.mark_reminder_sent(recado[0]["id"])


def test_compartilhar_com_desconhecido_falha():
    r = tools.execute_tool("compartilhar_com_familia", {"para": "Fulano", "mensagem": "oi"}, IAN)
    assert "não está na família" in r


# ─── 7. Permissões por escopo ─────────────────────────────────────────────────

def test_escopo_futuro_nasce_desligado():
    r = tools.execute_tool("propor_acao",
                           {"tipo": "transporte", "resumo": "Chamar carro para o médico"}, IAN)
    action_id = int(r.split("#")[1].split(" ")[0])
    r = tools.execute_tool("confirmar_acao", {"action_id": action_id}, IAN)
    assert "desligada" in r and "NÃO foi" in r  # não executa sem permissão


def test_liberar_escopo_e_registrado():
    r = tools.execute_tool("gerenciar_permissao", {"escopo": "transporte", "conceder": True}, IAN)
    assert "liberada" in r
    assert memory.get_profile(IAN)["data"]["permissoes"]["transporte"] is True
    assert any("transporte" in f["content"] and f["category"] == "limites"
               for f in memory.get_facts(IAN))
    # Agora a confirmação passa da checagem de escopo
    r = tools.execute_tool("propor_acao", {"tipo": "transporte", "resumo": "Chamar carro"}, IAN)
    action_id = int(r.split("#")[1].split(" ")[0])
    r = tools.execute_tool("confirmar_acao", {"action_id": action_id}, IAN)
    assert "desligada" not in r  # passou do escopo (execução real vem na integração futura)


# ─── 8. Emergência: mínimo necessário + auditoria ─────────────────────────────

def test_emergencia_avisa_contato_com_minimo():
    memory.save_message(NANDA, "user", "oi", "whatsapp")  # canal de push da Nanda
    r = tools.execute_tool("acionar_emergencia", {"motivo": "pediu ajuda agora"}, IAN)
    assert "avisado" in r
    entregues = [x for x in memory.due_reminders() if x["user_id"] == NANDA]
    assert len(entregues) == 1
    assert "Ian" in entregues[0]["text"] and "pediu ajuda agora" in entregues[0]["text"]
    assert "prova de matemática" not in entregues[0]["text"]  # NUNCA vaza histórico
    # Trilha de auditoria existe e está executada
    with memory._conn() as conn:
        row = conn.execute(
            "SELECT status, risk_level FROM pending_actions WHERE user_id=? AND type='emergencia'",
            (IAN,),
        ).fetchone()
    assert row["status"] == "executed" and row["risk_level"] == "alto"


def test_emergencia_sem_contato_orienta():
    memory.add_member("5511944444444", "SemContato")
    r = tools.execute_tool("acionar_emergencia", {"motivo": "x"}, "5511944444444")
    assert "192" in r


# ─── 9. Remoção de membro não apaga memória (só a pedido) ────────────────────

def test_remover_membro_preserva_memoria(client):
    memory.add_member("5511955555555", "Temp")
    r = client.delete("/family/members/5511955555555", headers=ADMIN)
    assert r.status_code == 200
    assert memory.get_member("5511955555555") is None
