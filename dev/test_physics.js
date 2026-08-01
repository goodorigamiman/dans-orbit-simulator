// Unit tests for the orbit simulator physics core. Run: node test_physics.js
const P = require('./physics.js');

let failures = 0;
function check(name, cond, detail) {
  if (cond) { console.log(`PASS  ${name}`); }
  else { failures++; console.log(`FAIL  ${name}${detail ? '  (' + detail + ')' : ''}`); }
}
function approx(x, y, tol) { return Math.abs(x - y) <= tol; }

const MU = P.MU, R = P.R_EARTH;

// --- Test 1: circular 300 km orbit — elements and roundtrip ---
{
  const r1 = R + 300;
  const vc = Math.sqrt(MU / r1);
  const s = { r: [r1, 0], v: [0, vc] };
  const el = P.elementsFromState(s);
  check('circular: a ≈ r', approx(el.a, r1, 1e-6 * r1), `a=${el.a}`);
  check('circular: e ≈ 0', el.e < 1e-8, `e=${el.e}`);
  const s2 = P.stateFromElements(el);
  check('circular roundtrip r', approx(s2.r[0], s.r[0], 1e-6) && approx(s2.r[1], s.r[1], 1e-6),
    `r=[${s2.r}]`);
  check('circular roundtrip v', approx(s2.v[0], s.v[0], 1e-9) && approx(s2.v[1], s.v[1], 1e-9),
    `v=[${s2.v}]`);
}

// --- Test 2: elliptical roundtrip at an off-axis point ---
{
  const s = { r: [5000, 4500], v: [-4.2, 5.1] };
  const el = P.elementsFromState(s);
  check('elliptical: bound orbit', el.a > 0 && el.e < 1, `a=${el.a} e=${el.e}`);
  const s2 = P.stateFromElements(el);
  check('elliptical roundtrip r', approx(s2.r[0], s.r[0], 1e-5) && approx(s2.r[1], s.r[1], 1e-5),
    `r=[${s2.r}] vs [${s.r}]`);
  check('elliptical roundtrip v', approx(s2.v[0], s.v[0], 1e-8) && approx(s2.v[1], s.v[1], 1e-8),
    `v=[${s2.v}] vs [${s.v}]`);
}

// --- Test 3: Kepler propagation over one full period returns to start ---
{
  const s = { r: [R + 400, 0], v: [0.9, 8.2] };
  const el = P.elementsFromState(s);
  const T = 2 * Math.PI * Math.sqrt(el.a ** 3 / MU);
  const el2 = P.propagateKepler(el, T);
  const s2 = P.stateFromElements(el2);
  check('full period returns to start (pos < 1 m)',
    approx(s2.r[0], s.r[0], 1e-3) && approx(s2.r[1], s.r[1], 1e-3),
    `r=[${s2.r}] vs [${s.r}]`);
}

// --- Test 4: RK4 coast tracks Kepler over a quarter orbit ---
{
  const s0 = { r: [R + 400, 0], v: [0, Math.sqrt(MU / (R + 400)) * 1.05] };
  const el0 = P.elementsFromState(s0);
  const T = 2 * Math.PI * Math.sqrt(el0.a ** 3 / MU);
  const dt = 1.0, steps = Math.round(T / 4 / dt);
  let s = { r: s0.r.slice(), v: s0.v.slice() };
  for (let i = 0; i < steps; i++) s = P.rk4Step(s, dt, null);
  const sk = P.stateFromElements(P.propagateKepler(el0, steps * dt));
  const err = Math.hypot(s.r[0] - sk.r[0], s.r[1] - sk.r[1]);
  check('RK4 vs Kepler quarter-orbit error < 0.5 km', err < 0.5, `err=${err} km`);
  const e0 = P.specificEnergy(s0), e1 = P.specificEnergy(s);
  check('RK4 energy drift tiny', Math.abs(e1 - e0) / Math.abs(e0) < 1e-9,
    `rel drift=${Math.abs(e1 - e0) / Math.abs(e0)}`);
}

// --- Test 5: Hohmann leg 1 — prograde impulse raises apoapsis to target ---
{
  const r1 = R + 300, r2 = R + 1000;
  const vc1 = Math.sqrt(MU / r1);
  const dv1 = vc1 * (Math.sqrt(2 * r2 / (r1 + r2)) - 1);
  const s = { r: [r1, 0], v: [0, vc1 + dv1] };
  const el = P.elementsFromState(s);
  const apo = el.a * (1 + el.e);
  check('Hohmann leg 1: apoapsis ≈ target', approx(apo, r2, 1.0), `apo=${apo} target=${r2}`);
  check('Hohmann leg 1: periapsis stays', approx(el.a * (1 - el.e), r1, 1.0),
    `peri=${el.a * (1 - el.e)}`);
}

