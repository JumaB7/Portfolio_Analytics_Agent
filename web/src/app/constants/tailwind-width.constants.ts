/**
 * Min ratio → Tailwind width utility (highest matching threshold wins).
 * Keep ordered descending by threshold when applying.
 */
export const WIDTH_CLASS_THRESHOLDS: ReadonlyArray<{ min: number; widthClass: string }> = [
  { min: 0.9, widthClass: 'w-full' },
  { min: 0.75, widthClass: 'w-4/5' },
  { min: 0.6, widthClass: 'w-3/4' },
  { min: 0.45, widthClass: 'w-1/2' },
  { min: 0.3, widthClass: 'w-2/5' },
  { min: 0.15, widthClass: 'w-1/4' },
];

export const WIDTH_CLASS_FALLBACK = 'w-1/6';
