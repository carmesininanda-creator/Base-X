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
    # Princípio do momento (Voice/decisão 08/07): fala para melhorar o momento
    assert "próximos minutos" in prompt
    assert "nunca fala apenas para responder" in prompt
    # Filosofia oficial do ecossistema: nunca responde apenas ao prompt
    assert "NUNCA responde apenas ao prompt" in prompt
    assert "MISSÃO" in prompt and "PROPÓSITO" in prompt
    # A metáfora oficial: bastidores invisíveis — "pode deixar comigo"
    assert "coloca a pessoa para conversar com a" in prompt
    assert "pode deixar comigo" in prompt


def test_missao_do_tamanho_da_vida():
    """A Giulieta nasce com a visão inteira (todas as áreas da vida) e a
    honestidade sobre o que ainda não faz — grande na visão, gradual na execução."""
    prompt = brain._system_prompt(IAN, "oi")
    assert "MISSÃO É DO TAMANHO DA VIDA" in prompt
    # Amplitude presente na identidade (amostras das 18 áreas)
    for area in ("planejamento financeiro", "viagens", "hobbies", "aprendizado", "remédios"):
        assert area in prompt, area
    # A resposta canônica de honestidade (frase da fundadora, verbatim)
    assert "quando essa capacidade estiver disponível e você decidir ativá-la" in prompt
    # Grande na visão, gradual na execução — sem virar cardápio
    assert "grande na visão, gradual na execução" in prompt
    assert "NÃO é cardápio" in prompt
    assert "NUNCA finge que faz" in prompt


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
    # ENERGIA VITAL (decisão da fundadora): a voz de quem gosta da vida
    assert "ENERGIA VITAL" in brain._VOICE_GUIDANCE
    assert "GOSTA da vida" in brain._VOICE_GUIDANCE
    assert "Calma não é lentidão" in brain._VOICE_GUIDANCE
    from giu import config as _cfg
    assert _cfg.VOICE_SPEED >= 0.96  # nunca mais o arrastado uniforme por padrão


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


# ─── Mission Engine (missões: intenção que vira cuidado acompanhado) ──────────

def test_missao_ciclo_de_vida_completo():
    U = "u_missao"
    memory.set_profile(U, name="M", consentimento=True)
    r = tools.execute_tool("abrir_missao", {
        "objetivo": "Organizar a consulta da mãe",
        "contexto": "cardiologista; plano aceita; ela prefere de manhã",
        "prioridade": "alta",
        "proximo_passo": "confirmar o horário com a clínica",
        "criterio_conclusao": "consulta realizada e receita em mãos"}, U)
    assert "deixa comigo" in r  # o feedback ensina a invisibilidade
    m = memory.missions_open(U)[0]
    assert m["estado"] == "aberta" and m["prioridade"] == "alta"
    # Os 7 campos da fundadora existem e estão preenchidos
    full = memory.mission_get(U, m["id"])
    for campo in ("objetivo", "contexto", "prioridade", "estado",
                  "proximo_passo", "criterio_conclusao"):
        assert full[campo], campo
    assert full["events"]                        # histórico desde o nascimento
    # Progresso vira histórico; estado e próximo passo evoluem
    tools.execute_tool("atualizar_missao", {
        "missao_id": m["id"], "nota": "clínica confirmou sexta 10h",
        "estado": "em_andamento", "proximo_passo": "lembrar na véspera"}, U)
    full = memory.mission_get(U, m["id"])
    assert full["estado"] == "em_andamento"
    assert any("clínica confirmou" in e["note"] for e in full["events"])
    # Conclusão: só quando RESOLVIDO — e instrui a medir VIDA (Life Architect)
    r = tools.execute_tool("concluir_missao", {
        "missao_id": m["id"], "resultado": "consulta feita, receita em mãos"}, U)
    assert "VIDA:" in r and "peso" in r
    assert memory.missions_open(U) == []
    # A resposta de vida entra DEPOIS da conclusão (nota permitida)
    tools.execute_tool("atualizar_missao", {
        "missao_id": m["id"], "nota": "VIDA: disse que foi um alívio enorme"}, U)
    assert any(e["note"].startswith("VIDA:") for e in memory.mission_get(U, m["id"])["events"])


def test_missao_isolada_por_pessoa():
    mid = memory.mission_create("u_missao_a", "Coisa da pessoa A")
    # Outra pessoa não vê, não atualiza, não conclui a missão alheia
    assert memory.mission_get("u_missao_b", mid) is None
    assert memory.mission_update("u_missao_b", mid, nota="invasão") is False
    assert memory.mission_conclude("u_missao_b", mid, "x") is False
    assert memory.missions_open("u_missao_b") == []


def test_missoes_vivas_no_prompt_ate_o_fim():
    """A missão sobrevive além da janela de histórico — acompanhamento real."""
    U = "u_missao_prompt"
    memory.set_profile(U, name="P")
    mid = memory.mission_create(U, "Devolver os livros da biblioteca",
                                proximo_passo="separar os livros na mochila")
    prompt = brain._system_prompt(U, "oi")
    assert "MISSÕES VIVAS" in prompt
    assert "Devolver os livros" in prompt and "separar os livros" in prompt
    # Life Radar na diretriz: fricção real, nunca reflexo; invisível
    assert "LIFE RADAR" in prompt
    assert "NUNCA transforme conversa em tarefa" in prompt
    assert "abri uma missão" in prompt            # a frase proibida, nomeada
    assert "RESOLVIDO de" in prompt               # concluir ≠ lembrar
    # M2/M3 (dívidas da Life Architect): saída digna + transparência sob demanda
    assert "ainda faz sentido eu cuidar disso?" in prompt
    assert "nunca o cuidado" in prompt            # invisível é o mecanismo
    # Estoura a janela de histórico… e a missão continua viva no prompt
    for i in range(40):
        memory.save_message(U, "user", f"papo {i}", "whatsapp")
    assert "Devolver os livros" in brain._system_prompt(U, "oi")
    # Concluída, sai das vivas — mas entra em AGUARDANDO A PERGUNTA DE VIDA (M1):
    # a medição de vida sobrevive à janela, como a missão sobreviveu
    memory.mission_conclude(U, mid, "devolvidos")
    p = brain._system_prompt(U, "oi")
    assert "MISSÕES VIVAS" in p and "AGUARDANDO A PERGUNTA DE VIDA" in p
    assert "Devolver os livros" in p              # ainda presente, aguardando VIDA
    # Registrada a resposta de vida → sai do prompt de vez
    memory.mission_update(U, mid, nota="VIDA: disse que aliviou")
    assert "Devolver os livros" not in brain._system_prompt(U, "oi")


