// Orbit simulator physics core — 2D two-body problem around Earth.
// Units: km, km/s, seconds. Vectors are [x, y] arrays so the math
// generalizes to 3D later by adding a component.
'use strict';

const MU = 398600.4418;   // Earth GM, km^3/s^2
const R_EARTH = 6371;     // km

const TWO_PI = Math.PI * 2;

function normAngle(a) {
  a = a % TWO_PI;
  return a < 0 ? a + TWO_PI : a;
}

function vdot(a, b) { return a[0] * b[0] + a[1] * b[1]; }
function vmag(a) { return Math.hypot(a[0], a[1]); }

function specificEnergy(s) {
  return vdot(s.v, s.v) / 2 - MU / vmag(s.r);
}

// State {r, v} -> elements {a, e, omega, nu, dir}
//   a     semi-major axis (km; negative if hyperbolic)
//   e     eccentricity
//   omega angle of periapsis from +x axis (rad)
//   nu    true anomaly, measured from periapsis IN the direction of motion (rad)
//   dir   +1 counter-clockwise orbit, -1 clockwise
function elementsFromState(s) {
  const r = s.r, v = s.v;
  const rm = vmag(r), vm2 = vdot(v, v);
  const h = r[0] * v[1] - r[1] * v[0];        // signed z-component
  const dir = h >= 0 ? 1 : -1;
  const energy = vm2 / 2 - MU / rm;
  const a = -MU / (2 * energy);
  const rv = vdot(r, v);
  const c = vm2 - MU / rm;
  const ex = (c * r[0] - rv * v[0]) / MU;
  const ey = (c * r[1] - rv * v[1]) / MU;
  const e = Math.hypot(ex, ey);
  let omega, nu;
  if (e < 1e-10) {
    // Circular: periapsis undefined; measure nu from the +x axis along motion.
    omega = 0;
    nu = normAngle(dir * Math.atan2(r[1], r[0]));
  } else {
    omega = Math.atan2(ey, ex);
    let cosNu = (ex * r[0] + ey * r[1]) / (e * rm);
    cosNu = Math.max(-1, Math.min(1, cosNu));
    nu = Math.acos(cosNu);
    if (rv < 0) nu = TWO_PI - nu;   // descending half
  }
  return { a, e, omega, nu, dir };
}

// Elements -> state {r, v}. Works for any conic as long as 1 + e*cos(nu) > 0.
function stateFromElements(el) {
  const { a, e, omega, nu, dir } = el;
  const p = a * (1 - e * e);                   // semi-latus rectum (>0 for any conic)
  const habs = Math.sqrt(Math.abs(MU * p));
  const rm = p / (1 + e * Math.cos(nu));
  const theta = omega + dir * nu;              // position angle in inertial frame
  const cosT = Math.cos(theta), sinT = Math.sin(theta);
  const vr = (MU / habs) * e * Math.sin(nu);   // radial speed (sign from sin nu)
  const vt = habs / rm;                        // transverse speed (magnitude)
  return {
    r: [rm * cosT, rm * sinT],
    v: [vr * cosT - dir * vt * sinT, vr * sinT + dir * vt * cosT],
  };
}

function trueToEccentric(nu, e) {
  return 2 * Math.atan2(Math.sqrt(1 - e) * Math.sin(nu / 2),
                        Math.sqrt(1 + e) * Math.cos(nu / 2));
}

function eccentricToTrue(E, e) {
  return normAngle(2 * Math.atan2(Math.sqrt(1 + e) * Math.sin(E / 2),
                                  Math.sqrt(1 - e) * Math.cos(E / 2)));
}

function solveKepler(M, e) {
  // Newton iteration on E - e*sin(E) = M
  let E = e < 0.8 ? M : Math.PI;
  for (let i = 0; i < 30; i++) {
    const f = E - e * Math.sin(E) - M;
    const fp = 1 - e * Math.cos(E);
    const dE = f / fp;
    E -= dE;
    if (Math.abs(dE) < 1e-13) break;
  }
  return E;
}

// Advance an elliptical orbit by dt seconds (analytic, drift-free).
function propagateKepler(el, dt) {
  const { a, e } = el;
  if (e >= 1 || a <= 0) throw new Error('propagateKepler: orbit is not elliptical');
  const n = Math.sqrt(MU / (a * a * a));
  const E0 = trueToEccentric(el.nu, e);
  const M0 = E0 - e * Math.sin(E0);
  const M = M0 + n * dt;
  const E = solveKepler(normAngle(M), e);
  return { ...el, nu: eccentricToTrue(E, e) };
}

function orbitalPeriod(a) {
  return TWO_PI * Math.sqrt(a * a * a / MU);
}

// One RK4 step of gravity plus optional thrust. thrustFn(r, v) -> [ax, ay] or null.
function rk4Step(s, dt, thrustFn) {
  function accel(r, v) {
    const rm = vmag(r);
    const g = -MU / (rm * rm * rm);
    let ax = g * r[0], ay = g * r[1];
    if (thrustFn) {
      const t = thrustFn(r, v);
      ax += t[0]; ay += t[1];
    }
    return [ax, ay];
  }
  const r0 = s.r, v0 = s.v;
  const a1 = accel(r0, v0);
  const r2 = [r0[0] + v0[0] * dt / 2, r0[1] + v0[1] * dt / 2];
  const v2 = [v0[0] + a1[0] * dt / 2, v0[1] + a1[1] * dt / 2];
  const a2 = accel(r2, v2);
  const r3 = [r0[0] + v2[0] * dt / 2, r0[1] + v2[1] * dt / 2];
  const v3 = [v0[0] + a2[0] * dt / 2, v0[1] + a2[1] * dt / 2];
  const a3 = accel(r3, v3);
  const r4 = [r0[0] + v3[0] * dt, r0[1] + v3[1] * dt];
  const v4 = [v0[0] + a3[0] * dt, v0[1] + a3[1] * dt];
  const a4 = accel(r4, v4);
  return {
    r: [r0[0] + dt / 6 * (v0[0] + 2 * v2[0] + 2 * v3[0] + v4[0]),
        r0[1] + dt / 6 * (v0[1] + 2 * v2[1] + 2 * v3[1] + v4[1])],
    v: [v0[0] + dt / 6 * (a1[0] + 2 * a2[0] + 2 * a3[0] + a4[0]),
        v0[1] + dt / 6 * (a1[1] + 2 * a2[1] + 2 * a3[1] + a4[1])],
  };
}

if (typeof module !== 'undefined') {
  module.exports = {
    MU, R_EARTH, normAngle, vdot, vmag, specificEnergy,
    elementsFromState, stateFromElements, propagateKepler,
    orbitalPeriod, rk4Step, trueToEccentric, eccentricToTrue, solveKepler,
  };
}
