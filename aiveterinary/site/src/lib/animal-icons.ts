/**
 * Face icons, now used only by the share images (src/lib/og.ts): satori cannot resolve the CSS classes
 * the site's sketch drawings (src/components/animal-art.ts) rely on. Also the source of IconKind.
 *
 * Shared SVG shape strings for the animal faces (48×48 grid, stroke 2.2). Fills use theme tokens.
 * Drawing rules for every face: dark ink outline, two tones per animal, eyes 2.4×2.9 with a highlight,
 * soft blush cheeks, small nose and mouth. Fills are drawn first and the outline on top, so coat
 * patches (guinea pig, ferret mask, horse blaze) never cross the edge. Front faces, except the
 * tortoise and fish, which only read in profile.
 */
export const ICONS: Record<string, string> = {
dog:`
<ellipse cx="10" cy="26" rx="5" ry="9.5" fill="var(--hs-dog-2)" transform="rotate(12 10 26)"/>
<ellipse cx="38" cy="26" rx="5" ry="9.5" fill="var(--hs-dog-2)" transform="rotate(-12 38 26)"/>
<circle cx="24" cy="27" r="15" fill="var(--hs-dog)"/>
<ellipse cx="24" cy="32" rx="7" ry="5.5" fill="var(--hs-cream)" stroke="none"/>
<ellipse cx="18.5" cy="25.5" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/><ellipse cx="29.5" cy="25.5" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/>
<circle cx="19.1" cy="24.2" r=".85" fill="var(--surface)" stroke="none"/><circle cx="30.1" cy="24.2" r=".85" fill="var(--surface)" stroke="none"/>
<path d="M22 30.5h4l-2 2.2z" fill="var(--art-ink)" stroke="var(--art-ink)" stroke-width="1"/>
<path d="M24 32.7v1.6M21.5 35c1 1 2 1.2 2.5 .4.5.8 1.5.6 2.5-.4" stroke-width="1.6"/>
<ellipse cx="13.5" cy="31" rx="2.2" ry="1.3" fill="var(--ic-blush)" stroke="none"/><ellipse cx="34.5" cy="31" rx="2.2" ry="1.3" fill="var(--ic-blush)" stroke="none"/>`,
cat:`
<path d="M11 20 L9 7 L20 14z" fill="var(--ic-ear)"/><path d="M37 20 L39 7 L28 14z" fill="var(--ic-ear)"/>
<ellipse cx="24" cy="27" rx="15" ry="13.5" fill="var(--hs-cat)"/>
<ellipse cx="18.0" cy="26.0" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/><ellipse cx="30.0" cy="26.0" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/>
<circle cx="18.6" cy="24.7" r=".85" fill="var(--surface)" stroke="none"/><circle cx="30.6" cy="24.7" r=".85" fill="var(--surface)" stroke="none"/>
<path d="M22.8 30.5h2.4l-1.2 1.4z" fill="var(--art-ink)" stroke="var(--art-ink)" stroke-width="1"/>
<path d="M21.5 33.2c1 1 2 1 2.5 .2.5.8 1.5.8 2.5-.2" stroke-width="1.6"/>
<path d="M4 27h7M4.5 31l6.5-1.2M44 27h-7M43.5 31l-6.5-1.2" stroke-width="1.6"/>
<ellipse cx="13" cy="31" rx="2.2" ry="1.3" fill="var(--ic-blush)" stroke="none"/><ellipse cx="35" cy="31" rx="2.2" ry="1.3" fill="var(--ic-blush)" stroke="none"/>`,
rabbit:`
<ellipse cx="17.5" cy="13" rx="4.5" ry="11" fill="var(--ic-rabbit)" transform="rotate(-8 17.5 13)"/><ellipse cx="17.5" cy="13" rx="2" ry="7.5" fill="var(--ic-ear)" stroke="none" transform="rotate(-8 17.5 13)"/>
<ellipse cx="30.5" cy="13" rx="4.5" ry="11" fill="var(--ic-rabbit)" transform="rotate(8 30.5 13)"/><ellipse cx="30.5" cy="13" rx="2" ry="7.5" fill="var(--ic-ear)" stroke="none" transform="rotate(8 30.5 13)"/>
<ellipse cx="24" cy="31" rx="13.5" ry="12" fill="var(--ic-rabbit)"/>
<ellipse cx="18.5" cy="30.0" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/><ellipse cx="29.5" cy="30.0" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/>
<circle cx="19.1" cy="28.7" r=".85" fill="var(--surface)" stroke="none"/><circle cx="30.1" cy="28.7" r=".85" fill="var(--surface)" stroke="none"/>
<path d="M22.8 34h2.4l-1.2 1.4z" fill="var(--ic-blush)" stroke="var(--art-ink)" stroke-width="1"/>
<path d="M22 37.5c.8 1 1.5 1 2-.2.5 1.2 1.2 1.2 2 .2" stroke-width="1.6"/>
<rect x="22.3" y="38.2" width="1.7" height="2.6" rx=".5" fill="var(--surface)" stroke-width="1.1"/><rect x="24" y="38.2" width="1.7" height="2.6" rx=".5" fill="var(--surface)" stroke-width="1.1"/>
<ellipse cx="13.5" cy="35" rx="2.2" ry="1.3" fill="var(--ic-blush)" stroke="none"/><ellipse cx="34.5" cy="35" rx="2.2" ry="1.3" fill="var(--ic-blush)" stroke="none"/>`,
'guinea-pig':`
<path d="M5.5 31C5.5 21 13.5 14 24 14s18.5 7 18.5 17c0 7.5-6.5 11.5-18.5 11.5S5.5 38.5 5.5 31z" fill="var(--hs-cream)"/>
<path d="M6.2 26.5C7.8 19.5 13 15 20.6 14.2c-.9 4.4-.6 10.8.9 16.4-5.6 2.6-11.6 1.2-15.3-4.1z" fill="var(--hs-dog-2)" stroke="none"/>
<path d="M28.6 14.3c6.7 1 11.9 5.3 13.4 11.6-3.4 1.6-7 1-8.6-1.3-1.4-2.6-2.3-6.6-4.8-10.3z" fill="var(--ic-horse-2)" stroke="none"/>
<path d="M5.5 31C5.5 21 13.5 14 24 14s18.5 7 18.5 17c0 7.5-6.5 11.5-18.5 11.5S5.5 38.5 5.5 31z"/>
<path d="M15.6 16.2c-3.2-1.9-7.4-.8-8.4 2.9 2.6 2 6.6 1.6 8.4-2.9z" fill="var(--hs-dog-2)"/><path d="M32.4 16.2c3.2-1.9 7.4-.8 8.4 2.9-2.6 2-6.6 1.6-8.4-2.9z" fill="var(--hs-dog-2)"/>
<ellipse cx="18" cy="27.5" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/><ellipse cx="30" cy="27.5" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/>
<circle cx="18.6" cy="26.2" r=".85" fill="var(--surface)" stroke="none"/><circle cx="30.6" cy="26.2" r=".85" fill="var(--surface)" stroke="none"/>
<path d="M22.8 31.6h2.4l-1.2 1.4z" fill="var(--art-ink)" stroke="var(--art-ink)" stroke-width="1"/>
<path d="M24 33v1.2M21.6 34.6c1 1 2 1 2.4.2.4.8 1.4.8 2.4-.2" stroke-width="1.6"/>
<ellipse cx="12.5" cy="33" rx="2.2" ry="1.3" fill="var(--ic-blush)" stroke="none"/><ellipse cx="35.5" cy="33" rx="2.2" ry="1.3" fill="var(--ic-blush)" stroke="none"/>
<ellipse cx="16" cy="42.3" rx="2.8" ry="1.6" fill="var(--ic-ear)" stroke-width="1.4"/><ellipse cx="32" cy="42.3" rx="2.8" ry="1.6" fill="var(--ic-ear)" stroke-width="1.4"/>`,
ferret:`
<circle cx="10.2" cy="21.4" r="3.6" fill="var(--ic-ferret)"/><circle cx="9.4" cy="21.4" r="1.6" fill="var(--ic-ear)" stroke="none"/>
<circle cx="37.8" cy="21.4" r="3.6" fill="var(--ic-ferret)"/><circle cx="38.6" cy="21.4" r="1.6" fill="var(--ic-ear)" stroke="none"/>
<path d="M24 10.5c8.4 0 13.5 6.2 13.5 14 0 6.8-4.2 11.4-8.6 14.6-1.8 1.4-3.2 2.6-4.9 2.6s-3.1-1.2-4.9-2.6c-4.4-3.2-8.6-7.8-8.6-14.6 0-7.8 5.1-14 13.5-14z" fill="var(--ic-ferret)"/>
<path d="M24 26.6c-4.6 0-8.6 3.4-8.6 7.6 0 1.6.5 2.6 1.6 3.6 1.9 1.6 4.2 3.3 7 3.3s5.1-1.7 7-3.3c1.1-1 1.6-2 1.6-3.6 0-4.2-4-7.6-8.6-7.6z" fill="var(--hs-cream)" stroke="none"/>
<path d="M10.9 25.2c2.5-3.6 8.6-4.3 11-1.4.8.9 1.4 1 2.1 1s1.3-.1 2.1-1c2.4-2.9 8.5-2.2 11 1.4-.8 3.7-4.4 5.9-8.4 5.2-1.9-.3-3.3-1.3-4.7-1.3s-2.8 1-4.7 1.3c-4 .7-7.6-1.5-8.4-5.2z" fill="var(--ic-ferret-2)" stroke="none"/>
<path d="M24 10.5c8.4 0 13.5 6.2 13.5 14 0 6.8-4.2 11.4-8.6 14.6-1.8 1.4-3.2 2.6-4.9 2.6s-3.1-1.2-4.9-2.6c-4.4-3.2-8.6-7.8-8.6-14.6 0-7.8 5.1-14 13.5-14z"/>
<ellipse cx="18" cy="26.6" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/><ellipse cx="30" cy="26.6" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/>
<circle cx="18.6" cy="25.3" r=".85" fill="var(--surface)" stroke="none"/><circle cx="30.6" cy="25.3" r=".85" fill="var(--surface)" stroke="none"/>
<path d="M22.1 34.2c0-1 .9-1.4 1.9-1.4s1.9.4 1.9 1.4c0 .9-1 1.9-1.9 1.9s-1.9-1-1.9-1.9z" fill="var(--ic-blush)" stroke="var(--art-ink)" stroke-width="1"/>
<path d="M24 36.1v1.1M22.1 37.8c.8.8 1.5.8 1.9.1.4.7 1.1.7 1.9-.1" stroke-width="1.6"/>
<ellipse cx="14.4" cy="32.6" rx="2" ry="1.3" fill="var(--ic-blush)" stroke="none"/><ellipse cx="33.6" cy="32.6" rx="2" ry="1.3" fill="var(--ic-blush)" stroke="none"/>`,
horse:`
<path d="M15.4 15.2 12.4 4.8l8.4 5.8z" fill="var(--ic-horse)"/><path d="M15.7 12 14.4 7.6l3.8 2.7z" fill="var(--ic-ear)" stroke="none"/>
<path d="M32.6 15.2 35.6 4.8l-8.4 5.8z" fill="var(--ic-horse)"/><path d="M32.3 12l1.3-4.4-3.8 2.7z" fill="var(--ic-ear)" stroke="none"/>
<path d="M24 8.5c7.8 0 12.8 5.2 12.8 12.4 0 3-.8 5.6-1.6 8.2-.9 3-.9 5.4-.9 6.9 0 5-4.6 8.4-10.3 8.4s-10.3-3.4-10.3-8.4c0-1.5 0-3.9-.9-6.9-.8-2.6-1.6-5.2-1.6-8.2 0-7.2 5-12.4 12.8-12.4z" fill="var(--ic-horse)"/>
<path d="M24 17c-1.1 4-1.5 9.5-1.3 14h2.6c.2-4.5-.2-10-1.3-14z" fill="var(--hs-cream)" stroke="none"/>
<ellipse cx="24" cy="36.8" rx="8.8" ry="6.4" fill="var(--hs-cream)" stroke="none"/>
<path d="M24 8.5c7.8 0 12.8 5.2 12.8 12.4 0 3-.8 5.6-1.6 8.2-.9 3-.9 5.4-.9 6.9 0 5-4.6 8.4-10.3 8.4s-10.3-3.4-10.3-8.4c0-1.5 0-3.9-.9-6.9-.8-2.6-1.6-5.2-1.6-8.2 0-7.2 5-12.4 12.8-12.4z"/>
<path d="M18.6 11c1 3.2 2.6 5.4 4.2 6.6.4-1.4.8-2.2 1.2-2.6.4.4.8 1.2 1.2 2.6 1.6-1.2 3.2-3.4 4.2-6.6-1.5-1.5-3.3-2.3-5.4-2.3s-3.9.8-5.4 2.3z" fill="var(--ic-horse-2)" stroke-width="1.6"/>
<ellipse cx="18.2" cy="24.5" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/><ellipse cx="29.8" cy="24.5" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/>
<circle cx="18.8" cy="23.2" r=".85" fill="var(--surface)" stroke="none"/><circle cx="30.4" cy="23.2" r=".85" fill="var(--surface)" stroke="none"/>
<ellipse cx="20.8" cy="36.4" rx="1.1" ry="1.5" fill="var(--art-ink)" stroke="none" opacity=".75"/><ellipse cx="27.2" cy="36.4" rx="1.1" ry="1.5" fill="var(--art-ink)" stroke="none" opacity=".75"/>
<path d="M21.8 40.2c1.4.9 3 .9 4.4 0" stroke-width="1.6"/>
<ellipse cx="16.2" cy="29.8" rx="2" ry="1.3" fill="var(--ic-blush)" stroke="none"/><ellipse cx="31.8" cy="29.8" rx="2" ry="1.3" fill="var(--ic-blush)" stroke="none"/>`,
bird:`
<ellipse cx="10.5" cy="29.5" rx="4.2" ry="7" fill="var(--ic-bird-2)" transform="rotate(25 10.5 29.5)"/><ellipse cx="37.5" cy="29.5" rx="4.2" ry="7" fill="var(--ic-bird-2)" transform="rotate(-25 37.5 29.5)"/>
<path d="M22.6 13.2c-1.4-3.4-.8-6.6 1.8-8.8.8 2.6.8 5-.2 7.4M25.6 13c.2-3 1.6-5.2 4.4-6.4 0 2.8-1.2 5-3.4 6.8" fill="var(--ic-bird)" stroke-width="1.8"/>
<circle cx="24" cy="27" r="14.5" fill="var(--ic-bird)"/>
<ellipse cx="18.5" cy="25.5" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/><ellipse cx="29.5" cy="25.5" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/>
<circle cx="19.1" cy="24.2" r=".85" fill="var(--surface)" stroke="none"/><circle cx="30.1" cy="24.2" r=".85" fill="var(--surface)" stroke="none"/>
<path d="M21.4 29.2h5.2l-2.6 3.6z" fill="var(--coral)" stroke-width="1.2"/>
<ellipse cx="13.5" cy="31" rx="2.2" ry="1.3" fill="var(--ic-blush)" stroke="none"/><ellipse cx="34.5" cy="31" rx="2.2" ry="1.3" fill="var(--ic-blush)" stroke="none"/>
<path d="M20.5 41.4v2.8M27.5 41.4v2.8M18.6 45l1.9-1.4 1.9 1.4M25.6 45l1.9-1.4 1.9 1.4" stroke-width="1.6"/>`,
reptile:`
<path d="M9.5 31v6.5c0 1.1.9 2 2 2h3c1.1 0 2-.9 2-2V31z" fill="var(--hs-dog)"/><path d="M26.5 31v6.5c0 1.1.9 2 2 2h3c1.1 0 2-.9 2-2V31z" fill="var(--hs-dog)"/>
<path d="M31.4 31.4c.6-3.8 2.2-6.4 4.4-8l3.8 4.4c-1.6 1-2.8 2.2-3.4 3.6z" fill="var(--hs-dog)"/>
<ellipse cx="40.4" cy="23.8" rx="5.6" ry="5" fill="var(--hs-dog)"/>
<path d="M4.5 32c0-11 7.8-19 17-19s17 8 17 19z" fill="var(--ic-shell)"/>
<path d="M21.5 17.5l4.6 2.8v5.4l-4.6 2.8-4.6-2.8v-5.4z" fill="var(--ic-shell-2)" stroke-width="1.6"/>
<path d="M12.6 21.2l3 2.2v4.8l-3.4 2.4H7.4c.3-3.6 2.1-7 5.2-9.4zM30.4 21.2l-3 2.2v4.8l3.4 2.4h4.4c-.3-3.6-2.1-7-5.2-9.4z" fill="var(--ic-shell-2)" stroke-width="1.6"/>
<rect x="3.5" y="30.2" width="36" height="4.2" rx="2.1" fill="var(--ic-shell-2)"/>
<ellipse cx="41.3" cy="22.9" rx="2.1" ry="2.5" fill="var(--art-ink)" stroke="none"/><circle cx="41.8" cy="21.8" r=".75" fill="var(--surface)" stroke="none"/>
<path d="M42.9 26.1c.7.4 1.5.3 2.1-.3" stroke-width="1.6"/>
<ellipse cx="40.5" cy="26.9" rx="1.3" ry=".8" fill="var(--ic-blush)" stroke="none"/>`,
fish:`
<path d="M15.5 24c-3.6-4.2-7-6.8-10.4-7.6-1 2.6-1.2 5.2-.4 7.6-.8 2.4-.6 5 .4 7.6 3.4-.8 6.8-3.4 10.4-7.6z" fill="var(--ic-bird)"/>
<path d="M19.6 15c1.8-4.2 6.2-6.6 11.6-6-1.6 2-2.2 4-2 6.2z" fill="var(--ic-bird)"/>
<path d="M24.4 33.4c.2 3.2 2.2 5.2 5.6 5.8-.6-1.8-.6-3.6 0-5.2z" fill="var(--ic-bird)"/>
<ellipse cx="27" cy="24" rx="14" ry="10.4" fill="var(--ic-bird-2)"/>
<path d="M23.2 16.6c-1.6 2.2-2.4 4.6-2.4 7.4s.8 5.2 2.4 7.4" stroke-width="1.6"/>
<ellipse cx="33" cy="21.6" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/><circle cx="33.6" cy="20.3" r=".85" fill="var(--surface)" stroke="none"/>
<path d="M39.2 26.4c-.8.8-1.9 1-2.9.6" stroke-width="1.6"/>
<ellipse cx="30.4" cy="27.4" rx="2" ry="1.2" fill="var(--ic-blush)" stroke="none"/>
<circle cx="43.2" cy="14.6" r="1.9" fill="var(--hs-cream)" stroke-width="1.4"/><circle cx="44.6" cy="8.8" r="1.2" fill="var(--hs-cream)" stroke-width="1.2"/>`,
hen:`
<circle cx="19.6" cy="12.4" r="2.9" fill="var(--coral)"/><circle cx="24" cy="10" r="3.2" fill="var(--coral)"/><circle cx="28.4" cy="12.4" r="2.9" fill="var(--coral)"/>
<ellipse cx="10.5" cy="29.5" rx="4" ry="6.8" fill="var(--ic-rabbit)" transform="rotate(25 10.5 29.5)"/><ellipse cx="37.5" cy="29.5" rx="4" ry="6.8" fill="var(--ic-rabbit)" transform="rotate(-25 37.5 29.5)"/>
<circle cx="24" cy="27" r="14.5" fill="var(--hs-cream)"/>
<ellipse cx="18.5" cy="24.5" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/><ellipse cx="29.5" cy="24.5" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/>
<circle cx="19.1" cy="23.2" r=".85" fill="var(--surface)" stroke="none"/><circle cx="30.1" cy="23.2" r=".85" fill="var(--surface)" stroke="none"/>
<path d="M21.4 28.2h5.2l-2.6 3.6z" fill="var(--ic-bird-2)" stroke-width="1.2"/>
<ellipse cx="13.5" cy="30.2" rx="2.2" ry="1.3" fill="var(--ic-blush)" stroke="none"/><ellipse cx="34.5" cy="30.2" rx="2.2" ry="1.3" fill="var(--ic-blush)" stroke="none"/>
<path d="M20.5 41.4v2.8M27.5 41.4v2.8M18.6 45l1.9-1.4 1.9 1.4M25.6 45l1.9-1.4 1.9 1.4" stroke-width="1.6"/>`,
paw:`
<ellipse cx="24" cy="31" rx="8" ry="6.5" fill="var(--hs-dog)"/>
<ellipse cx="13" cy="23" rx="3.3" ry="4" fill="var(--hs-dog)" transform="rotate(-20 13 23)"/>
<ellipse cx="20" cy="16.5" rx="3.3" ry="4" fill="var(--hs-dog)"/>
<ellipse cx="28" cy="16.5" rx="3.3" ry="4" fill="var(--hs-dog)"/>
<ellipse cx="35" cy="23" rx="3.3" ry="4" fill="var(--hs-dog)" transform="rotate(20 35 23)"/>`

};
ICONS.general = ICONS.paw;

/** Everything AnimalIcon can draw: every article species, the lexicon group icons, and the paw. */
export type IconKind = 'dog' | 'cat' | 'rabbit' | 'guinea-pig' | 'ferret' | 'horse' | 'bird' | 'reptile' | 'fish' | 'hen' | 'general' | 'paw';