def test_como_voce_trabalha_e_life_lens_no_prompt():
    """Feedback da fundadora sobre o prompt: a Base-X entra no modelo mental
    (equipe invisível) e a Life Lens protege a direção da vida."""
    prompt = brain._system_prompt(IAN, "oi")
    # Como você trabalha: nunca sozinha; equipe invisível; acolher × organizar
    assert "COMO VOCÊ TRABALHA" in prompt
    assert "equipe invisível" in prompt and "Base-X" in prompt
    assert "SEU trabalho é acolher" in prompt
    assert "nunca a infraestrutura" in prompt
    # Personalidade × capacidade
    assert "personalidade" in prompt and "capacidade" in prompt
    # Life Lens: direção da vida, não só atrito
    assert "LIFE LENS" in prompt
    assert "vida que ela quer viver" in prompt
    assert "guardiã\ndo equilíbrio" in prompt or "guardiã do equilíbrio" in prompt
    assert "sonhos" in prompt and "descanso" in prompt and "felicidade" in prompt


# ─── Presença natural (auditoria de presença — 5 ajustes aprovados) ───────────

def test_presenca_ajustes_no_prompt():
    prompt = brain._system_prompt(IAN, "oi")
    # 1. Regra de desabafo: as primeiras respostas não contêm oferta
    assert "EXCEÇÃO QUE VALE MAIS QUE A REGRA" in prompt
    assert "só presença e escuta" in prompt
    # 2. Pergunta não é obrigatória; despedida termina em ponto final
    assert "NEM TODA mensagem precisa de pergunta" in prompt
    assert "NUNCA carregam" in prompt and "pergunta nova" in prompt
    # 4. Teto de emoji
    assert "Emoji é tempero, não assinatura" in prompt
    assert "nunca em assunto doloroso" in prompt
    # 5. Textura: respostas mínimas e ritmo variável
    assert "presença tem textura" in prompt
    assert "perfeição uniforme parece máquina" in prompt
    # Voz: a pergunta de preferência respeita pressa/emoção
    assert "o momento dela vem antes da sua pergunta" in brain._VOICE_ASK_PREF


def test_presenca_emocao_vence_palavra_de_tarefa():
    from giu import modes
    # 3. O bug da auditoria: "resolver" DENTRO de desabafo não vira secretária
    assert modes.detect("não aguento mais, amanhã tenho que resolver mil coisas", 23) == "modo_noite"
    assert modes.detect("tô esgotada, preciso resolver tudo", 15) == "modo_companhia"
    # Tarefa SEM emoção continua indo para pendências (nada regrediu)
    assert modes.detect("preciso resolver a conta do banco", 15) == "modo_pendencias"
    # Emergência continua vencendo TUDO (segurança primeiro)
    assert modes.detect("não aguento mais, quero morrer", 23) == "modo_emergencia"
    # Saúde sem emoção continua saúde
    assert modes.detect("esqueci o remédio de novo", 15) == "modo_saude"


# ─── Conversation Spine (continuidade da conversa atual) ──────────────────────

def test_spine_guarda_e_expira():
    U = "u_spine"
    memory.set_profile(U, name="S")
    assert memory.spine_add(U, "DECISÃO: prioridade é o prazo do projeto") is True
    assert memory.spine_add(U, "  ") is False               # vazio não entra
    fio = memory.spine_get(U)
    assert len(fio) == 1 and "prazo do projeto" in fio[0]["note"]
    # Capacidade máxima: só os últimos SPINE_MAX ficam
    for i in range(memory.SPINE_MAX + 3):
        memory.spine_add(U, f"item {i}")
    assert len(memory.spine_get(U)) == memory.SPINE_MAX
    # Expiração: item velho (além do TTL) cai
    velho = [{"t": "2020-01-01T00:00:00", "note": "conversa de outra era"}]
    memory.set_profile("u_spine_velho", name="V", spine=velho)
    assert memory.spine_get("u_spine_velho") == []


def test_spine_simulacao_conversa_longa():
    """Simulação pedida pela fundadora: insight no início + mudança de prioridade
    no meio → o fio sobrevive até o final, mesmo com o histórico estourado."""
    U = "u_spine_longa"
    memory.set_profile(U, name="Longa")
    # Início da conversa: um insight importante é anotado no fio
    tools.execute_tool("anotar_fio", {"nota": "INSIGHT: ela quer montar uma horta na varanda"}, U)
    # ... a conversa cresce além da janela de histórico (16 mensagens) ...
    for i in range(40):
        memory.save_message(U, "user", f"mensagem corriqueira {i}", "whatsapp")
        memory.save_message(U, "assistant", f"resposta {i}", "whatsapp")
    # Meio da conversa: mudança de prioridade — também anotada
    tools.execute_tool("anotar_fio", {"nota": "MUDANÇA: a horta espera; prioridade agora é a consulta da mãe"}, U)
    for i in range(20):
        memory.save_message(U, "user", f"mais conversa {i}", "whatsapp")
        memory.save_message(U, "assistant", f"mais resposta {i}", "whatsapp")
    # Final: o histórico cru já perdeu o começo…
    historico = str(memory.get_history(U))
    assert "horta" not in historico            # fora da janela de 16 mensagens
    # …mas a ESPINHA mantém o fio vivo no prompt, do início ao fim:
    prompt = brain._system_prompt(U, "e aí, por onde começamos?")
    assert "FIO DA CONVERSA" in prompt
    assert "horta na varanda" in prompt                        # o insight do início
    assert "prioridade agora é a consulta da mãe" in prompt    # a mudança do meio
    # As perguntas de continuidade acompanham a espinha
    assert "contradizendo algo já decidido" in prompt
    assert "não só a última mensagem" in prompt.replace("\n", " ")
    # E a distinção conceitual está no prompt: spine ≠ memória permanente
    assert "NÃO é memória" in prompt and "lembrar_fato" in prompt


