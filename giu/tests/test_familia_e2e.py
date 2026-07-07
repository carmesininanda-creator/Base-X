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
    # IDENTIDADE SEMEADA (decisão da Nanda): membro com Blueprint nasce com o
    # apelido conhecido — a Giu NÃO pergunta o nome que já sabe. O onboarding
    # começa direto na pendência inicial; consentimento continua sendo da pessoa.
    assert memory.get_profile(IAN)["name"] == "Ian"
    assert onboarding.current_step(memory.get_profile(IAN)) == "pendencia_inicial"
    tools.execute_tool("registrar_onboarding", {"campo": "pendencia_inicial", "valor": "devolver livros"}, IAN)
    tools.execute_tool("registrar_onboarding", {"campo": "consentimento", "valor": "sim"}, IAN)
    assert onboarding.current_step(memory.get_profile(IAN)) is None

    # Pauline: apelido do Blueprint ("Nine") já conhecido; progresso NÃO vazou
    assert memory.get_profile(PAULINE)["name"] == "Nine"
    assert onboarding.current_step(memory.get_profile(PAULINE)) == "pendencia_inicial"
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
    # (welcome explícito na API tem prioridade sobre a abertura do Blueprint)
    assert pending_welcome(RAFAEL) == texto
    # Depois da primeira troca, o cérebro assume — nunca repete o script
    memory.save_message(RAFAEL, "user", "oi", "whatsapp")
    memory.save_message(RAFAEL, "assistant", texto, "whatsapp")
    assert pending_welcome(RAFAEL) is None
    # Membro do piloto sem texto explícito: recebe a abertura do Blueprint pelo nome
    from giu import welcomes
    assert pending_welcome(IAN) == welcomes.welcome_for("Ian")
    # Nome fora do piloto: sem script, cérebro desde a primeira mensagem
    memory.add_member("5511966666666", "Visitante")
    assert pending_welcome("5511966666666") is None


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


# ─── Lapidação da voz (bloqueadores das auditorias + preferência de relação) ──

def test_voice_vocefy_protege_dado_sensivel():
    from giu import voice
    # Valor: mantém a unidade (não some com o número, não fica mudo)
    assert "50 reais" in voice.vocefy("são R$ 50 no total")
    assert "1500 reais" in voice.vocefy("custa R$ 1.500,00")
    # Data: inclui o ANO quando existe (antes ele sumia do áudio)
    assert "de 2025" in voice.vocefy("consulta em 19/07/2025")
    # SEGURANÇA: fração de remédio NUNCA vira data ("1/2 comprimido" ≠ "dia 1 do 2")
    falado = voice.vocefy("tome 1/2 comprimido")
    assert "dia 1 do 2" not in falado
    assert "1/2" in falado


def test_voice_preferencia_governa_audio_determinista():
    import server
    U = "u_pref_audio"
    memory.set_profile(U, name="P")
    # Sem preferência escolhida: espelha o canal (voz→áudio, texto→só texto)
    assert server._should_send_audio(U, "voice") is True
    assert server._should_send_audio(U, "text") is False
    # "Só texto": NUNCA áudio, mesmo em turno de voz — determinístico, cumprido sempre
    memory.set_profile(U, voice_pref="text")
    assert server._should_send_audio(U, "voice") is False
    # "Voz"/"ambos": sempre áudio, mesmo quando ela escreveu
    memory.set_profile(U, voice_pref="voice")
    assert server._should_send_audio(U, "text") is True


def test_voice_definir_preferencia_e_flag_deterministico():
    U = "u_pref_tool"
    memory.set_profile(U, name="P", consentimento=True)
    r = tools.execute_tool("definir_preferencia_voz", {"preferencia": "texto"}, U)
    assert memory.voice_pref(U) == "text"
    # marca que já perguntou → nunca re-pergunta (isso seria cobrança)
    assert memory.get_profile(U)["data"]["voice_pref_asked"] is True
    # a preferência entra na memória de comunicação (o "Blueprint" da pessoa)
    assert any(f["category"] == "comunicacao" for f in memory.get_facts(U))
    # a Giu é instruída a confirmar em voz alta e ensinar que dá pra mudar
    assert "mudar" in r.lower()


