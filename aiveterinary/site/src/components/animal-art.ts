/**
 * Sketch drawings of the animals, 48×48 grid, all in profile facing right, standing on y≈44.6.
 * Style: docs/32-illustration-style.md. Each shape is one path used twice: a flat coat fill nudged
 * down-right (an off-register wash, like ink over watercolour) and the ink contour on top.
 * Strokes inherit from the <svg> (var(--sk-line), round caps); `.d` marks detail strokes that are
 * lighter and hidden at chip size. Keys match src/lib/animal-icons.ts so every kind still resolves.
 */
const W = 'class="w"';
/** Coat wash plus ink contour for one closed shape. */
const s = (d: string, fill: string) => `<path d="${d}" fill="var(${fill})" ${W}/><path d="${d}"/>`;
/** Ink contour only (open line). */
const l = (d: string, extra = '') => `<path d="${d}"${extra}/>`;
/** Detail line: lighter, dropped at small sizes. */
const dl = (d: string) => `<path class="d" d="${d}"/>`;
/** Dark eye with a pinpoint highlight. */
const eye = (x: number, y: number, r = 1.15) =>
  `<circle class="e" cx="${x}" cy="${y}" r="${r}"/><circle class="h" cx="${+(x + r * 0.3).toFixed(2)}" cy="${+(y - r * 0.35).toFixed(2)}" r="${+(r * 0.34).toFixed(2)}"/>`;
/** Soft ground shadow under the feet. */
const ground = (x1: number, x2: number) => `<path class="sk-g" d="M${x1} 45.4h${x2 - x1}"/>`;