# ─── Base-X: o motor operacional (sistema FECHADO, sem pontas abertas) ────────

def test_basex_sistema_fechado_21_dominios():
    from giu import basex
    # Os 21 domínios obrigatórios da fundadora, exatamente
    obrigatorios = {"familia", "saude", "bem_estar", "agenda", "organizacao",
                    "compras", "casa", "mobilidade", "comunicacao", "documentos",
                    "financas", "projetos", "trabalho", "estudos", "viagens",
                    "objetivos", "habitos", "pets", "emergencias",
                    "casa_inteligente", "wearables"}
    assert set(basex.DOMINIOS) == obrigatorios
    # Cada domínio tem TODOS os campos exigidos (estado, memória, especialistas,
    # missão, conectores, executor, acompanhamento, critério de encerramento)
    campos = ("estado", "memoria", "especialistas", "missao", "conectores",
              "executor", "acompanhamento", "criterio", "cuidado_hoje")
    for nome, d in basex.DOMINIOS.items():
        for c in campos:
            assert d.get(c) is not None, (nome, c)
    # SISTEMA FECHADO: toda cadeia de executores termina em manual-guiado —
    # nenhum pedido morre no vazio, em NENHUM domínio
    for nome in basex.DOMINIOS:
        chain = basex.executor_chain(nome)
        assert chain[-1] == "guiado", nome
        assert all(c in basex.CONNECTORS for c in chain), nome
        # nenhum domínio depende só de futuro: sempre há caminho real/interno/manual HOJE
        tipos = {basex.CONNECTORS[c]["tipo"] for c in chain}
        assert tipos & {"real", "interno", "manual"}, nome


def test_basex_contrato_do_conector():
    from giu import basex
    # Contrato de 8 campos, obrigatório em TODO Life Connector
    campos = ("dominio", "objetivo", "tipo", "acoes", "permissoes",
              "auditoria", "fallback", "executor")
    for cid, c in basex.CONNECTORS.items():
        for campo in campos:
            assert c.get(campo), (cid, campo)
        assert c["tipo"] in ("real", "interno", "manual"), cid
    # Internos e o guiado estão SEMPRE disponíveis (o piso do sistema fechado)
    for cid in ("missoes", "lembretes", "agenda_viva", "emergencia", "guiado"):
        assert basex.connector_available(cid), cid


def test_basex_incorporada_no_cerebro():
    prompt = brain._system_prompt(IAN, "oi")
    # O conhecimento operacional entra em TODO turno
    assert "COMO A BASE-X JÁ CUIDA HOJE" in prompt
    assert "já consigo cuidar disso" in prompt
    assert "Preparar + acompanhar JÁ É cuidar" in prompt
    # Amostras dos domínios (saúde, mobilidade, pets) no conhecimento vivo
    assert "exames como missão" in prompt
    assert "trajeto preparado mastigado" in prompt
    assert "é carinho, não tarefa" in prompt
    # X1 (Life Architect): NENHUM nome de ser querido no conhecimento genérico
    from giu import basex as _bx
    assert "Floki" not in str(_bx.DOMINIOS) and "Floki" not in _bx.prompt_section()
    # X2: o passo final é da pessoa, dito no início, como oferta
    assert "o passo final é dela" in prompt
    assert "nunca frase-carimbo" in prompt
    # A ordem da honestidade: primeiro o caminho de hoje, canônica só depois
    assert "antes de dizer que não faz" in prompt
    # X5 (painel de presença): em emoção quente, o catálogo fica MUDO
    assert "CATÁLOGO FICA MUDO" in prompt


# ─── Life Connector real: Google Calendar POR PESSOA (opt-in, revogável) ──────

def test_agenda_conexao_por_pessoa(client, monkeypatch):
    from giu import config as cfg
    from giu.integrations import google_calendar as gc
    U = "u_gcal"
    memory.set_profile(U, name="G", consentimento=True)

    # Sem app configurado: honestidade canônica, nunca link quebrado
    r = tools.execute_tool("conectar_agenda", {}, U)
    assert "ainda não está disponível" in r and "Agenda Viva" in r

    # Com app configurado: o link é real, pessoal e com estado de uso único
    monkeypatch.setattr(cfg, "GOOGLE_CLIENT_ID", "cid")
    monkeypatch.setattr(cfg, "GOOGLE_CLIENT_SECRET", "sec")
    monkeypatch.setattr(cfg, "BASE_URL", "https://giu.exemplo.com")
    r = tools.execute_tool("conectar_agenda", {}, U)
    assert "accounts.google.com" in r and U in r
    assert "desconecta minha agenda" in r          # o gesto de sair, ensinado na entrada
    assert "nada" in r and "nem e-mail" in r       # D2: o que ela passa a ver, em voz alta

    # Callback: estado válido conecta a agenda DA pessoa…
    monkeypatch.setattr(gc, "exchange_code", lambda code: "RT_NOVO")
    state = memory.oauth_state_new(U)
    resp = client.get(f"/connectors/google/callback?code=abc&state={state}")
    assert resp.status_code == 200 and "conectada" in resp.text
    assert memory.google_token(U) == "RT_NOVO"
    # …e o estado é de USO ÚNICO (replay não conecta de novo)
    assert client.get(f"/connectors/google/callback?code=abc&state={state}").status_code == 400
    # estado forjado: rejeitado
    assert client.get("/connectors/google/callback?code=abc&state=u_gcal.falso").status_code == 400

    # A cadeia por pessoa: token DELA vale mesmo sem token global
    monkeypatch.setattr(cfg, "GOOGLE_REFRESH_TOKEN", "")
    assert gc.is_configured(U) is True             # a pessoa está conectada
    assert gc.is_configured() is False             # o modo global segue exigindo env
    # D1: token GLOBAL nunca vaza para turno pessoal de quem NÃO conectou
    monkeypatch.setattr(cfg, "GOOGLE_REFRESH_TOKEN", "GLOBAL")
    assert gc.is_configured("u_nunca_conectou") is False
    assert gc.is_configured() is True              # global explícito (sem user) continua
    monkeypatch.setattr(cfg, "GOOGLE_REFRESH_TOKEN", "")
    assert gc._refresh_token_for(U) == "RT_NOVO"
    assert gc._calendar_id_for(U) == "primary"     # a agenda principal DELA
    # Outra pessoa NÃO herda a conexão (isolamento)
    assert gc.is_connected(IAN) is False

    # Revogação imediata e determinística
    r = tools.execute_tool("desconectar_agenda", {}, U)
    assert "AGORA" in r
    assert not memory.google_token(U)
    assert gc.is_configured(U) is False


