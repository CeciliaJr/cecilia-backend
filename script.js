const chatBox = document.getElementById("chat");
const sendButton = document.getElementById("sendButton");
const micButton = document.getElementById("mic-button");
const input = document.getElementById("messageInput");

console.log("Cecilia script v2.0 carregado");  // debug pra gente ver no console

// ================== VOZ DA CECÍLIA ==================

let ceciliaVoice = null;

function loadVoices() {
    const voices = window.speechSynthesis.getVoices();
    console.log("Vozes disponíveis:", voices);

    // 1) tenta pegar voz feminina em PT
    ceciliaVoice =
        voices.find(v =>
            v.lang.toLowerCase().startsWith("pt") &&
            /female|mulher|girl|crianca|child|brazil|brasil|portugu/i.test(v.name)
        )
        // 2) se não achar, pega qualquer PT
        || voices.find(v => v.lang.toLowerCase().startsWith("pt"))
        // 3) último fallback: primeira voz
        || voices[0];

    console.log("Voz escolhida para Cecília:", ceciliaVoice);
}

window.speechSynthesis.onvoiceschanged = loadVoices;
loadVoices();

// ================== CHAT ==================

function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.classList.add("message", sender, "bubble-enter"); // <--- aqui
    msg.innerText = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
    return msg;
}


// Enviar texto digitado
sendButton.addEventListener("click", sendMessage);
input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    addMessage(text, "user");
    input.value = "";
    talkToBackend(text);
}

// Conectar com o backend da Cecília
async function talkToBackend(message) {
    const thinkingMsg = addMessage("Cecília está pensando... ✨", "cecilia");

    try {
        const res = await fetch("https://cecilia-backend-xb86.onrender.com/cecilia", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        });

        const data = await res.json();

        // data pode ser {reply: "..."} ou uma string JSON
        let reply = null;

        if (data && typeof data === "object" && "reply" in data) {
            reply = data.reply;
        } else {
            reply = data;
        }

        // se por algum motivo ainda vier um JSON em string, tentamos parsear
        if (typeof reply === "string" && reply.trim().startsWith("{")) {
            try {
                const parsed = JSON.parse(reply);
                if (parsed && typeof parsed === "object" && "reply" in parsed) {
                    reply = parsed.reply;
                }
            } catch (e) {
                // se quebrar o parse, segue com reply como está
            }
        }

        if (!reply || typeof reply !== "string") {
            reply = "Desculpa, Audrey 💜 tive um errinho aqui. Pode tentar de novo?";
        }

        // remove o "pensando..."
        if (thinkingMsg && thinkingMsg.parentNode) {
            chatBox.removeChild(thinkingMsg);
        }

        addMessage(reply, "cecilia");
        speak(reply);

    } catch (err) {
        console.error("Erro falando com o backend:", err);

        if (thinkingMsg && thinkingMsg.parentNode) {
            chatBox.removeChild(thinkingMsg);
        }

        addMessage("Ops, tive um errinho aqui. Tenta de novo em um segundinho, tá? 💜", "cecilia");
    }
}

// ================== FALA (voz da Cecília) ==================

function speak(text) {
    if (!("speechSynthesis" in window)) {
        console.warn("SpeechSynthesis não suportado neste navegador.");
        return;
    }

    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "pt-BR";
    utter.pitch = 1.2;   // um pouquinho mais agudo
    utter.rate = 1.05;
    utter.volume = 1;

    if (ceciliaVoice) {
        utter.voice = ceciliaVoice;
    }

    speechSynthesis.speak(utter);
}

// ================== GRAVAÇÃO DE VOZ ==================

let recognition;
if ("webkitSpeechRecognition" in window) {
    recognition = new webkitSpeechRecognition();
    recognition.lang = "pt-BR";
    recognition.onresult = function(event) {
        const text = event.results[0][0].transcript;
        addMessage(text, "user");
        talkToBackend(text);
    };
}

micButton.addEventListener("click", () => {
    if (recognition) recognition.start();
});
