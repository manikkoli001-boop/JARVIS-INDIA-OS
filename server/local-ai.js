import axios from "axios";

export async function askJarvis(message) {
    try {
        const response = await axios.post(
            "http://localhost:11434/api/generate",
            {
                model: "phi3",
                prompt: message,
                stream: false
            }
        );

        return response.data.response;

    } catch (error) {
        console.log(error);
        return "❌ Ollama not running";
    }
}