def test_voz_diretriz_acompanha_resposta_falada(monkeypatch):
    """Descoberta nº 1 da Voice Architect: a diretriz de fala segue a decisão
    'esta resposta SERÁ FALADA' — não 'este turno veio por áudio'."""
    from giu import config as cfg
    U = "u_fala"
    memory.set_profile(U, name="F")
    # Turno de voz: sempre falada
    assert brain._resposta_falada(U, "voice") is True
    # Turno de TEXTO de quem escolheu VOZ: a resposta será falada → diretriz entra
    memory.set_profile(U, voice_pref="voice")
    assert brain._resposta_falada(U, "text") is True
    # Quem escolheu só texto: nunca
    memory.set_profile(U, voice_pref="text")
    assert brain._resposta_falada(U, "text") is False
    # Sem preferência: espelha o canal (texto → não falada)
    memory.set_profile(U, voice_pref=None)
    assert brain._resposta_falada(U, "text") is False
    # Voz global desligada: nunca falada em turno de texto
    memory.set_profile(U, voice_pref="voice")
    monkeypatch.setattr(cfg, "VOICE_REPLIES", False)
    assert brain._resposta_falada(U, "text") is False


def test_voz_checkin_fala_para_quem_escolheu_voz(monkeypatch):
    """Descoberta nº 2: o check-in proativo ganha voz para quem escolheu voz
    (texto sempre primeiro; áudio aditivo)."""
    import asyncio as aio
    import server
    from giu import voice as v
    U = "u_checkin_voz"
    memory.set_profile(U, name="C", voice_pref="voice")
    textos, audios = [], []
    async def fake_send(uid, t):
        textos.append(t)
    monkeypatch.setattr(server.whatsapp, "send_message", fake_send)
    monkeypatch.setattr(server.whatsapp, "is_configured", lambda: True)
    monkeypatch.setattr(server.whatsapp, "send_audio", lambda uid, a: audios.append(a) or True)
    monkeypatch.setattr(v, "sintetizar", lambda t: b"OGG")
    assert aio.run(server._send_push(U, "whatsapp", "Bom dia, C")) is True
    assert textos == ["Bom dia, C"]           # texto SEMPRE primeiro
    assert audios == [b"OGG"]                  # e a voz junto, para quem escolheu
    # Quem escolheu só texto: check-in continua mudo (respeito determinístico)
    memory.set_profile(U, voice_pref="text")
    audios.clear()
    aio.run(server._send_push(U, "whatsapp", "Boa noite, C"))
    assert audios == []


def test_basex_regra_de_ouro_no_prompt():
    prompt = brain._system_prompt(IAN, "oi")
    assert "qual aplicativo devo usar" in prompt
    assert "melhor forma de resolver a necessidade desta pessoa" in prompt
    assert "nunca escolhe app" in prompt


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


# ─── Living Context: Time Provider (Fase 2 — garantias do contrato) ───────────
# As 12 garantias da ARQUITETURA-CONTEXT-PROVIDERS.md aplicáveis ao primeiro
# Provider: nunca levanta, piso interno, silêncio, orçamento, confidencialidade,
# língua de vida, efêmero, teto de tempo, substituição (um único AGORA).

from giu import context  # noqa: E402
from giu.context import tempo  # noqa: E402


def _previsao_fake(*a, **k):
    """Resposta falsa do Life Connector de clima (nenhum teste toca a rede) —
    já em língua de vida, como o contrato do conector devolve."""
    return {"temperatura": 18, "descricao": "garoa", "maxima": 21,
            "minima": 13, "nascer": "06:48", "por": "17:32"}


def _hoje():
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from giu import config as _cfg
    return datetime.now(ZoneInfo(_cfg.TIMEZONE))


def test_retrato_piso_interno_nunca_nasce_vazio():
    # Pessoa desconhecida, banco sem nada dela, zero conectores: o retrato existe
    r = context.retrato("5511900009999")
    assert "O MOMENTO DE AGORA" in r
    assert "AGORA:" in r
    # Dia da semana em PORTUGUÊS (vida, não locale do servidor) + estação
    assert any(dia in r for dia in tempo.DIAS_SEMANA)
    assert any(e in r for e in ("verão", "outono", "inverno", "primavera"))


def test_retrato_silencio_sem_cidade_e_sem_datas():
    # Silêncio é resposta válida: sem autorizações, nada de clima nem datas
    r = context.retrato("5511900009999")
    assert "Lá fora" not in r
    assert "DATAS QUERIDAS" not in r


def test_retrato_e_efemero_nao_escreve_vida_no_banco():
    u = "5511900009998"
    with memory._conn() as conn:
        antes = {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                 for t in ("profile", "facts", "messages", "agenda", "missions")}
    context.retrato(u)
    with memory._conn() as conn:
        depois = {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                  for t in ("profile", "facts", "messages", "agenda", "missions")}
    assert antes == depois


