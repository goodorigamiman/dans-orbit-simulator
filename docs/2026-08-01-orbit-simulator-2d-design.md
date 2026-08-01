# Dan's Orbit Simulator — 2D Teaching Aid (v1 Design)

**Date:** 2026-08-01
**Status:** Approved by user (design approved in-session)
**Deliverable:** One self-contained HTML file: `orbit-simulator.html`

## Purpose

A layman-level training aid teaching the core counterintuitive principle of orbital
mechanics: *where and when you fire your engines determines where the orbit changes —
and the change happens on the opposite side of the orbit.* Built for self-paced
learners (no live instructor required). v1 is 2D; a 3D version is a possible later
phase and is explicitly out of scope, except that the physics core uses general
vector math so it can be extended.

## Audience & Tone

- Self-paced learners with no physics background ("we're not all rocket scientists").
- Every technical term (apoapsis, periapsis, prograde, delta-v, eccentricity) gets a
  plain-English label first and a hover tooltip explanation.
- Friendly failure handling: crashing or escaping Earth produces an encouraging
  message and a reset, never an error state.

## Core Simulation

- **Model:** 2D two-body problem — Earth (point mass, real μ = 398,600.4418 km³/s²,
  radius 6,371 km) plus one ship. No atmosphere drag, no third bodies.
- **Propagation (hybrid):**
  - **Coasting:** analytic Kepler propagation from orbital elements. Orbit is exact
    and drift-free at any time warp.
  - **Thrusting:** numerical integration (RK4) of gravity + thrust acceleration,
    with sub-stepping bounded so integration stays accurate at moderate warp.
  - Orbital elements are recomputed from the state vector continuously, powering the
    live predicted-orbit overlay.
- **Units shown to the user:** altitude in km, speed in km/s, delta-v in m/s,
  period in minutes. Internally consistent km/s/kg SI-derived units.
- **Time warp:** slider from 1× to ~10,000×. Thrust is limited/disabled above a warp
  threshold (burns auto-drop warp to a safe level).

## Display

Canvas scene, centered on Earth (scale auto-fits the current orbit with margin):

- Earth disc with surface + faint atmosphere ring.
- Ship marker with heading indicator; short fading trail.
- **Current orbit ellipse drawn live** — updates continuously during burns (the
  signature visual: hold prograde and watch the far side balloon outward).
- Apoapsis/periapsis markers on the ellipse with altitude labels.
- Target orbit (dashed, distinct color) when a lesson defines one.
- Readout panel (plain-English labels + tooltips): Altitude, Speed, High point
  (apoapsis), Low point (periapsis), Orbit time (period), plus total delta-v spent.

## Burn Modes

1. **Real-time:** hold Prograde / Retrograde buttons (or arrow keys). Thrust applies
   while held; the orbit ellipse deforms live. Teaches the *feel*.
2. **Planned (maneuver node):** pause, click a point on the orbit to place a node,
   set prograde/retrograde delta-v with a slider, see a dashed preview of the
   post-burn orbit, then Execute — the sim fast-forwards to the node and applies the
   burn as an impulse. Teaches the *planning* (and makes the two-burn transfer
   clean).

## Lessons (guided mode)

Each lesson has: a plain-English goal card, an optional target orbit drawn on
screen, automatic success detection (orbit parameters within tolerance), and a short
"why that worked" explainer on completion. Lesson definitions are data-driven
(array of scenario objects), not hard-coded UI.

1. **What is an orbit?** — observe a circular orbit; explanation that orbiting is
   falling around the Earth. Success: just proceed after reading/watching.
2. **Raise the far side** — fire prograde; watch apoapsis rise on the *opposite*
   side. Success: apoapsis above a stated altitude.
3. **Where you burn matters** — apply the same burn at different points on the
   orbit and compare outcomes. Success: complete the comparison steps.
4. **The two-burn transfer** — raise apoapsis to a target altitude, coast to
   apoapsis, burn again to circularize (Hohmann transfer). Success: both apoapsis
   and periapsis within tolerance of the target circular orbit.
5. **Coming home** — retrograde burn to lower periapsis below the atmosphere line.
   Success: periapsis below the stated re-entry altitude.

## Sandbox

All controls unlocked, no goal. Reset button restores the starting circular orbit.
Fuel is infinite in v1 but cumulative delta-v spent is displayed.

## Edge Handling

- **Crash:** periapsis (or radius) below surface at the ship's position → friendly
  "You deorbited!" overlay + reset offer.
- **Escape:** eccentricity ≥ 1 → friendly "You've escaped Earth's gravity!"
  overlay + reset offer; hyperbolic path rendered up to a bounded range.
- Numerical guards on element conversion near-circular/near-parabolic cases.

## Architecture

Single HTML file, vanilla JS + Canvas 2D, zero external dependencies, works
offline. Internally sectioned as clear modules within the file:

- `physics` — element↔state conversions, Kepler propagation, RK4 thrust step.
  Written with general vector helpers (extensible to 3D later).
- `renderer` — canvas drawing (scene, orbits, markers, labels).
- `ui` — controls, readouts, tooltips, time warp, burn buttons, maneuver-node
  interaction.
- `lessons` — data-driven scenario definitions + success detection + explainers.
- `main` — game loop, state machine (coast / burn / paused / overlay).

## Verification

- Physics sanity checks: energy and angular-momentum conservation while coasting;
  Hohmann transfer delta-v for a known case (e.g. 300 km → 1,000 km circular)
  matches textbook values within tolerance.
- Manual browser verification of all five lessons and both burn modes via the
  in-app flow before delivery.

## Out of Scope (v1)

3D visualization, inclination/plane changes, normal/radial burn directions, fuel
mass & Tsiolkovsky, multiple bodies, atmosphere drag modeling, sound.
