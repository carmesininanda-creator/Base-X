"""
✉️ Communication Provider — a mecânica do domínio 5 (Comunicação) das
Capacidades de Vida.

Domínio (decisão da fundadora, ampliado em 08/07/2026): TODA comunicação
relevante da vida da pessoa — e-mail, mensagens, documentos, notificações
importantes — não apenas Gmail. Fricção que reduz: a pendência que cobra
silenciosamente da cabeça; o convite que expira; o documento esperado.

Piso interno (zero conector): o que a PESSOA conta — pendências guardadas na
agenda sem data (o "preciso resolver X" que não tem dia) e fatos da
categoria pendencias. Gmail/mensagens chegam como enriquecimento, por
ativação, com o parecer de privacidade rígido (a caixa de entrada INTEIRA
jamais entra no retrato).

Este Provider assume as pendências sem data que moravam no Calendar (dívida
C5 da Life Architect: "silêncio perpétuo é esquecimento") — uma porta só.
Anti-cobrança por desenho: o retrato mostra o RESUMO (quantas, e a mais
antiga), nunca a lista; a instrução CP-1 viaja com o dado (UMA oferta; o
"não" encerra).
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from .. import config, memory


def _idade_dias(created_at, now):
    try:
        nascimento = datetime.fromisoformat(created_at)
        return max(0, (now.replace(tzinfo=None) - nascimento).days)
    except (ValueError, TypeError):
        return None


def snapshot(user_id, _now=None):
    """Como está a COMUNICAÇÃO/as pendências da vida desta pessoa? (1-2 linhas)"""
    now = _now or datetime.now(ZoneInfo(config.TIMEZONE))
    sem_data = [i for i in memory.get_agenda(user_id) if not i["date"]]
    recusadas = memory.pendencias_recusadas(user_id)
    # M2: recusa tem memória DURÁVEL — pendência silenciada nunca reabre oferta
    ofertaveis = [i for i in sem_data
                  if (i["title"] or "").strip().lower() not in recusadas]
    pendencias_fatos = [f for f in memory.get_facts(user_id)
                        if f["category"] == "pendencias"]

    linhas = []
    if ofertaveis:
        mais_antiga = min(ofertaveis, key=lambda i: i.get("created_at") or "9999")
        idade = _idade_dias(mais_antiga.get("created_at"), now)
        ha = f", há {idade} dia(s)" if idade is not None and idade > 0 else ""
        linhas.append(
            f"PENDÊNCIAS em aberto: {len(sem_data)} (a mais antiga: "
            f"\"{mais_antiga['title']}\"{ha}). No momento LEVE, UMA oferta de ajuda "
            "— e distinga: 'já resolvi' → concluir_compromisso; 'não quero ajuda' → "
            "silenciar_pendencia (o item segue vivo em ver_agenda; NUNCA marque como "
            "feita uma coisa não feita). A idade orienta VOCÊ — nunca a diga a ela. "
            "EM DESABAFO OU EMOÇÃO QUENTE, ESTA LINHA FICA MUDA."
        )
    if pendencias_fatos:
        visiveis = pendencias_fatos[:2]  # as mais ANTIGAS: fricção velha primeiro (M3)
        resto = len(pendencias_fatos) - len(visiveis)
        itens = "; ".join(f["content"] for f in visiveis)
        if resto > 0:
            itens += f" (e mais {resto})"
        linhas.append(
            f"Ela contou que precisa resolver: {itens} — acompanhe com "
            "naturalidade quando o assunto aparecer; resolvido = esquecer_fato."
        )
    return "\n".join(linhas[:2])


PROVIDER = {
    "nome": "Communication Provider",
    "area": "5. Comunicação",
    "available": lambda user_id: True,  # o piso é o que ela conta: nunca falta
    "snapshot": snapshot,
}
