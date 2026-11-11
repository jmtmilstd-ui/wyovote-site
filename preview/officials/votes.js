/* Roll-call fields in preview/data/roll-calls-2026.json, in order:
   date, bill, title, stage, category, bill lean.
   This page stores only [rollCallId, vote]. */
(function () {
  var details = document.querySelector(".vote-details");
  var dataEl = document.getElementById("vote-ids");
  if (!details || !dataEl) return;

  var rollsPromise = null;
  var pairs = JSON.parse(dataEl.textContent);

  function cell(text) {
    var td = document.createElement("td");
    td.textContent = text;
    return td;
  }

  function load(url) {
    if (!rollsPromise) {
      rollsPromise = fetch(url).then(function (res) {
        if (!res.ok) throw new Error("status " + res.status);
        return res.json();
      });
    }
    return rollsPromise;
  }

  function render(rolls) {
    var tbody = details.querySelector("tbody");
    var frag = document.createDocumentFragment();
    for (var i = 0; i < pairs.length; i++) {
      var row = rolls[pairs[i][0]];
      var tr = document.createElement("tr");
      tr.appendChild(cell(row[0]));
      tr.appendChild(cell(row[1]));
      tr.appendChild(cell(row[2]));
      tr.appendChild(cell(row[3]));
      tr.appendChild(cell(pairs[i][1]));
      tr.appendChild(cell(row[4]));
      tr.appendChild(cell(row[5]));
      frag.appendChild(tr);
    }
    tbody.appendChild(frag);
    details.querySelector(".vote-wait").hidden = true;
    details.querySelector("table").hidden = false;
  }

  function fail() {
    var wait = details.querySelector(".vote-wait");
    wait.hidden = false;
    wait.textContent = "The roll-call list did not load.";
  }

  details.addEventListener("toggle", function () {
    if (!details.open || details.getAttribute("data-ready")) return;
    details.setAttribute("data-ready", "loading");
    load(details.getAttribute("data-rolls")).then(function (rolls) {
      render(rolls);
      details.setAttribute("data-ready", "1");
    }).catch(function () {
      details.removeAttribute("data-ready");
      rollsPromise = null;
      fail();
    });
  });
})();
