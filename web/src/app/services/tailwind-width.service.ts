import { Injectable } from '@angular/core';
import {
  WIDTH_CLASS_FALLBACK,
  WIDTH_CLASS_THRESHOLDS,
} from '../constants/tailwind-width.constants';

/** Maps relative magnitudes to discrete Tailwind width utilities. */
@Injectable({ providedIn: 'root' })
export class TailwindWidthService {
  widthClassForRatio(ratio: number): string {
    for (const step of WIDTH_CLASS_THRESHOLDS) {
      if (ratio >= step.min) {
        return step.widthClass;
      }
    }
    return WIDTH_CLASS_FALLBACK;
  }

  /** Attach `widthClass` on each item relative to the max `value` in the list. */
  withRelativeWidths<T extends { revenue: number }>(
    rows: readonly T[],
  ): Array<T & { widthClass: string }> {
    const max = rows.length ? Math.max(...rows.map((row) => row.revenue), 1) : 1;
    return rows.map((row) => ({
      ...row,
      widthClass: this.widthClassForRatio(row.revenue / max),
    }));
  }
}
