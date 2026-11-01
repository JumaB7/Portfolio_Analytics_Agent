/** Allowlisted tool names the chat UI knows how to render. */
export const ToolName = {
  GetSalesSummary: 'get_sales_summary',
  CompareSalesPeriods: 'compare_sales_periods',
  GetRevenueByCategory: 'get_revenue_by_category',
  GetProductPerformance: 'get_product_performance',
} as const;

export type ToolName = (typeof ToolName)[keyof typeof ToolName];
