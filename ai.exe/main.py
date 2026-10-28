import queue
import threading
import time

from core.state import State
from core.brain import Brain
from core.life import LifeDevelopment
from core.autonomous import AutonomousResponse
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
    autonomous = AutonomousResponse()

    updater = threading.Thread(target=state_updater, args=(state,), daemon=True)
    updater.start()

    user_name = memory.get("user_name")
    if user_name is None:
        user_name = input("??? : Siapa kamu?\nUser: ").strip()
        memory.set("user_name", user_name)

    ai_name = memory.get("ai_name")
    if ai_name is None:
        ai_name = input("??? : Siapa namaku?\nUser: ").strip()
        memory.set("ai_name", ai_name)

    print()
    print(f"{ai_name}: Halo {user_name}.")
    print(f"{ai_name}: Bagaimana kabarmu?")
    print()
    print("P6: /diary <catatan>, /diary show, /goal <tujuan>, /goals,")
    print("    /goal-done <ID>, /reflect <pengamatan> | <pelajaran> | <langkah>,")
    print("    /reflections, /milestones, /time")
    print("Autonomous response: /initiative status | on | off | now")
    print(f"[Autonomous] Aktif; inisiatif setelah {autonomous.idle_seconds} detik idle, cooldown {autonomous.cooldown_seconds} detik.")

    # A dedicated input thread lets the main loop check scheduled initiatives
    # while the terminal is waiting for the next line.
    input_queue = queue.Queue()
    input_ready = threading.Event()
    input_ready.set()

    def input_worker():
        while True:
            # Tahan prompt berikutnya sampai main loop selesai memproses pesan.
            input_ready.wait()
            input_ready.clear()
            try:
                value = input(f"{user_name} (ketik /voice untuk bicara): ")
            except (EOFError, KeyboardInterrupt):
                input_queue.put("exit")
                return
            input_queue.put(value)

    threading.Thread(target=input_worker, daemon=True).start()

    running = True
    while running:
        try:
            user_input = input_queue.get(timeout=1.0).strip()
        except queue.Empty:
            trigger = autonomous.evaluate(
                state=brain.analyze_state(),
                recent_history=history.get_recent(5),
                active_goals=life.get_goals(status="active"),
            )
            if trigger:
                try:
                    context = {
                        "identity": brain.analyze_identity(),
                        "state": brain.analyze_state(),
                        "memory": brain.analyze_memory(),
                        "ai_memory": brain.analyze_ai_memory(
                            history.get_recent(1)[-1].get("user", "")
                            if history.get_recent(1) else ""
                        ),
                        "recent_history": history.get_recent(5),
                    }
                    message = response.generate_initiative(trigger, context)
                    if message:
                        print(f"\n{ai_name} (inisiatif): {message}")
                        history.add("[inisiatif]", message)
                        autonomous.mark_sent()
                except Exception as error:
                    # A failed local model call should not kill the chat loop.
                    print(f"\n[Autonomous] Gagal membuat pesan: {error}")
                    autonomous.mark_sent()
            input_ready.set()
            continue

        autonomous.user_interacted()

        if user_input.lower() == "exit":
            print(f"{ai_name}: Dimengerti, sampai jumpa lagi, {user_name}.")
            running = False
            input_ready.set()
            continue

        if user_input.lower().startswith("/initiative"):
            _, _, argument = user_input.partition(" ")
            option = argument.strip().lower()
            if option == "on":
                autonomous.set_enabled(True)
                print(f"[Autonomous] Aktif. Ambang idle {autonomous.idle_seconds} detik.")
            elif option == "off":
                autonomous.set_enabled(False)
                print("[Autonomous] Dimatikan untuk sesi ini.")
            elif option == "status" or not option:
                status = "aktif" if autonomous.enabled else "mati"
                print(
                    f"[Autonomous] {status}; terkirim {autonomous.sent_this_session}/"
                    f"{autonomous.max_per_session}; idle {autonomous.idle_seconds}s; "
                    f"cooldown {autonomous.cooldown_seconds}s."
                )
            elif option == "now":
                trigger = autonomous.evaluate(
                    state=brain.analyze_state(),
                    recent_history=history.get_recent(5),
                    active_goals=life.get_goals(status="active"),
                    force=True,
                )
                if not trigger:
                    print("[Autonomous] Tidak ada pesan yang dibuat.")
                else:
                    try:
                        context = {
                            "identity": brain.analyze_identity(),
                            "state": brain.analyze_state(),
                            "memory": brain.analyze_memory(),
                            "ai_memory": brain.analyze_ai_memory(
                                history.get_recent(1)[-1].get("user", "")
                                if history.get_recent(1) else ""
                            ),
                            "recent_history": history.get_recent(5),
                        }
                        message = response.generate_initiative(trigger, context)
                        if message:
                            print(f"{ai_name} (inisiatif): {message}")
                            history.add("[inisiatif]", message)
                            autonomous.mark_sent()
                        else:
                            print("[Autonomous] Model tidak menghasilkan pesan.")
                    except Exception as error:
                        print(f"[Autonomous] Gagal membuat pesan: {error}")
            else:
                print("Gunakan /initiative status, /initiative on, /initiative off, atau /initiative now.")
            input_ready.set()
            continue

        if user_input.startswith("/") and handle_life_command(user_input, life, ai_name):
            input_ready.set()
            continue

        if user_input.lower() == "/voice":
            print("Mendengarkan selama 5 detik...")
            voice_result = brain.listen(duration=5, input_device=1)
            if not voice_result.get("success"):
                print(f"{ai_name}: Maaf, suara belum bisa diproses. {voice_result.get('error', '')}")
                input_ready.set()
                continue
            user_input = voice_result.get("text", "").strip()
            if not user_input:
                print(f"{ai_name}: Aku belum menangkap ucapanmu.")
                input_ready.set()
                continue
            print(f"[Transkripsi] {user_input}")
            autonomous.user_interacted()
            if user_input.lower() == "exit":
                print(f"{ai_name}: Dimengerti, sampai jumpa lagi, {user_name}.")
                running = False
                input_ready.set()
                continue

        if not user_input:
            input_ready.set()
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
                "activity": thought["state"]["activity"],
            }
            ai_memory.add_experience(ai_experience)

        if thought["important_event"] is not None:
            ai_memory.add_important_event(thought["important_event"])

        ai_message = response.generate(llm_context)
        print(f"{ai_name}: {ai_message}")
        history.add(user_input, ai_message)
        input_ready.set()


if __name__ == "__main__":
    main()
