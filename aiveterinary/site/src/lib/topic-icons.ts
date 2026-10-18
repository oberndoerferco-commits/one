/** Small topic glyphs (32×32 grid) shared by the animal index and topic pages. */
export const TOPIC: Record<string, string> = {
  symptoms: '<rect x="13" y="4" width="6" height="18" rx="3" fill="var(--surface)"/><circle cx="16" cy="24" r="5" fill="var(--coral)"/><path d="M16 12v10"/>',
  conditions: '<path d="M16 27s-10-6-10-13a5.5 5.5 0 0 1 10-3 5.5 5.5 0 0 1 10 3c0 7-10 13-10 13z" fill="var(--coral-soft)"/><path d="M9 16h4l2-3 3 6 2-3h3"/>',
  medications: '<rect x="5" y="11" width="22" height="10" rx="5" fill="var(--surface)" transform="rotate(-35 16 16)"/><path d="M12 10l8 12" />',
  'first-aid': '<rect x="5" y="9" width="22" height="17" rx="4" fill="var(--surface)"/><path d="M12 9V6h8v3M16 13v9M11.5 17.5h9" stroke="var(--danger)"/>',
  travel: '<rect x="5" y="11" width="22" height="15" rx="4" fill="var(--ic-sun)"/><path d="M12 11V7h8v4M5 17h22"/>',
  care: '<path d="M5 16h22l-3 9H8z" fill="var(--hs-dog)"/><path d="M11 12c0-2 2-2 2-4M16 12c0-2 2-2 2-4M21 12c0-2 2-2 2-4" stroke-width="1.8"/>',
};
