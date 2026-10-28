(function () {
  "use strict";

  function fallbackCopy(text) {
    var area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    area.remove();
    return ok ? Promise.resolve() : Promise.reject(new Error("copy failed"));
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).catch(function () { return fallbackCopy(text); });
    }
    return fallbackCopy(text);
  }

  function feedback(button, ok) {
    var label = button.getAttribute("data-label") || button.textContent;
    button.setAttribute("data-label", label);
    button.textContent = ok ? (document.documentElement.lang === "pt-BR" ? "Copiado" : "Copied") : (document.documentElement.lang === "pt-BR" ? "Selecione e copie" : "Select and copy");
    window.setTimeout(function () { button.textContent = label; }, 1600);
  }

  document.addEventListener("click", function (event) {
    var button = event.target.closest ? event.target.closest(".copyk") : null;
    if (!button) return;
    var code = button.previousElementSibling;
    if (!code || !code.matches("pre.code")) return;
    copyText(code.textContent).then(function () { feedback(button, true); }, function () { feedback(button, false); });
  });

  var printState = [];
  window.addEventListener("beforeprint", function () {
    printState = [];
    document.querySelectorAll("details").forEach(function (details) {
      if (!details.open) { printState.push(details); details.open = true; }
    });
  });
  window.addEventListener("afterprint", function () {
    printState.forEach(function (details) { details.open = false; });
    printState = [];
  });
}());
