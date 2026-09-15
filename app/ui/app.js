(function () {
  "use strict";

  var chatLog = document.getElementById("chatLog");
  var chatInput = document.getElementById("chatInput");
  var sendBtn = document.getElementById("sendBtn");
  var statusLine = document.getElementById("statusLine");
  var bridge = null;

  function addMessage(text, kind) {
    var el = document.createElement("div");
    el.className = "msg " + kind;
    // textContent, never innerHTML: agent output is not trusted markup.
    el.textContent = text;
    chatLog.appendChild(el);
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  function setBusy(busy) {
    sendBtn.disabled = busy;
    chatInput.disabled = busy;
    statusLine.textContent = busy ? "thinking" : "";
    statusLine.className = "status-line mono" + (busy ? " busy" : "");
    if (!busy) chatInput.focus();
  }

  function send() {
    var text = chatInput.value.trim();
    if (!text || !bridge) return;
    addMessage(text, "user");
    chatInput.value = "";
    bridge.sendMessage(text);
  }

  sendBtn.addEventListener("click", send);
  chatInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });

  function tickClock() {
    var d = new Date();
    var p = function (n) { return String(n).padStart(2, "0"); };
    document.getElementById("clock").textContent =
      p(d.getHours()) + ":" + p(d.getMinutes()) + ":" + p(d.getSeconds()) +
      "  //  " + p(d.getMonth() + 1) + "." + p(d.getDate()) + "." + d.getFullYear();
  }
  tickClock();
  setInterval(tickClock, 1000);

  new QWebChannel(qt.webChannelTransport, function (channel) {
    bridge = channel.objects.jarvisBridge;

    bridge.replyReady.connect(function (text) { addMessage(text, "agent"); });
    bridge.agentFailed.connect(function (msg) { addMessage("agent error - " + msg, "error"); });
    bridge.busyChanged.connect(setBusy);

    statusLine.textContent = "";
    chatInput.focus();
  });
})();
