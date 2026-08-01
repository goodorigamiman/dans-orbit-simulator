# Dan's Orbit Simulator v2 — Multi-Burn Plans, Vectored Thrust, and the Moon

**Date:** 2026-08-01
**Status:** Approved by user (design approved in-session)
**Baseline:** v1 `orbit-simulator.html` (see `2026-08-01-orbit-simulator-2d-design.md`) —
all v1 behavior (lessons 1–5, live + planned burns, sandbox, hazards) must survive
regression unchanged unless stated here.

## Feature 1 — Multi-burn flight plan

- `app.plan` = ordered array of nodes `{nu, dv, angDeg}`; node k is defined **on the
  orbit that exists after node k−1** (chained semantics).
- Chained preview: successive post-burn orbits drawn dashed, numbered ① ② ③ at node
  markers; predicted high/low text reflects the **final** orbit of the chain.
- Plan list UI: one row per node (number, burn size, direction); selecting a row binds
  the dv/direction sliders to it; per-row delete; Clear plan.
- Placement: canvas click or @ Low/@ High snaps place the next node on the LAST
  planned orbit.
- Execute: sequentially — warp to node 1 (`timeToNu` on the current orbit), apply
  impulse, re-derive orbit, continue to node 2, etc. Auto-warp targets ~4 real
  seconds per leg. Any live thrust cancels the remaining plan (pilot override);
  the un-flown nodes are discarded with a banner note.
- Frame switches (SOI handoff) clear the plan — plans are frame-local.

## Feature 2 — Vectored thrust (still 2D)

- Direction convention: angle relative to **prograde** (velocity direction).
  0° = prograde, 180° = retrograde, ±90° = sideways (radial out/in by sign).
- **Planned nodes:** full direction dial −180°…180°, 5° steps. Impulse vector =
  `rotate(v̂ at node, angDeg) × dv`.
- **Live burns:** the ▲/▼ buttons keep their meaning (0°/180°); a "steer" slider
  adds ±90° offset to whichever is held. Thrust flame renders in the true thrust
  direction.
- Teaching payoff (lesson 6): off-axis burns rotate/reshape the orbit but add little
  size — prograde is the most fuel-efficient way to change orbit size.

## Feature 3 — The Moon (patched conics)

- **Model:** two-body patched conics. Ship belongs to exactly one primary at a time
  (`earth` or `moon` frame). Crossing the Moon's sphere of influence converts the
  state vector between frames (subtract/add the Moon's position & circular-orbit
  velocity); each frame is pure Kepler around that body's μ.
- **Constants:** μ_moon = 4902.8 km³/s², R_moon = 1737.4 km. Moon on a circular,
  counter-clockwise orbit around Earth; SOI = a_moon·(μ_moon/μ_earth)^(2/5).
- **Scale toggle (user-selected "Both"):**
  - *Real Moon:* a_moon = 384,400 km (SOI ≈ 66,200 km, transfer ≈ 5 days).
  - *Classroom Moon:* a_moon = 100,000 km (SOI ≈ 17,200 km, transfer ≈ 17 h) — same
    physics, Moon simply closer so Earth + orbit + Moon fit one view.
  - Toggling resets the active scenario (in-flight states are scale-dependent).
- **Propagation:** coasting stays fully analytic in both frames. Hyperbolic Kepler
  propagation (hyperbolic anomaly + Newton on M = e·sinh F − F) is added so flybys
  and escapes are drift-free at max warp. RK4 (current primary's gravity only)
  remains the thrust integrator.
- **SOI crossing detection:** when the earth-frame orbit can reach Moon vicinity
  (apoapsis > 0.5 × a_moon), coast frames are internally substepped (~24×) so high
  time warp cannot tunnel through the SOI. Entry/exit swaps frames, shows a banner,
  clears the plan, and re-centers the camera (smooth lerp) on the new primary.
- **Rendering:** Moon disc + faint dashed SOI circle (a named teaching element);
  moon-frame orbits drawn around the Moon's current position; camera centers on the
  active primary and fits that frame's orbit envelope. Escape overlay moves out to
  ~1.5 × a_moon; zoom clamp updated to match.
- **Hazards:** surface contact on the Moon → friendly "You hit the Moon!" overlay;
  leaving the SOI outbound after a flyby is not an error (banner explains the
  slingshot; lesson 8 treats it as "try again, brake earlier").

## Lessons 6–8 (same layman tone, success detection, debriefs)

6. **Steering the burn** — no Moon. Steer ≥60° off-prograde, burn ≥40 m/s; watch the
   orbit *tilt* more than it grows. Debrief compares with a prograde burn and states
   the rule: prograde buys the most orbit per unit of fuel.
7. **Lead the Moon** — Moon enabled. Plan a transfer burn; when a planned orbit's
   high point reaches Moon altitude, a **ghost Moon at your arrival time** is drawn.
   Success: actually enter the SOI. Concepts: lead angle, transfer window, "aim
   where it will be."
8. **Lunar orbit insertion** — starts just inside the SOI on an incoming flyby
   (perilune ≈ 150 km, v∞ ≈ 0.8 km/s); doing nothing slingshots you back out.
   Success: burn retrograde near closest approach until captured (bound moon orbit,
   apolune < 0.9 × SOI). Concepts: SOI handoff, capture burn, "arriving is braking."

Sandbox gains: Moon on/off checkbox, Real/Classroom scale radio, existing presets.

## Build stages (each verified in browser before the next)

A. Physics core generalized to any μ + hyperbolic Kepler (+ hyperbolic `timeToNu`);
   TDD in scratchpad Node tests first.
B. Vectored thrust (steer slider, node direction dial, flame).
C. Multi-burn plan (chained preview, list UI, sequential execute, override cancel).
D. Moon: frames, SOI handoff, scale toggle, camera, lessons 6–8, sandbox controls.

Definition of done: lessons 1–8 full play-through passes, hazards verified in both
frames, physics badge green, Node tests green, console clean, repo + Pages updated.

## Out of scope (v2)

3D, inclination, n-body/free-return trajectories, fuel mass, atmosphere drag model,
sound, Lagrange points, landing on either body.
