1| # Partner
2| 
3| This project is a Giftia-inspired emotional AI companion prototype.
4| 
5| The idea is not just a normal chatbot. It is designed to feel like a personal companion: it can greet the user, listen by voice, remember details, track mood and activity, form a personality, and r[...]
6| 
7| The project is inspired by the broader Giftia concept: a synthetic companion with identity, memory, personality, and emotional presence. In this repository, that idea is implemented as a small Pyth[...]
8| 
9| ## Project vision
10| 
11| The core concept behind this project is:
12| 
13| - a companion AI with a name and identity
14| - memory of the user and prior interactions
15| - a personality model that changes over time
16| - emotional state tracking such as happiness, curiosity, energy, and social mood
17| - conversation flow that feels personal instead of mechanical
18| - voice input and transcription support
19| - local LLM-based response generation via Ollama
20| 
21| This is intentionally a prototype and experimental project rather than a production-grade product.
22| 
23| ## Why it is called a Giftia project
24| 
25| The term "Giftia" here refers to an AI companion with a personality and emotional presence, not a literal executable program or a commercial product. The project is designed around the feeling of:
26| 
27| - companionship
28| - memory
29| - empathy
30| - emotional continuity
31| - gradual personal connection with a user
32| 
33| This is reflected across the codebase, especially in:
34| 
35| - `core/ai_memory.py` for identity, personality, values, and experiences
36| - `core/state.py` for mood and activity simulation
37| - `core/brain.py` for interpretation and decision-making
38| - `conversation/response.py` for empathetic, context-aware replies
39| 
40| ## Repository structure
41| 
42| ```text
43| .
44| ├── README.md
45| ├── .gitignore
46| └── ai.exe/
47|     ├── main.py
48|     ├── core/
49|     │   ├── ai_memory.py
50|     │   ├── audio_stream.py
51|     │   ├── brain.py
52|     │   ├── hearing.py
53|     │   ├── memory.py
54|     │   ├── perception.py
55|     │   ├── personality.py
56|     │   ├── state.py
57|     │   ├── voice_activity.py
58|     │   └── __init__.py
59|     ├── conversation/
60|     │   ├── history.py
61|     │   ├── response.py
62|     │   └── __init__.py
63|     ├── data/
64|     │   ├── conversation_history.json
64|     │   ├── memory.json
64|     │   └── __init__
65|     ├── llm/
66|     │   └── __init__.py
67|     ├── test/
68|     │   ├── test_audio_stream.py
69|     │   ├── test_voice_activity.py
70|     │   └── __init__
71|     └── __init__
72| ```
73| 
74| ## Main runtime (`ai.exe/main.py`)
75| 
76| This file is the entry point of the project. It initializes the assistant, creates the memory systems, launches the background state updater, asks for names if they are missing, and then starts th[...]
77| 
78| The flow is:
79| 
80| 1. create `Memory`
81| 2. create `AIMemory`
|82| 3. create `State`
|83| 4. create `ConversationHistory`
|84| 5. create `Brain`
|85| 6. create `Response`
|86| 7. ask for the user's and AI's names if required
|87| 8. accept chat input or voice input
|88| 9. process the input with the brain
|89| 10. build LLM context
|90| 11. generate a response
|91| 12. save history and memory
|92| 
|93| It supports both text chat and microphone voice input using `/voice`.
|94| 
|95| ## Core subsystem overview
|96| 
|97| ### `ai.exe/core/state.py`
|98| This file tracks the internal emotional state of the AI. The state includes:
|99| 
|100| - happiness
|101| - energy
|102| - curiosity
|103| - social level
|104| - current activity
|105| 
|106| The system can change those values based on events like user messages or periods of idleness. This gives the AI a simple but effective emotional model.
|107| 
|108| ### `ai.exe/core/brain.py`
|109| This is the central decision layer. It handles:
|110| 
|111| - intent detection
|112| - context analysis
|113| - memory analysis
|114| - AI experience detection
|115| - opinion and personality updates
|116| - response planning
|117| - LLM prompt context preparation
|118| 
|119| In other words, `Brain` acts like the AI's cognitive core.
|120| 
|121| ### `ai.exe/core/memory.py`
|122| This is a simple persistent memory store for general app data. It saves values like:
|123| 
|124| - user name
|125| - AI name
|126| - preferences
|127| 
|128| It uses JSON files under the `data/` directory, making the project stateful across runs.
|129| 
|130| ### `ai.exe/core/ai_memory.py`
|131| This is the more advanced long-term memory model. It holds:
|132| 
|133| - identity
|134| - personality traits
|135| - likes/dislikes
|136| - opinions
|137| - values
|138| - morality/principles
|139| - self-model
|140| - important events
|141| - experiences
|142| 
|143| This is where the giftia-like identity is actually modeled: the assistant is not just a response generator, it is an entity that keeps a memory of itself and its experiences.
|144| 
|145| ### `ai.exe/core/perception.py`
|146| This module keeps track of environmental and contextual awareness, including:
|147| 
|148| - current time and date
|149| - activity state
|150| - platform information
|151| - event detection
|152| - hearing and vision availability
|153| 
|154| It gives the companion a more alive and situational understanding of its environment.
|155| 
|156| ### `ai.exe/core/hearing.py`
|157| This is the speech pipeline. It uses:
|158| 
|159| - microphone capture
|160| - noise reduction
|161| - voice activity detection
|162| - normalization
|163| - Whisper transcription
|164| 
|165| This allows the assistant to hear the user and convert spoken words into text before processing them.
|166| 
|167| ### `ai.exe/core/audio_stream.py`
|168| This file provides continuous microphone streaming with a bounded queue. It is built for real-time capture and supports resource-aware audio handling.
|169| 
|170| ### `ai.exe/conversation/history.py`
|171| This stores the recent conversation history in JSON format and keeps only the most recent messages.
|172| 
|173| ### `ai.exe/conversation/response.py`
|174| This is the final text generation layer. It sends contextual information to Ollama and asks the model to act as the assistant while keeping style, identity, and safety constraints in mind.
|175| 
|176| The model used is:
|177| 
|178| ```python
|179| qwen3:latest
|180| ```
|181| 
|182| This means the assistant uses a local Ollama model to produce responses.
|183| 
|184| ## Data layer (`ai.exe/data`)
|185| 
|186| The `data/` folder stores the project's persistent state:
|187| 
|188| - `memory.json` for general memory data
|189| - `conversation_history.json` for chat logs
|190| 
|191| These files are created and updated during runtime.
|192| 
|193| ## Voice/interaction model
|194| 
|195| The project supports two interaction styles:
|196| 
|197| 1. normal text input
|198| 2. spoken voice input via microphone
|199| 
|200| The voice pipeline is designed to:
|201| 
|202| - capture audio
|203| - clean the signal
|204| - detect whether speech is present
|205| - transcribe to text
|206| - feed the result back into the normal conversation system
|207| 
|208| This allows the AI to function more like a companion than a terminal-only chat bot.
|209| 
|210| ## LLM and local runtime
|211| 
|212| The project depends on local Python libraries plus Ollama.
|213| 
|214| Typical runtime dependencies include:
|215| 
|216| - `numpy`
|217| - `sounddevice`
|218| - `scipy`
|219| - `noisereduce`
|220| - `whisper`
|221| - `ollama`
|222| 
|223| To run the project locally, you usually need:
|224| 
|225| ```bash
|226| ollama serve
|227| ollama pull qwen3:latest
|228| ```
|229| 
|230| Then run:
|231| 
|232| ```bash
|233| cd ai.exe
|234| python main.py
|235| ```
|236| 
|237| ## Design intent
|238| 
|239| This project is best understood as a Giftia-style companion AI prototype:
|240| 
|241| - it is conversational
|242| - it is memory-driven
|243| - it has a personality model
|244| - it tracks emotional state
|245| - it listens and responds using voice
|246| - it keeps persistent data on disk
|247| - it aims to feel personal and alive
|248| 
|249| It is not a full commercial assistant, but it captures a clear emotional-companion concept in code.
|250| 
|251| ## Conclusion
|252| 
|253| The `ai.exe` folder is the heart of the project. It contains an experimental AI companion prototype with:
|254| 
|255| - identity and memory
|256| - emotional state simulation
|257| - voice recognition
|258| - LLM-powered conversation
|259| - persistent data storage
|260| - a Giftia-inspired personal companion design
|261| 
|262| recomended to download ollama.cpp or just tune to your own llm
|263| 
|264| In short, this repository is a small, local implementation of a Giftia-inspired AI companion built as a Python project.
|265| 
