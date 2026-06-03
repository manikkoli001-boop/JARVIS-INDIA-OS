import { askJarvis } from "./local-ai.js";

async function test() {
    const response = await askJarvis("Hello Jarvis");

    console.log("🚀 LOCAL AI ONLINE");
    console.log(response);
}

test();