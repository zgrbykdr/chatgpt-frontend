async function sendMessage() {
    const message = document.getElementById("message").value;
    if (!message) return;

    const response = await fetch("https://chatgpt-backend.onrender.com/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    });

    const data = await response.json();
    document.getElementById("response").innerText = data.response || "Hata oluştu!";
}
