import { exec } from "child_process";

function controlApp(command) {

    command = command.toLowerCase();

    if (command.includes("chrome")) {

        console.log("🌐 Opening Chrome...");
        exec("start chrome");
    }

    else if (command.includes("youtube")) {

        console.log("▶ Opening YouTube...");
        exec("start https://youtube.com");
    }

    else if (command.includes("whatsapp")) {

        console.log("💬 Opening WhatsApp...");
        exec("start https://web.whatsapp.com");
    }

    else {

        console.log("❌ Unknown app");
    }
}

controlApp("open chrome");