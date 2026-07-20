from gtts import gTTS
def tts(text, filename):
    tts = gTTS(text=text, lang='en')
    tts.save(f"{filename}.mp3")
    return f"{filename}.mp3"
