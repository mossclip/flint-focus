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
    var answer = check.getAttribute("data-answer");
    var feedback = check.querySelector(".feedback");
    var inputs = check.querySelectorAll("input");
    function mark(right) {
      check.classList.toggle("right", right);
      check.classList.toggle("wrong", !right);
      feedback.textContent = right ? "That’s right." : "Not quite. Take another look above.";
    }
    if (state.done[i]) {
      inputs[answer].checked = true;
      mark(true);
    }
    Array.prototype.forEach.call(inputs, function (input) {
      input.addEventListener("change", function () {
        var right = input.value === answer;
        mark(right);
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