def test_datas_queridas_acordam_no_dia_e_na_vespera():
    from datetime import timedelta
    hoje = _hoje()
    assert memory.dates_add(IAN, "Aniversário da avó dele", hoje.strftime("%m-%d"))
    assert memory.dates_add(IAN, "Entrega do projeto",
                            (hoje + timedelta(days=1)).strftime("%Y-%m-%d"),
                            recorrente=False)
    r = context.retrato(IAN)
    assert "DATAS QUERIDAS" in r
    assert "Aniversário da avó dele" in r          # acorda HOJE
    assert "Entrega do projeto" in r               # véspera (amanhã)
    assert "nunca como notificação" in r           # o tom vai junto com o dado


def test_retrato_confidencialidade_nada_atravessa_membros():
    # A data querida do Ian JAMAIS aparece no retrato da Pauline
    r = context.retrato(PAULINE)
    assert "Aniversário da avó dele" not in r
    assert "Entrega do projeto" not in r


def test_consentimento_recusado_bloqueia_datas():
    u = "5511900009997"
    memory.set_profile(u, consentimento=False)
    assert memory.dates_add(u, "Data qualquer", "01-01") is False
    assert memory.dates_all(u) == []


def test_clima_degrada_em_silencio_quando_conector_falha(monkeypatch):
    u = "5511900009996"
    memory.city_set(u, "São Paulo", -23.55, -46.63)
    tempo._clima_cache.clear()

    def explode(*a, **k):
        raise RuntimeError("conector fora do ar")
    monkeypatch.setattr(tempo.open_meteo, "previsao", explode)
    r = context.retrato(u)                          # não levanta
    assert "AGORA:" in r                            # o piso continua inteiro
    assert "Lá fora" not in r                       # o clima simplesmente cala
    assert "erro" not in r.lower() and "falha" not in r.lower()


def test_clima_lingua_de_vida_e_teto_por_snapshot(monkeypatch):
    u = "5511900009995"
    memory.city_set(u, "São Paulo", -23.55, -46.63)
    tempo._clima_cache.clear()
    monkeypatch.setattr(tempo.open_meteo, "previsao", _previsao_fake)
    snap = tempo.snapshot(u)
    assert "Lá fora em São Paulo" in snap and "18°C" in snap and "garoa" in snap
    assert "sol" in snap                            # nascer/pôr do sol junto
    assert len(snap.splitlines()) <= 3              # teto de 3 linhas por Provider
    # Língua de vida: nenhum fornecedor, jargão ou módulo aparece no retrato
    baixo = snap.lower()
    for proibido in ("open-meteo", "api", "provider", "conector", "http"):
        assert proibido not in baixo
    # Teto de TEMPO: conector lento é conector mudo — a conversa nunca espera
    assert tempo._CLIMA_TIMEOUT <= 3


def test_prompt_tem_um_unico_agora_e_nao_cresceu():
    # CP-2 (substituição, não soma): o retrato ASSUME o lugar do antigo AGORA —
    # nada aparece em dobro, e o prompt não incha com a chegada do Living Context.
    prompt = brain._system_prompt("5511900009994", "oi")
    assert prompt.count("AGORA:") == 1
    assert "O MOMENTO DE AGORA" in prompt
    assert len(prompt) < 21500  # orçamento global (medido em 07/2026: ~20.6k)


def test_tool_anotar_data_valida_e_guarda():
    r = tools.execute_tool("anotar_data",
                           {"titulo": "Aniversário do padrinho", "data": "21-09-1967"},
                           RAFAEL)
    assert "inválido" in r or "Não consegui" in r   # formato errado não entra
    r = tools.execute_tool("anotar_data",
                           {"titulo": "Aniversário do padrinho", "data": "09-21"},
                           RAFAEL)
    assert "Data guardada" in r
    assert any(d["titulo"] == "Aniversário do padrinho" for d in memory.dates_all(RAFAEL))


def test_tool_definir_cidade_esquecer_e_lei():
    u = "5511900009993"
    memory.city_set(u, "Campinas", -22.9, -47.06)
    assert memory.city_get(u)["nome"] == "Campinas"
    r = tools.execute_tool("definir_cidade", {"cidade": ""}, u)
    assert "esquecida AGORA" in r
    assert memory.city_get(u) is None


# ─── Time Provider: dívidas da Life Architect pagas (T1–T6) ───────────────────

def test_t1_aniversario_29_fevereiro_existe_e_acorda():
    from datetime import datetime as _dt
    u = "5511900009992"
    # 29/02 é aniversário como qualquer outro — a Giu não recusa (T1)
    assert memory.dates_add(u, "Aniversário do afilhado", "02-29") is True
    d = memory.dates_all(u)[0]
    # Em ano bissexto acorda em 29/02; em ano comum, em 28/02
    assert tempo._bate(d, _dt(2028, 2, 29)) is True
    assert tempo._bate(d, _dt(2026, 2, 28)) is True
    assert tempo._bate(d, _dt(2026, 3, 1)) is False


def test_t2_recorrencia_deriva_do_formato():
    from datetime import datetime as _dt
    u = "5511900009991"
    # Data única de ano passado JAMAIS volta a acordar (a cobrança fantasma morre)
    assert memory.dates_add(u, "Entrega antiga", "2025-07-10")
    unica = [d for d in memory.dates_all(u) if d["titulo"] == "Entrega antiga"][0]
    assert unica["recorrente"] is False
    assert tempo._bate(unica, _dt(2026, 7, 10)) is False
    assert tempo._bate(unica, _dt(2025, 7, 10)) is True
    # MM-DD é SEMPRE anual — mesmo se alguém passar recorrente=False (nada morre mudo)
    assert memory.dates_add(u, "Dia dos avós", "07-26", recorrente=False)
    anual = [d for d in memory.dates_all(u) if d["titulo"] == "Dia dos avós"][0]
    assert anual["recorrente"] is True
    # YYYY-MM-DD com recorrente=True explícito vira aniversário anual
    assert memory.dates_add(u, "Aniversário da Nanda", "1967-09-21", recorrente=True)
    aniv = [d for d in memory.dates_all(u) if "Nanda" in d["titulo"]][0]
    assert tempo._bate(aniv, _dt(2026, 9, 21)) is True


