

// ======== DOM Elements =========
const rpmValueElement = document.getElementById("rpm-value");
const rpmTextElement  = document.querySelector(".RPM-text");
const backgrounds = {
  work : document.getElementById("bg-work"),
  turbo: document.getElementById("bg-turbo"),
  jail : document.getElementById("bg-jail"),
};

// ======== Global State =========
let e_stop     = false;
let rpmSocket  = null;
let estopSocket= null;

// ======== Helper: change background =========
function changeBackground(bgToActivate) {
  Object.values(backgrounds).forEach(bg => bg.classList.remove("active"));
  if (bgToActivate) bgToActivate.classList.add("active");
}

// ======== Connect to RPM Socket =========
function connectRpmSocket() {
  rpmSocket = new WebSocket("ws://Schaublin.local:8000");

  rpmSocket.onopen = () => {
    console.log("[RPM] Connected");
  };

  rpmSocket.onmessage = (event) => {
    // Ignore keep-alive "pong"
    if (event.data === "pong") return;

    // If server sends "ping," respond with "pong"
    if (event.data === "ping") {
      rpmSocket.send("pong");
      return;
    }

    // Don’t update display if E-Stop is active
    if (e_stop) return;

    // Handle the RPM value
    const rpm = parseInt(event.data, 10) || 0;
    rpmValueElement.textContent = rpm;

    if (rpm > 2000) {
      rpmValueElement.style.color = "yellow";
      changeBackground(backgrounds.turbo);
    } else {
      rpmValueElement.style.color = "white";
      changeBackground(backgrounds.work);
    }
  };

  // On close or error, try reconnecting after short delay
  rpmSocket.onclose = () => {
    console.log("[RPM] Disconnected – retry in 2s");
    setTimeout(connectRpmSocket, 2000);
  };

  rpmSocket.onerror = (err) => {
    console.error("[RPM] Socket error:", err);
    // Close before reconnecting to ensure a clean state
    rpmSocket.close();
  };
}

// ======== Connect to E-Stop Socket =========
function connectEstopSocket() {
  estopSocket = new WebSocket("ws://Schaublin.local:8002");

  estopSocket.onopen = () => {
    console.log("[E-Stop] Connected");
  };

  estopSocket.onmessage = (event) => {
    // Ignore keep-alive "pong"
    if (event.data === "pong") return;

    // If server sends "ping," respond with "pong"
    if (event.data === "ping") {
      estopSocket.send("pong");
      return;
    }

    // If E-Stop is triggered
    if (event.data === "1") {
      e_stop = true;
      rpmValueElement.style.color = "red";
      rpmValueElement.textContent = "Not AUS!!!";
      changeBackground(backgrounds.jail);
      rpmTextElement.style.display = "none";
    }
    // If E-Stop is released
    else if (event.data === "0") {
      e_stop = false;
      rpmValueElement.textContent = "...";
      rpmValueElement.style.color = "white";
      changeBackground(backgrounds.work);
      rpmTextElement.style.display = "inline";
    }
  };

  estopSocket.onclose = () => {
    console.log("[E-Stop] Disconnected – retry in 2s");
    setTimeout(connectEstopSocket, 2000);
  };

  estopSocket.onerror = (err) => {
    console.error("[E-Stop] Socket error:", err);
    estopSocket.close();
  };
}

// ======== Periodic Keep-Alive Ping (optional) =========
setInterval(() => {
  if (rpmSocket && rpmSocket.readyState === WebSocket.OPEN) {
    rpmSocket.send("ping");
  }
  if (estopSocket && estopSocket.readyState === WebSocket.OPEN) {
    estopSocket.send("ping");
  }
}, 5000); // ping every 5 seconds

// ======== Initialize both sockets on page load =========
connectRpmSocket();
connectEstopSocket();
