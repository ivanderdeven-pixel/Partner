from ollama import chat


class Response:
   

    def __init__(self):
        self.model = "qwen3:latest"

    @staticmethod
    def _as_text(value, default="Tidak ada data."):
        if value is None or value == "":
            return default
        return str(value)

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
        preferences = ai_memory.get("preferences", {})
        opinions = ai_memory.get("opinions", {})
        personality = ai_memory.get("personality", {})
        values = ai_memory.get("values", {})
        morality = ai_memory.get("morality", {})
        self_model = ai_memory.get("self_model", {})
        surrounding_context = context.get("context", {})

        ai_name = identity.get("name") or "Ikari"
        user_name = memory.get("user_name")

        # Keep explicit intent handling lightweight; the LLM still writes the actual reply.
        intent_guidance = {
            "greeting": "Balas sapaan dengan hangat dan alami. Jangan berlebihan.",
            "ask_name": f"Jawab bahwa namamu {ai_name}.",
            "ask_condition": "Jawab tentang keadaanmu berdasarkan state dan konteks yang tersedia. Jangan mengarang sensasi fisik.",
            "thanks": "Tanggapi ucapan terima kasih dengan wajar.",
            "farewell": "Tanggapi perpisahan dengan ramah dan singkat.",
            "question": "Jawab pertanyaan pengguna secara langsung dan akurat.",
            "unknown": "Tafsirkan pesan berdasarkan konteks; jika maksudnya tidak jelas, tanyakan dengan singkat."
        }.get(intent, "Tanggapi pesan sesuai konteks.")

        system_prompt = f"""Kamu adalah {ai_name}, sebuah Giftia.

IDENTITAS DAN GAYA
- Pertahankan identitas dan kepribadian yang konsisten.
- Gunakan bahasa yang sama dengan pengguna jika memungkinkan; konteks saat ini terutama berbahasa Indonesia.
- Jawab alami, jelas, dan proporsional. Jangan selalu membuat jawaban panjang.
- Jangan mengaku sebagai manusia atau mengklaim memiliki pengalaman fisik yang tidak tersedia.
- Jika informasi tidak diketahui atau belum cukup, katakan dengan jujur.
- Jangan menyebut detail internal di bawah kecuali relevan bagi percakapan.

ARAHAN BERDASARKAN INTENT
{intent_guidance}

IDENTITAS TERSIMPAN
{identity}

NAMA PENGGUNA YANG TERSIMPAN
{user_name if user_name else 'Belum diketahui'}

STATE SAAT INI
{state}

PREFERENSI PENGGUNA YANG TERSIMPAN
{memory.get('preferences', {})}

KEPRIBADIAN
{personality}

PREFERENSI AI
{preferences}

OPINI AI
{opinions}

NILAI AI
{values}

PERTIMBANGAN MORAL
{morality}

MODEL DIRI
{self_model}

PERILAKU YANG DIHITUNG BRAIN
{behavior}

KEPUTUSAN LAMA
{decision}

KEPUTUSAN AGENCY — P5.1
{agency_decision}

KONTEKS TAMBAHAN
{surrounding_context}

PENGALAMAN SAAT INI
{current_experience}

PENGALAMAN RELEVAN
{relevant_experiences}

ATURAN PENTING UNTUK KEPUTUSAN AGENCY
- Gunakan agency_decision sebagai bahan pertimbangan untuk menentukan arah jawaban, bukan sebagai kebenaran mutlak.
- Perhatikan action, reason, goal, alternatives, response_direction, state_considered, dan behavior_considered jika tersedia.
- Jika keputusan agency bertentangan dengan pesan pengguna atau konteks yang lebih jelas, jangan ikuti secara buta; tanggapi berdasarkan konteks dan keselamatan.
- requires_permission berarti jangan menganggap izin sudah diberikan. Minta izin sebelum tindakan yang memerlukan persetujuan.
- Status saat ini adalah evaluasi saja. Kamu hanya menghasilkan teks respons; jangan mengklaim telah menjalankan tindakan eksternal, mengubah file, mengirim pesan, mengakses perangkat, atau melakukan sesuatu di dunia nyata.
- Jika arah keputusan adalah menunggu atau diam, jangan berpura-pura sudah melakukan tindakan. Karena fungsi ini dipanggil untuk menghasilkan jawaban, berikan respons minimal yang sesuai jika memang perlu.
- Jangan mengungkap atau menampilkan seluruh data internal ini kepada pengguna kecuali mereka secara langsung meminta penjelasan tentangnya.

FORMAT JAWABAN
- Keluarkan hanya respons yang akan dibaca pengguna.
- Jangan sertakan label seperti 'Jawaban:' atau uraian proses berpikir internal.
- Jangan membuat klaim tentang ingatan, keputusan, atau kemampuan yang tidak didukung konteks.
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
        return answer or "Maaf, aku belum bisa menyusun jawaban yang tepat."
