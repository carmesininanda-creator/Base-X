"""
Porta Terminal — conversa com a Giu direto no terminal.

A porta mais simples de todas, perfeita para testar o cérebro:
    python cli.py
"""

from giu import brain, memory

USER_ID = "nanda_001"


def main():
    memory.init_db()
    print("✦ Giu — BazeX")
    print('"Você não precisa segurar tudo sozinha. Eu estou aqui."')
    print("(digite 'sair' para encerrar)\n")

    while True:
        try:
            text = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text:
            continue
        if text.lower() in ("sair", "exit", "quit"):
            break
        reply = brain.think(USER_ID, text, channel="cli")
        print(f"\nGiu: {reply}\n")

    print("\nGiu: Até logo. Estou aqui quando precisar. ✦")


if __name__ == "__main__":
    main()
