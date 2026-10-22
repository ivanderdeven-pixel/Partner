
import threading
import time

from core.state import State
from core.brain import Brain
from conversation.response import Response
from conversation.history import ConversationHistory
from core.memory import Memory
from core.ai_memory import AIMemory


def state_updater(state):
    while True:
        state.update_activity()
        time.sleep(0.5)


def main():
    print("program start")

    memory = Memory()
    ai_memory = AIMemory()

    state = State()
    history = ConversationHistory()
    brain = Brain(state, history, memory, ai_memory)
    response = Response()

    ai_name = brain.ai_memory.get_ai_name()
    if ai_name is None:
        brain.ai_memory.set_ai_name()

    updater = threading.Thread(
        target=state_updater,
        args=(state,),
        daemon=True
    )
    updater.start()

    user_name = memory.get("user_name")

    if user_name is None:
        user_name = input("??? : Siapa kamu?\nUser: ")
        memory.set("user_name", user_name)

    ai_name = memory.get("ai_name")

    if ai_name is None:
        ai_name = input("??? : Siapa namaku?\nUser: ")
        memory.set("ai_name", ai_name)

    print()
    print(f"{ai_name}: Halo {user_name}.")
    print(f"{ai_name}: Bagaimana kabarmu?")
    print()

    while True:
        user_input = input(
            f"{user_name} (ketik /voice untuk bicara): "
        ).strip()

        if user_input.lower() == "exit":
            print(
                f"{ai_name}: Dimengerti, "
                f"Sampai jumpa lagi, {user_name}."
            )
            break

        # P4.6: Input suara melalui mikrofon
        if user_input.lower() == "/voice":
            print("Mendengarkan selama 5 detik...")

            voice_result = brain.listen(
                duration=5,
                input_device=1
            )

            if not voice_result.get("success"):
                print(
                    f"{ai_name}: Maaf, suara belum bisa "
                    f"diproses. {voice_result.get('error', '')}"
                )
                continue

            user_input = voice_result.get("text", "").strip()

            if not user_input:
                print(f"{ai_name}: Aku belum menangkap ucapanmu.")
                continue

            print(f"[Transkripsi] {user_input}")

            if user_input.lower() == "exit":
                print(
                    f"{ai_name}: Dimengerti, "
                    f"Sampai jumpa lagi, {user_name}."
                )
                break

        if not user_input:
            continue

        state.apply_event("user_message")

        thought = brain.think(user_input)

        llm_context = brain.build_llm_context(
            thought,
            user_input
        )

        if thought["new_memory"] is not None:
            new_memory = thought["new_memory"]

            memory.remember(
                new_memory["type"],
                new_memory["value"]
            )

        if thought["ai_experience"] is not None:
            ai_experience = thought["ai_experience"]
            ai_experience["context"] = {
                "mood": thought["state"]["mood"],
                "activity": thought["state"]["activity"]
            }

            ai_memory.add_experience(ai_experience)

        if thought["important_event"] is not None:
            important_event = thought["important_event"]
            ai_memory.add_important_event(important_event)

        ai_message = response.generate(llm_context)

        print(f"{ai_name}: {ai_message}")

        history.add(user_input, ai_message)


if __name__ == "__main__":
    main()
