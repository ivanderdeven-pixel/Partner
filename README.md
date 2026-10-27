# Partner

This project is a Giftia-inspired emotional AI companion prototype.

The idea is not just a normal chatbot. It is designed to feel like a personal companion: it can greet the user, listen by voice, remember details, track mood and activity, form a personality, and respond in a more human-like and emotionally aware way.

The project is inspired by the broader Giftia concept: a synthetic companion with identity, memory, personality, and emotional presence. In this repository, that idea is implemented as a small Python-based prototype inside the `ai.exe` folder.

## Project vision

The core concept behind this project is:

- a companion AI with a name and identity
- memory of the user and prior interactions
- a personality model that changes over time
- emotional state tracking such as happiness, curiosity, energy, and social mood
- conversation flow that feels personal instead of mechanical
- voice input and transcription support
- local LLM-based response generation via Ollama

This is intentionally a prototype and experimental project rather than a production-grade product.

## Why it is called a Giftia project

The term "Giftia" here refers to an AI companion with a personality and emotional presence, not a literal executable program or a commercial product. The project is designed around the feeling of:

- companionship
- memory
- empathy
- emotional continuity
- gradual personal connection with a user

This is reflected across the codebase, especially in:

- `core/ai_memory.py` for identity, personality, values, and experiences
- `core/state.py` for mood and activity simulation
- `core/brain.py` for interpretation and decision-making
- `conversation/response.py` for empathetic, context-aware replies

## Repository structure

```text
.
├── README.md
├── .gitignore
└── ai.exe/
    ├── main.py
    ├── core/
    │   ├── ai_memory.py
    │   ├── audio_stream.py
    │   ├── brain.py
    │   ├── hearing.py
    │   ├── memory.py
    │   ├── perception.py
    │   ├── personality.py
    │   ├── state.py
    │   ├── voice_activity.py
    │   └── __init__.py
    ├── conversation/
    │   ├── history.py
    │   ├── response.py
    │   └── __init__.py
    ├── data/
    │   ├── conversation_history.json
    │   ├── memory.json
    │   └── __init__
    ├── llm/
    │   └── __init__.py
    ├── test/
    │   ├── test_audio_stream.py
    │   ├── test_voice_activity.py
    │   └── __init__
    └── __init__
```

## Main runtime (`ai.exe/main.py`)

This file is the entry point of the project. It initializes the assistant, creates the memory systems, launches the background state updater, asks for names if they are missing, and then starts the conversation loop.

The flow is:

1. create `Memory`
2. create `AIMemory`
3. create `State`
4. create `ConversationHistory`
5. create `Brain`
6. create `Response`
7. ask for the user's and AI's names if required
8. accept chat input or voice input
9. process the input with the brain
10. build LLM context
11. generate a response
12. save history and memory

It supports both text chat and microphone voice input using `/voice`.

## Core subsystem overview

### `ai.exe/core/state.py`
This file tracks the internal emotional state of the AI. The state includes:

- happiness
- energy
- curiosity
- social level
- current activity

The system can change those values based on events like user messages or periods of idleness. This gives the AI a simple but effective emotional model.

### `ai.exe/core/brain.py`
This is the central decision layer. It handles:

- intent detection
- context analysis
- memory analysis
- AI experience detection
- opinion and personality updates
- response planning
- LLM prompt context preparation

In other words, `Brain` acts like the AI's cognitive core.

### `ai.exe/core/memory.py`
This is a simple persistent memory store for general app data. It saves values like:

- user name
- AI name
- preferences

It uses JSON files under the `data/` directory, making the project stateful across runs.

### `ai.exe/core/ai_memory.py`
This is the more advanced long-term memory model. It holds:

- identity
- personality traits
- likes/dislikes
- opinions
- values
- morality/principles
- self-model
- important events
- experiences

This is where the giftia-like identity is actually modeled: the assistant is not just a response generator, it is an entity that keeps a memory of itself and its experiences.

### `ai.exe/core/perception.py`
This module keeps track of environmental and contextual awareness, including:

- current time and date
- activity state
- platform information
- event detection
- hearing and vision availability

It gives the companion a more alive and situational understanding of its environment.

### `ai.exe/core/hearing.py`
This is the speech pipeline. It uses:

- microphone capture
- noise reduction
- voice activity detection
- normalization
- Whisper transcription

This allows the assistant to hear the user and convert spoken words into text before processing them.

### `ai.exe/core/audio_stream.py`
This file provides continuous microphone streaming with a bounded queue. It is built for real-time capture and supports resource-aware audio handling.

### `ai.exe/conversation/history.py`
This stores the recent conversation history in JSON format and keeps only the most recent messages.

### `ai.exe/conversation/response.py`
This is the final text generation layer. It sends contextual information to Ollama and asks the model to act as the assistant while keeping style, identity, and safety constraints in mind.

The model used is:

```python
qwen3:latest
```

This means the assistant uses a local Ollama model to produce responses.

## Data layer (`ai.exe/data`)

The `data/` folder stores the project's persistent state:

- `memory.json` for general memory data
- `conversation_history.json` for chat logs

These files are created and updated during runtime.

## Voice/interaction model

The project supports two interaction styles:

1. normal text input
2. spoken voice input via microphone

The voice pipeline is designed to:

- capture audio
- clean the signal
- detect whether speech is present
- transcribe to text
- feed the result back into the normal conversation system

This allows the AI to function more like a companion than a terminal-only chat bot.

## LLM and local runtime

The project depends on local Python libraries plus Ollama.

Typical runtime dependencies include:

- `numpy`
- `sounddevice`
- `scipy`
- `noisereduce`
- `whisper`
- `ollama`

To run the project locally, you usually need:

```bash
ollama serve
ollama pull qwen3:latest
```

Then run:

```bash
cd ai.exe
python main.py
```

## Design intent

This project is best understood as a Giftia-style companion AI prototype:

- it is conversational
- it is memory-driven
- it has a personality model
- it tracks emotional state
- it listens and responds using voice
- it keeps persistent data on disk
- it aims to feel personal and alive

It is not a full commercial assistant, but it captures a clear emotional-companion concept in code.

## Conclusion

The `ai.exe` folder is the heart of the project. It contains an experimental AI companion prototype with:

- identity and memory
- emotional state simulation
- voice recognition
- LLM-powered conversation
- persistent data storage
- a Giftia-inspired personal companion design

recomended to download ollama.cpp or just tune to your own llm

In short, this repository is a small, local implementation of a Giftia-inspired AI companion built as a Python project.
