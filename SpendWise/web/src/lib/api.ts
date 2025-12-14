/**
 * SpendWise API Client
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Transaction {
  id: number;
  date: string;
  description: string;
  amount: number;
  currency: string;
  category_id: number | null;
  category_name: string | null;
  merchant: string | null;
  source: string | null;
}

export interface Budget {
  id: number;
  category_id: number;
  category_name: string;
  color: string;
  budget: number;
  spent: number;
  remaining: number;
  usage_percent: number;
  status: 'ok' | 'warning' | 'over';
}

export interface Category {
  id: number;
  name: string;
  description: string | null;
  icon: string | null;
  color: string | null;
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return response.json();
}

// Transactions
export async function getTransactions(limit = 50, offset = 0) {
  return fetchApi<{ transactions: Transaction[]; count: number }>(
    `/api/transactions?limit=${limit}&offset=${offset}`
  );
}

export async function getTransactionSummary(period: 'week' | 'month' | 'year' = 'week') {
  return fetchApi<{
    period: string;
    income: number;
    expenses: number;
    net: number;
    by_category: { name: string; total: number }[];
  }>(`/api/transactions/summary?period=${period}`);
}

export async function getCategories() {
  return fetchApi<{ categories: Category[] }>('/api/transactions/categories');
}

// Budgets
export async function getBudgets() {
  return fetchApi<{ budgets: Budget[]; week_start: string; week_end: string }>(
    '/api/budgets'
  );
}

export async function getBudgetStatus() {
  return fetchApi<{
    total_budget: number;
    total_spent: number;
    total_remaining: number;
    overall_usage_percent: number;
    counts: { ok: number; warning: number; over: number };
  }>('/api/budgets/status');
}

// Chat
export interface AgentUsed {
  id: string;
  name: string;
  icon: string;
  color: string;
}

export interface ChatMetadata {
  agents_used: AgentUsed[];
  tools: { tool: string; count: number }[];
  execution_time: number;
}

export interface ChatResponse {
  message: string;
  metadata: ChatMetadata | null;
}

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  return fetchApi<ChatResponse>('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message }),
  });
}

export async function getAgents() {
  return fetchApi<{
    mcp_ready: boolean;
    agents: AgentUsed[];
  }>('/api/chat/agents');
}

// Travel
export async function planTrip(
  destination: string,
  startDate: string,
  endDate: string,
  travelers = 1,
  style = 'medium'
) {
  return fetchApi<{ destination: string; response: string; success: boolean }>(
    '/api/travel/plan',
    {
      method: 'POST',
      body: JSON.stringify({
        destination,
        start_date: startDate,
        end_date: endDate,
        travelers,
        style,
      }),
    }
  );
}

export async function getPopularCities() {
  return fetchApi<{
    cities: { name: string; code: string; country: string }[];
  }>('/api/travel/cities');
}

// Stocks
export interface StockPosition {
  ticker: string;
  quantity: number;
  invested: number;
}

export interface StockQuote {
  symbol: string;
  data: string;
  success: boolean;
  error?: string;
}

export async function getStockBalance() {
  return fetchApi<{ balance: number; currency: string }>('/api/stocks/balance');
}

export async function getStockPortfolio() {
  return fetchApi<{ portfolio: StockPosition[]; total_positions: number }>(
    '/api/stocks/portfolio'
  );
}

export async function buyStock(ticker: string, quantity: number, price: number) {
  return fetchApi<{
    ticker: string;
    added: number;
    price: number;
    total_cost: number;
    new_quantity: number;
    total_invested: number;
  }>('/api/stocks/buy', {
    method: 'POST',
    body: JSON.stringify({ ticker, quantity, price }),
  });
}

export async function sellStock(ticker: string, quantity: number, price: number) {
  return fetchApi<{
    ticker: string;
    removed: number;
    price: number;
    total_sale: number;
    new_quantity: number;
    total_invested: number;
  }>('/api/stocks/sell', {
    method: 'POST',
    body: JSON.stringify({ ticker, quantity, price }),
  });
}

export async function analyzeStocks(symbols: string[]) {
  return fetchApi<{
    symbols: string[];
    analysis: string;
    success: boolean;
  }>('/api/stocks/analyze', {
    method: 'POST',
    body: JSON.stringify({ symbols }),
  });
}

export async function getStockQuote(symbol: string) {
  return fetchApi<StockQuote>(`/api/stocks/quote/${symbol}`);
}

export async function getStockRecommendations() {
  return fetchApi<{
    stocks: { symbol: string; name: string }[];
    analysis?: string;
    source: string;
  }>('/api/stocks/recommendations');
}

