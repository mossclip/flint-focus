// Progress lookups: an RA types their first name and sees their own numbers.
// The numbers are encrypted in the page; this week's PIN (from James's email) unlocks them.
(function () {
  var holder = document.getElementById("focus-data");
  var boxes = document.querySelectorAll(".lookup");
  if (!holder || !boxes.length) return;
  var week = (document.querySelector(".week") || {}).getAttribute ? document.querySelector(".week").getAttribute("data-week") : "";
  var payload = JSON.parse(holder.textContent);
  var cache = null;

  function b64(s) { var bin = atob(s), out = new Uint8Array(bin.length); for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i); return out; }
  function storedPin() { try { return localStorage.getItem("focus-pin-" + week) || ""; } catch (e) { return ""; } }

  function unlock(pin) {
    if (!window.crypto || !crypto.subtle) return Promise.reject(new Error("nocrypto"));
    var enc = new TextEncoder();
    return crypto.subtle.importKey("raw", enc.encode(String(pin)), "PBKDF2", false, ["deriveKey"])
      .then(function (km) {
        return crypto.subtle.deriveKey({ name: "PBKDF2", salt: b64(payload.salt), iterations: payload.iter, hash: "SHA-256" },
          km, { name: "AES-GCM", length: 256 }, false, ["decrypt"]);
      })
      .then(function (key) { return crypto.subtle.decrypt({ name: "AES-GCM", iv: b64(payload.iv) }, key, b64(payload.ct)); })
      .then(function (buf) { cache = JSON.parse(new TextDecoder().decode(buf)); return cache; });
  }
  function getData(pin) { return cache ? Promise.resolve(cache) : unlock(pin || storedPin()); }

  function el(tag, cls, html) { var x = document.createElement(tag); if (cls) x.className = cls; if (html != null) x.innerHTML = html; return x; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  // ---- fireworks ----------------------------------------------------------
  function fireworks() {
    if (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var c = el("canvas", "fw"); document.body.appendChild(c);
    var ctx = c.getContext("2d"), dpr = window.devicePixelRatio || 1, W, H, parts = [], t0 = performance.now();
    function size() { W = innerWidth; H = innerHeight; c.width = W * dpr; c.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
    size();
    var colors = ["#f76900", "#ffb347", "#2b72d7", "#1e7a46", "#ffd23f", "#e8457c", "#9fb3ff"];
    function burst() {
      var x = W * (0.15 + Math.random() * 0.7), y = H * (0.15 + Math.random() * 0.35), col = colors[Math.floor(Math.random() * colors.length)];
      for (var k = 0; k < 60; k++) {
        var a = Math.random() * Math.PI * 2, v = 2 + Math.random() * 4.5;
        parts.push({ x: x, y: y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, life: 1, col: Math.random() < 0.25 ? "#fff" : col });
      }
    }
    var timer = setInterval(burst, 380); burst(); burst();
    setTimeout(function () { clearInterval(timer); }, 3000);
    (function frame(now) {
      ctx.clearRect(0, 0, W, H);
      parts.forEach(function (p) {
        p.x += p.vx; p.y += p.vy; p.vy += 0.06; p.vx *= 0.985; p.vy *= 0.985; p.life -= 0.012;
        if (p.life > 0) { ctx.globalAlpha = p.life; ctx.fillStyle = p.col; ctx.beginPath(); ctx.arc(p.x, p.y, 2.4, 0, 7); ctx.fill(); }
      });
      parts = parts.filter(function (p) { return p.life > 0; });
      if (now - t0 < 5200 || parts.length) requestAnimationFrame(frame); else c.remove();
    })(t0);
  }

  var TWIX = '<svg class="twix" viewBox="0 0 240 90" role="img" aria-label="A Twix bar">' +
    '<rect x="6" y="18" width="228" height="56" rx="10" fill="#c8a24a"/>' +
    '<path d="M6 30 l10 -6 l10 6 l10 -6 l10 6 M6 62 l10 6 l10 -6 l10 6 l10 -6" stroke="#a8842f" stroke-width="2" fill="none"/>' +
    '<path d="M234 30 l-10 -6 l-10 6 l-10 -6 l-10 6 M234 62 l-10 6 l-10 -6 l-10 6 l-10 -6" stroke="#a8842f" stroke-width="2" fill="none"/>' +
    '<rect x="52" y="24" width="136" height="44" rx="6" fill="#d71e28"/>' +
    '<text x="120" y="56" text-anchor="middle" font-family="Archivo, Arial Black, sans-serif" font-weight="800" font-size="30" fill="#fff" letter-spacing="2">TWIX</text>' +
    '</svg>';

  // ---- renderers ----------------------------------------------------------
  function dk2(r, d) {
    var k = r.dk2, out = el("div", "result");
    var stat = '<p class="big-stat"><strong>' + k.done + "</strong> of " + k.total + " residents <span>(" + k.pct + "%)</span></p>";
    var msg, tone, list = false;
    if (k.pct >= 100) { tone = "win"; msg = "<strong>Thank you, " + esc(r.name) + "!</strong> You're at 100%."; }
    else if (k.pct >= 75) { tone = "good"; msg = "<strong>Good work, " + esc(r.name) + ".</strong> You're almost there."; list = true; }
    else if (k.pct > 50) { tone = "good"; msg = "<strong>You're getting there, " + esc(r.name) + ".</strong> You're more than halfway done."; list = true; }
    else if (k.done > 0) { tone = "start"; msg = "<strong>You're off to a good start, " + esc(r.name) + ".</strong> Keep it going this week."; list = true; }
    else { tone = "zero"; msg = "<strong>" + esc(r.name) + ", we really need you to get started on these, please.</strong> Let James know if you need any help, or if something's going on that he should know about."; }
    out.classList.add("tone-" + tone);
    out.innerHTML = '<p class="asof-top">Updated ' + esc(d.asof) + ". If you've done more since then, thank you!</p>" + '<p class="msg">' + msg + "</p>" + stat;
    if (tone === "win" && r.twix) out.innerHTML += '<div class="treat">' + TWIX + "<p>This one's for you, " + esc(r.name) + ". Thank you!</p></div>";
    if (list) {
      var cols = el("div", "ticks");
      cols.innerHTML = '<div><p class="tick-h ok">Done (' + k.did.length + ")</p><ul>" + k.did.map(function (x) { return '<li class="ok">' + esc(x) + "</li>"; }).join("") + "</ul></div>" +
        '<div><p class="tick-h no">Still to go (' + k.todo.length + ")</p><ul>" + k.todo.map(function (x) { return '<li class="no">' + esc(x) + "</li>"; }).join("") + "</ul></div>";
      out.appendChild(cols);
    }
    if (tone === "win") fireworks();
    return { node: out, done: true };
  }

  function oh(r, d, section) {
    var o = r.oh, out = el("div", "result");
    if (o.caught) {
      out.classList.add("tone-win");
      out.innerHTML = '<div class="allclear"><span class="bigcheck" aria-hidden="true">✓</span><p class="msg"><strong>You\'re all caught up, ' + esc(r.name) +
        "!</strong> Every Office Hours reflection from the \'Cuse Chat #1 period is in. Thank you.</p></div>";
      out.appendChild(el("p", "asof", "Counted for the \'Cuse Chat #1 period (Aug 31 to Nov 1), as of " + esc(d.asof) + "."));
      fireworks();
      return { node: out, done: true };
    }
    var miss = o.weeks.filter(function (w) { return !w.ok; }).length;
    out.classList.add("tone-start");
    out.innerHTML = '<p class="msg"><strong>Thanks for checking, ' + esc(r.name) + ".</strong> Roompact is missing " + (miss === 1 ? "one week" : miss + " weeks") +
      " from the 'Cuse Chat #1 period. Kim closed the Office Hours form today, so " + (miss === 1 ? "it" : "they") + " can no longer be submitted. Hopefully we can stay on top of them better moving forward.</p>" +
      '<ul class="weeks">' + o.weeks.map(function (w) { return '<li class="' + (w.ok ? "ok" : "no") + '">' + esc(w.l) + "</li>"; }).join("") + "</ul>";
    out.appendChild(el("p", "asof", "Counted for the 'Cuse Chat #1 period (Aug 31 to Nov 1), as of " + esc(d.asof) + "."));
    var b = el("button", "confirm", "Got it"); b.type = "button";
    b.addEventListener("click", function () { b.disabled = true; b.textContent = "Thank you!"; if (window.FocusPager) FocusPager.markDone(section); });
    out.appendChild(b);
    return { node: out, done: false };
  }

  // ---- wiring -------------------------------------------------------------
  Array.prototype.forEach.call(boxes, function (box) {
    var section = box.closest(".screen"), input = box.querySelector(".lookup-in"), go = box.querySelector(".lookup-go"), res = box.querySelector(".lookup-out");
    var kind = box.getAttribute("data-kind");
    function pinPrompt(msg) {
      res.innerHTML = "";
      var p = el("div", "pinask"); p.innerHTML = "<p>" + msg + "</p>";
      var i = el("input"); i.inputMode = "numeric"; i.placeholder = "PIN"; i.autocomplete = "off";
      var b = el("button", null, "Unlock"); b.type = "button";
      b.addEventListener("click", function () {
        unlock(i.value.replace(/[\s,]/g, "")).then(function () {
          try { localStorage.setItem("focus-pin-" + week, i.value.replace(/[\s,]/g, "")); } catch (e) {}
          run();
        }).catch(function () { pinPrompt("That PIN didn't unlock it. Use the exact PIN from this week's email."); });
      });
      p.appendChild(i); p.appendChild(b); res.appendChild(p);
    }
    function run() {
      var name = input.value.trim().toLowerCase().replace(/[^a-z' -]/g, "");
      if (!name) { res.innerHTML = '<p class="nf">Type your first name first.</p>'; return; }
      res.innerHTML = '<p class="loading">Looking you up…</p>';
      getData().then(function (d) {
        var key = d.aliases[name] || name.split(" ")[0];
        key = d.aliases[key] || key;
        var r = d.ras[key];
        if (!r) { res.innerHTML = '<p class="nf">We couldn\'t find "' + esc(input.value.trim()) + '". Try the first name the team knows you by.</p>'; return; }
        var x = kind === "dk2" ? dk2(r, d) : oh(r, d, section);
        res.innerHTML = ""; res.appendChild(x.node);
        if (x.done && window.FocusPager) FocusPager.markDone(section);
      }).catch(function (e) {
        if (e && e.message === "nocrypto") { res.innerHTML = '<p class="nf">This browser can\'t open the progress check. Try Safari or Chrome.</p>'; return; }
        pinPrompt("Enter this week's PIN from James's email to see your progress.");
      });
    }
    go.addEventListener("click", run);
    input.addEventListener("keydown", function (ev) { if (ev.key === "Enter") { ev.preventDefault(); run(); } });
  });
})();
