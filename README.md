# Partner

Partner is a Python-based local AI companion prototype inspired by the emotional, memory-driven companion archetypes behind projects like Alma and Giftia.

The project is designed to feel more like a personal companion than a traditional chatbot: it keeps identity context, remembers user details, updates mood and activity, and can respond with a more human-like conversational flow.

## What this project does

- Maintains a persistent identity for the assistant
- Stores user and AI memory in local JSON files
- Tracks emotional state and activity over time
- Builds conversation context and response prompts from memory and recent history
- Supports text and voice input workflows
- Runs locally with Ollama for LLM generation
- Includes a life/development layer for goals, reflections, diary entries, and time context
- Includes experimental autonomous initiative behavior for idle conversational decisions

## Project goals

This repository is primarily a research and prototype project focused on:

- emotional companionship
- long-term memory and identity modeling
- personalized interaction patterns
- local-first AI behavior without cloud dependency
- experimentation with self-directed conversation and life context tracking

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
    │   ├── autonomous.py
    │   ├── brain.py
    │   ├── hearing.py
    │   ├── life.py
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
    │   ├── life.json
    │   ├── memory.json
    │   └── __init__
    ├── llm/
    │   └── __init__.py
    ├── test/
    │   ├── test_audio_stream.py
    │   ├── test_autonomous_response.py
    │   ├── test_voice_activity.py
    │   └── __init__
    └── __init__
```

## Requirements

- Python 3.10+
- Git
- Ollama installed and running locally

## Install dependencies

Use pip to install the project requirements:

```bash
pip install numpy sounddevice scipy noisereduce openai-whisper ollama
```

If your environment is missing additional packages, install them individually as needed.

## Start Ollama

```bash
ollama serve
```

Then pull the local model used by the project:

```bash
ollama pull qwen3:latest
```

## Run the app

From the repository root:

```bash
cd ai.exe
python main.py
```

On first launch, the app may ask for:

- the user's name
- the AI companion's name

These values are stored in the local data files and reused on later runs.

## Example interaction

```text
Hello
Partner: Hi! Nice to meet you. What's your name?
```

The assistant is built to behave more like a companion than a plain terminal chatbot, with state, memory, and emotional context shaping the tone and content of responses.

## Built-in commands

The project includes several local runtime commands:

- `/diary <note>`
- `/diary show`
- `/goal <title>`
- `/goals`
- `/goal-done <goal-id>`
- `/reflect <observation> | <lesson> | <next step>`
- `/reflections`
- `/milestones`
- `/time`
- `/initiative status | on | off | now`
- `/voice`

These commands are handled locally and are intended for experimentation and personal interaction rather than external service calls.

## Data storage

The app persists its local state under `ai.exe/data/`: 

- `memory.json` for general memory data
- `conversation_history.json` for chat logs
- `life.json` for diary, goals, reflections, and time metadata

## Notes

This is a prototype and experimental project, not a production-ready product. It is intended as a local, personal AI companion framework for experimentation and learning.

The repository is primarily Python-based and is centered around the `ai.exe` system, which contains the core companion logic, memory, state simulation, voice processing, and local LLM reasoning layers.

## License

This repository does not currently declare a license file in the root. If you plan to reuse or distribute the project, verify the intended licensing before publication or commercial use.

## Summary

Partner is a local, Giftia-inspired AI companion project built in Python. It focuses on identity, memory, emotional context, life tracking, and a more personal interaction style for a terminal-based companion experience.
