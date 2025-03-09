document.getElementById("send-chat").addEventListener("click", async () => {
    const input = document.getElementById("chat-input").value;
    if (!input) return;

    document.querySelector(".chat-messages").innerHTML += `<div class="user-message"><p>${input}</p></div>`;

    const response = await fetch("/chat", {
        method: "POST",
        body: JSON.stringify({ message: input }),
        headers: { "Content-Type": "application/json" }
    });

    const result = await response.json();
    document.querySelector(".chat-messages").innerHTML += `<div class="bot-message"><p>${result.response || "Error processing request"}</p></div>`;
});

document.getElementById("download-button").addEventListener("click", async () => {
    const url = document.getElementById("url-input").value;
    if (!url) return alert("Enter a valid URL");

    const response = await fetch("/download", {
        method: "POST",
        body: JSON.stringify({ url }),
        headers: { "Content-Type": "application/json" }
    });

    const result = await response.json();
    alert(result.message || result.error);
});

document.getElementById("generate-highlights").addEventListener("click", async () => {
    const url = document.getElementById("url-input").value;
    if (!url) return alert("Enter a valid URL");

    const response = await fetch("/generate_highlights", {
        method: "POST",
        body: JSON.stringify({ url }),
        headers: { "Content-Type": "application/json" }
    });

    const result = await response.json();
    alert(result.message || result.error);
});
