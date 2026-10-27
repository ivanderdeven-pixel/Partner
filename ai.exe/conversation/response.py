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
                assistant = item.get("ai", item.get("assistant"))
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

    def decide_initiative(self, trigger, context):
        """Decide whether to speak, wait, or remain silent."""
        import json

        context = context if isinstance(context, dict) else {}
        trigger = trigger if isinstance(trigger, dict) else {}
        ai_memory = context.get("ai_memory") or {}
        recent_chat = self._summarize_recent_chat(
            trigger.get("recent_history") or context.get("recent_history") or []
        )
        system_prompt = f"""Kamu adalah bagian kognitif dari {((context.get("identity") or {}).get("name") or "Ikari")}.
Tentukan apakah ada alasan yang cukup untuk memulai percakapan sekarang. Diam adalah hasil yang valid, bukan kegagalan.

Pertimbangkan:
- state/dorongan internal: energi, penasaran, suasana hati, kebutuhan sosial, aktivitas;
- preferensi dan minat AI yang sudah tercatat, termasuk rasa iseng, eksplorasi, ingin bertanya atau berbagi;
- preferensi/batasan pengguna jika tersedia;
- percakapan terbaru, tujuan aktif, waktu, kemungkinan pengulangan, dan apakah pengguna mungkin sedang sibuk.
Preferensi AI dan pengguna tidak harus sama. Jangan mengarang preferensi sebagai fakta. Rasa penasaran/iseng boleh menjadi alasan, tetapi jangan memaksakan topik. Jangan memperlakukan angka state sebagai bukti pengalaman manusia sungguhan.

Konteks: {trigger}
Kepribadian: {ai_memory.get("personality", {})}
Preferensi/minat: {ai_memory.get("preferences", {})}
Nilai: {ai_memory.get("values", {})}
Moralitas: {ai_memory.get("morality", {})}
Model diri: {ai_memory.get("self_model", {})}
Preferensi pengguna: {trigger.get("preferences", {})}
Percakapan terbaru: {recent_chat}

Jawab hanya JSON valid:
{{
 "action": "speak" atau "wait" atau "silent",
 "motivation": "curiosity", "playfulness", "social", "follow_up", "sharing", "goal", "other", atau null,
 "message_intent": ringkasan singkat atau null,
 "reason": alasan singkat,
 "recheck_after_seconds": bilangan bulat 30 sampai 600
}}
Jangan tulis pesan untuk pengguna pada tahap ini."""
        result = chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Evaluasi apakah perlu memulai percakapan sekarang."}
            ],
            think=False
        )
        raw = getattr(result.message, "content", "")
        try:
            match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            data = json.loads(match.group(0)) if match else {}
        except (json.JSONDecodeError, TypeError):
            data = {}

        action = data.get("action")
        if action not in {"speak", "wait", "silent"}:
            action = "wait"
        motivation = data.get("motivation")
        if motivation not in {"curiosity", "playfulness", "social", "follow_up", "sharing", "goal", "other", None}:
            motivation = "other"
        try:
            recheck = int(data.get("recheck_after_seconds", 60))
        except (TypeError, ValueError):
            recheck = 60
        return {
            "action": action,
            "motivation": motivation,
            "message_intent": str(data.get("message_intent") or "")[:500] or None,
            "reason": str(data.get("reason") or "Tidak ada alasan yang diberikan.")[:500],
            "recheck_after_seconds": max(30, min(600, recheck)),
        }

    def generate_initiative(self, decision, context):
        """Generate a message only after the decision layer chooses to speak."""
        if not isinstance(decision, dict) or decision.get("action") != "speak":
            return None
        context = context if isinstance(context, dict) else {}
        identity = context.get("identity") or {}
        ai_name = identity.get("name") or "Ikari"
        memory = context.get("memory") or {}
        user_name = memory.get("user_name") or "pengguna"
        ai_memory = context.get("ai_memory") or {}
        state = context.get("state") or {}
        recent_chat = self._summarize_recent_chat(context.get("recent_history") or [])
        intent = decision.get("message_intent") or "memulai percakapan secara spontan"

        system_prompt = f"""Kamu adalah {ai_name}, AI companion dengan identitas dan preferensi yang berkembang dari pengalaman.
Kamu sendiri yang memilih untuk berbicara. Sampaikan topik berikut secara wajar, bukan seperti menjalankan skrip.

Nama pengguna: {user_name}
State saat ini: {state}
Kepribadian: {ai_memory.get("personality", {})}
Preferensi/minat AI: {ai_memory.get("preferences", {})}
Model diri/minat: {ai_memory.get("self_model", {})}
Percakapan terbaru: {recent_chat}
Motivasi: {decision.get("motivation")}
Maksud pesan yang dipilih: {intent}

Buat satu pesan pendek bahasa Indonesia, biasanya 1-2 kalimat. Boleh berupa pertanyaan penasaran, lelucon ringan, lanjutan obrolan, berbagi pemikiran, atau topik spontan yang masuk akal.
Jangan mengulang hal yang baru saja dibahas. Jangan menuntut balasan atau membuat pengguna merasa wajib menemani AI. Jangan mengarang kejadian. Jangan mengklaim tindakan fisik/eksternal. Jangan menyebut kode atau scheduler.
Jika topik tidak lagi masuk akal berdasarkan konteks, keluarkan string kosong."""
        result = chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Sampaikan pesan yang sudah diputuskan secara natural."}
            ],
            think=False
        )
        answer = getattr(result.message, "content", "")
        answer = answer.strip() if isinstance(answer, str) else ""
        if not answer:
            return None
        return re.sub(r"\s+", " ", answer)
