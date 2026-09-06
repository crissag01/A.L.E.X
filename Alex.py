from Brain.brain import ask

print("Alex iniciada. Escribe 'salir' para terminar.\n")

while True:

    user_input = input("Tú: ")

    if user_input.lower() in ["salir", "exit", "quit"]:
        print("Alex: Hasta la vista.")
        break

    try:

        reply = ask(user_input, channel="cli")

        print(f"Alex: {reply}\n")

    except Exception as e:

        print("Error:", e)