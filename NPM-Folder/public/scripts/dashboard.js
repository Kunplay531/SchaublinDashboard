// ======== DOM Elements =========
const rpmValueElement = document.getElementById("rpm-value");
const rpmTextElement  = document.querySelector(".RPM-text");
const connectionPopup = document.getElementById("connection-popup");

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
  rpmSocket = new WebSocket("ws://schaublin.local:8000");

  rpmSocket.onopen = () => {
    console.log("[RPM] Connected");
  };

  rpmSocket.onmessage = (event) => {
    if (event.data === "pong") return;
    if (event.data === "ping") {
      rpmSocket.send("pong");
      return;
    }
    if (e_stop) return;

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

  rpmSocket.onclose = () => {
    console.log("[RPM] Disconnected – retry in 2s");
    setTimeout(connectRpmSocket, 2000);
  };

  rpmSocket.onerror = (err) => {
    console.error("[RPM] Socket error:", err);
    rpmSocket.close();
  };
}

// ======== Connect to E-Stop Socket (only if env var is set) =========
function connectEstopSocket() {
  const estopUrl = window.ESTOP_SOCKET_URL;

  if (!estopUrl) {
    console.warn("[E-Stop] Skipping connection – no ESTOP_SOCKET_URL defined");
    return;
  }

  estopSocket = new WebSocket(estopUrl);

  estopSocket.onopen = () => {
    console.log("[E-Stop] Connected to", estopUrl);
  };

  estopSocket.onmessage = (event) => {
    if (event.data === "pong") return;
    if (event.data === "ping") {
      estopSocket.send("pong");
      return;
    }

    if (event.data === "1") {
      e_stop = true;
      rpmValueElement.style.color = "red";
      rpmValueElement.textContent = "Not AUS!!!";
      changeBackground(backgrounds.jail);
      rpmTextElement.style.display = "none";
    } else if (event.data === "0") {
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



let serverReachable = true;

function checkServerReachability() {
  fetch("/", { method: "HEAD", cache: "no-store" })
    .then(() => {
      if (!serverReachable) {
        console.log("[Server] Connection restored.");
        serverReachable = true;
        connectionPopup.classList.add("hidden"); // Hides the popup
      }
    })
    .catch(() => {
      if (serverReachable) {
        console.warn("[Server] Server not reachable!");
        serverReachable = false;
        connectionPopup.classList.remove("hidden"); // Shows the popup
      }
    });
}

document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") {
    console.log("[Page] Became visible – checking connections");

    checkServerReachability(); // force a check immediately

    if (!rpmSocket || rpmSocket.readyState !== WebSocket.OPEN) {
      connectRpmSocket();
    }
    if (window.ESTOP_SOCKET_URL && (!estopSocket || estopSocket.readyState !== WebSocket.OPEN)) {
      connectEstopSocket();
    }
  }
});


// ======== Initialize both sockets on page load =========
connectRpmSocket();
connectEstopSocket(); // will be skipped if env var is not defined
setInterval(checkServerReachability, 5000); // every 5 seconds