def test_voice_fallback_de_stt_nao_e_beco(monkeypatch):
    # Bloqueador de acessibilidade: quando o STT falha, quem SÓ usa voz não pode
    # ficar sem saída. O aviso convida a tentar DE NOVO por voz (e vai em áudio também).
    import server
    from giu.channels import whatsapp as wa
    from giu import voice
    enviados = []
    monkeypatch.setattr(wa, "download_media", lambda mid: b"bytes")
    monkeypatch.setattr(voice, "transcrever", lambda b: None)          # STT falha
    monkeypatch.setattr(wa, "send_message_sync", lambda to, t: enviados.append(t) or True)
    monkeypatch.setattr(voice, "sintetizar", lambda t: None)           # sem API: TTS None
    server._audio_turn_blocking("u_voz_falha", "MEDIA")
    assert len(enviados) == 1
    msg = enviados[0].lower()
    assert "de novo" in msg                       # convida a repetir por voz
    assert "escrev" in msg                         # texto é alternativa, não a única porta
    assert msg != "não consegui entender o áudio. pode me mandar por escrito?"  # não é a antiga parede


def test_voice_guidance_texto_acompanha_e_vinculo():
    from giu import brain
    g = brain._VOICE_GUIDANCE
    assert "SERÁ OUVIDA EM ÁUDIO" in g
    assert "peguei certo" in g                 # read-back de ação sensível preservado
    assert "saudade" in g                      # anti-dependência preservado
    assert "TEXTO SEMPRE ACOMPANHA" in g       # promessa "por escrito" cumprida (já vai junto)
    assert "não uma pessoa" in g               # âncora de identidade na voz
    assert "AINDA NÃO ESCOLHEU" in brain._VOICE_ASK_PREF  # oferta de preferência no 1º turno


def test_persona_lapidacao_no_prompt():
    prompt = brain._system_prompt(IAN, "oi")
    assert "A informação serve à relação" in prompt    # item 9
    assert "interpretei isso errado" in prompt         # item 3 (pedir desculpas)
    assert "hoje eu não sei" in prompt                 # item 5 (saber não saber)
    assert "ainda faz sentido eu te ajudar" in prompt  # item 2 (direito ao silêncio)
    assert "pequenas coisas" in prompt                 # item 7 (pequenas lembranças)
    assert "sem tarefa" in prompt                      # item 8 (presença/surpresa)
    # Diretriz conceitual: a Giu soma, nunca substitui os vínculos humanos
    assert "SOMA, nunca substitui" in prompt
    assert "ocupar o lugar" in prompt


def test_posicionamento_e_ponte_no_nucleo():
    """Posicionamento oficial: a Giu organiza a vida para sobrar mais vida —
    e a ponte para os vínculos humanos vale em QUALQUER canal, não só na voz."""
    prompt = brain._system_prompt(IAN, "oi")
    # A frase-posicionamento vive na identidade (não é slogan de marketing)
    assert "pequenas cargas" in prompt
    assert "as pessoas, os sonhos e a" in prompt
    # Ponte ativa: devolve a pessoa a quem ela ama, sem esperar ela puxar
    assert "Ponte, não destino" in prompt
    assert "QUALQUER canal" in prompt
    # Salvaguardas: nunca inventar recência; crédito da conquista é da pessoa
    assert "NUNCA invente recência" in prompt
    assert "foi você quem ligou" in prompt
    # Ponte nunca no lugar do acolhimento (primeiro estar, depois devolver)
    assert "primeiro esteja" in prompt
    # Promessa 8: horizonte honesto — nunca prometer função que não existe
    assert "NUNCA prometa função que ainda" in prompt
    assert "mais pequenas cargas da vida dela" in prompt
    # A voz mantém o reforço próprio (a diretriz não saiu de lá)
    assert "vínculo humano" in brain._VOICE_GUIDANCE


# ─── Primeiro encontro por Blueprint (onboarding personalizado) ────────────────

