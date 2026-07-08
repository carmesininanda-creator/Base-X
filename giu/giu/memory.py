"""
Memória da Vida — o coração da Giu.

Três tipos de memória:
- Perfil:    quem é a pessoa (nome, pessoas importantes, preferências)
- Fatos:     memória semântica ("Nanda prefere resolver tudo por voz")
- Conversas: memória episódica (histórico de mensagens por canal)

Mais a Agenda Viva e os Lembretes, que são memória do futuro.
"""

import hashlib
import json
import secrets
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from . import config


def _conn():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS profile (
                user_id    TEXT PRIMARY KEY,
                name       TEXT,
                data       TEXT DEFAULT '{}',
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS facts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    TEXT NOT NULL,
                category   TEXT DEFAULT 'geral',
                content    TEXT NOT NULL,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS messages (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    TEXT NOT NULL,
                channel    TEXT DEFAULT 'web',
                role       TEXT NOT NULL,
                content    TEXT NOT NULL,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS agenda (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    TEXT NOT NULL,
                title      TEXT NOT NULL,
                date       TEXT,
                time       TEXT,
                notes      TEXT,
                done       INTEGER DEFAULT 0,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS reminders (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    TEXT NOT NULL,
                channel    TEXT DEFAULT 'web',
                text       TEXT NOT NULL,
                due_at     TEXT NOT NULL,
                sent       INTEGER DEFAULT 0,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS pending_actions (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      TEXT NOT NULL,
                type         TEXT NOT NULL,
                summary      TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                risk_level   TEXT DEFAULT 'baixo',
                status       TEXT DEFAULT 'pending',
                created_at   TEXT,
                confirmed_at TEXT,
                executed_at  TEXT
            );
            CREATE TABLE IF NOT EXISTS family_members (
                user_id           TEXT PRIMARY KEY,
                name              TEXT NOT NULL,
                role              TEXT DEFAULT 'member',
                status            TEXT DEFAULT 'invited',
                token_hash        TEXT NOT NULL,
                emergency_contact TEXT,
                welcome           TEXT,
                created_at        TEXT
            );
            CREATE TABLE IF NOT EXISTS processed_messages (
                channel_msg_id TEXT PRIMARY KEY,
                created_at     TEXT
            );
            CREATE TABLE IF NOT EXISTS missions (
                id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id            TEXT NOT NULL,
                objetivo           TEXT NOT NULL,
                contexto           TEXT,
                prioridade         TEXT DEFAULT 'normal',
                estado             TEXT DEFAULT 'aberta',
                proximo_passo      TEXT,
                criterio_conclusao TEXT,
                created_at         TEXT,
                updated_at         TEXT,
                concluded_at       TEXT
            );
            CREATE TABLE IF NOT EXISTS mission_events (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_id INTEGER NOT NULL,
                note       TEXT NOT NULL,
                created_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_missions_user ON missions(user_id, estado);
            CREATE INDEX IF NOT EXISTS idx_mission_events ON mission_events(mission_id, id);
            CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id, id);
            CREATE INDEX IF NOT EXISTS idx_facts_user ON facts(user_id, id);
            CREATE INDEX IF NOT EXISTS idx_reminders_due ON reminders(sent, due_at);
            CREATE INDEX IF NOT EXISTS idx_actions_user ON pending_actions(user_id, status);
        """)
        # Migrações leves: colunas adicionadas depois da criação original
        for stmt in (
            "ALTER TABLE family_members ADD COLUMN welcome TEXT",
            "ALTER TABLE reminders ADD COLUMN attempts INTEGER DEFAULT 0",
            "ALTER TABLE messages ADD COLUMN modality TEXT DEFAULT 'text'",
            "ALTER TABLE agenda ADD COLUMN lugar TEXT",      # T8 (Calendar/Mobility)
            "ALTER TABLE agenda ADD COLUMN duracao INTEGER",  # T9 (janela de conflito)
            "ALTER TABLE agenda ADD COLUMN cancelado INTEGER DEFAULT 0",  # cancelar ≠ concluir
            "ALTER TABLE reminders ADD COLUMN recorrencia TEXT",     # dito UMA vez
            "ALTER TABLE reminders ADD COLUMN disparos INTEGER DEFAULT 0",
        ):
            try:
                conn.execute(stmt)
            except sqlite3.OperationalError:
                pass  # coluna já existe


# ─── Deduplicação de mensagens do canal (bloqueador: webhook reenviado) ───────

def already_processed(channel_msg_id):
    """Registra o id da mensagem do canal e diz se ela JÁ havia sido processada.
    Idempotente: a Meta reenvia webhooks; isto impede fato/ação em dobro."""
    if not channel_msg_id:
        return False
    with _conn() as conn:
        try:
            conn.execute(
                "INSERT INTO processed_messages (channel_msg_id, created_at) VALUES (?,?)",
                (channel_msg_id, _now()),
            )
            return False
        except sqlite3.IntegrityError:
            return True  # já existia → duplicata


def _now():
    """Agora no fuso configurado, salvo como horário local naive (comparável por string)."""
    return datetime.now(ZoneInfo(config.TIMEZONE)).replace(tzinfo=None).isoformat(timespec="seconds")


# ─── Perfil ───────────────────────────────────────────────────────────────────

def get_profile(user_id):
    with _conn() as conn:
        row = conn.execute("SELECT * FROM profile WHERE user_id=?", (user_id,)).fetchone()
    if not row:
        return {"user_id": user_id, "name": None, "data": {}}
    return {"user_id": row["user_id"], "name": row["name"], "data": json.loads(row["data"] or "{}")}


def set_profile(user_id, name=None, **data):
    profile = get_profile(user_id)
    name = name or profile["name"]
    merged = {**profile["data"], **data}
    with _conn() as conn:
        conn.execute(
            """INSERT INTO profile (user_id, name, data, created_at) VALUES (?,?,?,?)
               ON CONFLICT(user_id) DO UPDATE SET name=excluded.name, data=excluded.data""",
            (user_id, name, json.dumps(merged, ensure_ascii=False), _now()),
        )


# ─── Fatos (memória semântica) ────────────────────────────────────────────────

def remember_fact(user_id, content, category="geral"):
    # Portão de consentimento: se a pessoa recusou/revogou, não guardamos
    # preferências. A categoria 'limites' (registros de consentimento/permissão)
    # é sempre gravada — é a prova governamental da própria recusa.
    if category != "limites":
        profile = get_profile(user_id)
        if profile["data"].get("consentimento") is False:
            return False
    with _conn() as conn:
        conn.execute(
            "INSERT INTO facts (user_id, category, content, created_at) VALUES (?,?,?,?)",
            (user_id, category, content, _now()),
        )
    return True


def get_facts(user_id, limit=40):
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, category, content FROM facts WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return [{"id": r["id"], "category": r["category"], "content": r["content"]} for r in reversed(rows)]


def facts_remove(user_id, trecho):
    """'Esquece isso' e 'já resolvi' precisam de mão real (M1 da Life
    Architect): apaga fatos cujo conteúdo contém o trecho. A categoria
    'limites' (provas de consentimento) é INAPAGÁVEL por aqui. Retorna
    quantos saíram."""
    alvo = (trecho or "").strip().lower()
    if len(alvo) < 3:
        return 0  # trecho curto demais apagaria a memória errada
    with _conn() as conn:
        cur = conn.execute(
            "DELETE FROM facts WHERE user_id=? AND category != 'limites' "
            "AND lower(content) LIKE ?",
            (user_id, f"%{alvo}%"),
        )
        return cur.rowcount


def pendencia_recusar(user_id, titulo):
    """M2 da Life Architect: o 'não quero ajuda' ganha memória DURÁVEL.
    A pendência continua viva (ver_agenda) — só a OFERTA silencia para
    sempre; a pessoa reabre quando quiser."""
    titulo = (titulo or "").strip().lower()
    if not titulo:
        return False
    recusadas = set(get_profile(user_id)["data"].get("pendencias_recusadas", []))
    recusadas.add(titulo)
    set_profile(user_id, pendencias_recusadas=sorted(recusadas))
    return True


def pendencias_recusadas(user_id):
    return set(get_profile(user_id)["data"].get("pendencias_recusadas", []))


def delete_fact(user_id, fact_id):
    with _conn() as conn:
        cur = conn.execute("DELETE FROM facts WHERE user_id=? AND id=?", (user_id, fact_id))
        return cur.rowcount > 0


def forget_user(user_id):
    """Apagamento total dos dados pessoais desta pessoa — 'apagou, sumiu' de
    verdade: fatos, conversas, agenda, lembretes, ações pendentes E o perfil
    (nome, consentimento, permissões, preferências). Não toca o cadastro de
    membro (isso é remoção de membro, feita à parte). Após isto, a pessoa
    recomeça do zero, inclusive o onboarding."""
    counts = {}
    with _conn() as conn:
        for table in ("facts", "messages", "agenda", "reminders", "pending_actions", "profile"):
            cur = conn.execute(f"DELETE FROM {table} WHERE user_id=?", (user_id,))
            counts[table] = cur.rowcount
    return counts


def search_facts(user_id, query, limit=10):
    with _conn() as conn:
        rows = conn.execute(
            "SELECT category, content FROM facts WHERE user_id=? AND content LIKE ? ORDER BY id DESC LIMIT ?",
            (user_id, f"%{query}%", limit),
        ).fetchall()
    return [{"category": r["category"], "content": r["content"]} for r in rows]


# ─── Conversas (memória episódica) ────────────────────────────────────────────

def save_message(user_id, role, content, channel="web", modality="text"):
    """Registra uma mensagem. modality='voice' marca que o turno foi por voz
    (o canal continua 'whatsapp' para o roteamento de push não quebrar)."""
    with _conn() as conn:
        conn.execute(
            "INSERT INTO messages (user_id, channel, role, content, created_at, modality) VALUES (?,?,?,?,?,?)",
            (user_id, channel, role, content, _now(), modality),
        )


def last_modality(user_id):
    """Modalidade da última mensagem DA PESSOA (voice/text) — para a Giu saber
    se a última interação foi por voz."""
    with _conn() as conn:
        row = conn.execute(
            "SELECT modality FROM messages WHERE user_id=? AND role='user' ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()
    return row["modality"] if row else "text"


def voice_pref(user_id):
    """Preferência de MODALIDADE de resposta, escolhida pela pessoa (não pelo
    sistema): 'voice' | 'text' | 'both' | None (ainda não escolheu). Guardada no
    perfil e consultada de forma DETERMINÍSTICA no envio — não depende do modelo,
    para que 'me responde só por escrito' seja cumprido 100% das vezes."""
    return get_profile(user_id)["data"].get("voice_pref")


# ─── Life Connector: Google (conexão POR PESSOA — opt-in, revogável) ─────────

def google_connect(user_id, refresh_token):
    set_profile(user_id, google_refresh_token=refresh_token)


def google_token(user_id):
    return get_profile(user_id)["data"].get("google_refresh_token")


def google_disconnect(user_id):
    """Revogação imediata e determinística — 'desconecta minha agenda' é lei."""
    set_profile(user_id, google_refresh_token=None)


def oauth_state_new(user_id):
    """Estado de uso único para o link de consentimento (validade 15 min)."""
    token = secrets.token_urlsafe(24)
    set_profile(user_id, oauth_state=token, oauth_state_at=_now())
    return f"{user_id}.{token}"


def oauth_state_take(state):
    """Valida e CONSOME o estado (uso único). Retorna o user_id ou None."""
    from datetime import timedelta
    if not state or "." not in state:
        return None
    user_id, token = state.split(".", 1)
    data = get_profile(user_id)["data"]
    if not token or data.get("oauth_state") != token:
        return None
    emitido = data.get("oauth_state_at", "")
    limite = (datetime.now(ZoneInfo(config.TIMEZONE)).replace(tzinfo=None)
              - timedelta(minutes=15)).isoformat(timespec="seconds")
    set_profile(user_id, oauth_state=None)  # consome SEMPRE (uso único)
    if emitido < limite:
        return None  # expirado
    return user_id


# ─── Datas queridas e cidade (Time Provider — Living Context, Fase 2) ────────

def dates_add(user_id, titulo, data, recorrente=None, origem=None):
    """Guarda uma data que a PESSOA pediu para lembrar (aniversário, evento).
    data: 'MM-DD' (SEMPRE anual) ou 'YYYY-MM-DD' (única por padrão; recorrente
    =True explícito a torna anual — aniversário com ano conhecido). A
    recorrência deriva do formato (T2 da Life Architect): data única de ano
    passado JAMAIS volta a acordar; 'MM-DD' jamais morre muda. Respeita o
    mesmo portão de consentimento da memória."""
    titulo = (titulo or "").strip()
    data = (data or "").strip()
    if not titulo or not data:
        return False
    try:  # validação real, em ano BISSEXTO — 29/02 é aniversário como qualquer
        if len(data) == 5:  # (T1 da Life Architect)
            datetime.strptime(f"2000-{data}", "%Y-%m-%d")
            recorrente = True                      # MM-DD é anual por definição
        else:
            datetime.strptime(data, "%Y-%m-%d")
            recorrente = bool(recorrente)          # única, salvo pedido explícito
    except ValueError:
        return False
    profile = get_profile(user_id)
    if profile["data"].get("consentimento") is False:
        return False
    datas = [d for d in profile["data"].get("datas", [])
             if not (d.get("titulo") == titulo and d.get("data") == data)]
    nova = {"titulo": titulo[:120], "data": data, "recorrente": recorrente}
    if origem:
        nova["origem"] = origem  # 'semeada' = veio do cadastro, não da pessoa (S2)
    datas.append(nova)
    set_profile(user_id, datas=datas[-40:])
    return True


def dates_all(user_id):
    return get_profile(user_id)["data"].get("datas", [])


def dates_remove(user_id, titulo):
    """'Esquece essa data' tem a mesma dignidade de 'esquece minha cidade':
    remoção imediata pelo título (T3 da Life Architect). Retorna quantas saíram."""
    alvo = (titulo or "").strip().lower()
    if not alvo:
        return 0
    datas = dates_all(user_id)
    vivas = [d for d in datas if alvo not in d.get("titulo", "").lower()]
    if len(vivas) == len(datas):
        return 0
    set_profile(user_id, datas=vivas)
    return len(datas) - len(vivas)


def city_set(user_id, nome, lat=None, lon=None):
    """Cidade AUTORIZADA pela pessoa (nível cidade, nunca localização precisa)
    — permite clima e sol no retrato. Opt-in explícito, revogável (city_clear).
    Respeita o portão de consentimento (T6): recusa de memória vale para a
    cidade também."""
    if get_profile(user_id)["data"].get("consentimento") is False:
        return False
    set_profile(user_id, cidade={"nome": nome, "lat": lat, "lon": lon})
    return True


def city_get(user_id):
    return get_profile(user_id)["data"].get("cidade")


def city_clear(user_id):
    """Revogação imediata e determinística — 'esquece minha cidade' é lei."""
    set_profile(user_id, cidade=None)


# ─── Conversation Spine (a espinha da conversa ATUAL — não é memória de longo
#     prazo: fatos permanentes continuam em remember_fact; a spine expira) ─────

SPINE_TTL_HOURS = 24
SPINE_MAX = 10


def spine_add(user_id, note):
    """Anota um item no fio da conversa atual (decisão, insight, mudança de
    direção, compromisso). Vive no perfil, expira em SPINE_TTL_HOURS e guarda
    só os últimos SPINE_MAX — é continuidade, não arquivo."""
    note = (note or "").strip()
    if not note:
        return False
    spine = spine_get(user_id)  # já filtrada por validade
    spine.append({"t": _now(), "note": note[:300]})
    set_profile(user_id, spine=spine[-SPINE_MAX:])
    return True


def spine_get(user_id):
    """Itens vivos do fio da conversa atual (ordem cronológica). Itens mais
    velhos que SPINE_TTL_HOURS caem — a espinha é da conversa, não da vida."""
    from datetime import timedelta
    raw = get_profile(user_id)["data"].get("spine", [])
    cutoff = (datetime.now(ZoneInfo(config.TIMEZONE)).replace(tzinfo=None)
              - timedelta(hours=SPINE_TTL_HOURS)).isoformat(timespec="seconds")
    return [x for x in raw if isinstance(x, dict) and x.get("t", "") >= cutoff][-SPINE_MAX:]


def get_history(user_id, limit=16):
    with _conn() as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


def message_count(user_id):
    with _conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM messages WHERE user_id=?", (user_id,)).fetchone()[0]


# ─── Agenda Viva ──────────────────────────────────────────────────────────────

def add_agenda(user_id, title, date=None, time=None, notes=None,
               lugar=None, duracao=None):
    """duracao em minutos (opcional): habilita o conflito por sobreposição
    real (T9); lugar (opcional): o 'onde' que a Mobilidade vai precisar (T8)."""
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO agenda (user_id, title, date, time, notes, lugar, duracao, created_at)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (user_id, title, date, time, notes, lugar, duracao, _now()),
        )
        return cur.lastrowid


def get_agenda(user_id, include_done=False):
    sql = ("SELECT id, title, date, time, notes, done, created_at, lugar, duracao "
           "FROM agenda WHERE user_id=? AND COALESCE(cancelado,0)=0")
    if not include_done:
        sql += " AND done=0"
    sql += " ORDER BY date IS NULL, date, time"
    with _conn() as conn:
        rows = conn.execute(sql, (user_id,)).fetchall()
    return [dict(r) for r in rows]


def reschedule_agenda(user_id, item_id, date=None, time=None, lugar=None, duracao=None):
    """Remarca um compromisso — a vida remarca o tempo todo; a Giu acompanha.
    Só altera os campos informados. Retorna o item novo ou None."""
    sets, vals = [], []
    for campo, valor in (("date", date), ("time", time), ("lugar", lugar), ("duracao", duracao)):
        if valor is not None:
            sets.append(f"{campo}=?"); vals.append(valor)
    if not sets:
        return None
    with _conn() as conn:
        cur = conn.execute(
            f"UPDATE agenda SET {', '.join(sets)} WHERE user_id=? AND id=? "
            "AND done=0 AND COALESCE(cancelado,0)=0",
            (*vals, user_id, item_id),
        )
        if cur.rowcount == 0:
            return None
        row = conn.execute("SELECT id, title, date, time, lugar FROM agenda WHERE id=?",
                           (item_id,)).fetchone()
        return dict(row)


def cancel_agenda(user_id, item_id):
    """Cancela um compromisso — HONESTAMENTE: cancelado nunca vira 'feito'
    (a lei do M2 vale aqui também). O registro permanece, fora do retrato."""
    with _conn() as conn:
        cur = conn.execute(
            "UPDATE agenda SET cancelado=1 WHERE user_id=? AND id=? AND done=0",
            (user_id, item_id),
        )
        return cur.rowcount > 0


def complete_agenda(user_id, item_id):
    with _conn() as conn:
        cur = conn.execute("UPDATE agenda SET done=1 WHERE user_id=? AND id=?", (user_id, item_id))
        return cur.rowcount > 0


# ─── Lembretes ────────────────────────────────────────────────────────────────

RECORRENCIAS_VALIDAS = ("diario", "semanal", "mensal")  # + "dias:..." e "mensal:<dia>"
_DIAS_SEMANA_IDX = {"seg": 0, "ter": 1, "qua": 2, "qui": 3, "sex": 4, "sab": 5, "dom": 6}
# A cada N disparos, UMA pergunta gentil de re-consentimento (cerca da Life
# Architect: ignorar ocorrências gera pergunta, nunca insistência)
_PULSO_RECONSENTIMENTO = {"diario": 14, "semanal": 4, "mensal": 3, "dias": 10}


def recorrencia_valida(recorrencia):
    if not recorrencia:
        return True
    if recorrencia in RECORRENCIAS_VALIDAS:
        return True
    if recorrencia.startswith("mensal:"):
        try:
            return 1 <= int(recorrencia[7:]) <= 31
        except ValueError:
            return False
    if recorrencia.startswith("dias:"):
        dias = [d.strip() for d in recorrencia[5:].split(",") if d.strip()]
        return bool(dias) and all(d in _DIAS_SEMANA_IDX for d in dias)
    return False


def proxima_ocorrencia(due_iso, recorrencia, agora_iso=None):
    """A próxima vez, avançando a partir de max(due, agora) — reiniciar o
    serviço nunca gera enxurrada de lembretes atrasados."""
    from datetime import timedelta
    base = datetime.fromisoformat(due_iso)
    agora = datetime.fromisoformat(agora_iso) if agora_iso else datetime.fromisoformat(_now())
    ancora = max(base, agora)
    if recorrencia == "diario":
        prox = ancora + timedelta(days=1)
        return prox.replace(hour=base.hour, minute=base.minute,
                            second=0, microsecond=0).isoformat(timespec="seconds")
    if recorrencia == "semanal":
        prox = ancora + timedelta(days=7 - ((ancora.weekday() - base.weekday()) % 7) or 7)
        return prox.replace(hour=base.hour, minute=base.minute,
                            second=0, microsecond=0).isoformat(timespec="seconds")
    if recorrencia == "mensal" or (recorrencia and recorrencia.startswith("mensal:")):
        # R2: o dia-alvo é PERSISTIDO ("mensal:31") — 31/jan→28/fev→31/MAR,
        # nunca "28 para sempre"; e a âncora no agora não pula meses
        alvo = int(recorrencia[7:]) if recorrencia.startswith("mensal:") else base.day
        ano, mes = ancora.year, ancora.month + 1
        if mes > 12:
            ano, mes = ano + 1, 1
        import calendar as _cal
        dia = min(alvo, _cal.monthrange(ano, mes)[1])  # 31 → último do mês curto
        return base.replace(year=ano, month=mes, day=dia).isoformat(timespec="seconds")
    if recorrencia and recorrencia.startswith("dias:"):
        alvos = sorted(_DIAS_SEMANA_IDX[d.strip()] for d in recorrencia[5:].split(","))
        for delta in range(1, 8):
            cand = ancora + timedelta(days=delta)
            if cand.weekday() in alvos:
                return cand.replace(hour=base.hour, minute=base.minute,
                                    second=0, microsecond=0).isoformat(timespec="seconds")
    return None


def add_reminder(user_id, text, due_at, channel="web", recorrencia=None):
    """recorrencia: None (única) | 'diario' | 'semanal' | 'mensal' |
    'dias:seg,qua,sex' — dito UMA vez, cuidado para sempre; parar é uma frase."""
    if not recorrencia_valida(recorrencia):
        recorrencia = None  # nunca grava lixo — vira lembrete único
    if recorrencia == "mensal":  # R2: congela o dia-alvo do mês na criação
        recorrencia = f"mensal:{datetime.fromisoformat(due_at).day}"
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO reminders (user_id, channel, text, due_at, created_at, recorrencia)"
            " VALUES (?,?,?,?,?,?)",
            (user_id, channel, text, due_at, _now(), recorrencia),
        )
        return cur.lastrowid


def due_reminders():
    """Lembretes vencidos e ainda não enviados — usados pelo scheduler."""
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, user_id, channel, text, due_at, recorrencia, disparos "
            "FROM reminders WHERE sent=0 AND due_at <= ?",
            (_now(),),
        ).fetchall()
    return [dict(r) for r in rows]


_PERIODO_DIAS = {"diario": 1, "dias": 2, "semanal": 7, "mensal": 30}


def atraso_grave(reminder, agora_iso=None):
    """Outage multi-dia: se o lembrete recorrente está atrasado mais de 1,5
    período, ocorrências intermediárias NÃO saíram — a Giu conta (R5: o
    silêncio sobre o pulo fere a honestidade que o projeto inteiro tem)."""
    recorrencia = reminder.get("recorrencia")
    if not recorrencia:
        return ""
    from datetime import timedelta
    agora = datetime.fromisoformat(agora_iso) if agora_iso else datetime.fromisoformat(_now())
    devido = datetime.fromisoformat(reminder["due_at"])
    periodo = _PERIODO_DIAS.get(recorrencia.split(":")[0], 7)
    if agora - devido > timedelta(days=periodo * 1.5):
        return ("\n(Fiquei um tempo fora do ar e algumas vezes deste lembrete "
                "não saíram — me desculpa. Já voltei a cuidar.)")
    return ""


def pulso_devido(reminder):
    """Pré-envio (só leitura): é a vez da pergunta gentil de re-consentimento?
    A linha viaja NA PRÓPRIA mensagem — nunca uma mensagem extra de cobrança."""
    recorrencia = reminder.get("recorrencia")
    if not recorrencia:
        return ""
    chave = recorrencia.split(":")[0]
    pulso = _PULSO_RECONSENTIMENTO.get(chave, 10)
    proximo_disparo = (reminder.get("disparos") or 0) + 1
    if proximo_disparo % pulso == 0:
        return ("\n(Sigo te lembrando disso com carinho — se não fizer mais "
                "sentido, é só dizer \"pode parar\" que eu paro na hora.)")
    return ""


def reminder_delivered(reminder):
    """Entrega registrada: o único morre (sent=1); o RECORRENTE se rearma
    para a próxima ocorrência — dito uma vez, cuidado para sempre."""
    rid = reminder["id"]
    recorrencia = reminder.get("recorrencia")
    with _conn() as conn:
        conn.execute("UPDATE reminders SET disparos = COALESCE(disparos,0)+1, attempts=0 "
                     "WHERE id=?", (rid,))
        if not recorrencia:
            conn.execute("UPDATE reminders SET sent=1 WHERE id=?", (rid,))
            return
        proxima = proxima_ocorrencia(reminder["due_at"], recorrencia)
        if proxima:
            conn.execute("UPDATE reminders SET due_at=? WHERE id=?", (proxima, rid))
        else:
            conn.execute("UPDATE reminders SET sent=1 WHERE id=?", (rid,))


def reminders_stop(user_id, trecho):
    """'Pode parar' é lei: encerra na hora os lembretes ativos que contêm o
    trecho — tão fácil quanto criar. Devolve OS TEXTOS parados (R4: a Giu
    nomeia o que parou e pode devolver o que parou por engano). Zero culpa."""
    alvo = (trecho or "").strip().lower()
    if len(alvo) < 3:
        return []
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, text FROM reminders WHERE user_id=? AND sent=0 "
            "AND lower(text) LIKE ?",
            (user_id, f"%{alvo}%"),
        ).fetchall()
        if rows:
            conn.execute(
                f"UPDATE reminders SET sent=1 WHERE id IN ({','.join('?'*len(rows))})",
                [r["id"] for r in rows],
            )
        return [r["text"] for r in rows]


def mark_reminder_sent(reminder_id):
    with _conn() as conn:
        conn.execute("UPDATE reminders SET sent=1 WHERE id=?", (reminder_id,))


def mark_reminder_failed(reminder_id, max_attempts=5):
    """Conta uma tentativa falha. Após max_attempts: o lembrete ÚNICO encerra
    (sent=1, impede loop infinito); o RECORRENTE jamais morre por falha de
    entrega (R1 da Life Architect: a janela de 24h fechada mataria o remédio
    da mãe em 5 minutos, para sempre, em silêncio) — ele PULA a ocorrência,
    rearma para a próxima e zera as tentativas. Retorna True só na
    desistência definitiva (único)."""
    with _conn() as conn:
        conn.execute("UPDATE reminders SET attempts = attempts + 1 WHERE id=?", (reminder_id,))
        row = conn.execute(
            "SELECT attempts, recorrencia, due_at FROM reminders WHERE id=?",
            (reminder_id,),
        ).fetchone()
        if row and row["attempts"] >= max_attempts:
            if row["recorrencia"]:
                proxima = proxima_ocorrencia(row["due_at"], row["recorrencia"])
                if proxima:
                    conn.execute(
                        "UPDATE reminders SET due_at=?, attempts=0 WHERE id=?",
                        (proxima, reminder_id),
                    )
                    return False  # pulou a ocorrência; o cuidado continua vivo
            conn.execute("UPDATE reminders SET sent=1 WHERE id=?", (reminder_id,))
            return True  # desistiu (só o único)
    return False


def reminders_today(user_id):
    """Lembretes ainda não enviados com vencimento hoje."""
    today = _now()[:10]
    with _conn() as conn:
        rows = conn.execute(
            "SELECT text, due_at FROM reminders WHERE user_id=? AND sent=0 AND substr(due_at,1,10)=?",
            (user_id, today),
        ).fetchall()
    return [dict(r) for r in rows]


# ─── Missões (Mission Engine — intenção que vira cuidado acompanhado) ─────────
# O motor NÃO referencia nenhum conector: uma missão carrega objetivo, contexto
# e próximos passos; quando Life Connectors existirem, eles executarão passos
# pela escada de autorização de sempre — sem alterar nada aqui (preparação
# arquitetural exigida pela fundadora).

MISSION_OPEN_STATES = ("aberta", "em_andamento", "aguardando")


def mission_create(user_id, objetivo, contexto=None, prioridade="normal",
                   proximo_passo=None, criterio_conclusao=None):
    """Abre uma missão (os 7 campos da fundadora: objetivo, contexto,
    prioridade, estado, histórico, próximos passos, critério de conclusão)."""
    now = _now()
    with _conn() as conn:
        cur = conn.execute(
            """INSERT INTO missions (user_id, objetivo, contexto, prioridade, estado,
                                     proximo_passo, criterio_conclusao, created_at, updated_at)
               VALUES (?,?,?,?,'aberta',?,?,?,?)""",
            (user_id, objetivo, contexto, prioridade, proximo_passo, criterio_conclusao, now, now),
        )
        mid = cur.lastrowid
        conn.execute(
            "INSERT INTO mission_events (mission_id, note, created_at) VALUES (?,?,?)",
            (mid, f"Missão aberta: {objetivo}", now),
        )
        return mid


def mission_get(user_id, mission_id):
    """Missão da PRÓPRIA pessoa (isolamento por user_id), com histórico."""
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM missions WHERE user_id=? AND id=?", (user_id, mission_id)
        ).fetchone()
        if not row:
            return None
        mission = dict(row)
        mission["events"] = [
            dict(e) for e in conn.execute(
                "SELECT note, created_at FROM mission_events WHERE mission_id=? ORDER BY id",
                (mission_id,),
            ).fetchall()
        ]
        return mission


def missions_open(user_id):
    """Missões vivas da pessoa (abertas/em andamento/aguardando), mais antigas primeiro."""
    marks = ",".join("?" * len(MISSION_OPEN_STATES))
    with _conn() as conn:
        rows = conn.execute(
            f"SELECT id, objetivo, contexto, prioridade, estado, proximo_passo, criterio_conclusao "
            f"FROM missions WHERE user_id=? AND estado IN ({marks}) ORDER BY id",
            (user_id, *MISSION_OPEN_STATES),
        ).fetchall()
    return [dict(r) for r in rows]


def mission_update(user_id, mission_id, nota=None, proximo_passo=None,
                   estado=None, prioridade=None):
    """Atualiza a missão e registra no histórico. Nota é permitida mesmo em
    missão concluída (é assim que a resposta de VIDA entra depois do fim)."""
    mission = mission_get(user_id, mission_id)
    if not mission:
        return False
    now = _now()
    with _conn() as conn:
        sets, vals = ["updated_at=?"], [now]
        if proximo_passo is not None:
            sets.append("proximo_passo=?"); vals.append(proximo_passo)
        if estado in MISSION_OPEN_STATES:
            sets.append("estado=?"); vals.append(estado)
        if prioridade in ("baixa", "normal", "alta"):
            sets.append("prioridade=?"); vals.append(prioridade)
        conn.execute(f"UPDATE missions SET {', '.join(sets)} WHERE user_id=? AND id=?",
                     (*vals, user_id, mission_id))
        if nota:
            conn.execute(
                "INSERT INTO mission_events (mission_id, note, created_at) VALUES (?,?,?)",
                (mission_id, nota[:400], now),
            )
    return True


def missions_awaiting_life(user_id, days=7):
    """Concluídas recentes ainda SEM nota 'VIDA:' — a pergunta de vida não pode
    depender da janela de contexto (dívida M1 da Life Architect). Após `days`
    dias, sai da lista: perguntar tarde demais vira estranheza, não cuidado."""
    from datetime import timedelta
    cutoff = (datetime.now(ZoneInfo(config.TIMEZONE)).replace(tzinfo=None)
              - timedelta(days=days)).isoformat(timespec="seconds")
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, objetivo, concluded_at FROM missions "
            "WHERE user_id=? AND estado='concluida' AND concluded_at >= ? ORDER BY id",
            (user_id, cutoff),
        ).fetchall()
        out = []
        for r in rows:
            tem_vida = conn.execute(
                "SELECT 1 FROM mission_events WHERE mission_id=? AND note LIKE 'VIDA:%' LIMIT 1",
                (r["id"],),
            ).fetchone()
            if not tem_vida:
                out.append(dict(r))
    return out


def mission_conclude(user_id, mission_id, resultado):
    """Fecha a missão com o resultado. Toda conclusão é material da Life
    Architect: a pergunta que mede o cuidado é feita NA CONVERSA depois."""
    mission = mission_get(user_id, mission_id)
    if not mission:
        return False
    now = _now()
    with _conn() as conn:
        conn.execute(
            "UPDATE missions SET estado='concluida', concluded_at=?, updated_at=? WHERE user_id=? AND id=?",
            (now, now, user_id, mission_id),
        )
        conn.execute(
            "INSERT INTO mission_events (mission_id, note, created_at) VALUES (?,?,?)",
            (mission_id, f"CONCLUÍDA: {resultado}"[:400], now),
        )
    return True


# ─── Semear a vida (CC5 — decisão da fundadora: identidade + VIDA) ───────────

SEED_CATEGORIAS = {
    "pessoas": ("familia", None),
    "projetos": ("geral", "projeto atual"),
    "objetivos": ("geral", "objetivo"),
    "rotina": ("rotina", None),
    "preferencias": ("preferencias", None),
    "contexto": ("geral", None),
    "friccoes": ("rotina", "fricção conhecida"),
    # Ampliação da fundadora: "quem a pessoa é, o que ama, o que sonha"
    "interesses": ("preferencias", "interesse"),
    "sonhos": ("geral", "sonho declarado (hipótese viva)"),
    "desafios": ("rotina", "desafio (cuidar sem julgamento)"),
}


def seed_life(user_id, vida):
    """Semeia a VIDA de um membro no cadastro (pessoas importantes, projetos,
    objetivos, rotina, preferências, contexto, fricções conhecidas, datas).
    "Não quero apenas identidade. Quero identidade + vida." — a base sobre a
    qual a Giulieta aprende continuamente.

    HONESTIDADE ARQUITETURAL: fatos semeados levam o marcador '[de partida]'
    — a Giu sabe que vieram do cadastro da família (hipótese de contexto),
    NUNCA 'você me contou'. O que a pessoa mostrar vivendo prevalece e
    substitui. Respeita o portão de consentimento; deduplica por conteúdo;
    retorna quantos itens entraram."""
    if get_profile(user_id)["data"].get("consentimento") is False:
        return 0

    def _ja_existe(content):  # dedupe por SQL (S7): não depende de limite de leitura
        with _conn() as conn:
            return conn.execute("SELECT 1 FROM facts WHERE user_id=? AND content=? LIMIT 1",
                                (user_id, content)).fetchone() is not None

    plantados = 0
    for chave, (categoria, rotulo) in SEED_CATEGORIAS.items():
        for item in (vida.get(chave) or []):
            item = (item or "").strip()
            if not item:
                continue
            content = f"[de partida] {rotulo + ': ' if rotulo else ''}{item}"
            if _ja_existe(content):
                continue
            if remember_fact(user_id, content, categoria):
                plantados += 1
    ja = {(d.get("titulo"), d.get("data")) for d in dates_all(user_id)}
    for d in (vida.get("datas") or []):
        titulo = (d.get("titulo") or "").strip()[:120]  # compara já truncado (S7)
        data = (d.get("data") or "").strip()
        if (titulo, data) in ja:
            continue
        if dates_add(user_id, titulo, data, d.get("recorrente"), origem="semeada"):
            plantados += 1  # datas levam origem (S2): o retrato nunca mente o dono
    return plantados


def seed_purge(user_id):
    """S1 da Life Architect: o "não" da pessoa EXPURGA o semeio inteiro — fatos
    '[de partida]' e datas de origem semeada somem na hora. Dados sobre você,
    fornecidos por terceiros, jamais sobrevivem à sua recusa."""
    fatos = facts_remove(user_id, "[de partida]")
    datas = dates_all(user_id)
    vivas = [d for d in datas if d.get("origem") != "semeada"]
    if len(vivas) != len(datas):
        set_profile(user_id, datas=vivas)
    return fatos + (len(datas) - len(vivas))


# ─── Família (identidade e confidencialidade) ─────────────────────────────────

def _hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


def add_member(user_id, name, role="member", emergency_contact=None, welcome=None):
    """Registra um membro da família. Retorna o token pessoal (mostrado UMA vez).
    Sem texto explícito de boas-vindas, aplica a abertura do Relationship
    Blueprint pelo nome (welcomes.py) — o primeiro encontro é personalizado;
    um welcome passado explicitamente sempre tem prioridade.
    IDENTIDADE SEMEADA: membro com Blueprint nasce com o apelido conhecido no
    perfil e a etapa 'nome' do onboarding concluída — a Giu não pergunta o que
    já sabe. Se a própria pessoa já escolheu um nome, o recadastro NÃO mexe."""
    if welcome is None:
        from . import welcomes
        welcome = welcomes.welcome_for(name)
    from . import blueprints
    apelido = blueprints.preferred_name(name)
    token = secrets.token_urlsafe(32)
    with _conn() as conn:
        conn.execute(
            """INSERT INTO family_members (user_id, name, role, status, token_hash, emergency_contact, welcome, created_at)
               VALUES (?,?,?,?,?,?,?,?)
               ON CONFLICT(user_id) DO UPDATE SET name=excluded.name, role=excluded.role,
                 emergency_contact=excluded.emergency_contact, welcome=excluded.welcome""",
            (user_id, name, role, "invited", _hash_token(token), emergency_contact, welcome, _now()),
        )
    if apelido:
        profile = get_profile(user_id)
        if not profile["name"]:  # nunca sobrescreve um nome que a pessoa escolheu
            done = profile["data"].get("onboarding", {})
            done["nome"] = True
            set_profile(user_id, name=apelido, onboarding=done)
    return token


def get_member(user_id):
    with _conn() as conn:
        row = conn.execute(
            "SELECT user_id, name, role, status, emergency_contact, welcome FROM family_members WHERE user_id=?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def get_member_by_name(name):
    with _conn() as conn:
        row = conn.execute(
            "SELECT user_id, name, role, status, emergency_contact FROM family_members "
            "WHERE lower(name)=lower(?)",
            (name,),
        ).fetchone()
    return dict(row) if row else None


def get_member_by_token(token):
    with _conn() as conn:
        row = conn.execute(
            "SELECT user_id, name, role, status, emergency_contact FROM family_members WHERE token_hash=?",
            (_hash_token(token),),
        ).fetchone()
    return dict(row) if row else None


def list_members():
    """Cadastro da família — sem tokens, sem memória de ninguém."""
    with _conn() as conn:
        rows = conn.execute(
            "SELECT user_id, name, role, status, emergency_contact, created_at FROM family_members ORDER BY created_at"
        ).fetchall()
    return [dict(r) for r in rows]


def activate_member(user_id):
    with _conn() as conn:
        conn.execute("UPDATE family_members SET status='active' WHERE user_id=?", (user_id,))


def remove_member(user_id):
    with _conn() as conn:
        cur = conn.execute("DELETE FROM family_members WHERE user_id=?", (user_id,))
        return cur.rowcount > 0


def last_push_channel(user_id):
    """Canal com push da última conversa desta pessoa (para entregar recados)."""
    with _conn() as conn:
        row = conn.execute(
            "SELECT channel FROM messages WHERE user_id=? AND channel IN ('whatsapp','telegram') "
            "ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()
    return row["channel"] if row else None


def push_users():
    """Usuários alcançáveis proativamente: (user_id, canal da última conversa com push)."""
    with _conn() as conn:
        rows = conn.execute(
            "SELECT user_id, channel FROM messages WHERE id IN ("
            "  SELECT MAX(id) FROM messages WHERE channel IN ('whatsapp','telegram') GROUP BY user_id"
            ")"
        ).fetchall()
    return [(r["user_id"], r["channel"]) for r in rows]


# ─── Ações Pendentes (execução com autorização real) ──────────────────────────

def add_pending_action(user_id, action_type, summary, payload, risk_level="baixo"):
    with _conn() as conn:
        cur = conn.execute(
            """INSERT INTO pending_actions (user_id, type, summary, payload_json, risk_level, created_at)
               VALUES (?,?,?,?,?,?)""",
            (user_id, action_type, summary, json.dumps(payload, ensure_ascii=False), risk_level, _now()),
        )
        return cur.lastrowid


def get_pending_action(user_id, action_id):
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM pending_actions WHERE user_id=? AND id=?", (user_id, action_id)
        ).fetchone()
    if not row:
        return None
    action = dict(row)
    action["payload"] = json.loads(action.pop("payload_json"))
    return action


def list_pending_actions(user_id):
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, type, summary, risk_level, created_at FROM pending_actions "
            "WHERE user_id=? AND status='pending' ORDER BY id",
            (user_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def mark_action_executed(user_id, action_id):
    now = _now()
    with _conn() as conn:
        conn.execute(
            "UPDATE pending_actions SET status='executed', confirmed_at=?, executed_at=? "
            "WHERE user_id=? AND id=?",
            (now, now, user_id, action_id),
        )
