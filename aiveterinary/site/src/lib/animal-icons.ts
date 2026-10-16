/** Shared SVG shape strings for the animal faces (48×48 grid, stroke 2.2). Fills use theme tokens. */
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
horse:`
<path d="M14 14 L11 4 L19 11z" fill="var(--ic-horse-2)"/><path d="M34 14 L37 4 L29 11z" fill="var(--ic-horse-2)"/>
<path d="M13 18c0-6 5-9 11-9s11 3 11 9v10c0 9-5 15-11 15S13 37 13 28V18z" fill="var(--ic-horse)"/>
<path d="M20 10c-2 1-3 3-3 6M24 9c-1 2-1.5 4-1 7M28 10c1 2 1 4 .5 6" stroke-width="1.8"/>
<ellipse cx="24" cy="35" rx="7.5" ry="6" fill="var(--hs-cream)" stroke="none"/>
<ellipse cx="18.0" cy="22.0" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/><ellipse cx="30.0" cy="22.0" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/>
<circle cx="18.6" cy="20.7" r=".85" fill="var(--surface)" stroke="none"/><circle cx="30.6" cy="20.7" r=".85" fill="var(--surface)" stroke="none"/>
<ellipse cx="20.5" cy="36" rx="1" ry="1.4" fill="var(--art-ink)" stroke="none" opacity=".75"/><ellipse cx="27.5" cy="36" rx="1" ry="1.4" fill="var(--art-ink)" stroke="none" opacity=".75"/>
<path d="M21 40.5c2 1 4 1 6 0" stroke-width="1.6"/>`,
bird:`
<path d="M10 42h28" stroke-width="1.6"/>
<ellipse cx="24" cy="27" rx="13.5" ry="12.5" fill="var(--ic-bird)"/>
<path d="M22 10c0-3 1-5 3-6M24 10c1-3 3-4 5-4" stroke-width="1.6"/>
<ellipse cx="17" cy="30" rx="4" ry="6.5" fill="var(--ic-bird-2)" transform="rotate(25 17 30)" stroke-width="1.8"/>
<ellipse cx="29.0" cy="24.0" rx="2.4" ry="2.9" fill="var(--art-ink)" stroke="none"/><circle cx="29.6" cy="22.7" r=".85" fill="var(--surface)" stroke="none"/>
<path d="M37 26.5 L43 28 L37 30z" fill="var(--coral)"/>
<ellipse cx="32" cy="30" rx="2.2" ry="1.3" fill="var(--ic-blush)" stroke="none"/>
<path d="M20 39.5v2.5M28 39.5v2.5M18 42l2-2 2 2M26 42l2-2 2 2" stroke-width="1.6"/>`,
paw:`
<ellipse cx="24" cy="31" rx="8" ry="6.5" fill="var(--hs-dog)"/>
<ellipse cx="13" cy="23" rx="3.3" ry="4" fill="var(--hs-dog)" transform="rotate(-20 13 23)"/>
<ellipse cx="20" cy="16.5" rx="3.3" ry="4" fill="var(--hs-dog)"/>
<ellipse cx="28" cy="16.5" rx="3.3" ry="4" fill="var(--hs-dog)"/>
<ellipse cx="35" cy="23" rx="3.3" ry="4" fill="var(--hs-dog)" transform="rotate(20 35 23)"/>`

};
ICONS.general = ICONS.paw; ICONS.ferret = ICONS.paw;
