// One screen at a time, with a quick check that unlocks Next.
// Without JavaScript, every screen simply shows in order.
(function () {
  var week = document.querySelector(".week");
  if (!week) return;
  var screens = Array.prototype.slice.call(week.querySelectorAll(".screen"));
  var back = week.querySelector(".back");
  var next = week.querySelector(".next");
  var bar = week.querySelector(".bar");
  var key = "focus-" + week.getAttribute("data-week");
  var state = { step: 0, done: {} };

  try {
    var saved = JSON.parse(localStorage.getItem(key) || "null");
    if (saved && typeof saved.step === "number") state = saved;
  } catch (err) {}

  function save() {
    try { localStorage.setItem(key, JSON.stringify(state)); } catch (err) {}
  }

  function passed(i) {
    var check = screens[i].querySelector(".check");
    return !check || state.done[i];
  }

  function show(i, focus) {
    state.step = Math.max(0, Math.min(i, screens.length - 1));
    screens.forEach(function (s, k) { s.hidden = k !== state.step; });
    back.disabled = state.step === 0;
    next.hidden = state.step === screens.length - 1;
    next.disabled = !passed(state.step);
    bar.style.width = ((state.step + 1) / screens.length) * 100 + "%";
    if (focus) {
      var h = screens[state.step].querySelector("h2");
      if (h) h.focus();
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
    save();
  }

  screens.forEach(function (s, i) {
    var check = s.querySelector(".check");
    if (!check) return;
    if (check.classList.contains("picked")) {
      var sels = check.querySelectorAll("select"), pfb = check.querySelector(".feedback");
      function pgrade() {
        var right = Array.prototype.every.call(sels, function (s) { return s.value === s.getAttribute("data-answer"); });
        check.classList.toggle("right", right); check.classList.toggle("wrong", !right);
        pfb.textContent = right ? "That’s right." : "Not quite. Check the date and time.";
        if (right) state.done[i] = true;
        if (i === state.step) next.disabled = !passed(i);
        save();
      }
      if (state.done[i]) {
        Array.prototype.forEach.call(sels, function (s) { s.value = s.getAttribute("data-answer"); });
        check.classList.add("right"); pfb.textContent = "That’s right.";
      }
      check.querySelector(".typed-go").addEventListener("click", pgrade);
      return;
    }
    if (check.classList.contains("typed")) {
      var pats = JSON.parse(check.getAttribute("data-patterns")).map(function (p) { return new RegExp(p, "i"); });
      var box = check.querySelector(".typed-in"), fb = check.querySelector(".feedback");
      function grade(show) {
        var v = box.value.replace(/\s+/g, " ");
        var right = pats.every(function (r) { return r.test(v); });
        if (show || right) {
          check.classList.toggle("right", right); check.classList.toggle("wrong", !right);
          fb.textContent = right ? "That’s right." : "Not quite. Type the whole deadline.";
        }
        if (right) state.done[i] = true;
        if (i === state.step) next.disabled = !passed(i);
        save();
      }
      if (state.done[i]) { check.classList.add("right"); fb.textContent = "That’s right."; }
      check.querySelector(".typed-go").addEventListener("click", function () { grade(true); });
      box.addEventListener("keydown", function (ev) { if (ev.key === "Enter") { ev.preventDefault(); grade(true); } });
      return;
    }
    var answers = check.getAttribute("data-answer").split(",");
    var custom = JSON.parse(check.getAttribute("data-feedback") || "null");
    var feedback = check.querySelector(".feedback");
    var inputs = check.querySelectorAll("input");
    function mark(right, k) {
      check.classList.toggle("right", right);
      check.classList.toggle("wrong", !right);
      feedback.textContent = (custom && k != null && custom[k]) ? custom[k]
        : (right ? "That’s right." : "Not quite. Take another look above.");
    }
    if (state.done[i]) {
      var k0 = state.pick && state.pick[i] != null ? state.pick[i] : answers[0];
      inputs[k0].checked = true;
      mark(true, k0);
    }
    Array.prototype.forEach.call(inputs, function (input) {
      input.addEventListener("change", function () {
        var right = answers.indexOf(input.value) !== -1;
        state.pick = state.pick || {}; state.pick[i] = input.value;
        mark(right, input.value);
        if (right) state.done[i] = true;
        if (i === state.step) next.disabled = !passed(i);
        save();
      });
    });
  });

  back.addEventListener("click", function () { show(state.step - 1, true); });
  next.addEventListener("click", function () { if (passed(state.step)) show(state.step + 1, true); });
  week.classList.add("paged");
  show(state.step, false);
})();
