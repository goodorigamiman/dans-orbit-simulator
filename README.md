# Dan's Orbit Simulator

A 2D orbital-mechanics training aid. **Double-click `orbit-simulator.html`** — it opens
in any web browser, works offline, and needs no installation.

## What it teaches

The most important (and most counterintuitive) idea in orbital mechanics:

> **Where and when you fire your engines decides where your orbit changes — and the
> change shows up on the opposite side of the orbit.**

## How to use it

- **Lessons tab** — nine short guided lessons, in order:
  1. *What is an orbit?* — orbiting is falling sideways forever
  2. *Raise the far side* — a prograde burn raises the opposite side
  3. *Where you burn matters* — same burn, different spot, different orbit
  4. *The two-burn transfer* — the Hohmann transfer: two burns to move both sides
  5. *Coming home* — slow down here, re-enter over there
  6. *Steering the burn* — sideways thrust rotates the orbit; prograde grows it
  7. *Breaking free* — escape velocity: the √2 speed where the orbit tears open
  8. *Lead the Moon* — aim where the Moon WILL be (transfer windows)
  9. *Lunar orbit insertion* — arrive on a flyby, brake at closest approach, get captured
- **Sandbox tab** — free play with the Moon, presets, no goals, reset any time.
- **Live burns** — hold ▲ Prograde / ▼ Retrograde (or the ↑/↓ arrow keys) and watch
  the orbit deform in real time; the *Steer* slider tilts the engine up to ±90°.
- **Flight plan** — chain up to **5 maneuver points**, each its own block with a burn
  strength AND direction, individually editable/removable; the dashed previews and
  the plan summary always show the combined result of every scheduled burn. A Range
  selector (±100 / ±500 / ±3500 m/s) switches the slider between trim burns and big
  departures, and a number box takes exact values.
- **The Moon** — orbits Earth with its real gravity; cross the dashed *sphere of
  influence* and the sim hands you over to Moon-centered orbit (patched conics, the
  same model mission planners teach). Toggle between the real 384,400 km distance
  and a closer "classroom" Moon that fits on one screen.
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
