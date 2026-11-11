(function () {
  var mounts = document.querySelectorAll("[data-news]");
  if (!mounts.length) return;

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

  function startOfToday() {
    var now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), now.getDate());
  }

  function formatDate(value) {
    var date = parseISODate(value);
    if (!date) return "";
    return months[date.getMonth()] + " " + date.getDate() + ", " + date.getFullYear();
  }

  function joinRoot(root, url) {
    if (!url) return "";
    if (/^(?:[a-z]+:|\/)/i.test(url)) return url;
    return (root || "") + url;
  }

  function specialState(special, today) {
    if (!special || !special.title || !special.url || !special.date) return "none";
    var expires = parseISODate(special.expires);
    if (!expires) return "none";
    if (today < expires) return "current";
    return "expired";
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function box(item, kind, root, extra) {
    var article = el("article", "news-box" + (kind === "special" ? " news-box-special" : " news-box-news"));
    article.appendChild(el("p", "news-kicker", kind === "special" ? "Special" : "News"));
    var date = el("p", "news-date");
    var time = el("time", "", item.date_label || formatDate(item.date));
    if (parseISODate(item.date)) time.setAttribute("datetime", item.date);
    date.appendChild(time);
    article.appendChild(date);
    var heading = el("h3");
    var titleLink = el("a", "", item.title || "");
    titleLink.href = joinRoot(root, item.url);
    heading.appendChild(titleLink);
    article.appendChild(heading);
    if (item.summary) article.appendChild(el("p", "news-summary", item.summary));
    var more = el("p", "news-more");
    var moreLink = el("a", "", "Read more");
    moreLink.href = joinRoot(root, item.url);
    more.appendChild(moreLink);
    article.appendChild(more);
    if (extra) article.appendChild(extra);
    return article;
  }

  function pastLink(root) {
    var past = el("p", "news-past");
    var link = el("a", "", "Past news");
    link.href = joinRoot(root, "archive/articles.html");
    past.appendChild(link);
    return past;
  }

  function renderHome(mount, data, today) {
    var root = mount.getAttribute("data-root") || "";
    var state = specialState(data.special, today);
    var news = data.current_news && data.current_news.title && data.current_news.url ? data.current_news : null;
    var hasPast = (data.archive && data.archive.length) || state === "expired";
    mount.textContent = "";
    if (state !== "current" && !news && !hasPast) {
      mount.hidden = true;
      return;
    }
    mount.hidden = false;
    if (state === "current") mount.appendChild(box(data.special, "special", root));
    if (news) {
      mount.appendChild(box(news, "news", root, pastLink(root)));
    } else if (hasPast) {
      mount.appendChild(pastLink(root));
    }
  }

  function archiveItems(data, today) {
    var items = [];
    (data.archive || []).forEach(function (item) {
      if (item && item.title && item.url) items.push(item);
    });
    if (specialState(data.special, today) === "expired") {
      var special = data.special;
      var already = items.some(function (item) { return item.url === special.url; });
      if (!already) items.push({
        date: special.date,
        title: special.title,
        summary: special.summary,
        url: special.url,
        kind: "special"
      });
    }
    items.sort(function (a, b) {
      var ad = parseISODate(a.date);
      var bd = parseISODate(b.date);
      if (ad && bd) return bd - ad;
      if (bd) return 1;
      if (ad) return -1;
      return 0;
    });
    return items;
  }

  function renderArchive(mount, data, today) {
    var root = mount.getAttribute("data-root") || "";
    var items = archiveItems(data, today);
    mount.textContent = "";
    mount.hidden = false;
    if (!items.length) {
      mount.appendChild(el("p", "news-empty", "No past news yet."));
      return;
    }
    items.forEach(function (item) {
      mount.appendChild(box(item, item.kind === "special" ? "special" : "news", root));
    });
  }

  function fail(mount) {
    mount.hidden = false;
    mount.textContent = "";
    mount.appendChild(el("p", "news-empty", "News could not be loaded."));
  }

  var today = startOfToday();
  mounts.forEach(function (mount) {
    var url = mount.getAttribute("data-json");
    if (!url) return;
    fetch(url)
      .then(function (response) {
        if (!response.ok) throw new Error("news");
        return response.json();
      })
      .then(function (data) {
        if (mount.getAttribute("data-news") === "archive") renderArchive(mount, data, today);
        else renderHome(mount, data, today);
      })
      .catch(function () { fail(mount); });
  });
})();
