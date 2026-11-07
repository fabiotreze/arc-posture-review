// ---------- Verdict, start-here cards and guide search (one source for EN-US and PT-BR; strings follow the page language) ----------
var UXT = (document.documentElement.lang === "en") ? {
  vTitle: "Verdict", vSub: "Where you stand and what matters now",
  vHead: function (g, i, n) { return g + " verified gap" + (g === 1 ? "" : "s") + " to address · " + i + " improvement opportunit" + (i === 1 ? "y" : "ies") + " · " + n + " point" + (n === 1 ? "" : "s") + " still to verify."; },
  gap: "Verified gaps", imp: "Improvement opportunities", nv: "Not verified (to collect)", ok: "Meets the criterion", inf: "Informational / N/A",
  how: "A verified gap is a condition observed with enough evidence. An improvement opportunity is a hardening or visibility step that is not configured; it does not mean a practice is insecure. Not verified means the evidence was not collected or is documentary: a collection task, not a finding.",
  doTitle: "Do first", doSub: "The actions with the biggest gain, in order", noGain: "No scorable control yet: complete the collection to rank the actions.",
  pts: "pts", nChecks: "checks", tagGap: "Verified gap", tagImp: "Improvement",
  startTitle: "Start here", startSub: "Three steps. Everything is read-only and runs in your browser.",
  s1: "Collect", s1d: "Define the scope, generate the script and run it in Cloud Shell. You get one .zip.",
  s2: "Open", s2d: "Load the .zip: the analysis and the canonical v4 report (Zero Trust) open here.",
  s3: "Deliver", s3d: "Save the analysis (.html) and the v4 report, or print to PDF.", go: "Open →",
  search: "Search the guide: CHK-23, extension, baseline…", found: "section(s) found"
} : {
  vTitle: "Veredito", vSub: "Onde você está e o que importa agora",
  vHead: function (g, i, n) { return g + " lacuna" + (g === 1 ? "" : "s") + " verificada" + (g === 1 ? "" : "s") + " a tratar · " + i + " oportunidade" + (i === 1 ? "" : "s") + " de melhoria · " + n + " ponto" + (n === 1 ? "" : "s") + " ainda sem verificação."; },
  gap: "Lacunas verificadas", imp: "Oportunidades de melhoria", nv: "Não verificado (a coletar)", ok: "Atende ao critério", inf: "Informativo / N/A",
  how: "Lacuna verificada é uma condição observada com evidência suficiente. Oportunidade de melhoria é um passo de hardening ou visibilidade que não está configurado; não significa que a prática seja insegura. Não verificado indica que a evidência não foi coletada ou é documental: é uma tarefa de coleta, não um achado.",
  doTitle: "Faça primeiro", doSub: "As ações de maior ganho, em ordem", noGain: "Ainda não há controle pontuável: complete a coleta para ordenar as ações.",
  pts: "pts", nChecks: "checks", tagGap: "Lacuna verificada", tagImp: "Melhoria",
  startTitle: "Comece aqui", startSub: "Três passos. Tudo é somente leitura e roda no seu navegador.",
  s1: "Coletar", s1d: "Defina o escopo, gere o script e rode no Cloud Shell. Você recebe um único .zip.",
  s2: "Abrir", s2d: "Carregue o .zip: a análise e o relatório canônico v4 (Zero Trust) abrem aqui.",
  s3: "Entregar", s3d: "Salve a análise (.html) e o relatório v4, ou imprima em PDF.", go: "Abrir →",
  search: "Buscar no guia: CHK-23, extensão, baseline…", found: "seção(ões) encontrada(s)"
};
// Icons: copied or adapted from Feather Icons (MIT, Copyright (c) 2013-2023 Cole Bemis). See THIRD-PARTY-NOTICES.md.
var UXI = {
  gap: '<circle cx="12" cy="12" r="9"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
  imp: '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
  nv: '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="11"/><line x1="11" y1="14" x2="11.01" y2="14"/>'
};
function uxIcon(k) { return '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + UXI[k] + "</svg>"; }
function uxCount(L, list) { return L.filter(function (x) { return list.indexOf(x.status) >= 0; }).length; }
function verdictHtml(L) {
  var T = UXT, g = uxCount(L, ["FAIL"]), i = uxCount(L, ["WARN"]), n = uxCount(L, ["TODO", "PARTIAL", "ERROR"]), o = uxCount(L, ["PASS"]), f = uxCount(L, ["INFO", "N/A"]);
  var seg = [["gap", g], ["imp", i], ["nv", n], ["ok", o], ["inf", f]].filter(function (s) { return s[1]; });
  var bar = seg.map(function (s) { return '<i class="uxo-' + s[0] + '" style="flex:' + s[1] + '" title="' + esc(T[s[0]]) + ": " + s[1] + '"></i>'; }).join("");
  var leg = seg.map(function (s) { return '<span><i class="uxo-' + s[0] + '"></i><b>' + s[1] + "</b> " + esc(T[s[0]]) + "</span>"; }).join("");
  var cards = [["gap", g], ["imp", i], ["nv", n]].map(function (c) { return '<div class="uxk uxk-' + c[0] + '"><span class="uxico">' + uxIcon(c[0]) + "</span><strong>" + c[1] + "</strong><span>" + esc(T[c[0]]) + "</span></div>"; }).join("");
  var top = gains(L).slice(0, 3);
  var first = top.length ? '<ol class="uxdo">' + top.map(function (u, k) {
    var m0 = u.members[0], isGap = u.members.some(function (x) { return x.status === "FAIL"; });
    var ids = u.members.map(function (x) { return x.it.id; });
    return '<li><a class="jump uxdoc" href="#pr-' + ids[0] + '" data-target="pr-' + ids[0] + '"><span class="uxn">' + (k + 1) + "</span><b>" + esc(u.title) + '</b><span class="uxm"><span class="uxtag ' + (isGap ? "uxtag-gap" : "uxtag-imp") + '">' + esc(isGap ? T.tagGap : T.tagImp) + "</span>" +
      (m0.it.owner ? '<span class="uxtag">' + esc(m0.it.owner) + "</span>" : "") + '<span class="uxtag uxtag-gain">+' + u.gain + " " + esc(T.pts) + "</span></span><small>" + esc(ids.join(", ")) + (ids.length > 1 ? " · " + ids.length + " " + esc(T.nChecks) : "") + "</small></a></li>";
  }).join("") + "</ol>" : '<p class="msg">' + esc(T.noGain) + "</p>";
  return '<section class="uxv" id="uxVerdict"><h2>' + esc(T.vTitle) + '</h2><p class="uxsub">' + esc(T.vSub) + '</p><p class="uxhead">' + esc(T.vHead(g, i, n)) + '</p><p class="uxhow">' + esc(T.how) + '</p><div class="uxkpis">' + cards + '</div><div class="uxstack" role="img" aria-label="' + esc(T.vTitle) + '">' + bar + '</div><div class="uxlegend">' + leg + '</div>' +
    '<h3>' + esc(T.doTitle) + '</h3><p class="uxsub">' + esc(T.doSub) + "</p>" + first + "</section>";
}
function uxInitGuide() {
  var pane = $("pane-guide"); if (!pane || $("uxStart")) return;
  var T = UXT, host = pane.querySelector(".guide") || pane.firstChild;
  var steps = [["script", "1", T.s1, T.s1d], ["summary", "2", T.s2, T.s2d], ["result", "3", T.s3, T.s3d]];
  var start = document.createElement("section"); start.id = "uxStart"; start.className = "uxstart";
  start.innerHTML = "<h2>" + esc(T.startTitle) + '</h2><p class="uxsub">' + esc(T.startSub) + '</p><div class="uxsteps">' + steps.map(function (s) {
    return '<button type="button" class="uxstep" data-goto="' + s[0] + '"><span class="uxsn">' + s[1] + "</span><b>" + esc(s[2]) + "</b><small>" + esc(s[3]) + '</small><span class="uxgo">' + esc(T.go) + "</span></button>"; }).join("") +
    '</div><div class="uxsearch"><input type="search" id="uxGuideSearch" placeholder="' + esc(T.search) + '" aria-label="' + esc(T.search) + '"><span id="uxGuideCount" class="msg"></span></div>';
  pane.insertBefore(start, pane.firstElementChild || null);
  var input = $("uxGuideSearch"), count = $("uxGuideCount");
  input.addEventListener("input", function () {
    var q = input.value.trim().toLowerCase(), shown = 0;
    pane.querySelectorAll(".guide .act.gf3").forEach(function (sec) {
      var hit = !q || sec.textContent.toLowerCase().indexOf(q) >= 0;
      sec.style.display = hit ? "" : "none";
      if (hit) shown++;
      if (q && hit && !sec.classList.contains("open")) { var h = sec.querySelector(".acth"); if (h) toggleAct(h, true); }
    });
    count.textContent = q ? shown + " " + T.found : "";
  });
}
uxInitGuide();
