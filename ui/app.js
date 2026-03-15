const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const messagesContainer = document.getElementById('messages');
const welcomeScreen = document.getElementById('welcome-screen');
const typingIndicator = document.getElementById('typing-indicator');
const charVal = document.getElementById('char-val');
const themeToggle = document.getElementById('theme-toggle');

// Textarea auto-resize
chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = (chatInput.scrollHeight) + 'px';
    charVal.innerText = chatInput.value.length;
});

// Handle Send
const handleSend = async () => {
    const query = chatInput.value.trim();
    if (!query) return;

    // Remove welcome screen on first message
    if (welcomeScreen.style.display !== 'none') {
        welcomeScreen.style.display = 'none';
    }

    // Add user message to UI
    appendMessage(query, 'user');
    chatInput.value = '';
    chatInput.style.height = 'auto';
    charVal.innerText = '0';

    // Show typing indicator
    typingIndicator.style.display = 'flex';
    messagesContainer.appendChild(typingIndicator);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();

        // Hide typing indicator
        typingIndicator.style.display = 'none';

        // Add bot message
        appendMessage(data.answer, 'bot');
    } catch (error) {
        typingIndicator.style.display = 'none';
        appendMessage("Sorry, I'm having trouble connecting to the server. Please ensure the backend is running.", 'bot');
    }
};

sendBtn.addEventListener('click', handleSend);
chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
});

// Helper to append messages
function appendMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    // Process text for highlighting URLs
    const urlPattern = /https?:\/\/[^\s]+/g;
    let processedText = text.replace(/\n/g, '<br>');

    // Find URL for citation button
    const urls = text.match(urlPattern);
    let citationHtml = '';

    if (urls && urls.length > 0) {
        const lastUrl = urls[urls.length - 1];
        // Remove the URL text from processedText if it's the citation
        if (text.includes("Last updated from sources:")) {
            processedText = processedText.split("Last updated from sources:")[0];
            citationHtml = `<a href="${lastUrl}" target="_blank" class="citation-btn">
                <i class="fa-solid fa-link"></i> View Official Source
            </a>`;
        }
    }

    messageDiv.innerHTML = `
        <div class="message-content">
            ${processedText}
            ${citationHtml}
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Quick Query function
function sendQuickQuery(query) {
    chatInput.value = query;
    handleSend();
}

// Theme Toggle
themeToggle.addEventListener('click', () => {
    const body = document.body;
    const isDark = body.getAttribute('data-theme') === 'dark';
    body.setAttribute('data-theme', isDark ? 'light' : 'dark');
    themeToggle.querySelector('i').className = isDark ? 'fa-solid fa-moon' : 'fa-solid fa-sun';
    themeToggle.querySelector('span').innerText = isDark ? 'Dark Mode' : 'Light Mode';
});

// Fetch Metadata (Phase 5)
async function fetchMetadata() {
    const syncStatus = document.getElementById('sync-status').querySelector('span');
    try {
        const response = await fetch('/metadata');
        const data = await response.json();
        if (data.metadata && data.metadata.last_updated) {
            syncStatus.innerText = `Last Synced: ${data.metadata.last_updated}`;
        } else {
            syncStatus.innerText = "Last Synced: Unknown";
        }
    } catch (error) {
        console.error("Error fetching metadata:", error);
        syncStatus.innerText = "Last Synced: Offline";
    }
}

// Initial Load
window.addEventListener('DOMContentLoaded', fetchMetadata);
