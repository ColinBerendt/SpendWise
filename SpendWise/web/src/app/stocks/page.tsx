'use client';

import { useState, useEffect } from 'react';
import {
  getStockBalance,
  getStockPortfolio,
  analyzeStocks,
  buyStock,
  sellStock,
  StockPosition,
} from '@/lib/api';

interface StockAnalysis {
  symbol: string;
  name?: string;
  price?: number;
  change?: number;
  pe?: number;
  roe?: number;
  priceTarget?: number;
  upside?: number;
  recommendation?: 'BUY' | 'HOLD' | 'SELL';
  insight?: string; // AI-generated recommendation text
}

// Predefined pool of popular stocks for market analysis
// Note: In production, this could be replaced with a market movers API
const HOT_STOCKS_POOL = [
  { symbol: 'NVDA', name: 'NVIDIA Corporation' },
  { symbol: 'META', name: 'Meta Platforms' },
  { symbol: 'TSLA', name: 'Tesla Inc' },
  { symbol: 'AAPL', name: 'Apple Inc' },
  { symbol: 'MSFT', name: 'Microsoft Corporation' },
  { symbol: 'GOOGL', name: 'Alphabet Inc' },
  { symbol: 'AMZN', name: 'Amazon.com Inc' },
  { symbol: 'AMD', name: 'Advanced Micro Devices' },
  { symbol: 'NFLX', name: 'Netflix Inc' },
  { symbol: 'CRM', name: 'Salesforce Inc' },
];

// Shuffle array helper
function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

