const rpmValueElement = document.getElementById("rpm-value");
const rpmContainer = document.querySelector(".RPMcontainer");
const rpmTextElement = document.querySelector(".RPM-text");

// Background layers (preloaded for instant switch)
const backgrounds = {
    work: document.getElementById("bg-work"),
    turbo: document.getElementById("bg-turbo"),
    jail: document.getElementById("bg-jail")
};

let e_stop = 0;
let rpmSocket = null;
let estopSocket = null;
let pingInterval = null;
let reconnectInterval = null;
let reconnectAttempts = {};

function changeBackground(activeBg) {
    // Remove 'active' class from all backgrounds
    Object.values(backgrounds).forEach(bg => bg.classList.remove("active"));

    // Add 'active' class to the selected background
    activeBg.classList.add("active");
}

// Function to initialize WebSockets
function initializeSockets() {
    connectRpmSocket();
    connectEstopSocket();
    startHeartbeat();
    startConnectionMonitor();
}


// Function to create and connect RPM WebSocket
function connectRpmSocket() {
    if (rpmSocket) rpmSocket.close(); // Ensure no duplicate connections
    rpmSocket = createWebSocket("ws://192.168.1.186:8000", handleRpmMessage);
}

// Function to create and connect E-Stop WebSocket
function connectEstopSocket() {
    if (estopSocket) estopSocket.close();
    estopSocket = createWebSocket("ws://192.168.1.186:8002", handleEStopMessage);
}

// Function to create WebSocket and handle reconnect logic
function createWebSocket(url, onMessageHandler) {
    const socket = new WebSocket(url);
    
    socket.onopen = () => {
        console.log(`WebSocket connected to ${url}`);
        reconnectAttempts[url] = 0; // Reset reconnect attempts
    };

    socket.onmessage = (event) => {
        if (event.data === "pong") return; // Ignore pong responses
        onMessageHandler(event);
    };

    socket.onclose = (event) => {
        console.log(`WebSocket disconnected from ${url}. Reason: ${event.reason} Code: ${event.code}`);
        if (url.includes("8000")) displayReconnectingMessage();
    };

    socket.onerror = (error) => {
        console.error(`WebSocket error on ${url}:`, error);
    };

    return socket;
}

// Function to handle reconnection
function reconnectSocket(url) {
    const attempt = reconnectAttempts[url] || 1;
    const delay = Math.min(3000 * attempt, 10000); // Exponential backoff (max 10s)

    console.log(`Attempting to reconnect to ${url} in ${delay / 1000} seconds...`);
    
    setTimeout(() => {
        if (url.includes("8000")) {
            connectRpmSocket();
            displayReconnectingMessage();
        } else if (url.includes("8002")) {
            connectEstopSocket();
        }
        reconnectAttempts[url] = attempt + 1; // Increase backoff
    }, delay);
}

// Function to continuously check WebSocket status and reconnect if necessary
function startConnectionMonitor() {
    if (reconnectInterval) clearInterval(reconnectInterval);
    reconnectInterval = setInterval(() => {
        if (!rpmSocket || rpmSocket.readyState === WebSocket.CLOSED) {
            reconnectSocket("ws://192.168.1.186:8000");
        }
        if (!estopSocket || estopSocket.readyState === WebSocket.CLOSED) {
            reconnectSocket("ws://192.168.1.186:8002");
        }
    }, 5000); // Check every 5 seconds
}

// Function to send heartbeat signals to keep connections alive
function startHeartbeat() {
    if (pingInterval) clearInterval(pingInterval);
    pingInterval = setInterval(() => {
        if (rpmSocket && rpmSocket.readyState === WebSocket.OPEN) rpmSocket.send("ping");
        if (estopSocket && estopSocket.readyState === WebSocket.OPEN) estopSocket.send("ping");
    }, 5000);
}

// Function to handle RPM WebSocket messages
function handleRpmMessage(event) {
    if (e_stop === 1) return;

    const rpmValue = event.data;
    rpmValueElement.textContent = rpmValue;

    if (rpmValue > 2000) {
        rpmValueElement.style.color = "yellow";
        changeBackground(backgrounds.turbo);
    } else {
        rpmValueElement.style.color = "white";
        changeBackground(backgrounds.work);
    }
}

// Function to handle E-Stop WebSocket messages
function handleEStopMessage(event) {
    const estopValue = event.data;
    if (estopValue === "1") {
        e_stop = 1;
        rpmValueElement.style.color = "red";
        rpmValueElement.textContent = "Not AUS!!!";
        changeBackground(backgrounds.jail);
        rpmTextElement.style.display = "none";
    } else if (estopValue === "0") {
        e_stop = 0;
        rpmValueElement.style.color = "white";
        rpmValueElement.textContent = "...";
        changeBackground(backgrounds.work);
        rpmTextElement.style.display = "inline";
    }
}


// Function to display reconnecting message
function displayReconnectingMessage() {
    if (e_stop === 1) return;
    rpmValueElement.textContent = "...";
    rpmValueElement.style.color = "red";
}

// Initialize sockets when the page loads
initializeSockets();
