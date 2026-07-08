# 🌱 Ficha de Vida Inicial — Família Fundadora (CC5)

> **Decisão da fundadora:** "Não quero apenas identidade. Quero identidade +
> vida." Cada membro começa com a vida semeada — a base sobre a qual a
> Giulieta aprende continuamente.
>
> ⚠️ **REGRA DE PRIVACIDADE:** este arquivo no git é o MODELO VAZIO. A ficha
> PREENCHIDA contém vida real — **jamais entra no git, em issue, em PR ou em
> chat público**. Caminho de entrega: a Nanda preenche → o Despacho aplica
> via `POST /family/members/{numero}/vida` (token de operadora) → a ficha
> preenchida é apagada. Alternativa sem técnica: a própria pessoa CONTA na
> conversa (a Giu guarda sozinha).
>
> **Como a Giu trata o que for semeado:** tudo entra marcado "[de partida]" —
> hipótese de contexto da família. Ela NUNCA dirá "você me contou"; confirma
> vivendo, e o que a pessoa mostrar prevalece e substitui. Vale o Portão do
> Cuidado de Quem Não Escolheu: sobre terceiros (a mãe, amigos), o MÍNIMO
> necessário.

---

## Modelo por membro (copiar 4×: Nanda · Ian · Pauline · Rafael)

```json
{
  "pessoas": [
    "… quem importa na vida dela/dele (nome + relação + 1 traço). Sobre quem NÃO é membro: o MÍNIMO — e NUNCA saúde, endereço ou dado sensível de terceiros (Portão do Cuidado de Quem Não Escolheu). Ex: 'A mãe — a Nanda coordena os cuidados dela'"
  ],
  "projetos": [
    "… o que está construindo AGORA. Ex: 'montar a horta em casa'"
  ],
  "objetivos": [
    "… o que quer alcançar em meses/anos. Ex: 'aprender inglês para viajar'"
  ],
  "rotina": [
    "… como os dias funcionam. Ex: 'acorda cedo; trabalho intenso de manhã; noite é família'"
  ],
  "preferencias": [
    "… jeitos de ser cuidado. Ex: 'mensagens curtas; detesta lista grande; prefere voz'"
  ],
  "contexto": [
    "… o que mais a Giu deveria saber de partida. Ex: 'está num período puxado na empresa'"
  ],
  "friccoes": [
    "… as fricções JÁ identificadas. Ex: 'esquece consultas da mãe; a lista do mercado vive na cabeça'"
  ],
  "interesses": [
    "… o que a pessoa AMA (viram convites de conexão, nunca rótulos). Ex: 'mergulho', 'hipismo', 'carros'"
  ],
  "sonhos": [
    "… o que gostaria de construir nos próximos anos (a Giu acompanha durante toda a relação). Ex: 'morar fora'"
  ],
  "desafios": [
    "… onde crescer — a Giu cuida SEM julgamento e nunca abre o assunto; orienta o cuidado quando a pessoa trouxer. Ex: 'depende da família para a vida prática'"
  ],
  "datas": [
    {"titulo": "Aniversário dela/dele", "data": "MM-DD"},
    {"titulo": "Aniversário de …", "data": "MM-DD"},
    {"titulo": "Data única importante", "data": "YYYY-MM-DD", "recorrente": false}
  ]
}
```

## Aplicação (Despacho)

```bash
curl -X POST "$BASE_URL/family/members/<NUMERO>/vida" \
  -H "Authorization: Bearer $GIU_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @vida-<nome>.json
# depois: apagar o arquivo vida-<nome>.json (a vida agora mora na memória da Giu)
```

Reaplicar é seguro: o semeio deduplica (nada entra duas vezes). Consentimento
recusado bloqueia o semeio — e se a pessoa disser "não" no onboarding DEPOIS
do semeio, **tudo o que foi semeado é EXPURGADO automaticamente** (fatos e
datas): a recusa da pessoa vale mais que a ficha, sempre (S1 da Life
Architect). O que ela mesma contar depois, em conversa, nasce limpo e é dela.
