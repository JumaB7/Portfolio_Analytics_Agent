import { Injectable } from '@angular/core';

/** Presentation formatting for structured tool-result cards. */
@Injectable({ providedIn: 'root' })
export class ToolResultsFormatService {
  rangeHint(result: Record<string, unknown>): string | undefined {
    const start = result['start_date'];
    const end = result['end_date'];
    if (!start || !end) {
      return undefined;
    }
    return `${start} → ${end}`;
  }

  formatZar(value: unknown): string {
    const amount = Number(value ?? 0);
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR',
      maximumFractionDigits: 2,
    }).format(amount);
  }
}
