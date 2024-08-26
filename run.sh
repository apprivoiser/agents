export LIVEKIT_API_KEY=devkey
export LIVEKIT_API_SECRET=secret
export LIVEKIT_URL=http://localhost:7880
export DEEPGRAM_API_KEY=xxx
export OPENAI_API_KEY=xxx
export CARTESIA_API_KEY=xxx

#python examples/voice-assistant/stt.py
python examples/voice-assistant/minimal_assistant.py start
#pytest tests/test_stt.py
#python examples/speech-to-text/deepgram_stt.py start