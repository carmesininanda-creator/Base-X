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


def test_status_expoe_modo_familia(client):
    # Verificável de fora, sem autenticação: produção mostra se a portaria está ativa
    assert client.get("/").json()["modo_familia"] is True


# ─── 3. Onboarding individual e independente ──────────────────────────────────

def test_onboarding_individual():
    # A ordem da primeira conversa: NOME primeiro (decisão da Nanda), depois
    # a pendência inicial, depois o consentimento
    assert onboarding.current_step(memory.get_profile(IAN)) == "nome"
    tools.execute_tool("registrar_onboarding", {"campo": "nome", "valor": "Ian"}, IAN)
    assert onboarding.current_step(memory.get_profile(IAN)) == "pendencia_inicial"
    tools.execute_tool("registrar_onboarding", {"campo": "pendencia_inicial", "valor": "devolver livros"}, IAN)
    tools.execute_tool("registrar_onboarding", {"campo": "consentimento", "valor": "sim"}, IAN)
    assert onboarding.current_step(memory.get_profile(IAN)) is None

    # Pauline ainda está no começo do dela — progresso NÃO vazou
    assert onboarding.current_step(memory.get_profile(PAULINE)) == "nome"
    tools.execute_tool("registrar_onboarding", {"campo": "nome", "valor": "Nine"}, PAULINE)
    tools.execute_tool("registrar_onboarding", {"campo": "pendencia_inicial", "valor": "agendar dentista"}, PAULINE)
    tools.execute_tool("registrar_onboarding", {"campo": "consentimento", "valor": "sim"}, PAULINE)


def test_abertura_personalizada_por_membro(client):
    from server import pending_welcome
    texto = "Rafa, sou a Giu! Como você prefere que eu te chame?"
    r = client.post(
        "/family/members",
        json={"user_id": RAFAEL, "name": "Rafael", "emergency_contact": NANDA, "welcome": texto},
        headers=ADMIN,
    )
    assert r.status_code == 200
    # Primeiro contato: o texto aprovado pela operadora, verbatim
    assert pending_welcome(RAFAEL) == texto
    # Depois da primeira troca, o cérebro assume — nunca repete o script
    memory.save_message(RAFAEL, "user", "oi", "whatsapp")
    memory.save_message(RAFAEL, "assistant", texto, "whatsapp")
    assert pending_welcome(RAFAEL) is None
    # Membro sem texto aprovado: sem script, cérebro desde a primeira mensagem
    assert pending_welcome(IAN) is None


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

def test_emergencia_entrega_sincrona_com_template_fixo(monkeypatch):
    # B1: a emergência envia DIRETO e SÍNCRONO, verifica a entrega e nunca vaza o motivo
    enviados = []
    def fake_sync(to, text):
        enviados.append((to, text))
        return True  # simula entrega bem-sucedida
    monkeypatch.setattr("giu.tools.whatsapp.send_message_sync", fake_sync)
    memory.save_message(NANDA, "user", "oi", "whatsapp")  # canal de push da Nanda

    motivo_do_modelo = "pediu ajuda depois de contar detalhe íntimo X"
    r = tools.execute_tool("acionar_emergencia", {"motivo": motivo_do_modelo}, IAN)
    assert "avisado agora" in r  # sucesso honesto
    assert len(enviados) == 1
    to, texto = enviados[0]
    assert to == NANDA
    # Template determinístico: identifica a pessoa e a urgência...
    assert "Ian" in texto and "precisa de ajuda AGORA" in texto
    # ...e NUNCA contém o texto livre do modelo nem histórico de conversa
    assert motivo_do_modelo not in texto and "íntimo" not in texto
    assert "prova de matemática" not in texto
    # O motivo fica só na trilha de auditoria, com o resultado da entrega
    with memory._conn() as conn:
        row = conn.execute(
            "SELECT status, risk_level, summary FROM pending_actions WHERE user_id=? AND type='emergencia'",
            (IAN,),
        ).fetchone()
    assert row["status"] == "executed" and row["risk_level"] == "alto"
    assert motivo_do_modelo in row["summary"] and "entregue=True" in row["summary"]


def test_emergencia_falha_honesta_quando_nao_entrega(monkeypatch):
    # B1: se o envio falha, a Giu NÃO finge que avisou — orienta a ligar 192
    monkeypatch.setattr("giu.tools.whatsapp.send_message_sync", lambda to, text: False)
    monkeypatch.setattr("giu.tools.telegram.send_message_sync", lambda to, text: False)
    r = tools.execute_tool("acionar_emergencia", {"motivo": "queda"}, IAN)
    assert "NÃO consegui avisar" in r and "192" in r


def test_emergencia_sem_contato_orienta():
    memory.add_member("5511944444444", "SemContato")
    r = tools.execute_tool("acionar_emergencia", {"motivo": "x"}, "5511944444444")
    assert "192" in r


# ─── Correções dos bloqueadores do piloto (B1–B5) ─────────────────────────────

def test_b2_dedup_de_mensagem_do_canal():
    # B2: a mesma mensagem do canal (wamid) só é processada uma vez
    assert memory.already_processed("wa:ABC123") is False  # 1ª vez
    assert memory.already_processed("wa:ABC123") is True    # reenvio → duplicata
    assert memory.already_processed("wa:OUTRA") is False    # id diferente é novo


def test_b3_consentimento_nao_bloqueia_preferencias():
    # B3: quem recusa consentimento não tem preferências guardadas...
    memory.set_profile("u_negou", name="X", consentimento=False)
    assert memory.remember_fact("u_negou", "gosta de café", "preferencias") is False
    assert memory.get_facts("u_negou") == []
    # ...mas o registro de consentimento (categoria limites) SEMPRE persiste
    assert memory.remember_fact("u_negou", "recusou guardar preferências", "limites") is True
    # e quem consentiu, guarda normalmente
    memory.set_profile("u_ok", name="Y", consentimento=True)
    assert memory.remember_fact("u_ok", "gosta de chá", "preferencias") is True


