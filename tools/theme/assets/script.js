/* ==========================================================================
   Ampera Trinity AI — interaksi situs dokumentasi
   Tanpa dependensi eksternal.
   ========================================================================== */
(function () {
  "use strict";

  /* ---------------------------------------------------------------- */
  /* Menu sidebar untuk layar kecil                                    */
  /* ---------------------------------------------------------------- */
  var menuBtn = document.querySelector(".menu-btn");
  var sidebar = document.querySelector(".sidebar");
  var overlay = document.querySelector(".nav-overlay");

  function closeNav() {
    if (!sidebar) return;
    sidebar.classList.remove("open");
    if (overlay) overlay.classList.remove("show");
    if (menuBtn) menuBtn.setAttribute("aria-expanded", "false");
  }

  if (menuBtn && sidebar) {
    menuBtn.addEventListener("click", function () {
      var open = sidebar.classList.toggle("open");
      if (overlay) overlay.classList.toggle("show", open);
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }
  if (overlay) overlay.addEventListener("click", closeNav);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeNav();
  });

  /* ---------------------------------------------------------------- */
  /* Penyaring navigasi sidebar                                        */
  /* ---------------------------------------------------------------- */
  var search = document.getElementById("nav-search");
  if (search) {
    var groups = Array.prototype.slice.call(document.querySelectorAll(".nav-group"));
    var emptyMsg = document.querySelector(".nav-empty");

    search.addEventListener("input", function () {
      var q = search.value.trim().toLowerCase();
      var totalVisible = 0;

      groups.forEach(function (group) {
        var items = Array.prototype.slice.call(group.querySelectorAll("li"));
        var shown = 0;

        items.forEach(function (li) {
          var link = li.querySelector("a");
          if (!link) return;
          var hay = (link.textContent + " " + (link.dataset.keywords || "")).toLowerCase();
          var match = q === "" || hay.indexOf(q) !== -1;
          li.style.display = match ? "" : "none";
          if (match) shown++;
        });

        group.style.display = shown ? "" : "none";
        totalVisible += shown;
      });

      if (emptyMsg) emptyMsg.style.display = totalVisible ? "none" : "block";
    });

    // Pintasan "/" untuk fokus ke kolom pencarian
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== search &&
          !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) {
        e.preventDefault();
        search.focus();
      }
    });
  }

  /* ---------------------------------------------------------------- */
  /* Tombol salin pada blok kode                                       */
  /* ---------------------------------------------------------------- */
  document.querySelectorAll(".md pre").forEach(function (pre) {
    var wrap = document.createElement("div");
    wrap.className = "code-block";
    pre.parentNode.insertBefore(wrap, pre);
    wrap.appendChild(pre);

    var btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.type = "button";
    btn.textContent = "Salin";
    btn.setAttribute("aria-label", "Salin kode");

    btn.addEventListener("click", function () {
      var text = pre.innerText;
      var done = function () {
        btn.textContent = "Tersalin!";
        btn.classList.add("done");
        setTimeout(function () {
          btn.textContent = "Salin";
          btn.classList.remove("done");
        }, 1800);
      };

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, fallback);
      } else {
        fallback();
      }

      function fallback() {
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand("copy"); done(); } catch (err) { /* diam */ }
        document.body.removeChild(ta);
      }
    });

    wrap.appendChild(btn);
  });

  /* ---------------------------------------------------------------- */
  /* Tabel yang bisa digulir horizontal                                */
  /* ---------------------------------------------------------------- */
  document.querySelectorAll(".md table").forEach(function (table) {
    if (table.parentNode.classList.contains("table-scroll")) return;
    var wrap = document.createElement("div");
    wrap.className = "table-scroll";
    table.parentNode.insertBefore(wrap, table);
    wrap.appendChild(table);
  });

  /* ---------------------------------------------------------------- */
  /* Sorot entri daftar isi sesuai posisi gulir                        */
  /* ---------------------------------------------------------------- */
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".toc a"));
  if (tocLinks.length && "IntersectionObserver" in window) {
    var byId = {};
    var headings = [];

    tocLinks.forEach(function (link) {
      var id = decodeURIComponent(link.getAttribute("href") || "").replace(/^#/, "");
      var el = id && document.getElementById(id);
      if (el) { byId[id] = link; headings.push(el); }
    });

    var visible = new Set();

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) visible.add(entry.target.id);
        else visible.delete(entry.target.id);
      });

      var activeId = null;
      for (var i = 0; i < headings.length; i++) {
        if (visible.has(headings[i].id)) { activeId = headings[i].id; break; }
      }
      // Kalau tidak ada judul yang terlihat, pakai judul terakhir yang sudah dilewati
      if (!activeId) {
        var top = window.scrollY + 120;
        headings.forEach(function (h) {
          if (h.offsetTop <= top) activeId = h.id;
        });
      }

      tocLinks.forEach(function (l) { l.classList.remove("active"); });
      if (activeId && byId[activeId]) byId[activeId].classList.add("active");
    }, { rootMargin: "-80px 0px -70% 0px", threshold: 0 });

    headings.forEach(function (h) { observer.observe(h); });
  }

  /* ---------------------------------------------------------------- */
  /* Gulirkan sidebar ke item aktif                                    */
  /* ---------------------------------------------------------------- */
  var active = document.querySelector(".nav-group a.active");
  if (active && sidebar && window.innerWidth > 860) {
    var top = active.offsetTop;
    if (top > sidebar.clientHeight - 120) {
      sidebar.scrollTop = top - sidebar.clientHeight / 2;
    }
  }
})();
