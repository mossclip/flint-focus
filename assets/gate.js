// Password curtain: any prime over 1000 opens the site for the current week.
// Not real security; the content is public. It keeps casual visitors out.
(function () {
  var key = "focus-open-" + (window.FOCUS_WEEK || "");
  var root = document.documentElement;
  try { if (localStorage.getItem(key) === "1") root.classList.remove("locked"); } catch (err) {}

  function isPrime(n) {
    if (n < 2 || n % 2 === 0) return n === 2;
    for (var d = 3; d * d <= n; d += 2) if (n % d === 0) return false;
    return true;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var gate = document.getElementById("gate");
    if (!gate) return;
    if (!root.classList.contains("locked")) { gate.remove(); return; }
    var form = gate.querySelector("form");
    var input = gate.querySelector("input");
    var msg = gate.querySelector(".gate-msg");
    input.focus();
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var raw = input.value.replace(/[\s,]/g, "");
      var n = /^\d{4,12}$/.test(raw) ? parseInt(raw, 10) : NaN;
      if (n > 1000 && isPrime(n)) {
        try { localStorage.setItem(key, "1"); } catch (err) {}
        root.classList.remove("locked");
        gate.remove();
        var h = document.querySelector("main h1");
        if (h) { h.setAttribute("tabindex", "-1"); h.focus(); }
      } else {
        msg.textContent = "That’s not it. Check this week’s email.";
        form.classList.remove("shake"); void form.offsetWidth; form.classList.add("shake");
        input.select();
      }
    });
  });
})();