export default function StocksPage() {
  const [balance, setBalance] = useState<number | null>(null);
  const [portfolio, setPortfolio] = useState<StockPosition[]>([]);
  const [portfolioAnalysis, setPortfolioAnalysis] = useState<StockAnalysis[]>([]);
  const [hotAnalysis, setHotAnalysis] = useState<StockAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [analyzingPortfolio, setAnalyzingPortfolio] = useState(false);
  const [analyzingHot, setAnalyzingHot] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tradeModal, setTradeModal] = useState<{
    type: 'buy' | 'sell';
    symbol: string;
    currentPrice?: number;
    maxQty?: number;
  } | null>(null);
  const [tradeQty, setTradeQty] = useState(1);
  const [trading, setTrading] = useState(false);

  // Load initial data
  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    setError(null);

    try {
      const [balanceRes, portfolioRes] = await Promise.all([
        getStockBalance(),
        getStockPortfolio(),
      ]);

      setBalance(balanceRes.balance);
      setPortfolio(portfolioRes.portfolio || []);
    } catch (err) {
      setError('Failed to load data. Make sure MockBank and API are running.');
    } finally {
      setLoading(false);
    }
  }

  /**
   * Parses AI agent response text into structured stock analysis data.
   * Handles multiple formats: numbered lists, single stock format, etc.
   */
  function parseAnalysis(text: string): StockAnalysis[] {
    const results: StockAnalysis[] = [];
    
    // Split response into individual stock blocks by detecting numbered items
    // Pattern: "1. SYMBOL" or "1. SYMBOL (Name)" at start of line
    const stockBlocks: string[] = [];
    const lines = text.split('\n');
    let currentBlock = '';
    
    for (const line of lines) {
      // Detect new stock entry patterns: "1. AAPL", "1. AAPL (Apple)", "AAPL -", "AAPL (Apple)"
      const newStockPattern = /^\d+\.\s*([A-Z]{2,5})\s*[\(\-]|^([A-Z]{2,5})\s+[\(\-]/;
      
      if (newStockPattern.test(line.trim()) && currentBlock) {
        stockBlocks.push(currentBlock);
        currentBlock = line;
      } else {
        currentBlock += '\n' + line;
      }
    }
    if (currentBlock) stockBlocks.push(currentBlock);
    
    // Fallback: if no numbered blocks found, check for single stock format
    if (stockBlocks.length <= 1 && text.includes('Price:')) {
      const singleMatch = text.match(/([A-Z]{2,5})\s*[\(\-\s]/);
      if (singleMatch) {
        stockBlocks.length = 0;
        stockBlocks.push(text);
      }
    }
    
    // Extract structured data from each stock block
    for (const block of stockBlocks) {
      let symbol: string | undefined;
      let name: string | undefined;
      
      // Extract symbol and name using multiple regex patterns
      const pattern1 = block.match(/(\d+\.\s*)?([A-Z]{2,5})\s*\(([^)]+)\)/); // "1. AAPL (Apple Inc.)"
      const pattern2 = block.match(/([A-Z]{2,5})\s*-\s*([^\n]+)/); // "AAPL - Apple Inc."
      const pattern3 = block.match(/\d+\.\s*([A-Z]{2,5})\b/); // "1. AAPL"
      const pattern4 = block.match(/^([A-Z]{2,5})\b/); // "AAPL" at start
      
      if (pattern1) {
        symbol = pattern1[2];
        name = pattern1[3].replace(/\*\*/g, '').trim();
      } else if (pattern2) {
        symbol = pattern2[1];
        name = pattern2[2].replace(/\*\*/g, '').trim();
      } else if (pattern3) {
        symbol = pattern3[1];
      } else if (pattern4) {
        symbol = pattern4[1];
      }
      
      if (!symbol) continue;
      
      const analysis: StockAnalysis = { symbol, name };
      
      // Extract price and change percentage using multiple patterns
      const pricePatterns = [
        /Price:\s*\$?([\d,.]+)\s*\(([-+]?[\d.]+)%\)/i,
        /Price:\s*\$?([\d,.]+)/i,
        /Current:\s*\$?([\d,.]+)/i,
        /\$([\d,.]+)\s*\(([-+]?[\d.]+)%\)/,
        /\$([\d,.]+)/,
      ];
      
      for (const pattern of pricePatterns) {
        const match = block.match(pattern);
        if (match) {
          analysis.price = parseFloat(match[1].replace(',', ''));
          if (match[2]) analysis.change = parseFloat(match[2]);
          break;
        }
      }
      
      // Extract change percentage if not already found
      if (analysis.price && !analysis.change) {
        const changeMatch = block.match(/\(([-+]?[\d.]+)%\)/);
        if (changeMatch) analysis.change = parseFloat(changeMatch[1]);
      }
      
      // Extract P/E ratio
      const peMatch = block.match(/P\/E(?:\s*Ratio)?:?\s*([\d.]+)/i);
      if (peMatch) analysis.pe = parseFloat(peMatch[1]);
      
      // Extract ROE (Return on Equity)
      const roeMatch = block.match(/ROE:?\s*([\d.]+)%?/i);
      if (roeMatch) analysis.roe = parseFloat(roeMatch[1]);
      
      // Extract price target
      const targetPatterns = [
        /(?:Price\s*)?Target:?\s*\$?([\d,.]+)/i,
        /PT:?\s*\$?([\d,.]+)/i,
      ];
      for (const pattern of targetPatterns) {
        const match = block.match(pattern);
        if (match) {
          analysis.priceTarget = parseFloat(match[1].replace(',', ''));
          break;
        }
      }
      
      // Extract upside percentage
      const upsideMatch = block.match(/(?:Upside:?\s*|[\+\-])([\d.]+)%\s*upside/i) ||
                          block.match(/Upside:?\s*([\d.]+)%?/i);
      if (upsideMatch) analysis.upside = parseFloat(upsideMatch[1]);
      
      // Calculate upside if price and target are available but upside not provided
      if (!analysis.upside && analysis.price && analysis.priceTarget) {
        analysis.upside = ((analysis.priceTarget - analysis.price) / analysis.price) * 100;
      }
      
      // Extract recommendation (BUY/HOLD/SELL)
      const recPatterns = [
        /Verdict:?\s*(?:Strong\s*)?(BUY|HOLD|SELL)/i,
        /Recommendation:?\s*(BUY|HOLD|SELL)/i,
        /\b(BUY|HOLD|SELL)\b/i,
      ];
      for (const pattern of recPatterns) {
        const match = block.match(pattern);
        if (match) {
          analysis.recommendation = match[1].toUpperCase() as 'BUY' | 'HOLD' | 'SELL';
          break;
        }
      }
      
      // Generate AI-like insight text based on extracted metrics
      analysis.insight = generateInsight(analysis);
      
      // Only include analysis if we have meaningful data (symbol + at least one metric)
      if (symbol && (analysis.price || analysis.recommendation || analysis.pe)) {
        results.push(analysis);
      }
    }
    
    return results;
  }

  /**
   * Generates recommendation text based on stock analysis metrics.
   * Uses recommendation, upside, P/E, and ROE to create contextual insights.
   */
  function generateInsight(analysis: StockAnalysis): string {
    const rec = analysis.recommendation;
    const upside = analysis.upside || 0;
    const pe = analysis.pe || 0;
    const roe = analysis.roe || 0;
    
    if (rec === 'BUY') {
      if (upside > 30) {
        return `Strong opportunity! ${upside.toFixed(0)}% upside potential with solid fundamentals.`;
      } else if (roe > 50) {
        return `Exceptional ROE of ${roe.toFixed(0)}% signals strong profitability. Good entry point.`;
      } else {
        return `Analysts see ${upside.toFixed(0)}% upside. Consider adding to your portfolio.`;
      }
    } else if (rec === 'HOLD') {
      if (pe > 50) {
        return `Fairly valued but high P/E (${pe.toFixed(0)}). Wait for a better entry.`;
      } else {
        return `Solid position. Hold for long-term gains, limited short-term upside.`;
      }
    } else if (rec === 'SELL') {
      return `Consider taking profits. Limited upside at current valuation.`;
    }
    
    return `Analyze this position based on your risk tolerance.`;
  }

  async function analyzePortfolioStocks() {
    if (portfolio.length === 0) return;
    
    setAnalyzingPortfolio(true);
    try {
      const symbols = portfolio.slice(0, 6).map(p => p.ticker);
      const result = await analyzeStocks(symbols);
      const parsed = parseAnalysis(result.analysis);
      setPortfolioAnalysis(parsed);
    } catch (err) {
      setError('Portfolio analysis failed');
    } finally {
      setAnalyzingPortfolio(false);
    }
  }

  async function analyzeHotStocks() {
    setAnalyzingHot(true);
    try {
      // Filter out stocks already in portfolio
      const availableStocks = HOT_STOCKS_POOL.filter(
        h => !portfolio.some(p => p.ticker === h.symbol)
      );
      
      // Shuffle and pick max 3 random stocks
      const selectedStocks = shuffleArray(availableStocks).slice(0, 3);
      
      if (selectedStocks.length === 0) {
        setHotAnalysis([]);
        setError('All hot stocks are already in your portfolio!');
        return;
      }
      
      const hotSymbols = selectedStocks.map(h => h.symbol);
      
      const result = await analyzeStocks(hotSymbols);
      const parsed = parseAnalysis(result.analysis);
      
      // Fallback: If parsing failed, create minimal entries
      if (parsed.length === 0) {
        const fallback: StockAnalysis[] = selectedStocks.map(s => ({
          symbol: s.symbol,
          name: s.name,
          recommendation: 'HOLD' as const,
          insight: 'Analysis data unavailable. Try again later.',
        }));
        setHotAnalysis(fallback);
      } else {
        setHotAnalysis(parsed);
      }
    } catch (err) {
      // On error, pick 3 random from pool as fallback
      const availableStocks = HOT_STOCKS_POOL.filter(
        h => !portfolio.some(p => p.ticker === h.symbol)
      );
      const selectedStocks = shuffleArray(availableStocks).slice(0, 3);
      
      const fallback: StockAnalysis[] = selectedStocks.map(s => ({
        symbol: s.symbol,
        name: s.name,
        recommendation: 'HOLD' as const,
        insight: 'Could not fetch live data.',
      }));
      setHotAnalysis(fallback);
      setError('Hot stocks analysis failed - showing cached data');
    } finally {
      setAnalyzingHot(false);
    }
  }

  async function handleTrade() {
    if (!tradeModal || !tradeModal.currentPrice) return;

    setTrading(true);
    try {
      const price = tradeModal.currentPrice;
      if (tradeModal.type === 'buy') {
        await buyStock(tradeModal.symbol, tradeQty, price);
      } else {
        await sellStock(tradeModal.symbol, tradeQty, price);
      }
      
      await loadData();
      setPortfolioAnalysis([]);
      setTradeModal(null);
      setTradeQty(1);
    } catch (err) {
      setError(`Trade failed: ${err}`);
    } finally {
      setTrading(false);
    }
  }

  // Get analysis for a specific stock
  const getAnalysisForStock = (symbol: string): StockAnalysis | undefined => {
    return portfolioAnalysis.find(a => a.symbol === symbol) || 
           hotAnalysis.find(a => a.symbol === symbol);
  };

  const portfolioValue = portfolio.reduce((sum, p) => sum + p.invested, 0);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          Stock AI
        </h1>
        <p className="text-gray-500 mt-1">AI-powered portfolio intelligence</p>
      </div>

      {/* Balance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-emerald-600/20 to-emerald-700/10 rounded-xl border border-emerald-500/30 p-6">
          <div className="text-emerald-400 text-sm mb-1">Cash Balance</div>
          <div className="text-3xl font-bold text-white">
            {balance !== null ? `${balance.toLocaleString()} CHF` : '—'}
          </div>
        </div>
        <div className="bg-gradient-to-br from-blue-600/20 to-blue-700/10 rounded-xl border border-blue-500/30 p-6">
          <div className="text-blue-400 text-sm mb-1">Portfolio Value</div>
          <div className="text-3xl font-bold text-white">
            {portfolioValue > 0 ? `${portfolioValue.toLocaleString()} CHF` : '—'}
          </div>
        </div>
        <div className="bg-gradient-to-br from-purple-600/20 to-purple-700/10 rounded-xl border border-purple-500/30 p-6">
          <div className="text-purple-400 text-sm mb-1">Total Positions</div>
          <div className="text-3xl font-bold text-white">{portfolio.length}</div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400">
          {error}
          <button onClick={() => setError(null)} className="ml-4 underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Loading */}
      {loading && <LoadingSkeleton />}

      {/* Portfolio Section */}
      {!loading && portfolio.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <WalletIcon />
              Your Holdings
            </h2>
            <button
              onClick={analyzePortfolioStocks}
              disabled={analyzingPortfolio}
              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:from-gray-700 disabled:to-gray-700 text-white text-sm font-medium rounded-lg transition-all flex items-center gap-2"
            >
              {analyzingPortfolio ? (
                <>
                  <LoadingSpinner />
                  Analyzing...
                </>
              ) : (
                <>
                  <SparklesIcon />
                  Analyze Portfolio
                </>
              )}
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {portfolio.map((stock) => (
              <StockCard
                key={stock.ticker}
                symbol={stock.ticker}
                quantity={stock.quantity}
                invested={stock.invested}
                analysis={getAnalysisForStock(stock.ticker)}
                isOwned={true}
                onBuy={() => {
                  const analysis = getAnalysisForStock(stock.ticker);
                  setTradeModal({ 
                    type: 'buy', 
                    symbol: stock.ticker,
                    currentPrice: analysis?.price 
                  });
                  setTradeQty(1);
                }}
                onSell={() => {
                  const analysis = getAnalysisForStock(stock.ticker);
                  setTradeModal({
                    type: 'sell',
                    symbol: stock.ticker,
                    currentPrice: analysis?.price,
                    maxQty: stock.quantity,
                  });
                  setTradeQty(1);
                }}
              />
            ))}
          </div>
        </div>
      )}

      {/* Hot Stocks Section */}
      {!loading && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <FireIcon />
              <span className="bg-gradient-to-r from-orange-400 to-red-500 bg-clip-text text-transparent">
                Hot Market Picks
              </span>
            </h2>
            <button
              onClick={analyzeHotStocks}
              disabled={analyzingHot}
              className="px-4 py-2 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 disabled:from-gray-700 disabled:to-gray-700 text-white text-sm font-medium rounded-lg transition-all flex items-center gap-2"
            >
              {analyzingHot ? (
                <>
                  <LoadingSpinner />
                  Scanning...
                </>
              ) : (
                <>
                  <SparklesIcon />
                  Analyze Market
                </>
              )}
            </button>
          </div>
          
          {hotAnalysis.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {hotAnalysis.map((stock) => (
                <StockCard
                  key={stock.symbol}
                  symbol={stock.symbol}
                  name={stock.name}
                  analysis={stock}
                  isOwned={false}
                  isHot={true}
                  onBuy={() => {
                    setTradeModal({ 
                      type: 'buy', 
                      symbol: stock.symbol,
                      currentPrice: stock.price 
                    });
                    setTradeQty(1);
                  }}
                />
              ))}
            </div>
          ) : (
            <div className="bg-gradient-to-br from-orange-600/5 to-red-600/5 rounded-xl border border-orange-500/20 p-8 text-center">
              <div className="text-gray-400 text-lg mb-2">Discover Hot Opportunities</div>
              <div className="text-gray-500 text-sm mb-4">
                Click "Analyze Market" to discover trending stocks
              </div>
            </div>
          )}
        </div>
      )}

      {/* Trade Modal */}
      {tradeModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
          <div className="bg-[#1a1a1a] rounded-2xl border border-[#333] p-6 w-full max-w-md">
            <h3 className="text-xl font-bold text-white mb-4">
              {tradeModal.type === 'buy' ? 'Buy' : 'Sell'} {tradeModal.symbol}
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-gray-400 text-sm mb-2">Quantity</label>
                <input
                  type="number"
                  min="1"
                  max={tradeModal.maxQty || 999}
                  value={tradeQty}
                  onChange={(e) => setTradeQty(parseInt(e.target.value) || 1)}
                  className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-3 text-white"
                />
                {tradeModal.maxQty && (
                  <p className="text-gray-500 text-xs mt-1">
                    Max: {tradeModal.maxQty} shares
                  </p>
                )}
              </div>

              <div>
                <label className="block text-gray-400 text-sm mb-2">Price per Share (CHF)</label>
                <div className="w-full bg-black/30 border border-white/5 rounded-xl px-4 py-3 text-white flex items-center justify-between">
                  <span className="text-xl font-semibold">
                    {tradeModal.currentPrice ? `$${tradeModal.currentPrice.toFixed(2)}` : 'N/A'}
                  </span>
                  <span className="text-gray-500 text-sm">Live Price</span>
                </div>
              </div>

              {tradeModal.currentPrice && (
                <div className="bg-white/5 rounded-xl p-4">
                  <div className="text-gray-400 text-sm">Total</div>
                  <div className="text-2xl font-bold text-white">
                    {(tradeQty * tradeModal.currentPrice).toFixed(2)} CHF
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setTradeModal(null)}
                className="flex-1 px-4 py-3 bg-white/10 text-white rounded-xl hover:bg-white/20"
              >
                Cancel
              </button>
              <button
                onClick={handleTrade}
                disabled={trading || !tradeModal.currentPrice}
                className={`flex-1 px-4 py-3 rounded-xl font-semibold transition-all ${
                  tradeModal.type === 'buy'
                    ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
                    : 'bg-red-600 hover:bg-red-500 text-white'
                } disabled:bg-gray-700`}
              >
                {trading ? 'Processing...' : tradeModal.type === 'buy' ? 'Buy' : 'Sell'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Stock Card with AI Analysis
function StockCard({
  symbol,
  name,
  quantity,
  invested,
  analysis,
  isOwned,
  isHot,
  onBuy,
  onSell,
}: {
  symbol: string;
  name?: string;
  quantity?: number;
  invested?: number;
  analysis?: StockAnalysis;
  isOwned: boolean;
  isHot?: boolean;
  onBuy?: () => void;
  onSell?: () => void;
}) {
  const hasAnalysis = !!analysis?.price;
  const recColor = {
    BUY: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    HOLD: 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30',
    SELL: 'text-red-400 bg-red-500/20 border-red-500/30',
  };

  // Calculate upside if we have both values
  const calculatedUpside = analysis?.upside || 
    (analysis?.price && analysis?.priceTarget 
      ? ((analysis.priceTarget - analysis.price) / analysis.price) * 100 
      : null);

  return (
    <div
      className={`rounded-xl border p-5 transition-all hover:scale-[1.02] ${
        isHot
          ? 'bg-gradient-to-br from-orange-600/15 to-red-600/10 border-orange-500/30'
          : isOwned
          ? 'bg-gradient-to-br from-blue-600/15 to-indigo-600/10 border-blue-500/30'
          : 'bg-gradient-to-br from-emerald-600/15 to-teal-600/10 border-emerald-500/30'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className="text-xl font-bold text-white flex items-center gap-2">
            {symbol}
          </div>
          <div className="text-gray-500 text-sm">{name || analysis?.name}</div>
        </div>
        {analysis?.recommendation && (
          <span className={`px-3 py-1 rounded-lg text-xs font-bold border ${recColor[analysis.recommendation]}`}>
            {analysis.recommendation}
          </span>
        )}
      </div>

      {/* Price & Change */}
      {hasAnalysis && (
        <div className="flex items-baseline gap-2 mb-3">
          <span className="text-2xl font-bold text-white">${analysis.price?.toFixed(2)}</span>
          <span className={`text-sm font-medium ${
            (analysis.change || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'
          }`}>
            {(analysis.change || 0) >= 0 ? '+' : ''}{analysis.change?.toFixed(2)}%
          </span>
        </div>
      )}

      {/* Metrics Grid */}
      {hasAnalysis && (
        <div className="grid grid-cols-2 gap-2 mb-3">
          <div className="bg-black/20 rounded-lg p-2">
            <div className="text-gray-500 text-xs">P/E</div>
            <div className="text-white font-semibold">{analysis.pe?.toFixed(1) || '—'}</div>
          </div>
          <div className="bg-black/20 rounded-lg p-2">
            <div className="text-gray-500 text-xs">ROE</div>
            <div className="text-white font-semibold">{analysis.roe ? `${analysis.roe.toFixed(1)}%` : '—'}</div>
          </div>
          <div className="bg-black/20 rounded-lg p-2 col-span-2">
            <div className="text-gray-500 text-xs">Price Target</div>
            <div className="flex items-center justify-between">
              <span className="text-white font-semibold">
                {analysis.priceTarget ? `$${analysis.priceTarget.toFixed(0)}` : '—'}
              </span>
              {calculatedUpside !== null && (
                <span className={`text-sm font-medium ${calculatedUpside >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {calculatedUpside >= 0 ? '+' : ''}{calculatedUpside.toFixed(1)}% upside
                </span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* AI Insight */}
      {analysis?.insight && (
        <div className="bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-lg p-3 mb-3 border border-purple-500/20">
          <p className="text-gray-300 text-sm leading-relaxed">{analysis.insight}</p>
        </div>
      )}

      {/* Owned Stats */}
      {isOwned && quantity && (
        <div className="bg-black/20 rounded-lg p-3 mb-3">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Shares Owned</span>
            <span className="text-white font-medium">{quantity}</span>
          </div>
          <div className="flex justify-between text-sm mt-1">
            <span className="text-gray-500">Invested</span>
            <span className="text-white font-medium">{invested?.toFixed(0)} CHF</span>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        {onBuy && (
          <button
            onClick={onBuy}
            className="flex-1 px-4 py-2 bg-emerald-600/20 hover:bg-emerald-600/40 border border-emerald-500/30 text-emerald-400 rounded-lg text-sm font-medium transition-all"
          >
            {isOwned ? 'Buy More' : 'Buy'}
          </button>
        )}
        {onSell && isOwned && (
          <button
            onClick={onSell}
            className="flex-1 px-4 py-2 bg-red-600/20 hover:bg-red-600/40 border border-red-500/30 text-red-400 rounded-lg text-sm font-medium transition-all"
          >
            Sell
          </button>
        )}
      </div>
    </div>
  );
}

// Loading Components
function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-[#141414] rounded-xl h-24"></div>
        <div className="bg-[#141414] rounded-xl h-24"></div>
        <div className="bg-[#141414] rounded-xl h-24"></div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-[#141414] rounded-xl h-64"></div>
        <div className="bg-[#141414] rounded-xl h-64"></div>
        <div className="bg-[#141414] rounded-xl h-64"></div>
      </div>
    </div>
  );
}

function LoadingSpinner() {
  return (
    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
        fill="none"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

// Icons
function SparklesIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
      />
    </svg>
  );
}

function WalletIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
      />
    </svg>
  );
}

function FireIcon() {
  return (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 23c-3.866 0-7-3.134-7-7 0-2.5 1.5-4.5 3-6 .5-.5 1-1.5 1-2.5 0-.5.5-1 1-1s1 .5 1 1c0 1.5-.5 3-1.5 4 1.5-1 2.5-2.5 2.5-4.5 0-1-.5-2-1-3 0 0 2 1 3 3 1 2 1.5 3.5 1.5 5 0 2.5-1 4.5-3 6 2 0 4-2 4-5 0-1-.5-2-1-3 2 2 3 4.5 3 7 0 3.866-3.134 7-7 7z"/>
    </svg>
  );
}