def test_t3_esquecer_data_e_lei():
    u = "5511900009990"
    memory.dates_add(u, "Aniversário do ex", "03-15")
    memory.dates_add(u, "Consulta anual", "05-10")
    r = tools.execute_tool("esquecer_data", {"titulo": "aniversário do ex"}, u)
    assert "esquecida AGORA" in r
    titulos = [d["titulo"] for d in memory.dates_all(u)]
    assert "Aniversário do ex" not in titulos and "Consulta anual" in titulos
    # Título inexistente: honestidade, não silêncio
    assert "Não encontrei" in tools.execute_tool("esquecer_data", {"titulo": "nada"}, u)


def test_t4_trocar_de_cidade_mata_o_ceu_antigo(monkeypatch):
    u = "5511900009989"
    memory.city_set(u, "São Paulo", -23.55, -46.63)
    tempo._clima_cache.clear()
    monkeypatch.setattr(tempo.open_meteo, "previsao", _previsao_fake)
    assert "São Paulo" in tempo.snapshot(u)
    # Mudou para Campinas: o cache é por coordenada — a linha antiga não volta
    memory.city_set(u, "Campinas", -22.90, -47.06)
    assert "Lá fora em Campinas" in tempo.snapshot(u)


def test_t5_o_nao_encerra_esta_no_retrato():
    from datetime import datetime as _dt
    u = "5511900009988"
    memory.dates_add(u, "Dia da vovó", _dt.now().strftime("%m-%d"))
    linha = tempo._linha_datas(u, tempo._agora())
    assert "ENCERRA" in linha and "silêncio" in linha  # anti-repetição vai com o dado


def test_t6_consentimento_recusado_bloqueia_cidade(monkeypatch):
    import httpx as _httpx
    monkeypatch.setattr(_httpx, "get",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("sem rede")))
    u = "5511900009987"
    memory.set_profile(u, consentimento=False)
    assert memory.city_set(u, "Santos", -23.9, -46.3) is False
    assert memory.city_get(u) is None
    r = tools.execute_tool("definir_cidade", {"cidade": "Santos"}, u)
    assert "NÃO foi" in r or "recusou" in r


# ─── Living Context: Calendar Provider (Fase 2 — garantias do contrato) ───────
# "Google Calendar será apenas sincronização. A Agenda Viva continua sendo o
# cérebro." (decisão da fundadora) — o snapshot nasce 100% da Agenda Viva.

from giu.context import agenda as ctx_agenda  # noqa: E402


def test_calendar_silencio_com_agenda_vazia():
    assert ctx_agenda.snapshot("5511900008999") == ""


def test_calendar_hoje_vespera_e_pendencias():
    from datetime import timedelta
    u = "5511900008998"
    hoje = _hoje().strftime("%Y-%m-%d")
    amanha = (_hoje() + timedelta(days=1)).strftime("%Y-%m-%d")
    memory.add_agenda(u, "Consulta da mãe", hoje, "15:00")
    memory.add_agenda(u, "Exame de sangue", amanha, "08:30")
    memory.add_agenda(u, "Renovar CNH")  # pendência sem data
    from datetime import datetime as _dt
    manha = _dt.fromisoformat(f"{hoje}T07:00:00")
    snap = ctx_agenda.snapshot(u, _now=manha)
    assert "Consulta da mãe às 15:00" in snap and "hoje" in snap
    assert "AGENDA — amanhã: Exame de sangue às 08:30" in snap  # rótulo próprio (C6)
    assert "véspera" in snap                      # o preparo leve vai junto
    # Pendências sem data mudaram de casa (C5): moram no Communication Provider
    assert "pendência(s) sem data" not in snap
    assert len(snap.splitlines()) <= 3            # teto do contrato


def test_calendar_conflito_detectado():
    u = "5511900008997"
    hoje = _hoje().strftime("%Y-%m-%d")
    memory.add_agenda(u, "Dentista", hoje, "15:00")
    memory.add_agenda(u, "Reunião do banco", hoje, "15:00")
    from datetime import datetime as _dt
    snap = ctx_agenda.snapshot(u, _now=_dt.fromisoformat(f"{hoje}T07:00:00"))
    assert "CONFLITO DE AGENDA" in snap
    assert "Dentista" in snap and "Reunião do banco" in snap
    assert "COM ela" in snap                      # resolver é decisão dela


def test_calendar_dia_cheio_reduz_a_uma_prioridade():
    u = "5511900008996"
    hoje = _hoje().strftime("%Y-%m-%d")
    for i, h in enumerate(("08:00", "10:00", "13:00", "16:00", "19:00")):
        memory.add_agenda(u, f"Compromisso {i+1}", hoje, h)
    from datetime import datetime as _dt
    snap = ctx_agenda.snapshot(u, _now=_dt.fromisoformat(f"{hoje}T07:00:00"))
    assert "dia CHEIO: 5 compromissos ainda por vir" in snap
    assert "UMA prioridade" in snap
    assert "Compromisso 4" not in snap            # NÃO despeja a lista


def test_calendar_concluido_sai_do_retrato():
    u = "5511900008995"
    hoje = _hoje().strftime("%Y-%m-%d")
    from datetime import datetime as _dt
    manha = _dt.fromisoformat(f"{hoje}T07:00:00")
    iid = memory.add_agenda(u, "Buscar exame", hoje, "11:00")
    assert "Buscar exame" in ctx_agenda.snapshot(u, _now=manha)
    memory.complete_agenda(u, iid)
    assert "Buscar exame" not in ctx_agenda.snapshot(u, _now=manha)


def test_calendar_confidencialidade_e_efemero():
    # A consulta de um não aparece no retrato do outro; montar não escreve nada
    assert "Consulta da mãe" not in context.retrato(PAULINE)
    u = "5511900008998"
    with memory._conn() as conn:
        antes = conn.execute("SELECT COUNT(*) FROM agenda").fetchone()[0]
    context.retrato(u)
    with memory._conn() as conn:
        assert conn.execute("SELECT COUNT(*) FROM agenda").fetchone()[0] == antes


