"""
Living Context — o retrato do momento de vida (Fase 2 da Base-X).

Providers não são fontes de dados: são DIMENSÕES DA VIDA HUMANA. Cada um
responde a UMA pergunta: "como está esta parte da vida desta pessoa neste
momento?". A Giulieta nunca pergunta às APIs — pergunta ao Living Context,
que pergunta aos Providers, que perguntam aos Life Connectors autorizados.
(Arquitetura aprovada pela fundadora: ARQUITETURA-CONTEXT-PROVIDERS.md.)

Contrato universal (as oito leis, resumidas no código):
- snapshot(user_id) devolve 1-3 linhas de VIDA (nunca de dado cru), ou "" —
  NUNCA levanta exceção, NUNCA bloqueia o turno (conector lento/quebrado
  degrada em silêncio para o piso interno).
- O retrato é efêmero: montado, usado no turno, descartado. Nenhum dado de
  vida é persistido na montagem (cache técnico volátil é a única exceção).
- Confidencialidade absoluta: o retrato de uma pessoa só contém a vida DELA.
- Substituição, não soma (CP-2): cada bloco antigo do prompt MIGRA para
  dentro do retrato quando o Provider correspondente nasce — o prompt não
  cresce com a chegada do Living Context.
"""

from . import agenda, tempo

# Ordem = prioridade no orçamento (a Fase 2 entra aqui um Provider por vez,
# na ordem da fundadora: Time → Calendar → Communication → Home → Mobility → Health).
PROVIDERS = [tempo.PROVIDER, agenda.PROVIDER]

RETRATO_MAX_LINHAS = 14   # orçamento de atenção do retrato inteiro
SNAPSHOT_MAX_LINHAS = 3   # teto por Provider (contrato)


def retrato(user_id):
    """Monta o bloco "O MOMENTO DE AGORA" do prompt a partir dos Providers.
    Nunca levanta: Provider que falhar simplesmente não aparece no retrato."""
    linhas = []
    for p in PROVIDERS:
        try:
            snap = p["snapshot"](user_id) or ""
        except Exception:
            snap = ""  # a conversa nunca paga pelo erro de um provedor
        vivas = [ln for ln in snap.strip().splitlines() if ln.strip()]
        linhas.extend(vivas[:SNAPSHOT_MAX_LINHAS])
        if len(linhas) >= RETRATO_MAX_LINHAS:
            break
    corpo = "\n".join(linhas[:RETRATO_MAX_LINHAS])
    return (
        "O MOMENTO DE AGORA (o retrato do momento — percebido pela sua atenção; "
        "use com naturalidade SÓ o que melhora a vida dela agora; o resto, silêncio):\n"
        + corpo
    )
