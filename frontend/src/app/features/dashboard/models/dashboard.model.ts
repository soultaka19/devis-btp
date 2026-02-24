export interface DashboardStats {
  total_quotes: number;
  quotes_this_month: number;
  avg_quote_value: number;
  status_breakdown: Record<string, number>;
}
