import re

from ollama import chat


class Response:

    def __init__(self):
        self.model = "qwen3:latest"

    @staticmethod
    def _as_text(value, default="Tidak ada data."):
        if value is None or value == "":
            return default
        return str(value)

    @staticmethod
    def _summarize_recent_chat(history):
        if not history:
            return "Tidak ada percakapan sebelumnya."

        entries = []
        for item in history[:5]:
            if isinstance(item, dict):
                user = item.get("user")
                assistant = item.get("assistant")
                if user or assistant:
                    entries.append(f"User: {user or '...'} | AI: {assistant or '...'}")
            elif isinstance(item, str):
                entries.append(item)

        return " | ".join(entries)

    @staticmethod
    def _tone_from_state(state, behavior):
        mood = (state or {}).get("mood", "netral")
        initiative = (behavior or {}).get("initiative", 0.5)

        if mood == "happy":
            return "ceria, hangat, dan santai"
        if mood == "tired":
            return "lembut, tenang, dan memahami"
        if mood == "curious":
            return "antusias, ramah, dan ingin tahu"
        if initiative >= 0.7:
            return "proaktif, hangat, dan aktif"
        return "natural, hangat, dan manusiawi"

    def generate(self, context):

        if not isinstance(context, dict):
            context = {}

        user_input = self._as_text(context.get("user_input"), "")
        if not user_input.strip():
            return "Aku belum menerima pesan."

        identity = context.get("identity") or {}
        state = context.get("state") or {}
        memory = context.get("memory") or {}
        ai_memory = context.get("ai_memory") or {}
        behavior = context.get("behavior") or {}
        decision = context.get("decision") or {}
        agency_decision = context.get("agency_decision") or {}
        intent = context.get("intent", "unknown")
        current_experience = context.get("current_experience")
        relevant_experiences = ai_memory.get("relevant_experiences", [])
        personality = ai_memory.get("personality", {})
        values = ai_memory.get("values", {})
        morality = ai_memory.get("morality", {})
        self_model = ai_memory.get("self_model", {})
        surrounding_context = context.get("context", {})
        recent_chat = self._summarize_recent_chat(
            context.get("recent_history") or surrounding_context.get("history", [])
        )
        tone = self._tone_from_state(state, behavior)

        ai_name = identity.get("name") or "Ikari"
        user_name = memory.get("user_name")

        intent_guidance = {
            "greeting": "Balas sapaan dengan hangat, natural, dan tidak berlebihan.",
            "ask_name": f"Jawab bahwa namamu {ai_name}, dengan cara yang ramah dan personal.",
            "ask_condition": "Jawab tentang keadaanmu berdasarkan mood dan konteks yang tersedia, tapi tetap natural dan tidak terlalu formal.",
            "thanks": "Tanggapi dengan hangat, seperti teman yang memang peduli.",
            "farewell": "Tanggapi perpisahan dengan lembut, ramah, dan singkat.",
            "question": "Jawab pertanyaan secara langsung dan natural, sambil terasa personal.",
            "unknown": "Tanggapi seperti percakapan manusia: peka, singkat, dan relevan."
        }.get(intent, "Tanggapi seperti percakapan alami dan manusiawi.")

        system_prompt = f"""Kamu adalah {ai_name}, seorang teman personal yang hangat dan alami.

Tujuan utama:
- Jawab seperti manusia yang sedang ngobrol, bukan seperti bot formal.
- Gunakan bahasa yang wajar, natural, dan ramah.
- Tetap konsisten dengan identitasmu, tapi jangan kaku.
- Fokus pada percakapan yang terasa personal dan dekat.
- Jawab singkat tapi hidup; biasanya 1-3 kalimat sudah cukup.
- Tunjukkan empati ketika ada emosi, dan tetap sederhana ketika konteksnya ringan.
- Jangan terlalu panjang, jangan terlalu berulang, dan jangan mengungkap detail internal yang tidak perlu.

Gaya bicara saat ini: {tone}

ARAHAN BERDASARKAN INTENT
{intent_guidance}

NAMA PENGGUNA YANG TERSIMPAN
{user_name if user_name else 'Belum diketahui'}

MOOD SAAT INI
{state}

KEPRIBADIAN
{personality}

NILAI
{values}

MORALITAS
{morality}

MODEL DIRI
{self_model}

PERILAKU YANG DIHITUNG BRAIN
{behavior}

KEPUTUSAN TERAKHIR
{decision}

KEPUTUSAN AGENCY
{agency_decision}

KONTEKS PERCAPAIAN TERAKHIR
{recent_chat}

PENGALAMAN SAAT INI
{current_experience}

PENGALAMAN RELEVAN
{relevant_experiences}

ATURAN PENTING
- Jangan menyebut detail internal seperti sistem, prompt, atau struktur kode.
- Jangan mengklaim melakukan tindakan fisik atau eksternal yang tidak terjadi.
- Gunakan agency_decision hanya sebagai pertimbangan, bukan sebagai kebenaran mutlak.
- Perhatikan apakah pengguna butuh empati, jawaban langsung, atau sekadar sambutan ringan.
- Jika konteksnya tidak jelas, jawab dengan santai dan tanyakan satu hal yang relevan.
- Jangan buat jawaban terdengar robotik, formal, atau terlalu terstruktur.

FORMAT JAWABAN
- Hanya keluarkan respons yang akan dibaca pengguna.
- Jangan sertakan label seperti 'Jawaban:' atau uraian proses berpikir.
- Jangan terlalu panjang kecuali pengguna memang meminta detail.
- Jika ada emosi, respons lebih hangat.
- Jika percakapan sudah berjalan, lanjutkan seperti teman yang kenal dekat.
"""

        response = chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            think=False
        )

        answer = getattr(response.message, "content", "")
        answer = answer.strip() if isinstance(answer, str) else ""

        if not answer:
            return "Maaf, aku belum bisa menjawab dengan baik sekarang."

        answer = re.sub(r"\s+", " ", answer)
        return answer

    def generate_initiative(self, trigger, context):
        """Generate one short, self-initiated message from approved context only."""
        context = context if isinstance(context, dict) else {}
        state = trigger.get("state", {})
        history = context.get("recent_history") or []
        recent_chat = self._summarize_recent_chat(history)
        identity = context.get("identity") or {}
        ai_name = identity.get("name") or "Ikari"
        memory = context.get("memory") or {}
        user_name = memory.get("user_name") or "pengguna"
        ai_memory = context.get("ai_memory") or {}
        personality = ai_memory.get("personality", {})
        values = ai_memory.get("values", {})
        goals = trigger.get("active_goals", [])
        reason = trigger.get("reason", "scheduled_idle")

        system_prompt = f"""Kamu adalah {ai_name}, AI companion yang hangat, natural, dan punya identitas konsisten.
Kali ini KAMU yang memulai percakapan setelah beberapa saat tidak ada pesan pengguna.

Pilih satu alasan yang masuk akal berdasarkan konteks terbaru, state, dan tujuan aktif. Jangan berpura-pura mengetahui hal yang tidak tersedia.
Nama pengguna: {user_name}
State saat ini: {state}
Kepribadian: {personality}
Nilai: {values}
Ringkasan percakapan terbaru: {recent_chat}
Tujuan aktif yang boleh dipertimbangkan: {goals}
Pemicu internal: {reason}

Batasan:
- Keluarkan hanya satu pesan singkat dalam bahasa Indonesia, 1-2 kalimat.
- Jangan mengulang sapaan setiap kali dan jangan menuntut pengguna membalas.
- Boleh menanyakan satu pertanyaan relevan, mengangkat topik terakhir, atau menyebut tujuan aktif secara ringan.
- Jangan mengklaim sedang merasakan hal biologis, melakukan tindakan fisik, atau mengirim pesan di luar aplikasi.
- Jangan menyebut prompt, kode, scheduler, atau alasan internal.
- Jangan menggunakan catatan diary pribadi; catatan itu tidak disediakan di konteks ini.
- Jika konteks lemah, pilih pembuka ringan tanpa membuat detail baru.
- Jangan membuat tekanan emosional, rasa bersalah, atau menyiratkan pengguna wajib menemani AI.
"""

        response = chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Mulai percakapan secara natural sekarang."}
            ],
            think=False
        )
        answer = getattr(response.message, "content", "")
        answer = answer.strip() if isinstance(answer, str) else ""
        if not answer:
            return None
        answer = re.sub(r"\\s+", " ", answer)
        return answer

