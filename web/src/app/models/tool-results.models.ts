/** Ranked metric row for tool-result bar charts. */
export interface RankRow {
  label: string;
  sublabel?: string;
  revenue: number;
  secondary?: string;
  /** Tailwind width utility from TailwindWidthService. */
  widthClass: string;
}

/** KPI-style card built from allowlisted tool JSON. */
export interface ToolSummaryCard {
  title: string;
  value: string;
  hint?: string;
}