def test_welcome_por_blueprint_nome_e_apelidos():
    from giu import welcomes
    # As quatro pessoas do piloto têm abertura própria
    for nome in ("Nanda", "Ian", "Pauline", "Rafael"):
        assert welcomes.welcome_for(nome), nome
    # Case-insensitive e apelidos do cadastro
    assert welcomes.welcome_for("ian") == welcomes.welcome_for("IAN")
    assert welcomes.welcome_for("Nine") == welcomes.welcome_for("Pauline")
    assert welcomes.welcome_for("Rafa") == welcomes.welcome_for("Rafael")
    # Fora do piloto: sem script (o cérebro assume desde a primeira mensagem)
    assert welcomes.welcome_for("Fulano") is None
    assert welcomes.welcome_for(None) is None


def test_welcome_uma_giu_quatro_portas():
    from giu import welcomes
    w = {n: welcomes.welcome_for(n) for n in ("Nanda", "Ian", "Pauline", "Rafael")}
    # As quatro são DIFERENTES (a primeira batida de cada um é memorável)
    assert len(set(w.values())) == 4
    # Identidade única: apresenta-se como Giulieta (exceto para a Nanda, que a criou)
    for nome in ("Ian", "Pauline", "Rafael"):
        assert "Eu sou a Giulieta" in w[nome], nome
    assert "Eu sou a Giulieta" not in w["Nanda"]
    assert "sonhou comigo" in w["Nanda"]
    # Confidencialidade explícita em todas
    for nome, texto in w.items():
        assert "só entre" in texto, nome
    # Anti-substituição: o alívio tem destino humano (Nanda e Nine, onde o tom permite)
    assert "ocupar o lugar das pessoas importantes" in w["Nanda"]
    assert "pra quem você ama" in w["Nanda"]
    assert "que você ama" in w["Pauline"]
    # Nine: companhia sem reciprocidade ("uma pra outra" foi vetado pelas revisoras)
    assert "uma pra outra" not in w["Pauline"]
    # Ian e Rafael: sem discurso de vínculo forçado (Blueprints respeitados)
    assert "não vim te cobrar" in w["Ian"].lower()
    assert "não decidir por você" in w["Rafael"]


def test_blueprint_e_garantia_arquitetural():
    """Princípio estrutural: a Giulieta pensa ATRAVÉS dos Blueprints. O fluxo
    número → identidade → Blueprint → memória → contexto é garantido por
    construção: membro identificado NUNCA recebe prompt sem a camada."""
    prompt_ian = brain._system_prompt(IAN, "oi")
    # A camada está presente e é do Ian
    assert "Relationship Blueprint" in prompt_ian
    assert "hipótese viva" in prompt_ian
    assert "parceria" in prompt_ian.lower()          # comunicação do Ian
    assert "Zero ironia" in prompt_ian               # o que nunca fazer com ele
    # Os princípios de preservação estão NA camada, não em documentação
    assert "NUNCA rótulo" in prompt_ian
    assert "sempre prevalece" in prompt_ian          # a pessoa > Blueprint
    assert "quem ensina quem ela é, é ela mesma" in prompt_ian
    # A camada é da pessoa certa (a da Pauline fala do jeito DELA)
    prompt_nine = brain._system_prompt(PAULINE, "oi")
    assert "NÃO se sente errada" in prompt_nine
    assert "consertando a vida dela" in prompt_nine
    # NÃO-VAZAMENTO: o conteúdo do Blueprint do Ian jamais entra no prompt da Nine
    assert "Zero ironia" not in prompt_nine
    assert "rejeitar cobranças" not in prompt_nine
    # Salvaguardas das revisoras, NA camada: fonte nunca vira argumento;
    # Blueprint nunca é citado nem lido como veredito; evidência atualiza hipótese
    assert "sua mãe disse que você" in prompt_ian     # a frase proibida, nomeada
    assert "nem a palavra \"Blueprint\" na conversa" in prompt_ian
    assert "não O QUE você diz" in prompt_ian
    assert "é a memória dela que atualiza a hipótese" in prompt_ian
    # Membro SEM Blueprint (fora do piloto): degrada com naturalidade, sem camada
    memory.add_member("5511977777701", "Visita")
    prompt_visita = brain._system_prompt("5511977777701", "oi")
    assert "Relationship Blueprint" not in prompt_visita
    # Não-membro (ex.: web fora do modo família): também sem camada, sem erro
    assert "Relationship Blueprint" not in brain._system_prompt("desconhecido", "oi")


