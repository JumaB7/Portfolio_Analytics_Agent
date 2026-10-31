import { CurrencyPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

import { ToolActivity } from '../../models/chat.models';

interface RankRow {
  label: string;
  sublabel?: string;
  revenue: number;
  secondary?: string;
}

@Component({
  selector: 'app-tool-results',
  standalone: true,
  imports: [CurrencyPipe],
  templateUrl: './tool-results.component.html',
  styleUrl: './tool-results.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolResultsComponent {
  readonly activity = input.required<ToolActivity[]>();

  readonly okActivities = computed(() =>
    this.activity().filter((item) => item.status === 'ok' && item.result)
  );

  readonly maxRevenue = computed(() => {
    const values = this.rankRows().map((row) => row.revenue);
    return values.length ? Math.max(...values) : 1;
  });

  readonly summaryCards = computed(() => {
    const cards: Array<{ title: string; value: string; hint?: string }> = [];
    for (const item of this.okActivities()) {
      const result = item.result ?? {};
      if (item.tool_name === 'get_sales_summary') {
        cards.push(
          {
            title: 'Revenue',
            value: this.formatZar(result['total_revenue']),
            hint: this.rangeHint(result),
          },
          {
            title: 'Orders',
            value: String(result['order_count'] ?? 0),
          },
          {
            title: 'Units sold',
            value: String(result['units_sold'] ?? 0),
          }
        );
      }
      if (item.tool_name === 'compare_sales_periods') {
        const current = (result['current_period'] as Record<string, unknown>) ?? {};
        const previous = (result['previous_period'] as Record<string, unknown>) ?? {};
        const pct = result['revenue_change_pct'];
        cards.push(
          {
            title: 'Current revenue',
            value: this.formatZar(current['total_revenue']),
            hint: this.rangeHint(current),
          },
          {
            title: 'Previous revenue',
            value: this.formatZar(previous['total_revenue']),
            hint: this.rangeHint(previous),
          },
          {
            title: 'Change',
            value: `${this.formatZar(result['revenue_change'])}${
              pct === null || pct === undefined ? '' : ` (${pct}%)`
            }`,
          }
        );
      }
    }
    return cards;
  });

  readonly rankRows = computed((): RankRow[] => {
    const rows: RankRow[] = [];
    for (const item of this.okActivities()) {
      const result = item.result ?? {};
      if (item.tool_name === 'get_revenue_by_category') {
        const categories = (result['categories'] as Array<Record<string, unknown>>) ?? [];
        for (const category of categories) {
          rows.push({
            label: String(category['category'] ?? ''),
            revenue: Number(category['revenue'] ?? 0),
            secondary: `${category['order_count'] ?? 0} orders`,
          });
        }
      }
      if (item.tool_name === 'get_product_performance') {
        const products = (result['products'] as Array<Record<string, unknown>>) ?? [];
        for (const product of products) {
          rows.push({
            label: String(product['product_name'] ?? ''),
            sublabel: String(product['sku'] ?? ''),
            revenue: Number(product['revenue'] ?? 0),
            secondary: `${product['units_sold'] ?? 0} units · ${product['category'] ?? ''}`,
          });
        }
      }
    }
    return rows;
  });

  barWidth(revenue: number): string {
    const max = this.maxRevenue() || 1;
    return `${Math.max(6, (revenue / max) * 100)}%`;
  }

  private rangeHint(result: Record<string, unknown>): string | undefined {
    const start = result['start_date'];
    const end = result['end_date'];
    if (!start || !end) {
      return undefined;
    }
    return `${start} → ${end}`;
  }

  private formatZar(value: unknown): string {
    const amount = Number(value ?? 0);
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR',
      maximumFractionDigits: 2,
    }).format(amount);
  }
}
