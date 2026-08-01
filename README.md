# Dan's Orbit Simulator

A 2D orbital-mechanics training aid. **Double-click `orbit-simulator.html`** — it opens
in any web browser, works offline, and needs no installation.

## What it teaches

The most important (and most counterintuitive) idea in orbital mechanics:

> **Where and when you fire your engines decides where your orbit changes — and the
> change shows up on the opposite side of the orbit.**

## How to use it

- **Lessons tab** — five short guided lessons, in order:
  1. *What is an orbit?* — orbiting is falling sideways forever
  2. *Raise the far side* — a prograde burn raises the opposite side
  3. *Where you burn matters* — same burn, different spot, different orbit
  4. *The two-burn transfer* — the Hohmann transfer: two burns to move both sides
  5. *Coming home* — slow down here, re-enter over there
- **Sandbox tab** — free play, no goals, reset any time.
- **Live burns** — hold ▲ Prograde / ▼ Retrograde (or the ↑/↓ arrow keys) and watch
  the orbit deform in real time.
- **Planned burns** — place a maneuver point on the orbit, dial in a burn, preview the
  dashed result, then execute — like real mission control.
- Hover any dotted-underlined term for a plain-English explanation.

## iPhone / iPad

Opening the raw HTML file from Messages, Mail, or the Files app shows Apple's
QuickLook preview, which does **not** run apps — the screen stays empty. On an iPad:

1. **Easiest:** open the hosted version in Safari —
   **https://goodorigamiman.github.io/dans-orbit-simulator/** — and optionally
   Share → *Add to Home Screen* for an app-style icon.
2. Landscape orientation works best. **Hold** the burn buttons (don't just tap).
3. Offline alternative: serve the folder from a computer on the same Wi-Fi
   (`python3 -m http.server 8080`) and open `http://<computer-ip>:8080/orbit-simulator.html`.

## Notes

- Real Earth physics (analytic Kepler propagation while coasting, RK4 during burns);
  the numbers you see — 7.7 km/s, 92-minute orbits — are the real ones.
- Design + implementation docs live in `docs/`.
- Planned next step (after mastering 2D): a 3D version. The physics core is written
  with general vector math so it can be extended.