def test_identidade_semeada_no_cadastro():
    from giu import blueprints
    # Cadastro com nome de Blueprint semeia o APELIDO e pula a pergunta do nome
    memory.add_member("5511977777702", "Rafael")
    p = memory.get_profile("5511977777702")
    assert p["name"] == "Rafa"                       # apelido, não o nome formal
    assert onboarding.current_step(p) == "pendencia_inicial"
    # Recadastro NÃO sobrescreve um nome que a própria pessoa escolheu
    memory.set_profile("5511977777702", name="Rafinha")
    memory.add_member("5511977777702", "Rafael")
    assert memory.get_profile("5511977777702")["name"] == "Rafinha"
    # Apelidos resolvem: Nine → Blueprint da Pauline
    assert blueprints.preferred_name("nine") == "Nine"
    assert blueprints.preferred_name("Fulano") is None


def test_friction_lens_no_prompt():
    """Comportamento mínimo aprovado pela fundadora: antes de responder, a Giu
    olha o momento pela lente da fricção — e decide agir, sugerir ou calar."""
    prompt = brain._system_prompt(IAN, "oi")
    assert "FRICTION LENS" in prompt
    # As cinco vidas onde a fricção mora
    for vida in ("prática", "cognitiva", "emocional", "relacional", "de saúde"):
        assert vida in prompt, vida
    # As perguntas de contenção: ajudar sem invadir, autorização, e o trilema
    assert "SEM INVADIR" in prompt
    assert "autorização" in prompt
    assert "AGIR" in prompt and "SUGERIR" in prompt and "FICAR QUIETA" in prompt
    # Anti-ruído e anti-insistência: a menor ajuda útil; "não" encerra
    assert "MENOR ajuda útil" in prompt
    assert "contexto sem benefício é ruído" in prompt
    assert '"não" encerra o assunto' in prompt


def test_falha_honesta_em_todos_os_canais(client, monkeypatch):
    """Lição do incidente: se o cérebro quebrar, a pessoa recebe resposta
    honesta — NUNCA silêncio (WhatsApp) nem 500 seco (web/Telegram)."""
    import server

    def explode(*a, **k):
        raise RuntimeError("provedor de IA fora do ar")

    monkeypatch.setattr(brain, "think", explode)
    # Conversa já iniciada (senão o turno entregaria a boas-vindas, que é o correto)
    memory.save_message(IAN, "user", "oi", "whatsapp")
    # WhatsApp (turno em background): responde honesto em vez de morrer calado
    enviados = []
    monkeypatch.setattr(server.whatsapp, "send_message_sync",
                        lambda to, t: enviados.append(t) or True)
    server._turn_blocking(IAN, "oi", "text")
    assert enviados and "Me perdi" in enviados[0]
    # Web /chat: 200 com resposta honesta, não HTTP 500
    r = client.post("/chat", json={"user_id": IAN, "message": "oi"},
                    headers={"Authorization": f"Bearer {TOKENS['Ian']}"})
    assert r.status_code == 200
    assert "Me perdi" in r.json()["reply"]


def test_welcome_aplicado_no_cadastro_automaticamente():
    from giu import welcomes
    # Cadastro sem welcome explícito → abertura do Blueprint pelo nome
    memory.add_member("5511988888801", "Nanda", role="admin")
    assert memory.get_member("5511988888801")["welcome"] == welcomes.welcome_for("Nanda")
    # Welcome explícito na API sempre vence (override da operadora)
    memory.add_member("5511988888802", "Ian", welcome="Texto aprovado à parte")
    assert memory.get_member("5511988888802")["welcome"] == "Texto aprovado à parte"
    # Nome fora do piloto → sem welcome
    memory.add_member("5511988888803", "Convidado")
    assert memory.get_member("5511988888803")["welcome"] is None