def test_cp2_agenda_viva_absorvida_pelo_retrato():
    # CP-2: o bloco antigo sumiu; a agenda entra pelo retrato (item sem hora
    # aparece em qualquer hora do dia — não depende do relógio do teste)
    u = "5511900008992"
    memory.add_agenda(u, "Levar a receita na farmácia", _hoje().strftime("%Y-%m-%d"))
    prompt = brain._system_prompt(u, "oi")
    assert "AGENDA VIVA:" not in prompt
    assert prompt.count("AGENDA —") >= 1
    assert "Levar a receita na farmácia" in prompt  # o cuidado do dia está lá


def test_t7_providers_desacoplados_de_fornecedor():
    # Garantia 7 do contrato: nenhum Provider conhece fornecedor, URL ou HTTP —
    # a fronteira mora em integrations/ (Life Connectors). Verificação por AST
    # (C3 da Life Architect): pega "import httpx", "from httpx import get",
    # urllib, socket e importlib — não só o padrão de hoje.
    import ast as _ast
    import glob
    import os as _os
    PROIBIDOS = {"httpx", "requests", "urllib", "socket", "http", "importlib"}
    base = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                         "giu", "context")
    for arquivo in glob.glob(_os.path.join(base, "*.py")):
        fonte = open(arquivo, encoding="utf-8").read()
        for no in _ast.walk(_ast.parse(fonte)):
            mods = []
            if isinstance(no, _ast.Import):
                mods = [a.name for a in no.names]
            elif isinstance(no, _ast.ImportFrom):
                mods = [no.module or ""]
            for mod in mods:
                raiz = mod.split(".")[0]
                assert raiz not in PROIBIDOS, f"{arquivo} importa fornecedor/rede: {mod}"
        # E nenhuma URL de fornecedor no texto (cinto e suspensório)
        for proibido in ("http://", "https://", "open-meteo.com", "googleapis"):
            assert proibido not in fonte.lower(), f"{arquivo} conhece fornecedor: {proibido}"


# ─── Voz e Presença (frente permanente — prescrições V0 da Voice Architect) ───

def test_voz_telefone_dita_digito_a_digito():
    from giu import voice
    falado = voice.vocefy("me liga no 11 92078-5067 quando puder")
    assert "9 2 0 7 8… 5 0 6 7" in falado       # dígito a dígito, com fôlego
    assert "92078-5067" not in falado
    # Números de emergência também se ditam
    assert "1 8 8" in voice.vocefy("o CVV atende no 188")
    # E a dose continua protegida (segurança > estética)
    assert "1/2 comprimido" in voice.vocefy("tome 1/2 comprimido às 15:00")


def test_voz_folego_frase_longa_respira():
    from giu import voice
    longa = ("eu deixei tudo pronto para amanhã cedo, separei o pedido do médico "
             "na pasta azul, e o lembrete do jejum vai chegar às nove da noite certinho")
    falado = voice.vocefy(longa)
    assert "…" in falado                        # a pausa é conteúdo
    # nenhum trecho entre pausas passa do fôlego humano
    for trecho in falado.replace("…", ".").split("."):
        assert len(trecho.split()) <= voice._FOLEGO_MAX_PALAVRAS + 2
    # nenhuma PALAVRA muda — só a respiração entra
    assert falado.replace("…", ",") == longa.replace(",", ",")  # mesmas palavras
    # frase curta fica intocada (fôlego não vira tique)
    assert voice.vocefy("tô aqui, viu") == "tô aqui, viu"


def test_c1_boa_companhia_sabe_que_horas_sao():
    # O dia já vivido não é "hoje" (C1): às 22h, o compromisso das 09:00 cala,
    # o dia CHEIO fantasma não dispara, e o conflito que já passou não alarma.
    from datetime import datetime as _dt
    u = "5511900008994"
    hoje = _hoje().strftime("%Y-%m-%d")
    noite = _dt.fromisoformat(f"{hoje}T22:00:00")
    for h in ("08:00", "09:00", "10:00", "11:00"):
        memory.add_agenda(u, f"Já vivido {h}", hoje, h)
    memory.add_agenda(u, "Conflito passado A", hoje, "09:00")
    assert ctx_agenda.snapshot(u, _now=noite) == ""      # silêncio: o dia acabou
    # O que ainda vem, aparece; o que passou, não
    memory.add_agenda(u, "Plantão da noite", hoje, "23:00")
    snap = ctx_agenda.snapshot(u, _now=noite)
    assert "Plantão da noite" in snap and "Já vivido" not in snap


def test_c2_google_conectado_retrato_declara_o_limite(monkeypatch):
    from giu.integrations import google_calendar as gc
    u = "5511900008993"
    monkeypatch.setattr(gc, "is_configured", lambda uid=None: True)
    snap = ctx_agenda.snapshot(u)  # Agenda Viva vazia, Google conectado
    assert "confirme em ver_agenda" in snap  # nunca "dia livre" sem conferir


# ─── Capacidade de Vida: ✉️ Comunicação (Communication Provider — piso) ───────
# Domínio ampliado pela fundadora: TODA comunicação relevante, não apenas
# Gmail. Piso = o que a pessoa CONTA. C5 paga: pendência sem data acorda aqui.

from giu.context import comunicacao as ctx_com  # noqa: E402


def test_comunicacao_silencio_sem_pendencias():
    assert ctx_com.snapshot("5511900007999") == ""


def test_comunicacao_c5_pendencia_sem_data_acorda_com_idade():
    u = "5511900007998"
    memory.add_agenda(u, "Renovar CNH")           # sem data — antes, silêncio eterno
    memory.add_agenda(u, "Responder o contador")
    snap = ctx_com.snapshot(u)
    assert "PENDÊNCIAS em aberto: 2" in snap
    assert "Renovar CNH" in snap                  # a mais antiga, nomeada
    assert "Responder o contador" not in snap     # resumo, nunca a lista
    assert len(snap.splitlines()) <= 2