// --- v2 Test 6: elements/state roundtrip around the MOON's mu ---
{
  const MU_M = P.MU_MOON, R_M = 1737.4;
  const r1 = R_M + 100;
  const vc = Math.sqrt(MU_M / r1);
  const s = { r: [r1, 0], v: [0, vc] };
  const el = P.elementsFromState(s, MU_M);
  check('moon circular: a ≈ r', approx(el.a, r1, 1e-6 * r1), `a=${el.a}`);
  const s2 = P.stateFromElements(el, MU_M);
  check('moon roundtrip', approx(s2.r[0], s.r[0], 1e-6) && approx(s2.v[1], s.v[1], 1e-9));
  const elP = P.propagateKepler(el, P.orbitalPeriod(el.a, MU_M), MU_M);
  const sP = P.stateFromElements(elP, MU_M);
  check('moon full period returns (<1 m)', approx(sP.r[0], s.r[0], 1e-3) && approx(sP.r[1], s.r[1], 1e-3),
    `r=[${sP.r}]`);
}

// --- v2 Test 7: hyperbolic roundtrip ---
{
  const s = { r: [8000, 2000], v: [3.0, 9.5] };   // well above escape speed
  const el = P.elementsFromState(s);
  check('hyperbolic: e > 1, a < 0', el.e > 1 && el.a < 0, `e=${el.e} a=${el.a}`);
  const s2 = P.stateFromElements(el);
  check('hyperbolic roundtrip r', approx(s2.r[0], s.r[0], 1e-4) && approx(s2.r[1], s.r[1], 1e-4),
    `r=[${s2.r}] vs [${s.r}]`);
  check('hyperbolic roundtrip v', approx(s2.v[0], s.v[0], 1e-7) && approx(s2.v[1], s.v[1], 1e-7),
    `v=[${s2.v}] vs [${s.v}]`);
}

// --- v2 Test 8: hyperbolic Kepler propagation matches RK4 ---
{
  const MU_M = P.MU_MOON;
  // incoming lunar flyby: perilune 150 km, vinf ~0.8 km/s
  const rp = 1737.4 + 150, vinf = 0.8;
  const a = -MU_M / (vinf * vinf);
  const e = 1 + rp * vinf * vinf / MU_M;
  const el0 = { a, e, omega: 0.3, nu: P.normAngle(-1.8), dir: 1 };
  let s = P.stateFromElements(el0, MU_M);
  const dt = 1.0, steps = 3000;
  for (let i = 0; i < steps; i++) s = P.rk4Step(s, dt, null, MU_M);
  const elK = P.propagateKepler(el0, steps * dt, MU_M);
  const sK = P.stateFromElements(elK, MU_M);
  const err = Math.hypot(s.r[0] - sK.r[0], s.r[1] - sK.r[1]);
  check('hyperbolic Kepler vs RK4 (<0.1 km after 3000 s)', err < 0.1, `err=${err} km`);
}

// --- v2 Test 9: timeToNu on a hyperbolic orbit reaches perilune ---
{
  const MU_M = P.MU_MOON;
  const rp = 1737.4 + 150, vinf = 0.8;
  const a = -MU_M / (vinf * vinf);
  const e = 1 + rp * vinf * vinf / MU_M;
  const el0 = { a, e, omega: 0, nu: P.normAngle(-1.2), dir: 1 };
  const t = P.timeToNu(el0, 0, MU_M);
  check('hyperbolic timeToNu positive & finite', isFinite(t) && t > 0, `t=${t}`);
  const el1 = P.propagateKepler(el0, t, MU_M);
  let nu1 = el1.nu > Math.PI ? el1.nu - 2 * Math.PI : el1.nu;
  check('propagating that long lands at perilune', Math.abs(nu1) < 1e-6, `nu=${nu1}`);
}

// --- v2 Test 10: elliptic timeToNu quarter-orbit sanity ---
{
  const r1 = R + 500;
  const s = { r: [r1, 0], v: [0, Math.sqrt(MU / r1)] };
  const el = P.elementsFromState(s);
  const t = P.timeToNu(el, Math.PI / 2);
  check('elliptic timeToNu = T/4 on circle', approx(t, P.orbitalPeriod(el.a) / 4, 1), `t=${t}`);
}

console.log(failures === 0 ? '\nALL TESTS PASSED' : `\n${failures} TEST(S) FAILED`);
process.exit(failures === 0 ? 0 : 1);
