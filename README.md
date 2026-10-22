# Partner

This repository contains a local prototype of a conversational "Giftia", not an AI assistant, but a  digital human. The main logic lives inside the `ai.exe` folder, which is a Python project directory rather than a literal Windows executable.

The project combines:
- a text-based chat loop
- a persistent memory system
- a simulated emotional/state model
- voice capture and speech transcription
- a large language model response layer via Ollama

The result is a small personal AI prototype that can greet a user, remember names and preferences, track mood/activity, and respond using an LLM.

## Overview

The project is designed around a simple runtime loop:

1. initialize memory and AI memory
2. ask for user and AI names
3. start a background state updater
4. accept chat input or voice input
5. let the brain interpret the message
6. enrich context with memory and state
7. generate a reply from the LLM
8. save conversation history and memory updates

This is a research/demo assistant rather than a production service.

## Folder structure

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

## What is inside `ai.exe`?

### `main.py`
This is the entry point for the application.

It does the following:
- creates the memory stores
- creates the AI state object and conversation history
- starts a background thread that updates activity/state every 0.5 seconds
- asks for the user's name and the AI's name if they are not already stored
- starts a chat loop
- supports `/voice` to accept microphone input
- sends user input into the brain for interpretation and generation
- stores learned memory and conversation history

The main loop is roughly:

```python
memory = Memory()
ai_memory = AIMemory()
state = State()
history = ConversationHistory()
brain = Brain(state, history, memory, ai_memory)
response = Response()
```

Then each message is processed by:

```python
thought = brain.think(user_input)
llm_context = brain.build_llm_context(thought, user_input)
ai_message = response.generate(llm_context)
```

### `core/brain.py`
This is the central intelligence layer. It coordinates:
- state changes
- conversation understanding
- memory updates
- perception data
- LLM context building

It decides how the AI should interpret the message, what memories are relevant, what emotional state to reflect, and how to craft the final response context.

In short, `Brain` is the "decision engine" of the assistant.

### `core/state.py`
This file models the internal state of the AI.

Attributes include:
- happiness
- energy
- curiosity
- social
- activity
- last activity change

The state system can:
- increase/decrease mood values
- set activity like `talking`, `thinking`, or `idle`
- compute a current mood such as `happy`, `sad`, `curious`, `tired`, or `calm`

This makes the AI feel more alive and context-aware, instead of behaving like a static chatbot.

### `core/memory.py`
This is a lightweight JSON-based memory store for user and app data.

The file stores values such as:
- `user_name`
- `ai_name`
- `preferences`

It has helper methods such as:
- `get(key)`
- `set(key, value)`
- `remember(key, value)`
- `remember_preference(type, value)`

This is the simple, persistent memory for everyday application data.

### `core/ai_memory.py`
This is the deeper memory system for the AI itself.

It stores structured information such as:
- AI identity (`name`, `status`, `instance_id`)
- operational age / activation time
- likes and dislikes
- opinions
- personality
- values
- morality / boundaries
- self-model
- experiences
- important events
- development history

This file is much more advanced than the basic memory store and is where the assistant keeps a more human-like personality and long-term sense of self.

### `core/perception.py`
This is the environment awareness layer.

It monitors:
- current time of day and date
- activity status
- platform/environment information
- audio device availability
- input availability and state changes

It can detect change events such as:
- activity_changed
- period_changed

This gives the assistant contextual awareness beyond just raw chat text.

### `core/hearing.py`
This module implements the voice pipeline.

It uses:
- `sounddevice` for microphone capture
- `numpy` for numerical processing
- `scipy.signal` for filtering
- `noisereduce` for noise reduction
- `whisper` for transcription

It performs:
- audio recording
- resampling to 16 kHz
- filtering and noise suppression
- speech detection
- normalization
- Whisper transcription into text

The result is a structured response with information about:
- success/failure
- text transcription
- duration
- sample rate
- signal amplitude metrics

This is the backbone for spoken interaction.

### `core/audio_stream.py`
This file creates a continuous microphone stream using a queue.

It is meant for ongoing audio capture and is designed to keep only bounded recent audio instead of growing without limit.

