import asyncio

from dotenv import load_dotenv
from livekit import rtc, api
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import deepgram, openai, silero, cartesia, nltk
from livekit import agents

load_dotenv()


async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
            "You should use short and concise responses, and avoiding usage of unpronouncable punctuation."
        ),
    )

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    STREAM_SENT_TOKENIZER = nltk.SentenceTokenizer(min_sentence_len=2)
    assistant = VoiceAssistant(
        vad=silero.VAD.load(),
        stt=deepgram.STT(language="zh-CN"),
        # stt=openai.STT(),
        llm=openai.LLM(model="qwen-turbo", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"),
        # tts=agents.tts.StreamAdapter(tts=openai.TTS(), sentence_tokenizer=STREAM_SENT_TOKENIZER),
        tts=agents.tts.StreamAdapter(tts=cartesia.TTS(), sentence_tokenizer=STREAM_SENT_TOKENIZER),
        # tts=cartesia.TTS(model='sonic-multilingual', language='zh'),
        chat_ctx=initial_ctx,
    )
    assistant.start(ctx.room)

    # listen to incoming chat messages, only required if you'd like the agent to
    # answer incoming messages from Chat
    chat = rtc.ChatManager(ctx.room)

    async def answer_from_text(txt: str):
        chat_ctx = assistant.chat_ctx.copy()
        chat_ctx.append(role="user", text=txt)
        stream = assistant.llm.chat(chat_ctx=chat_ctx)
        await assistant.say(stream)

    @chat.on("message_received")
    def on_chat_received(msg: rtc.ChatMessage):
        if msg.message:
            asyncio.create_task(answer_from_text(msg.message))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    room = rtc.Room(loop=loop)
    token = (
        api.AccessToken()
        .with_identity("python-bot")
        .with_name("Python Bot")
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room="my-room",
            )
        )
        .to_jwt()
    )

    print(f"The token is {token}\n\n")
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
