(function () {
  var mount = document.getElementById("article-archive");
  if (!mount) return;

  var months = ["Jan.", "Feb.", "Mar.", "Apr.", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."];

  function parseISODate(value) {
    if (!value || typeof value !== "string") return null;
    var parts = value.split("-");
    if (parts.length !== 3) return null;
    var year = Number(parts[0]);
    var month = Number(parts[1]);
    var day = Number(parts[2]);
    if (!year || month < 1 || month > 12 || day < 1) return null;
    var date = new Date(year, month - 1, day);
    if (date.getFullYear() !== year || date.getMonth() !== month - 1 || date.getDate() !== day) return null;
    return date;
  }

  function formatDate(item) {
    if (item.date_label) return item.date_label;
    var date = parseISODate(item.date);
    if (!date) return "";
    return months[date.getMonth()] + " " + date.getDate() + ", " + date.getFullYear();
  }

  function joinRoot(root, url) {
    if (!url) return "";
    if (/^(?:[a-z]+:|\/)/i.test(url)) return url;
    return (root || "") + url;
  }

  function columnsForWidth() {
    if (window.matchMedia("(min-width: 960px)").matches) return 3;
    if (window.matchMedia("(min-width: 600px)").matches) return 2;
    return 1;
  }

  function layoutStack(list) {
    var cols = columnsForWidth();
    var count = list.children.length;
    var rows = Math.max(1, Math.ceil(count / cols));
    list.style.setProperty("--stack-cols", String(cols));
    list.style.setProperty("--stack-rows", String(rows));
  }

  function layoutAll() {
    var lists = mount.querySelectorAll(".article-stack");
    for (var i = 0; i < lists.length; i++) layoutStack(lists[i]);
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function entry(item, root) {
    var li = el("li", "article-entry");
    var title = el("p", "article-entry-title");
    if (item.kind === "news" || item.kind === "special" || item.kind === "research" || item.kind === "feature") {
      var kickerClass = "news-kicker";
      var kickerText = "News";
      if (item.kind === "special") {
        kickerClass = "news-kicker news-kicker-special";
        kickerText = "Special";
      } else if (item.kind === "research") {
        kickerClass = "news-kicker news-kicker-research";
        kickerText = "Research";
      } else if (item.kind === "feature") {
        kickerClass = "news-kicker news-kicker-feature";
        kickerText = "Feature";
      }
      title.appendChild(el("span", kickerClass, kickerText));
      title.appendChild(document.createTextNode(" "));
    }
    var link = el("a", "", item.title || "");
    link.href = joinRoot(root, item.url);
    title.appendChild(link);
    li.appendChild(title);
    var date = el("p", "article-entry-date");
    var time = el("time", "", formatDate(item));
    if (parseISODate(item.date)) time.setAttribute("datetime", item.date);
    date.appendChild(time);
    li.appendChild(date);
    return li;
  }

  function render(items, root) {
    items.sort(function (a, b) {
      var ad = parseISODate(a.date);
      var bd = parseISODate(b.date);
      if (ad && bd) return bd - ad;
      if (bd) return 1;
      if (ad) return -1;
      return 0;
    });
    var years = [];
    var byYear = {};
    items.forEach(function (item) {
      var date = parseISODate(item.date);
      var year = date ? String(date.getFullYear()) : "Undated";
      if (!byYear[year]) {
        byYear[year] = [];
        years.push(year);
      }
      byYear[year].push(item);
    });
    mount.textContent = "";
    years.forEach(function (year) {
      var section = el("section", "article-year");
      section.appendChild(el("h2", "", year));
      var list = el("ul", "article-stack");
      byYear[year].forEach(function (item) {
        list.appendChild(entry(item, root));
      });
      section.appendChild(list);
      mount.appendChild(section);
    });
    layoutAll();
  }

  function fromNews(data) {
    var items = [];
    function add(item, kind) {
      if (!item || !item.title || !item.url || !item.date) return;
      items.push({
        date: item.date,
        date_label: item.date_label || "",
        title: item.title,
        url: item.url,
        kind: kind || item.kind || ""
      });
    }
    add(data.current_news, "news");
    add(data.special, "special");
    (data.archive || []).forEach(function (item) {
      add(item, item && item.kind === "special" ? "special" : "news");
    });
    return items;
  }

  var embedded = document.getElementById("archive-articles");
  var regular = [];
  if (embedded) {
    try { regular = JSON.parse(embedded.textContent); } catch (error) { regular = []; }
  }
  var root = mount.getAttribute("data-root") || "";
  var url = mount.getAttribute("data-news");
  var seen = {};
  regular.forEach(function (item) {
    if (item && item.url) seen[item.url] = true;
  });

  function finish(extra) {
    var items = regular.slice();
    extra.forEach(function (item) {
      if (seen[item.url]) return;
      seen[item.url] = true;
      items.push(item);
    });
    render(items, root);
  }

  if (!url) {
    finish([]);
  } else {
    fetch(url)
      .then(function (response) {
        if (!response.ok) throw new Error("news");
        return response.json();
      })
      .then(function (data) { finish(fromNews(data)); })
      .catch(function () { finish([]); });
  }

  window.addEventListener("resize", layoutAll);
})();
