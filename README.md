# Speech Interface & TTS Voice Agent

A modular Python-based voice agent that combines **Speech-to-Text (STT), Large Language Model (LLM) responses, and Text-to-Speech (TTS)** to demonstrate an end-to-end voice interaction pipeline. The project supports multiple speech providers, offline mock testing, audio processing utilities, and latency evaluation.

## Overview

Voice interfaces enable users to interact with AI systems through spoken language rather than text alone. This project explores the core components of a voice-enabled AI assistant, from processing input audio and generating a response to synthesizing output audio.

The implementation uses a modular provider-based architecture, allowing different STT and TTS implementations to be selected through command-line arguments. Mock providers support local pipeline testing without requiring paid API calls.

## Key Features

- **Speech-to-Text (STT):** Transcribes input audio using supported speech recognition providers.
- **LLM-Based Response Generation:** Integrates language model responses into the voice interaction pipeline, with a mock response option for testing.
- **Text-to-Speech (TTS):** Converts generated responses into audio using supported synthesis providers.
- **Multiple Provider Options:** Supports OpenAI and local Whisper for STT, and OpenAI, ElevenLabs, and Piper for TTS, subject to provider configuration.
- **Offline Testing:** Mock STT, TTS, and response generation enable end-to-end testing without paid API calls.
- **Audio Utilities:** Includes audio file handling, sample audio generation, optional microphone recording, and local audio playback.
- **Latency Measurement:** Records STT, TTS, and total voice-agent processing latency.
- **TTS Evaluation Rubric:** Provides a structured scoring template for clarity, naturalness, latency, pronunciation, and avatar readiness.
- **Jupyter Notebook:** Includes a notebook for exploration and experimentation.

## System Architecture

The voice agent follows a modular processing pipeline:

```text
Input Audio
    |
    v
Speech-to-Text (STT)
    |
    v
Transcribed Text
    |
    v
LLM Response Generation
    |
    v
Generated Response Text
    |
    v
Text-to-Speech (TTS)
    |
    v
Output Audio
    |
    v
Latency and Result Reporting
```

### Pipeline Components

1. **Audio Input:** Accepts an audio file as input. A sample WAV file can be generated automatically when the default input file is missing.
2. **Speech Recognition:** Converts spoken input into text through the selected STT provider.
3. **Response Generation:** Produces a response using the configured language model or a deterministic mock response.
4. **Speech Synthesis:** Converts the response text into an audio file through the selected TTS provider.
5. **Performance Reporting:** Displays the transcript, response, audio output location, and measured processing latencies.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| AI and Language Models | OpenAI API |
| Speech-to-Text | OpenAI, local Whisper |
| Text-to-Speech | OpenAI, ElevenLabs, Piper |
| Audio Processing | NumPy, SoundFile, SoundDevice |
| Configuration | Python dotenv |
| Interactive Development | Jupyter Notebook |
| Testing | Python smoke test and mock providers |
| Version Control | Git and GitHub |

*Optional speech providers may require additional dependencies, model files, or system-level tools.*

## Project Structure

```text
speech-interface-tts-voice-agent/
│
├── app.py
├── audio_utils.py
├── evaluation_rubric.py
├── smoke_test.py
├── notebook.ipynb
│
├── stt_providers.py
├── tts_providers.py
├── voice_agent.py
│
├── requirements.txt
├── requirements_local_whisper_optional.txt
├── requirements_piper_optional.txt
├── .env.example
├── .gitignore
├── README.md
│
├── data/
│   └── sample_voice_question.wav
│
└── outputs/
```

**Note:** This is the intended project layout. Keep only files and folders that actually exist in your repository. Generated audio files and other temporary outputs do not need to be committed.

## Getting Started

### 1. Prerequisites

- Python 3.10 or a compatible version for the installed dependencies.
- Git.
- A terminal or IDE such as VS Code.
- API credentials for any cloud-based providers you intend to use.
- Additional dependencies for optional local speech recognition or synthesis.

### 2. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/speech-interface-tts-voice-agent.git
cd speech-interface-tts-voice-agent
```

Replace `YOUR_USERNAME` with your GitHub username.

### 3. Create a Virtual Environment

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

Use the actual filename in your repository if your dependency file is named differently. Optional providers may need separate installation steps.

### 5. Configure Environment Variables

For cloud-based integrations, create a local `.env` file in the project root and add the credentials required by the providers you use.

Example:

```dotenv
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

Only configure the credentials required for your chosen providers. Check the implementation for the exact environment variable names.

