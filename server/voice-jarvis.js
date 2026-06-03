import readlineSync from "readline-sync";
import { speak } from "./speak.js";
import { askJarvis } from "./local-ai.js";

async function startJarvis() {

    console.log("🤖 JARVIS VOICE ONLINE");

    while (true) {

        const userInput = readlineSync.question("🧑 You: ");

        if (userInput.toLowerCase() === "exit") {
            console.log("👋 Jarvis shutting down...");
            process.exit();
        }

        const response = await askJarvis(userInput);

        console.log("🤖 Jarvis:", response);

        await speak(response);
    }
}

startJarvis();