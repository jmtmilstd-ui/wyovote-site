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

  /* 7-day rule (Denver date): the News box and a Special leave the home
     page once they are more than home_max_age_days (7) old. An item dated
     D shows through D + 7 and leaves on the morning of D + 8. It stays on
     the Archive Articles page. */
  var DEFAULT_MAX_AGE = 7;

  function denverDay() {
    try {
      var p = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Denver", year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(new Date());
      var v = {};
      p.forEach(function (x) { v[x.type] = x.value; });
      return Date.UTC(Number(v.year), Number(v.month) - 1, Number(v.day));
    } catch (e) {
      var n = new Date();
      return Date.UTC(n.getFullYear(), n.getMonth(), n.getDate());
    }
  }

  function maxAge(data) {
    var n = Number(data && data.home_max_age_days);
    return n > 0 ? n : DEFAULT_MAX_AGE;
  }

  function tooOld(item, data) {
    var d = parseISODate(item && item.date);
    if (!d) return true;
    var t = Date.UTC(d.getFullYear(), d.getMonth(), d.getDate());
    return Math.round((denverDay() - t) / 86400000) > maxAge(data);
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

  function specialState(special, today, data) {
    if (!special || !special.title || !special.url || !special.date) return "none";
    var expires = parseISODate(special.expires);
    if (!expires) return "none";
    if (today < expires && !tooOld(special, data)) return "current";
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
    var listed = data.current_news && data.current_news.title && data.current_news.url ? data.current_news : null;
    var news = listed && !tooOld(listed, data) ? listed : null;
    var hasPast = (data.archive && data.archive.length) || specialState(data.special, today, data) === "expired" || (listed && !news);
    mount.textContent = "";
    if (!news && !hasPast) {
      mount.hidden = true;
      return;
    }
    mount.hidden = false;
    if (news) mount.appendChild(box(news, "news", root, pastLink(root)));
    else mount.appendChild(pastLink(root));
  }

  function renderSpotlight(mount, data, today) {
    var root = mount.getAttribute("data-root") || "";
    mount.textContent = "";
    mount.hidden = false;
    if (specialState(data.special, today, data) === "current") {
      mount.appendChild(box(data.special, "special", root));
      return;
    }
    mount.appendChild(el("p", "spotlight-note", "Specials and featured items appear here."));
  }

  function archiveItems(data, today) {
    var items = [];
    (data.archive || []).forEach(function (item) {
      if (item && item.title && item.url) items.push(item);
    });
    if (specialState(data.special, today, data) === "expired") {
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
        var mode = mount.getAttribute("data-news");
        if (mode === "archive") renderArchive(mount, data, today);
        else if (mode === "spotlight") renderSpotlight(mount, data, today);
        else renderHome(mount, data, today);
      })
      .catch(function () { fail(mount); });
  });
})();

/* Home Articles column: at most 4, none older than 7 days (Denver date).
   Features and research articles follow the same rule.
   The build (tools/build_home_articles.py) already applies the rule; this
   repeats it in the browser so articles leave on time without a redeploy. */
(function () {
  var list = document.querySelector(".article-list[data-max-age-days]");
  var prompt = document.querySelector(".archive-prompt");
  var foot = document.querySelector(".home-side .column-foot");
  if (!prompt) return;
  function denverToday() {
    try {
      var p = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Denver", year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(new Date());
      var v = {};
      p.forEach(function (x) { v[x.type] = x.value; });
      return Date.UTC(Number(v.year), Number(v.month) - 1, Number(v.day));
    } catch (e) {
      var n = new Date();
      return Date.UTC(n.getFullYear(), n.getMonth(), n.getDate());
    }
  }
  var left = 0;
  if (list) {
    var maxAge = Number(list.getAttribute("data-max-age-days")) || 7;
    var maxItems = Number(list.getAttribute("data-max-items")) || 4;
    var today = denverToday();
    Array.prototype.slice.call(list.querySelectorAll("li[data-date]")).forEach(function (li) {
      var d = li.getAttribute("data-date").split("-");
      var t = Date.UTC(Number(d[0]), Number(d[1]) - 1, Number(d[2]));
      var age = Math.round((today - t) / 86400000);
      if (isNaN(age) || age > maxAge || left >= maxItems) li.parentNode.removeChild(li);
      else left += 1;
    });
    if (!left) list.parentNode.removeChild(list);
  }
  prompt.hidden = left > 0;
  if (foot) foot.hidden = left === 0;
})();
