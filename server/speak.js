import edgeTTS from "edge-tts";
import player from "play-sound";

const audio = player();

export async function speak(text) {

    const file = "voice.mp3";

    await edgeTTS.tts({
        text,
        voice: "en-IN-NeerjaNeural",
        file
    });

    audio.play(file);
}