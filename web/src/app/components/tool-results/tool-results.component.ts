import { CurrencyPipe, NgClass } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  input,
} from '@angular/core';

import { ToolName } from '../../constants/tool-names.constants';
import { ToolActivity, ToolStatus } from '../../models/chat.models';
import { RankRow, ToolSummaryCard } from '../../models/tool-results.models';
import { TailwindWidthService } from '../../services/tailwind-width.service';
import { ToolResultsFormatService } from '../../services/tool-results-format.service';

@Component({
  selector: 'app-tool-results',
  standalone: true,
  imports: [CurrencyPipe, NgClass],
  templateUrl: './tool-results.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToolResultsComponent {
  private readonly widths = inject(TailwindWidthService);
  private readonly format = inject(ToolResultsFormatService);

  readonly activity = input.required<ToolActivity[]>();

  readonly okActivities = computed(() =>
    this.activity().filter((item) => item.status === ToolStatus.Ok && item.result),
  );

  readonly summaryCards = computed(() => {
    const cards: ToolSummaryCard[] = [];
    for (const item of this.okActivities()) {
      const result = item.result ?? {};
      if (item.tool_name === ToolName.GetSalesSummary) {
        cards.push(
          {
            title: 'Revenue',
            value: this.format.formatZar(result['total_revenue']),
            hint: this.format.rangeHint(result),
          },
          {
            title: 'Orders',
            value: String(result['order_count'] ?? 0),
          },
          {
            title: 'Units sold',
            value: String(result['units_sold'] ?? 0),
          },
        );
      }
      if (item.tool_name === ToolName.CompareSalesPeriods) {
        const current = (result['current_period'] as Record<string, unknown>) ?? {};
        const previous = (result['previous_period'] as Record<string, unknown>) ?? {};
        const pct = result['revenue_change_pct'];
        cards.push(
          {
            title: 'Current revenue',
            value: this.format.formatZar(current['total_revenue']),
            hint: this.format.rangeHint(current),
          },
          {
            title: 'Previous revenue',
            value: this.format.formatZar(previous['total_revenue']),
            hint: this.format.rangeHint(previous),
          },
          {
            title: 'Change',
            value: `${this.format.formatZar(result['revenue_change'])}${
              pct === null || pct === undefined ? '' : ` (${pct}%)`
            }`,
          },
        );
      }
    }
    return cards;
  });

  readonly rankRows = computed((): RankRow[] => {
    const rows: Omit<RankRow, 'widthClass'>[] = [];
    for (const item of this.okActivities()) {
      const result = item.result ?? {};
      if (item.tool_name === ToolName.GetRevenueByCategory) {
        const categories = (result['categories'] as Array<Record<string, unknown>>) ?? [];
        for (const category of categories) {
          rows.push({
            label: String(category['category'] ?? ''),
            revenue: Number(category['revenue'] ?? 0),
            secondary: `${category['order_count'] ?? 0} orders`,
          });
        }
      }
      if (item.tool_name === ToolName.GetProductPerformance) {
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

    return this.widths.withRelativeWidths(rows);
  });
}