export const ICONS: Record<string, string> = {
  // Sitting dog, lab type: stop between skull and muzzle, drop ear, deep chest, round haunch, tail up.
  dog: ground(6, 38) +
    `<path d="M7.2 38.4C3.6 36.6 2.4 31.6 4 27.6c.5-1.1 1.8-.8 1.7.4-.4 3.4.8 6.4 3.4 7.8z" fill="var(--hs-dog)" ${W}/>` +
    l('M7.2 38.4C3.6 36.6 2.4 31.6 4 27.6c.5-1.1 1.8-.8 1.7.4-.4 3.4.8 6.4 3.4 7.8') +
    s('M40.4 13.4c1.6.8 1.6 3.6.2 4.4-1.6.9-4 1.2-6.2 2.4-.8 3.2-.6 6.4-1.2 9.6l-.2 12.4c0 1 1.4 1.4 2.8 1.8.8.3.4 1-.6 1H11.6C7.4 44.8 5.2 41 5.6 36.4c.6-5.6 3.8-10.8 8.4-14.8 3.4-3 6.4-6.6 8.4-10.4 1.6-3.2 4.2-5.2 7.6-5 2.6.2 4.4 1.8 5.6 4 1.4 1.4 3 2.4 4.8 3.2z', '--hs-dog') +
    s('M27.4 7.6c-2.8.4-4.2 3.8-4 7.6.2 3 1.2 5.4 3 5.2 1.8-.2 2.6-3 3-6.4.2-2.6-.2-5-2-6.4z', '--hs-dog-2') +
    l('M22.8 15.6c3.4 2.8 7.4 4.6 11.8 5', ' stroke="var(--sk-accent)" stroke-width="2.4"') +
    `<circle cx="33.6" cy="22.8" r="1.2" fill="var(--sk-accent)" stroke="none"/>` +
    eye(34.2, 11.8) +
    `<ellipse cx="40.9" cy="14.2" rx="1.4" ry="1.1" class="e"/>` +
    dl('M40.4 17.4c-1 .4-2.2.4-3.2 0') +
    dl('M30 44.4V32M27.6 44.4c-.2-6.2-4.6-12.6-11.8-14.2M16.6 26.4c1.4-.8 2.4-2 3-3.4M22.2 44.6c.2-1 .2-1.8-.2-2.6'),

  // Sitting cat, profile: two upright ear triangles, short muzzle with whisker pad, tail wrapped round the paws.
  cat: ground(8, 38) +
    s('M24.4 11.2c.4-1.8 1.2-3.4 2.2-4.6l.4-5 4.2 5c1.2 0 2.4.2 3.4.6l3-3.8-.2 6.2c.8 1 1.4 2.2 1.6 3.6l.6 1.6c.2.8-.2 1.4-.8 1.8-.6 1.2-1.8 2-3 2.4l-.6.8c1.4 2.8 1.6 6 .8 9.6l-.2 11.2c1 .6 2.4.8 2.8 1.8.2.8-.4 1.2-1.4 1.2H13.4C8.6 44.6 7.2 40 8.2 34c1.2-7.4 6-14.4 11-19.4 1.8-1.4 3.4-2.4 5.4-3.4z', '--hs-cat') +
    s('M9.8 39.6c-3.4 3.8-.8 6.4 4.6 6.4h15c3.8 0 5.8-1.6 5-3.2-.6-1-1.8-.6-3 0-1 .4-2.2.4-3.4.4H15c-2.8 0-4.2-1-3.6-3.2z', '--hs-cat') +
    `<path d="M27.6 3.8l-.2 3 2.4-.2zM36.8 5.4l-1.2 2 1.2.6z" fill="var(--ic-ear)" stroke="none"/>` +
    eye(33.6, 12.6, 1.05) +
    `<path d="M38.4 14.4l1.2.4-.9.9z" fill="var(--sk-accent)" stroke="var(--sk-accent)" stroke-width=".8"/>` +
    dl('M39.4 16.4l5.4-1M39.2 17.6l5 1.2M38.8 18.6l4 2.4') +
    dl('M20.2 21.2c-1.2 1.4-2.4 2.2-4 2.6M18.6 25c-1 1.4-2.2 2.2-3.8 2.6M30.8 27.6v13M24.4 41.2c.4-5.4-2.4-10-7.6-12'),

  // Crouching rabbit: long ears laid back, round haunch high and wide, cotton tail, blunt muzzle.
  rabbit: ground(6, 39) +
    s('M28.6 20.6c-4.6-3.8-8.6-9.6-8.6-13.6 0-2 2.2-2.6 3.8-.8 3 3.2 5.6 8.4 7.2 13.4z', '--ic-rabbit') +
    s('M40.6 26.6c.8 1.6-.2 3.2-2 3.6-1.6 1.6-3 3.2-4 4.8.6 2.6 1.8 5.4 2.6 7.2 1.6.4 1.8 1.6.6 2H12.8C7.6 44.2 4.8 40 5.4 34.6 6.2 27.4 12.6 22.4 20 22.4c4.2 0 7.2-1.2 9.6-2.8 3.6-2.2 8-.8 10.2 3.2.4.8.6 2.2.8 3.8z', '--ic-rabbit') +
    s('M30.2 20.4c-2-4.8-3.6-10.6-3.2-14.6.2-2.4 2.6-2.8 3.6-.6 1.8 4 2.8 9.2 3 14.4z', '--ic-rabbit') +
    `<path d="M30.6 17.4c-1-3.6-1.6-7-1.6-10 .8 2.4 1.8 6 2.4 9.6z" fill="var(--ic-ear)" stroke="none"/>` +
    s('M8 28.4c-2.4-.6-4.6 1-4.6 3.4 0 2.4 2.4 3.8 4.6 3 1.4-.6 2-2 1.8-3.6-.2-1.4-.8-2.4-1.8-2.8z', '--hs-cream') +
    eye(34.6, 24.4, 1.3) +
    `<path d="M40.2 25.6l.9.8-1.1.5z" fill="var(--sk-accent)" stroke="var(--sk-accent)" stroke-width=".8"/>` +
    dl('M28.6 44.2c.6-7.2-4.4-13-11.6-13.2M30.8 44.2h-6M41 27.4l4.2-.8M40.8 28.6l3.8.8'),

  // Guinea pig: loaf body, big blunt head, petal ear, no tail, tiny feet; bicolour coat.
  'guinea-pig': ground(6, 40) +
    s('M41.4 28.4c1.4 2.6 1.2 5.6-.8 7.6-1.4 2.6-3.6 4.6-6.2 5.6-1.4 1.6-3.4 2.4-6 2.4H13C7.2 44 3.8 40 4.2 34.2 4.8 26.2 11.4 20.6 20.4 20.2c7.8-.4 15 1 18.6 4.4.8.8 1.8 2.4 2.4 3.8z', '--hs-cream') +
    `<path d="M5.4 30.6c1.4-5.6 6-9.4 12.4-10.2 1.4 6 .8 13.6-2 19.6-4.4 1.8-8.6 1-10.4-2.8z" fill="var(--hs-dog-2)" stroke="none"/>` +
    `<path d="M29.4 21.4c4.6.8 8.4 2.4 10.4 5.2.6 1.4-.4 2.8-2.2 3-3.4.4-6.4-.6-7.6-3-.6-1.6-.8-3.6-.6-5.2z" fill="var(--ic-horse-2)" stroke="none"/>` +
    l('M41.4 28.4c1.4 2.6 1.2 5.6-.8 7.6-1.4 2.6-3.6 4.6-6.2 5.6-1.4 1.6-3.4 2.4-6 2.4H13C7.2 44 3.8 40 4.2 34.2 4.8 26.2 11.4 20.6 20.4 20.2c7.8-.4 15 1 18.6 4.4.8.8 1.8 2.4 2.4 3.8z') +
    s('M30.6 22.8c.4-2.6 3.4-3.4 4.8-1.4.8 1.6-.6 3.4-2.6 3.6-1 0-1.8-.8-2.2-2.2z', '--ic-ear') +
    eye(36.2, 27.4, 1.3) +
    `<ellipse cx="41.6" cy="31" rx=".9" ry=".7" class="e"/>` +
    dl('M40.6 33.6c-.8.6-1.8.6-2.6.2M42.4 32.4l3.6-.8M42.2 33.6l3.4 1') +
    `<path d="M33 44.2h3.4M15.4 44.2h3.6" stroke="var(--ic-ear)" stroke-width="2"/>`,

  // Ferret, bounding: long arched body, short legs, small round ear, dark mask over the eye, long tail.
  ferret: ground(4, 40) +
    s('M8.4 31.6C4.8 34 3 38.4 2.6 42.6c0 1.2 1.2 1.4 1.6.2 1-3.8 2.8-6.4 5-7.4z', '--ic-ferret-2') +
    s('M45 34.4c.4 1.4-.8 2.2-2.6 2.2-2 .2-4 .2-5.8 1l-1 5c-.2 1.2-1.2 1.8-2.6 1.8h-2.8l1-1.4-.4-4.8c-1.8-4.2-5.2-6.8-8.8-6.8s-6.2 2.6-7.2 6.6l-.4 4.8c-.4 1.4-2 1.6-3.4 1.6H8.2l1.2-1.6c-.4-4.2-1.8-8.2-1.6-12.8.4-6.6 6.6-10.6 14.2-10.6 6 0 10.4 3.2 13.2 6.8 3.4.6 6.4 2.4 8.2 5.2.6 1 1.2 2 1.6 3z', '--ic-ferret') +
    `<path d="M15.4 34c-.8 2-1 5-1 8.8-.4 1.4-2 1.6-3.4 1.6H8.2l1.2-1.6c-.4-3.8-1.4-6.8-1.6-10.2 2.6.8 5.2 1.2 7.6 1.4zM30.6 37l.6 6-1 1.4H33c1.4 0 2.4-.6 2.6-1.8l1-5c-2 .2-4 0-6-.6z" fill="var(--ic-ferret-2)" stroke="none"/>` +
    `<path d="M37 29.6c1.8-.8 4.6-.2 5.6 1.8.4 1.2-.6 2-2 2-1.6 0-3.2-.6-4-1.8-.4-.8-.2-1.6.4-2z" fill="var(--ic-ferret-2)" stroke="none"/>` +
    `<path d="M41.6 34c1.2-.4 2.8-.2 3.4.8-.4 1.2-2 1.6-3.6 1.4-.8-.6-.6-1.6.2-2.2z" fill="var(--hs-cream)" stroke="none"/>` +
    s('M34.6 27.6c-.6-1.8.4-3.6 2.2-3.6 1.6 0 2.4 1.6 1.8 3.2z', '--ic-ferret') +
    eye(39.8, 31.2, 1.05) +
    `<ellipse cx="44.8" cy="34.3" rx=".8" ry=".65" class="e"/>` +
    dl('M30.6 38.6v4.4M14.8 38.4v4.4M17 22.4c1.6-.8 3.4-1 5-.8'),

  // Horse standing: long head angled down, arched neck with mane, level back, rounded croup,
  // tail, four slim legs with the hind cannon below a backward-pointing hock, hooves.
  horse: ground(8, 40) +
    s('M30.6 29.6L27.8 42c-.2.8 0 1.6.6 2.4h-3.6l.2-1.4L26.6 29.4z', '--ic-horse-2') +
    s('M18.6 29.4c.4 2.2.8 4 1.8 5.6l1.6 8c.2.6.6 1 1.2 1.4h-3.6l-.2-1.2-1.8-6.8-1.8-1.6-1-5.6z', '--ic-horse-2') +
    s('M7.6 19.4c-3 2.6-4.6 8.4-4.6 13.6 0 2 .4 3.4 1.4 4.4.2-3 1-6 2.6-8.8.2-1 .6-2.6.8-4z', '--ic-horse-2') +
    s('M45.4 13.4c.8 1.4.4 3.2-1.4 3.4-1.4.2-3 0-4 .8l-3.4 6.4c-.4 2-1 3.6-1.8 5.4l.2 11.6c0 1 .8 1.8 1.6 2.4v1h-3.8L32 30.8c-.4-.4-.8-.6-1.2-.6-5 .6-10 .8-15-.4l-1.6 6.2.4 7c.4.4.8.8 1.4 1.4h-3.6l-.6-7.4-1.4-1.4C9 31.4 7.4 28 7.2 23.4 7 19.6 9.4 17 12.8 16.8c4.6-.4 10.2.6 14.4-.6 2.8-.8 4.8-4.8 7-8.4.6-1.2 1-2.6 1-4l2 2.2c2.8 1.6 5.8 4.6 8.2 7.4z', '--ic-horse') +
    s('M34.6 6.6c-2.2 3.4-4 7.6-6.6 9.8 1.4.4 2.8.2 3.8-.2 1-1.6 2.4-3.4 3.4-5.4-.6 1.4-.8 2.4-.6 3.4 1.2-1.8 2-4 2-6.4-.6-.4-1.4-.8-2-1.2z', '--ic-horse-2') +
    eye(39.2, 9.6, 1.05) +
    `<ellipse cx="43.8" cy="14.6" rx=".7" ry=".9" class="e"/>` +
    dl('M41.6 16.6c-1 .6-2 .8-3 .4M32.2 30.4c.6-2 1.8-3 3.6-3.4M16 29.8c-2-.2-3.8-1.4-4.8-3.4M33.4 43.4h3.4M12.2 43.4h3.4'),

  // Budgie on a perch: round head, short hooked beak with cere, yellow face, green body,
  // scalloped folded wing, long tapered tail behind the perch, toes gripping (two forward).
  bird: s('M27.2 34.4L13 45.8c-.8.6-1.8.2-1.6-.8l7.8-14.8z', '--ic-shell') +
    s('M33.4 8.8c2.4 1.4 3.6 4 3 6.8l-1.2 3.4c1.8 2.6 2.4 6 1.4 9.2-1 3.6-3.6 6-7.4 6.8-3.2.6-6.6-.4-8.8-3-2-2.8-1.6-6.8-.6-10.4.8-3.4 2-7 3.8-10.4 2.2-3.8 6.6-4.6 9.8-2.4z', '--ic-shell') +
    `<path d="M33.6 9.4c2 1.4 3 3.8 2.6 6.4l-1.2 3.4c-1 1.6-2.8 2.2-4.6 1.6-1.4-3.2-1.8-7.4-.6-11.2 1.2-.6 2.6-.6 3.8-.2z" fill="var(--ic-bird)" stroke="none"/>` +
    s('M27 16c3.6 1.6 4.4 8.4 1.6 14-1.6 3.4-4.6 6-8.4 7.6.8-6.4 1.6-13 3.2-18.6.8-2 2-3 3.6-3z', '--ic-shell-2') +
    s('M35.6 13.2c2.2-.6 3.8 1 3.6 3.4-.2 1.6-1.2 2.8-2.4 3 .4-1.2.2-2-.8-2.4l-.6-.2z', '--hs-cream') +
    `<ellipse cx="35.8" cy="12.6" rx="1.1" ry=".8" fill="var(--ic-ear)" stroke="none"/>` +
    `<ellipse cx="33.2" cy="18.6" rx="1" ry=".7" fill="var(--accent)" stroke="none"/>` +
    eye(32, 12.4, 1.05) +
    dl('M25.2 21.6c1.4.6 2.4.4 3.4-.4M24.4 25.6c1.4.6 2.6.4 3.6-.4M23.4 29.6c1.4.6 2.6.4 3.6-.4M31.6 20.8h.1M33.4 21.4h.1') +
    s('M3.2 38.8c10.8-.8 27-1 41.8.2.6.2.6 1.8 0 2-14.6-.8-30.6-.6-41.8.2-.6-.4-.6-2 0-2.4z', '--hs-dog-2') +
    dl('M10 40.6c-.8 1.4-1 2.8-.6 4.2') +
    l('M27.6 35.6l-1 4.2M30.4 35l.4 4.6', ' stroke="var(--sk-accent)" stroke-width="1.6"'),

  // Tortoise: high domed shell with vertebral and costal scutes, marginal rim, elephant-like
  // front leg, head on a short neck, beak-like mouth, stub tail.
  reptile: ground(4, 40) +
    s('M36.4 27.4c2.6-3.6 5-5.6 7.6-5.8 2-.2 3.2 1.6 2.4 3.4-.6 1.4-2 2-3.6 2.2-1.6.2-2.8 1-3.8 2.2L37.4 31z', '--hs-dog') +
    s('M31.4 33.6c.4 3.4 0 6.6.2 9.4 1.6 1.2 5.6 1.2 7 .2-.2-3.4-.6-6.4-1.4-9.8zM7 33.6c-.2 3.2-.6 6.2-.4 9.2 1.6 1.2 5.6 1.2 6.6.2 0-3-.4-6-.8-9z', '--hs-dog') +
    l('M4.4 33.6L1.4 35.4l3.6.4') +
    s('M3.8 32.4C3.8 19.8 11.8 10 22 10s18.2 9.8 18.2 22.4z', '--ic-shell') +
    s('M2.8 31.2c11.8 2.6 26.4 2.6 38.4 0l.4 3.4c-12.2 3-26.6 3-39.2 0z', '--ic-shell-2') +
    l('M8.6 31.6c.4-8.4 6.2-15 13.4-15s13 6.6 13.4 15', ' class="d"') +
    dl('M16.6 17.8l1.6 5.4h7.6l1.6-5.4M18.2 23.2l-1 9.4M25.8 23.2l1 9.4M11.4 22.6l5.6 2.6M32.6 22.6l-5.6 2.6M8 32.6v2.4M15 33.4v2.6M22 33.8v2.6M29 33.4v2.6M36 32.6v2.4') +
    eye(43.4, 23.4, .95) +
    dl('M46.2 25.2c-.8.6-1.8.8-2.8.6M32.6 43.4v-1.4M35 43.6v-1.4M8.4 43.4V42M10.8 43.6v-1.4'),

  // Goldfish: deep oval body, forked tail, dorsal and anal fins, gill arc, big eye, bubbles.
  fish: s('M14.6 22.2C11.4 18.2 7.6 14.8 3.4 13.6c.6 4 1.8 7.6 4.2 10.4-2.4 2.8-3.6 6.4-4.2 10.4 4.2-1.2 8-4.6 11.2-8.6z', '--ic-bird') +
    s('M21 15.4c1.4-4.4 5.6-6.8 10.4-6.6-1.4 2-1.8 4.2-1 6.4zM24.2 33c.4 3.4 2.8 5.4 6.2 5.8-.8-1.8-.8-3.8 0-6z', '--ic-bird') +
    s('M40.2 24c0 5.6-6 9.6-13.8 9.6-6 0-10.6-3.2-12.8-7.2l-.4-2.4.4-2.4c2.2-4.2 6.8-7.2 12.8-7.2 7.8 0 13.8 4 13.8 9.6z', '--ic-bird-2') +
    l('M32.4 17.4c-1.8 3.2-1.8 10 0 13.2', ' class="d"') +
    dl('M29 26.6c1.6 2 1.4 4.2-.8 5.4M7.8 17.8c2 1.6 3.6 3.6 4.8 5.6M7.8 30.2c2-1.6 3.6-3.6 4.8-5.6') +
    eye(35.6, 21.4, 1.5) +
    dl('M40 25.6c-.8.6-1.8.6-2.6.2') +
    `<circle cx="44" cy="14" r="1.6" stroke-width="1.2"/><circle cx="45.4" cy="8.6" r="1" stroke-width="1.1"/>`,

  // Hen: plump breast, upright tail feathers, small head with single comb and wattle, short beak, legs.
  hen: ground(14, 32) +
    s('M37.4 10.6c.6 2 .2 4-1 5.4-.8 2 0 4 1 6.4 1.2 5-2 11.2-8.4 14-5 2-12 1.6-16.4-1.4C8.4 32 5.6 26.6 5 21c-.4-5-.4-10 1.4-13.4 2.2 2 4.6 4.8 7 8 4.2 2.6 10.6 3 15.2 1 .8-3 1-7 3.8-8.4 2.2-1 4.4.2 5 2.4z', '--hs-dog') +
    s('M15 22.6c5-2.2 13-1.2 16 3.2-2 4.8-9 6.4-14.4 4.2-2-2-2.6-5-1.6-7.4z', '--hs-dog-2') +
    s('M30.2 8.6c-.6-2.6.8-4 2.2-3 .2-2.2 2.4-2.4 3-.4 1.2-1.2 3-.2 2 2.4-1 1-5.4 1.4-7.2 1z', '--sk-accent') +
    `<path d="M36.4 15.4c1.6.4 2.2 2.4 1 3.6-1 .6-2-.6-1.6-2.2z" fill="var(--sk-accent)" stroke="none"/>` +
    s('M37.4 11.2l3.4 1.4-3.4 1.4z', '--ic-bird-2') +
    eye(34.4, 11.4, 1) +
    dl('M8 12c1.8 2.4 3.4 5.2 4.2 8M6.4 18.4c1.6 1.8 3 4 3.8 6.4M18.6 26.6c2.6-.6 5.4-.4 8 .6') +
    l('M21.6 37.6l-.4 6.2M26 37.2l.6 6.4', ' stroke="var(--ic-bird-2)" stroke-width="1.8"') +
    l('M19 44.4l2.2-.8 2.6.8M24.6 44.4l2-.8 2.6.6', ' stroke-width="1.4"'),

  // Paw print: four toe pads and the heart-shaped main pad.
  paw: s('M24 27.6c4.6 0 8.6 3.6 8.6 7.6 0 3-2.4 4.8-5 4.4-1.4-.2-2.4-.8-3.6-.8s-2.2.6-3.6.8c-2.6.4-5-1.4-5-4.4 0-4 4-7.6 8.6-7.6z', '--hs-dog') +
    s('M13.4 19.4c2.2-.4 4 1.8 4.2 4.4.2 2.4-1.2 4-3 4-2 0-3.6-2-3.8-4.4-.2-2 .8-3.8 2.6-4z', '--hs-dog') +
    s('M20.4 11.8c2.2 0 3.6 2.4 3.4 5.2-.2 2.4-1.6 4-3.4 3.8-2-.2-3.2-2.4-3.2-4.8.2-2.4 1.4-4.2 3.2-4.2z', '--hs-dog') +
    s('M28.2 11.8c1.8 0 3.2 1.8 3.2 4.2 0 2.4-1.2 4.6-3.2 4.8-1.8.2-3.2-1.4-3.4-3.8-.2-2.8 1.2-5.2 3.4-5.2z', '--hs-dog') +
    s('M35 19.4c1.8.2 2.8 2 2.6 4-.2 2.4-1.8 4.4-3.8 4.4-1.8 0-3.2-1.6-3-4 .2-2.6 2-4.8 4.2-4.4z', '--hs-dog'),
};
ICONS.general = ICONS.paw;

/** Stroke width (48-grid units) that gives about 1.2px of ink at chip size and 3–5px at hero size. */
export const strokeFor = (px: number) => +Math.min(2.8, ((1.15 + px * 0.012) * 48) / px).toFixed(2);

/**
 * One animal placed inside a larger scene: `x, y` is the top-left of its 48-grid box, `k` the scale
 * (negative mirrors it to face left). `sw` is the scene's stroke width, so the ink stays one weight.
 */
export const place = (kind: string, x: number, y: number, k: number, sw: number) => {
  const w = +(sw / Math.abs(k)).toFixed(3);
  return `<g class="sk-in" transform="translate(${x} ${y}) scale(${k} ${Math.abs(k)})" stroke-width="${w}" style="--sw:${w}">${ICONS[kind]}</g>`;
};