Key features:
- background audio capture thread
- queue-based buffering
- dropping old blocks when overloaded
- stream start/stop lifecycle

This is useful for real-time or streaming voice processing.

### `core/voice_activity.py`
This implements voice activity detection logic and verification behaviors for voice-based input.

It helps determine whether the microphone is receiving speech and whether the AI should treat the signal as meaningful input.

### `conversation/history.py`
This stores the running chat logs in a JSON file.

Behavior:
- loads `data/conversation_history.json`
- appends new messages
- keeps only the most recent 300 interactions
- saves the history back to disk

This provides short-term conversation memory without letting the saved data become unbounded.

### `conversation/response.py`
This is the LLM response generation layer.

It sends a structured system prompt to Ollama using the model:

```python
self.model = "qwen3:latest"
```

The system prompt includes:
- AI identity
- user name
- current state
- stored memory
- personality traits
- values and opinions
- current and relevant experiences
- agency decision context
- rules for safe and natural dialogue

This is the main text-generation interface for the assistant.

### `llm/`
This directory is present but currently minimal. It appears to be reserved for future LLM abstractions or wrappers.

### `data/`
This directory stores JSON memory and chat logs.

Files:
- `memory.json` — persistent simple memory
- `conversation_history.json` — recent chat log

The project creates these files automatically when it runs.

### `test/`
This folder contains lightweight tests for the voice-related features.

Examples:
- `test_audio_stream.py`
- `test_voice_activity.py`

These appear to validate microphone stream handling and voice activity detection behavior.

## Runtime behavior

When the app starts, it follows this flow:

1. Create `Memory` and `AIMemory`
2. Create `State` and `ConversationHistory`
3. Create `Brain` and `Response`
4. Ensure the AI has a name
5. Start state updater thread
6. Prompt for user name and AI name if missing
7. Print a greeting
8. Enter input loop
9. If user types `/voice`, capture microphone input and transcribe it
10. Pass the message into `brain.think()`
11. Build a context object using the user's message, memory, identity, and state
12. Call the LLM to generate a reply
13. Print the response and store the message in conversation history

## Voice pipeline summary

The voice workflow is:

- microphone records audio
- audio is normalized and filtered
- noise is reduced
- speech segments are detected
- Whisper transcribes the speech to text
- text is fed back into the normal conversational system

This is one of the most important parts of the project because it allows the assistant to listen instead of only reading text.

## Memory model summary

The project has two memory layers:

1. `Memory` — simple persistent dictionary for app data
2. `AIMemory` — structured long-term memory for identity, personality, experiences, and values

Together they allow the assistant to:
- remember names
- keep preferences
- learn from previous interactions
- maintain identity over time
- store emotionally important events

## LLM integration

The app uses Ollama with the model:

```text
qwen3:latest
```

This means the assistant relies on a local or configured Ollama model to generate natural conversation responses. The Python layer prepares the right prompt and passes it into the model.

## Requirements

The project depends on Python libraries such as:
- `numpy`
- `sounddevice`
- `scipy`
- `noisereduce`
- `whisper`
- `ollama`

You should also have Ollama installed and running locally, for example:

```bash
ollama serve
ollama pull qwen3:latest
```

## How to run

Run the project from the `ai.exe` folder so that relative paths such as `data/memory.json` resolve correctly:

```bash
cd ai.exe
python main.py
```

If you run from the repository root, the relative paths may not resolve as expected because the project stores its data under a local `data/` folder relative to the execution directory.

## Design note

This project is best understood as a prototype AI companion rather than a polished packaged app. It blends:
- conversational AI
- memory persistence
- emotional simulation
- voice processing
- local LLM usage

The architecture is intentionally modular, which makes it easier to extend with additional behaviors such as:
- more advanced planning
- tool calling
- file management
- image or environment perception
- better emotional models

## Conclusion

The `ai.exe` folder is the core of this project. It contains a small, self-contained AI assistant prototype that can:
- talk to a user
- listen through the microphone
- remember details
- track internal state
- use a local LLM to generate responses
- persist conversation and memory data to disk

In short, `ai.exe` is the brain and runtime environment of the Partner project.