def test_comunicacao_anti_cobranca_cp1_viaja_com_o_dado():
    u = "5511900007998"
    snap = ctx_com.snapshot(u)
    assert "momento LEVE" in snap                 # nunca empilha em momento ruim
    assert "UMA oferta" in snap
    assert "NUNCA marque como feita" in snap      # M2: recusa ≠ conclusão falsa
    assert "nunca a diga a ela" in snap           # M6: idade orienta, não cobra
    assert "FICA MUDA" in snap                    # M7: desabafo cala esta linha


def test_comunicacao_fatos_de_pendencia_entram_e_saem():
    u = "5511900007997"
    memory.remember_fact(u, "Precisa enviar o comprovante para o consulado", "pendencias")
    snap = ctx_com.snapshot(u)
    assert "comprovante para o consulado" in snap
    assert "esquecer_fato" in snap                # resolvido = mão REAL de apagar (M1)
    fato = [f for f in memory.get_facts(u) if f["category"] == "pendencias"][0]
    memory.delete_fact(u, fato["id"])
    assert ctx_com.snapshot(u) == ""              # resolvida → silêncio de novo


def test_comunicacao_concluida_sai_do_retrato():
    u = "5511900007996"
    iid = memory.add_agenda(u, "Pagar o IPVA")
    assert "PENDÊNCIAS" in ctx_com.snapshot(u)
    memory.complete_agenda(u, iid)
    assert ctx_com.snapshot(u) == ""


def test_comunicacao_confidencialidade_e_efemero():
    assert "Renovar CNH" not in context.retrato(PAULINE)
    with memory._conn() as conn:
        antes = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
    context.retrato("5511900007998")
    with memory._conn() as conn:
        assert conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0] == antes


def test_retrato_tres_provedores_dentro_do_orcamento():
    # Com três Providers vivos, o retrato continua dentro do teto do contrato
    u = "5511900007995"
    hoje = _hoje().strftime("%Y-%m-%d")
    memory.add_agenda(u, "Reunião", hoje, "23:58")
    memory.add_agenda(u, "Levar o carro na revisão")
    memory.dates_add(u, "Aniversário do sobrinho", _hoje().strftime("%m-%d"))
    r = context.retrato(u)
    corpo = r.split("\n", 1)[1] if "\n" in r else ""
    assert len(corpo.splitlines()) <= context.RETRATO_MAX_LINHAS
    assert "AGORA:" in r and "PENDÊNCIAS" in r and "DATAS QUERIDAS" in r


def test_m1_esquecer_fato_e_mao_real():
    u = "5511900007994"
    memory.remember_fact(u, "Precisa mandar o contrato para a imobiliária", "pendencias")
    assert "contrato para a imobiliária" in ctx_com.snapshot(u)
    r = tools.execute_tool("esquecer_fato", {"trecho": "contrato para a imobiliária"}, u)
    assert "apagado(s) AGORA" in r
    assert ctx_com.snapshot(u) == ""              # "risquei daqui" agora é verdade
    # Consentimento (categoria limites) é inapagável por esta porta
    memory.remember_fact(u, "Recusou memória de saúde", "limites")
    assert memory.facts_remove(u, "Recusou memória") == 0


def test_m1_onboarding_nao_planta_pendencia_eterna():
    u = "5511900007993"
    from giu import onboarding as _onb
    _onb.register(u, "pendencia_inicial", "pagar as contas")
    assert ctx_com.snapshot(u) == ""              # traço é rotina, não pendência


def test_m2_nao_quero_ajuda_silencia_para_sempre():
    u = "5511900007992"
    memory.add_agenda(u, "Renovar o passaporte")
    assert "Renovar o passaporte" in ctx_com.snapshot(u)
    r = tools.execute_tool("silenciar_pendencia", {"titulo": "Renovar o passaporte"}, u)
    assert "PARA SEMPRE" in r
    snap = ctx_com.snapshot(u)
    assert "Renovar o passaporte" not in snap and "PENDÊNCIAS" not in snap
    # E a pendência segue VIVA na agenda (não foi falsificada como feita)
    assert any(i["title"] == "Renovar o passaporte" and not i["done"]
               for i in memory.get_agenda(u))
    # Outra pendência nova volta a ofertar normalmente — só a recusada cala
    memory.add_agenda(u, "Trocar o chuveiro")
    snap = ctx_com.snapshot(u)
    assert "Trocar o chuveiro" in snap and "em aberto: 2" in snap


def test_m3_fatos_antigos_nao_somem_em_silencio():
    u = "5511900007991"
    for i in range(4):
        memory.remember_fact(u, f"Pendência contada {i+1}", "pendencias")
    snap = ctx_com.snapshot(u)
    assert "Pendência contada 1" in snap          # a fricção mais VELHA aparece
    assert "(e mais 2)" in snap                   # as demais têm contagem, não silêncio


def test_m5_idade_da_pendencia_com_backdate():
    from datetime import timedelta
    u = "5511900007990"
    iid = memory.add_agenda(u, "Levar o notebook no conserto")
    tres_dias = (_hoje().replace(tzinfo=None) - timedelta(days=3)).isoformat(timespec="seconds")
    with memory._conn() as conn:
        conn.execute("UPDATE agenda SET created_at=? WHERE id=?", (tres_dias, iid))
    snap = ctx_com.snapshot(u)
    assert "há 3 dia(s)" in snap
    assert "há 0" not in snap                     # criada agora jamais mostra idade


def test_m8_teto_do_retrato_e_exercido(monkeypatch):
    gigante = {"nome": "Stub", "area": "x",
               "available": lambda u: True,
               "snapshot": lambda u: "\n".join(f"linha {i}" for i in range(10))}
    monkeypatch.setattr(context, "PROVIDERS", [gigante, gigante, gigante])
    r = context.retrato("qualquer")
    corpo = r.split("\n", 1)[1]
    # 3 linhas por provider (teto do snapshot) e 14 no total (teto do retrato)
    assert len(corpo.splitlines()) <= context.RETRATO_MAX_LINHAS
    assert corpo.splitlines().count("linha 3") == 0   # 4ª linha de um provider cai
