import threading
import time

from core.state import State
from core.brain import Brain
from core.life import LifeDevelopment
from conversation.response import Response
from conversation.history import ConversationHistory
from core.memory import Memory
from core.ai_memory import AIMemory


def state_updater(state):
    while True:
        state.update_activity()
        time.sleep(0.5)


def handle_life_command(user_input, life, ai_name):
    """Handle local P6 commands without sending private diary text to the LLM."""
    command, _, argument = user_input.partition(" ")
    command = command.lower()
    argument = argument.strip()

    try:
        if command == "/diary":
            if argument.lower() == "show":
                entries = life.get_diary_entries()
                if not entries:
                    print(f"{ai_name}: Diary masih kosong.")
                else:
                    print(f"{ai_name}: Entri diary terbaru:")
                    for entry in entries:
                        print(f"  [{entry['created_at']}] {entry['text']}")
            elif argument:
                entry = life.add_diary_entry(argument)
                print(f"{ai_name}: Entri diary tersimpan secara lokal ({entry['id']}).")
            else:
                print("Gunakan /diary <catatan pribadi> atau /diary show.")
            return True

        if command == "/goal":
            if argument:
                goal = life.add_goal(argument)
                print(f"{ai_name}: Tujuan tersimpan ({goal['id']}): {goal['title']}")
            else:
                print("Gunakan /goal <tujuan baru>.")
            return True

        if command == "/goals":
            goals = life.get_goals()
            if not goals:
                print(f"{ai_name}: Belum ada tujuan yang tersimpan.")
            else:
                for goal in goals:
                    due = f", target {goal['target_date']}" if goal.get("target_date") else ""
                    print(f"  {goal['id']} [{goal['status']}] {goal['title']}{due}")
            return True

        if command == "/goal-done":
            if not argument:
                print("Gunakan /goal-done <ID tujuan>.")
            else:
                goal = life.update_goal_status(argument, "completed")
                print(f"{ai_name}: Tujuan selesai ditandai: {goal['title']}")
            return True

        if command == "/reflect":
            if not argument:
                print("Gunakan /reflect <pengamatan> | <pelajaran> | <langkah berikutnya>.")
            else:
                parts = [part.strip() for part in argument.split("|", 2)]
                parts += [""] * (3 - len(parts))
                reflection = life.add_reflection(parts[0], parts[1], parts[2])
                print(f"{ai_name}: Refleksi tersimpan ({reflection['id']}).")
            return True

        if command == "/reflections":
            reflections = life.get_reflections()
            if not reflections:
                print(f"{ai_name}: Belum ada refleksi.")
            else:
                for item in reflections:
                    print(f"  [{item['created_at']}] {item['observation']}")
                    if item.get("lesson"):
                        print(f"    Pelajaran: {item['lesson']}")
                    if item.get("next_step"):
                        print(f"    Langkah berikutnya: {item['next_step']}")
            return True

        if command == "/milestones":
            milestones = life.data.get("milestones", [])[-10:][::-1]
            if not milestones:
                print(f"{ai_name}: Belum ada milestone.")
            else:
                for item in milestones:
                    print(f"  [{item['created_at']}] {item['title']}: {item['detail']}".rstrip(": "))
            return True

        if command == "/time":
            context = life.get_time_context()
            gap = context["seconds_since_last_seen"]
            gap_text = "belum tercatat" if gap is None else f"{gap} detik sejak sesi sebelumnya"
            print(f"Waktu lokal: {context['now']} ({context['daypart']}); {gap_text}.")
            return True

    except (ValueError, KeyError) as error:
        print(f"{ai_name}: Perintah belum bisa diproses: {error}")
        return True

    return False


def main():
    print("program start")

    memory = Memory()
    ai_memory = AIMemory()
    life = LifeDevelopment()
    time_context = life.mark_started()
    print(f"[P6] Sesi dimulai: {time_context['now']} ({time_context['daypart']}).")

    state = State()
    history = ConversationHistory()
    brain = Brain(state, history, memory, ai_memory)
    response = Response()

    ai_name = brain.ai_memory.get_ai_name()
    if ai_name is None:
        # Retain the current repository's name setup behavior.
        ai_name = memory.get("ai_name")

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
    print("P6: /diary <catatan>, /diary show, /goal <tujuan>, /goals,")
    print("    /goal-done <ID>, /reflect <pengamatan> | <pelajaran> | <langkah>,")
    print("    /reflections, /milestones, /time")

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

        # Local P6 commands are handled separately from normal chat.
        if user_input.startswith("/") and handle_life_command(user_input, life, ai_name):
            continue

        # P4.6: voice input remains available but is not changed by this P6 work.
        if user_input.lower() == "/voice":
            print("Mendengarkan selama 5 detik...")
            voice_result = brain.listen(duration=5, input_device=1)

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
        llm_context = brain.build_llm_context(thought, user_input)

        if thought["new_memory"] is not None:
            new_memory = thought["new_memory"]
            memory.remember(new_memory["type"], new_memory["value"])

        if thought["ai_experience"] is not None:
            ai_experience = thought["ai_experience"]
            ai_experience["context"] = {
                "mood": thought["state"]["mood"],
                "activity": thought["state"]["activity"]
            }
            ai_memory.add_experience(ai_experience)

        if thought["important_event"] is not None:
            ai_memory.add_important_event(thought["important_event"])

        ai_message = response.generate(llm_context)
        print(f"{ai_name}: {ai_message}")
        history.add(user_input, ai_message)


if __name__ == "__main__":
    main()
