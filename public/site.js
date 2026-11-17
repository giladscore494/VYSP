// Public gallery: image fade-in and a full-screen viewer. Works without this script too:
// every photo is a plain link to its large version.
(function () {
  "use strict";
  document.documentElement.classList.add("js");

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  function markLoaded(img) { img.classList.add("is-loaded"); }

  // The lead photograph on phones fills the screen below the masthead; measure the masthead.
  function measureMasthead() {
    const m = document.querySelector(".masthead");
    if (m) document.documentElement.style.setProperty("--mast", Math.ceil(m.getBoundingClientRect().height) + "px");
  }

  function init() {
    measureMasthead();
    window.addEventListener("resize", measureMasthead, { passive: true });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(measureMasthead);
    const frames = Array.from(document.querySelectorAll(".frame"));

    frames.forEach(function (frame) {
      const img = frame.querySelector("img");
      if (!img) return;
      if (img.complete && img.naturalWidth > 0) markLoaded(img);
      else {
        img.addEventListener("load", function () { markLoaded(img); }, { once: true });
        img.addEventListener("error", function () { markLoaded(img); }, { once: true });
      }
    });

    const dialog = document.querySelector(".viewer");
    if (!dialog || !frames.length || typeof dialog.showModal !== "function") return;

    const view = dialog.querySelector(".viewer-img");
    const count = dialog.querySelector(".viewer-count");
    const caption = dialog.querySelector(".viewer-caption");
    const prevBtn = dialog.querySelector("[data-step='-1']");
    const nextBtn = dialog.querySelector("[data-step='1']");
    const total = frames.length;
    let index = 0;
    let opener = null;
    let loadToken = 0;

    const items = frames.map(function (frame) {
      const img = frame.querySelector("img");
      const item = frame.closest(".item");
      const cap = item && item.querySelector(".caption");
      return {
        frame: frame,
        thumb: img,
        large: frame.getAttribute("href"),
        w: Number(frame.dataset.w) || 0,
        h: Number(frame.dataset.h) || 0,
        alt: img ? img.alt : "",
        caption: cap ? cap.textContent : "",
      };
    });

    function preload(i) {
      if (i < 0 || i >= total) return;
      const im = new Image();
      im.decoding = "async";
      im.src = items[i].large;
    }

    function show(i) {
      index = Math.max(0, Math.min(total - 1, i));
      const it = items[index];
      const token = ++loadToken;
      // Show the already-loaded small version at once, then swap in the large one.
      const small = it.thumb ? (it.thumb.currentSrc || it.thumb.src) : it.large;
      view.src = small;
      if (it.w && it.h) { view.width = it.w; view.height = it.h; }
      view.alt = it.alt;
      if (small !== it.large) {
        const full = new Image();
        full.decoding = "async";
        full.onload = function () { if (token === loadToken) view.src = it.large; };
        full.src = it.large;
      }
      caption.textContent = it.caption;
      count.textContent = (index + 1) + " / " + total;
      prevBtn.disabled = index === 0;
      nextBtn.disabled = index === total - 1;
      preload(index + 1);
      preload(index - 1);
    }

    function withTransition(update, thumb) {
      if (!document.startViewTransition || reduceMotion.matches || !thumb) { update(); return; }
      thumb.style.viewTransitionName = "photo";
      const t = document.startViewTransition(function () {
        thumb.style.viewTransitionName = "";
        update();
        view.style.viewTransitionName = "photo";
      });
      t.finished.finally(function () { view.style.viewTransitionName = ""; });
    }

    function open(i) {
      opener = items[i].frame;
      withTransition(function () {
        show(i);
        dialog.showModal();
        document.documentElement.style.overflow = "hidden";
      }, items[i].thumb);
    }

    function close() {
      if (!dialog.open) return;
      const thumb = items[index].thumb;
      const target = items[index].frame;
      const finish = function () {
        dialog.close();
        document.documentElement.style.overflow = "";
      };
      if (!document.startViewTransition || reduceMotion.matches || !thumb || !inViewport(target)) {
        finish();
      } else {
        view.style.viewTransitionName = "photo";
        const t = document.startViewTransition(function () {
          view.style.viewTransitionName = "";
          finish();
          thumb.style.viewTransitionName = "photo";
        });
        t.finished.finally(function () { thumb.style.viewTransitionName = ""; });
      }
      const focusTarget = items[index].frame || opener;
      if (focusTarget) focusTarget.focus({ preventScroll: true });
    }

    function inViewport(el) {
      const r = el.getBoundingClientRect();
      return r.bottom > 0 && r.top < window.innerHeight;
    }

    function step(delta) {
      const next = index + delta;
      if (next < 0 || next >= total) return;
      show(next);
      // Keep the page behind in step, so closing returns to the photo just viewed.
      items[index].frame.scrollIntoView({ block: "nearest" });
    }

    frames.forEach(function (frame, i) {
      frame.addEventListener("click", function (e) {
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
        e.preventDefault();
        open(i);
      });
    });

    dialog.addEventListener("click", function (e) {
      const btn = e.target.closest("button");
      if (btn && btn.hasAttribute("data-close")) { close(); return; }
      if (btn && btn.dataset.step) { step(Number(btn.dataset.step)); return; }
      // A tap on the empty white around the photo closes the viewer.
      if (e.target === dialog || e.target.classList.contains("viewer-stage")) close();
    });

    dialog.addEventListener("cancel", function (e) { e.preventDefault(); close(); });

    // Right to left: the next photo sits to the left.
    dialog.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") { e.preventDefault(); step(1); }
      else if (e.key === "ArrowRight") { e.preventDefault(); step(-1); }
      else if (e.key === "Home") { e.preventDefault(); show(0); }
      else if (e.key === "End") { e.preventDefault(); show(total - 1); }
    });

    // Swipe. Finger moving right brings the next photo (right-to-left order).
    let sx = 0, sy = 0, tracking = false;
    const stage = dialog.querySelector(".viewer-stage");
    stage.addEventListener("touchstart", function (e) {
      if (e.touches.length !== 1) { tracking = false; return; }
      tracking = true;
      sx = e.touches[0].clientX;
      sy = e.touches[0].clientY;
    }, { passive: true });
    stage.addEventListener("touchend", function (e) {
      if (!tracking) return;
      tracking = false;
      if (window.visualViewport && window.visualViewport.scale > 1.01) return; // zoomed in: let the user pan
      const t = e.changedTouches[0];
      const dx = t.clientX - sx;
      const dy = t.clientY - sy;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.4) step(dx > 0 ? 1 : -1);
      else if (dy > 90 && Math.abs(dy) > Math.abs(dx) * 1.4) close();
    }, { passive: true });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
