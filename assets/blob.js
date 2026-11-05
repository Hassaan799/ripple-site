// A soft glass blob that breathes behind the hero screenshot.
// No dependencies. One still frame when the visitor prefers reduced motion.
(function () {
  "use strict";
  var canvas = document.getElementById("hero-blob");
  if (!canvas || !canvas.getContext) return;
  var ctx = canvas.getContext("2d");
  var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)");
  var points = 8, frame = 0, last = 0, width = 0, height = 0, ratio = 1;

  function resize() {
    ratio = Math.min(window.devicePixelRatio || 1, 2);
    width = canvas.clientWidth; height = canvas.clientHeight;
    canvas.width = Math.round(width * ratio); canvas.height = Math.round(height * ratio);
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  }

  function shape(t, cx, cy, base) {
    var out = [];
    for (var i = 0; i < points; i++) {
      var a = (i / points) * Math.PI * 2;
      var r = base * (1 + 0.10 * Math.sin(t * 0.9 + i * 1.7) + 0.06 * Math.sin(t * 1.6 + i * 2.9));
      out.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r * 0.82]);
    }
    return out;
  }

  function trace(pts) {
    // Closed smooth curve through the points (midpoint quadratic segments).
    var n = pts.length;
    ctx.beginPath();
    ctx.moveTo((pts[n - 1][0] + pts[0][0]) / 2, (pts[n - 1][1] + pts[0][1]) / 2);
    for (var i = 0; i < n; i++) {
      var p = pts[i], q = pts[(i + 1) % n];
      ctx.quadraticCurveTo(p[0], p[1], (p[0] + q[0]) / 2, (p[1] + q[1]) / 2);
    }
    ctx.closePath();
  }

  function draw(t) {
    ctx.clearRect(0, 0, width, height);
    var cx = width * 0.5, cy = height * 0.5, base = Math.min(width, height) * 0.36;
    var fill = ctx.createRadialGradient(cx - base * 0.3, cy - base * 0.4, base * 0.1, cx, cy, base * 1.2);
    fill.addColorStop(0, "rgba(200, 206, 214, 0.20)");
    fill.addColorStop(1, "rgba(120, 128, 140, 0.04)");
    trace(shape(t, cx, cy, base));
    ctx.fillStyle = fill; ctx.fill();
    ctx.lineWidth = 1.5; ctx.strokeStyle = "rgba(255, 255, 255, 0.16)"; ctx.stroke();
    // Two small droplets orbiting slowly, like Ripple's Blob mode.
    for (var d = 0; d < 2; d++) {
      var a = t * 0.25 + d * Math.PI;
      var dx = cx + Math.cos(a) * base * 1.25, dy = cy + Math.sin(a) * base * 0.95;
      trace(shape(t + d * 3, dx, dy, base * 0.12));
      ctx.fillStyle = "rgba(210, 216, 224, 0.10)"; ctx.fill(); ctx.stroke();
    }
  }

  function loop(now) {
    frame = requestAnimationFrame(loop);
    if (now - last < 33) return; // ~30 fps is plenty for a slow breath
    last = now;
    draw(now / 1000);
  }

  function start() {
    cancelAnimationFrame(frame);
    resize();
    if ((still && still.matches) || document.hidden) { draw(1.2); return; }
    frame = requestAnimationFrame(loop);
  }

  window.addEventListener("resize", start);
  document.addEventListener("visibilitychange", start);
  if (still && still.addEventListener) still.addEventListener("change", start);
  start();
})();