def test_b3_parser_de_consentimento_normalizado():
    from giu.onboarding import _interpret_consent
    for sim in ("sim", "pode sim", "claro que pode", "uhum", "autorizo", "SIM!"):
        assert _interpret_consent(sim) is True, sim
    for nao in ("não", "nao", "prefiro que não", "n", "nunca"):
        assert _interpret_consent(nao) is False, nao
    # ambíguo/sem sinal claro → padrão NÃO consentido (privacidade decide empate)
    assert _interpret_consent("sei lá") is False


def test_b4_apagamento_total_varre_tudo(client):
    memory.set_profile("u_apaga", name="Z", consentimento=True)
    memory.remember_fact("u_apaga", "fato", "geral")
    memory.save_message("u_apaga", "user", "mensagem que não pode voltar", "web")
    memory.add_agenda("u_apaga", "compromisso")
    memory.add_reminder("u_apaga", "lembrete", memory._now())
    counts = memory.forget_user("u_apaga")
    assert counts["facts"] == 1 and counts["messages"] == 1
    assert memory.get_facts("u_apaga") == []
    assert memory.get_history("u_apaga") == []   # o episódico NÃO reentra no contexto
    assert memory.get_agenda("u_apaga") == []
    # apagamento total inclui o perfil: nome e consentimento somem (recomeça do zero)
    assert memory.get_profile("u_apaga")["name"] is None
    assert memory.get_profile("u_apaga")["data"] == {}


def test_b3_gate_nao_e_contornavel_pelo_modelo():
    # Furo fechado: 'limites' saiu do enum de lembrar_fato, então o modelo não
    # pode rotular uma preferência como 'limites' para driblar a recusa
    from giu import tools
    enum = tools.TOOL_DEFINITIONS[0]["function"]["parameters"]["properties"]["categoria"]["enum"]
    assert "limites" not in enum
    # e as categorias legítimas continuam disponíveis
    assert {"preferencias", "saude", "afeto"}.issubset(set(enum))


def test_b5_lembrete_falho_nao_trava_a_fila_e_desiste():
    # B5: uma falha de entrega não aborta os outros e desiste após N tentativas
    rid = memory.add_reminder("u_lemb", "tomar remédio", memory._now(), "whatsapp")
    for _ in range(4):
        assert memory.mark_reminder_failed(rid) is False  # ainda vai retentar
        assert rid in [x["id"] for x in memory.due_reminders()]  # continua na fila
    assert memory.mark_reminder_failed(rid) is True  # 5ª tentativa → desiste
    assert rid not in [x["id"] for x in memory.due_reminders()]  # sai da fila


# ─── 9. Remoção de membro não apaga memória (só a pedido) ────────────────────

def test_remover_membro_preserva_memoria(client):
    memory.add_member("5511955555555", "Temp")
    r = client.delete("/family/members/5511955555555", headers=ADMIN)
    assert r.status_code == 200
    assert memory.get_member("5511955555555") is None


# ─── Voz no WhatsApp (canal, não motor) ───────────────────────────────────────

def test_voice_vocefy_prepara_texto_para_ouvido():
    from giu import voice
    t = voice.vocefy("**Dentista** sexta às 14:30, R$120 https://x.com 😀")
    assert "**" not in t and "😀" not in t          # sem markdown, sem emoji
    assert "14 e 30" in t                            # hora falada
    assert "120" in t and "R$" not in t              # símbolo removido
    assert "link enviado" in t                       # url não é lida
    # reticências e travessão viram pausa — preservados
    assert "…" in voice.vocefy("acontece… tá?")


def test_voice_modalidade_salva_na_memoria():
    # requisito: a memória sabe que o turno foi por voz
    memory.save_message("u_voz", "user", "oi por voz", "whatsapp", modality="voice")
    assert memory.last_modality("u_voz") == "voice"
    memory.save_message("u_voz", "user", "agora escrito", "whatsapp", modality="text")
    assert memory.last_modality("u_voz") == "text"


def test_voice_stt_tts_degradam_sem_quebrar():
    # sem OPENAI_API_KEY configurada no teste, STT/TTS retornam None (nunca levantam)
    from giu import voice
    assert voice.transcrever(b"bytes") is None
    assert voice.sintetizar("oi") is None


def test_voice_prompt_de_voz_so_entra_no_turno_de_voz():
    from giu import brain
    assert "SERÁ OUVIDA EM ÁUDIO" in brain._VOICE_GUIDANCE
    # read-back de ação sensível e anti-dependência estão nas diretrizes
    assert "peguei certo" in brain._VOICE_GUIDANCE
    assert "saudade" in brain._VOICE_GUIDANCE


def test_voice_parse_incoming_audio(client):
    from giu.channels import whatsapp
    # o webhook distingue áudio de texto
    payload_audio = {"entry": [{"changes": [{"value": {"messages": [
        {"from": "5511900000000", "type": "audio", "id": "wamid.AUDIO",
         "audio": {"id": "MEDIA123"}}]}}]}]}
    assert whatsapp.parse_incoming_audio(payload_audio) == ("5511900000000", "MEDIA123", "wamid.AUDIO")
    assert whatsapp.parse_incoming(payload_audio) is None  # não é texto


def test_voice_config_e_configuravel():
    from giu import config
    # a identidade sonora é 100% configurável (padrão do piloto = shimmer)
    assert config.VOICE_NAME == "shimmer"
    assert 0.5 <= config.VOICE_SPEED <= 1.5
    assert config.TTS_MODEL and config.STT_MODEL
