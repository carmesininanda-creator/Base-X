# 🔒 Política de Privacidade — Giu Família

Escrita para pessoas, não para advogados.

## O que a Giu guarda sobre você

Só o que você conta a ela: fatos da sua vida, preferências, rotina, saúde,
compromissos e o histórico das suas conversas. Tudo fica guardado **no seu
perfil, separado de todos os outros membros da família**.

## Quem vê suas conversas

**Ninguém.** Nem seus pais, nem seus irmãos, nem quem administra a conta da
família. A Giu de cada pessoa é só dela. A administradora consegue cadastrar
e remover membros — mas **não consegue ler a memória nem as conversas de
ninguém** pela API.

## Quando algo seu chega a outra pessoa

Em exatamente duas situações:

1. **Você pediu e confirmou.** Ex.: "Giu, avisa minha mãe que chego às 20h."
   A Giu mostra a mensagem exata e para quem vai, e só envia depois do seu
   "sim". Apenas aquela mensagem é enviada — nunca o resto da conversa.

2. **Risco sério.** Se a Giu perceber uma emergência de saúde ou segurança
   (ex.: você pedir socorro), ela pode acionar o seu contato de emergência
   com o **mínimo necessário** — algo como "Fulano pediu ajuda agora" — e
   **nunca** o conteúdo das suas conversas. Toda ação dessas fica registrada
   e você pode ver depois.

## Quando você fala por áudio (voz)

Você pode conversar com a Giu **por escrito ou por voz** — como preferir, e você
escolhe. Quando você manda um áudio:

- Para **entender** o que você disse, esse áudio é transcrito (virado texto) por
  um provedor de inteligência artificial (hoje, a OpenAI) — o mesmo que a Giu usa
  para pensar. É o único jeito de ela te ouvir.
- **A gravação em si não fica guardada.** Depois de transcrito, o que permanece é
  o texto da sua mensagem, no seu perfil — junto do resto da conversa, e só seu.
- **A escolha é sua e muda quando quiser.** No começo, a Giu pergunta se você
  prefere receber as respostas por voz, por escrito, ou os dois — e respeita isso.
  Você pode dizer "me responde só por escrito" a qualquer momento, e ela para de
  mandar áudio. É uma preferência de relacionamento, não uma configuração escondida.

## Seus direitos (a qualquer momento)

- **Ver tudo**: pergunte "o que você sabe sobre mim?" ou use seu token pessoal
  na API (`GET /memories/você`).
- **Apagar**: peça "esquece isso" na conversa ou apague pela API. Apagou, sumiu.
- **Revogar consentimento**: diga que não quer mais que a Giu guarde
  preferências — ela passa a guardar só o essencial e pergunta antes.
- **Sair**: peça para ser removida da família; seu cadastro é removido e sua
  memória pode ser apagada por completo a seu pedido.

## Ações em seu nome

A Giu **nunca** executa nada (agendar, lembrar, enviar recado, e futuramente
e-mail, transporte, comida, pagamentos) sem a sua confirmação explícita
naquela conversa. Funções novas nascem **desligadas** e só passam a existir
para você se você liberar — e você pode desligar de volta quando quiser.

## Limitações conhecidas desta fase (piloto familiar)

Honestidade acima de tudo — duas limitações técnicas existem hoje e serão
resolvidas nas próximas fases:

1. **Acesso à infraestrutura.** As proteções de "ninguém lê sua memória"
   valem para todos os acessos pela Giu e pela API. Porém, quem administra o
   servidor da família tem, tecnicamente, acesso ao banco de dados no nível
   da infraestrutura. Nesta fase, a confidencialidade nesse nível é um
   compromisso da administradora, não uma barreira técnica (criptografia por
   pessoa está no plano da plataforma).

2. **Processamento pelo provedor de IA.** Para pensar e responder, a Giu
   envia o contexto da sua conversa a um provedor de modelo de inteligência
   artificial (hoje, a OpenAI), sob os termos de proteção de dados desse
   provedor. Suas conversas não são usadas para treinar modelos de terceiros
   segundo a política de API vigente do provedor, mas o tráfego existe e você
   deve saber disso.

O que **não** é limitação (garantido e testado): mensagens não aparecem em
registros técnicos do servidor; o texto enviado ao contato de emergência é um
template fixo que nunca inclui o conteúdo das suas conversas.

## Base legal

Tratamento de dados pessoais com base no consentimento (LGPD, art. 7º, I),
colhido no onboarding e revogável a qualquer momento. Dados de saúde só são
guardados se você os contar e tiver consentido; são usados apenas para os
lembretes e cuidados que você pedir.
