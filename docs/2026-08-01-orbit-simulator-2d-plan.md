# Dan's Orbit Simulator (2D) Implementation Plan

> **For agentic workers:** Executed inline in the authoring session (executing-plans style). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-contained single-file 2D orbital-mechanics teaching simulator (`orbit-simulator.html`) with real-time and planned burns, 5 guided lessons, and a sandbox.

**Architecture:** Hybrid propagation — analytic Kepler coast from orbital elements, RK4 numerical integration during thrust. Physics developed and unit-tested standalone in Node first, then inlined into the single HTML file with renderer/ui/lessons/main sections.

**Tech Stack:** Vanilla JavaScript, Canvas 2D, zero dependencies. Node (already on this Mac) for physics unit tests during development only.

**Spec:** `docs/2026-08-01-orbit-simulator-2d-design.md`

---

### Task 1: Physics core (TDD in scratchpad, then inline)

**Files:**
- Create: `<scratchpad>/physics.js` (development copy; later inlined)
- Test: `<scratchpad>/test_physics.js` (run with `node`)

Constants: `MU = 398600.4418` km³/s², `R_EARTH = 6371` km. Units km, km/s, s.

Key formulas (2D):
- Specific energy ε = v²/2 − μ/r → semi-major axis a = −μ/(2ε)
- Angular momentum (scalar) h = x·vy − y·vx
- Eccentricity vector e⃗ = ((v²−μ/r)·r⃗ − (r⃗·v⃗)·v⃗)/μ; e = |e⃗|; ϖ = atan2(ey, ex)
- True anomaly ν from angle(e⃗ → r⃗), sign of r⃗·v⃗
- Kepler propagation: ν→E→M, M += n·dt (n = √(μ/a³)), solve M = E − e·sinE (Newton, 30 iter cap), E→ν→ state
- RK4 step for r̈ = −μ r⃗/r³ + a_thrust (thrust along/against velocity unit vector)

- [x] Step 1: Write failing tests — element/state roundtrip on a circular 300 km orbit; propagate one full period returns to start (< 1 m error); energy+h conserved over 10 orbits of coast; prograde impulse Δv₁ = v_c1(√(2r₂/(r₁+r₂))−1) at 300 km raises apoapsis to 1000 km ± 1 km (Hohmann leg 1); RK4 coast (no thrust) tracks Kepler within tolerance over ¼ orbit.
- [x] Step 2: Run `node test_physics.js` — expect failures (module empty).
- [x] Step 3: Implement `elementsFromState`, `stateFromElements`, `propagateKepler`, `rk4Step`, vector helpers.
- [x] Step 4: Run tests until all pass.

### Task 2: HTML skeleton, renderer, coast loop

**Files:**
- Create: `orbit-simulator.html` (project root)

- [x] Layout: full-viewport canvas left, side panel right (readouts, controls, lesson card). Dark space theme, plain-English labels + tooltips.
- [x] Renderer: world→screen transform auto-fit to current orbit (smooth zoom), Earth disc + atmosphere ring, orbit ellipse from elements, apoapsis/periapsis markers with km labels, ship marker + fading trail.
- [x] Main loop: requestAnimationFrame; Kepler coast; time-warp slider 1×–10,000×; readouts (Altitude, Speed, High point, Low point, Orbit time, Δv spent).
- [x] Verify in browser (local http server): stable circular orbit, correct readouts.

### Task 3: Real-time burns

- [x] Prograde/Retrograde buttons (hold) + ArrowUp/ArrowDown keys; while thrusting switch to RK4 sub-stepped integration; auto-cap warp at 50× during burns; accumulate Δv spent.
- [x] Live orbit ellipse deforms during the burn (elements recomputed every frame).
- [x] Verify: prograde burn raises the opposite side; retrograde lowers it.

### Task 4: Planned maneuver nodes

- [x] Pause + click near orbit → nearest-point-on-ellipse node (store true anomaly); Δv slider (retrograde…prograde, m/s); dashed preview orbit from impulse-applied state; Execute = warp to node, apply impulse, clear node.
- [x] Verify: plan Hohmann leg 2 at apoapsis, preview shows circular orbit, execute circularizes.

### Task 5: Lessons + sandbox

- [x] Data-driven lesson array: {id, title, goal, setup orbit, target (apo/peri + tolerance) or step checks, explainer}. Success detection each frame; completion card with "why that worked"; next-lesson navigation; target orbit drawn dashed.
- [x] Lessons per spec: (1) What is an orbit — observe + continue; (2) Raise the far side — apoapsis above target; (3) Where you burn matters — burn near marker A, auto-reset, burn near marker B; (4) Two-burn transfer — apo & peri within tolerance of target circle; (5) Coming home — periapsis below re-entry altitude.
- [x] Sandbox mode: free play, reset button, Δv counter.

### Task 6: Edge handling + polish

- [x] Crash (radius < R_EARTH + 0.1 during sim): "You deorbited!" overlay + reset. Escape (e ≥ 1): switch to RK4 rendering of departure + "You've escaped!" overlay + reset. Guards near-circular (e < 1e-6) and near-parabolic element math.
- [x] Tooltips on every technical term; layman phrasing pass.

### Task 7: Browser verification (all lessons, both modes)

- [x] Serve folder via `.claude/launch.json` http server; play through all 5 lessons + sandbox; check console for errors; screenshot proof for user.

## Self-review

Spec coverage: every spec section maps to a task (physics→1, display→2, real-time→3, planned→4, lessons/sandbox→5, edges/tooltips→6, verification→1+7). No placeholders — formulas and tolerances stated where risk lives; full code is authored in Task steps by the same agent that wrote this plan. Naming used consistently: `elementsFromState`, `stateFromElements`, `propagateKepler`, `rk4Step`.