**Security:** Never commit your `.env` file, API keys, or other secrets to GitHub. Keep `.env` listed in `.gitignore`.

## Running the Application

The application exposes a command-line interface for selecting STT and TTS providers.

### 1. Run with Mock Providers

```bash
python app.py --stt mock --tts mock
```

This is the recommended starting point. It exercises the voice-agent pipeline using mock providers and does not require paid speech API calls.

### 2. Use OpenAI Speech-to-Text and Text-to-Speech

```bash
python app.py --stt openai --tts openai --input data/sample_voice_question.wav
```

Requires valid credentials and the relevant provider configuration.

### 3. Use OpenAI STT with ElevenLabs TTS

```bash
python app.py --stt openai --tts elevenlabs
```

Requires the credentials and configuration for both selected providers.

### 4. Use Local Whisper for STT

```bash
python app.py --stt local-whisper --tts openai
```

Install the optional Whisper dependencies and any required system tools before running this configuration.

### 5. Use Piper for TTS

```bash
python app.py --stt openai --tts piper
```

Piper may require a compatible installation and separately downloaded voice model files.

### Command-Line Arguments

| Argument | Purpose |
|---|---|
| `--stt` | Selects `mock`, `openai`, or `local-whisper` |
| `--tts` | Selects `mock`, `openai`, `elevenlabs`, or `piper` |
| `--input` | Specifies the input audio file |
| `--output` | Specifies the output audio path |
| `--mock-llm` | Uses deterministic response generation instead of the OpenAI LLM |

For provider-specific requirements, refer to the implementation and dependency files.

## Testing

The project includes a smoke test to verify the basic pipeline using mock providers.

Run:

```bash
python smoke_test.py
```

The smoke test generates sample input audio, runs a voice-agent turn using mock STT and TTS, checks that a transcript is returned, and verifies that an output audio file is created.

This test does not require paid API calls.

## Performance Evaluation

The project measures the latency of individual speech-processing stages and the overall voice-agent interaction.

The command-line application reports:

- STT latency in milliseconds.
- TTS latency in milliseconds.
- Total voice-agent processing latency.

The `evaluation_rubric.py` module provides a CSV-based evaluation template with the following dimensions:

| Evaluation Dimension | Purpose |
|---|---|
| Clarity | How understandable the generated speech is |
| Naturalness | How natural the synthesized voice sounds |
| Latency | Perceived or measured response speed |
| Pronunciation | Accuracy of spoken words |
| Avatar Readiness | Suitability of the speech output for an avatar-based interface |

The rubric uses a 1–5 scoring scale. The scores are intended to be filled in during evaluation; they are not precomputed performance results.

## Optional Components

### Local Whisper

The optional requirements file supports local speech recognition using Whisper. Installation may require FFmpeg and additional computational resources.

### Piper TTS

The optional Piper requirements file supports local text-to-speech synthesis. A compatible voice model may need to be downloaded separately.

### Microphone Recording and Audio Playback

The audio utilities include optional microphone recording and local audio playback functions. These features require compatible audio dependencies and operating-system permissions.

## Engineering Concepts Demonstrated

- Modular software design and provider abstraction.
- Integration of speech-processing APIs.
- Coordination of STT, LLM, and TTS components.
- Audio file generation and handling.
- Environment-based configuration and credential management.
- Latency instrumentation and performance reporting.
- Offline testing using mock implementations.
- Structured evaluation of synthesized speech.

## Limitations

- Cloud-based providers require network access and valid credentials.
- API usage may incur costs depending on the provider and account.
- Local Whisper and Piper require additional setup and suitable models.
- Mock mode is intended for development and pipeline testing, not for evaluating real speech-recognition accuracy or natural speech quality.
- Actual latency and speech quality depend on the provider, model, input audio, network conditions, and hardware.

## Future Improvements

- Add a real-time microphone-to-response interaction mode.
- Introduce automated evaluation of transcription quality and response latency.
- Add more speech providers through the existing modular architecture.
- Build a user interface for recording, playback, and transcript display.
- Improve error handling, logging, and automated test coverage.

## Learning Outcomes

This project provides practical experience in integrating speech technologies into a modular AI application. It demonstrates how audio input, language model responses, and speech synthesis can be combined into a single pipeline, while highlighting provider flexibility, testing, performance measurement, and evaluation.

## License

Choose and add an appropriate open-source license before distributing the project. If no license has been added, all rights remain reserved by default.

---

**Author:** Anudev SD

**Focus Areas:** Generative AI, AI Engineering, Speech Interfaces, and LLM Integration