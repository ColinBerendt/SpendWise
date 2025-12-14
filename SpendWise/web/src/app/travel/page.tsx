'use client';

import { useState } from 'react';
import { planTrip } from '@/lib/api';

interface DataSource {
  name: string;
  source: string;
  isLive: boolean;
}

interface ParsedTrip {
  destination: string | null;
  dates: string | null;
  nights: string | null;
  flightsPrice: string | null;
  flightsInfo: string | null;
  hotelPrice: string | null;
  hotelInfo: string | null;
  hotelList: string[];
  dailyBudget: string | null;
  dailyInfo: string | null;
  onsiteTotal: string | null;
  totalCost: string | null;
  weatherTemp: string | null;
  weatherInfo: string | null;
  highlights: string[];
  recommendation: string | null;
  dataSources: DataSource[];
}

export default function TravelPage() {
  const [destination, setDestination] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [rawResponse, setRawResponse] = useState<string | null>(null);
  const [parsedTrip, setParsedTrip] = useState<ParsedTrip | null>(null);
  const [error, setError] = useState<string | null>(null);

  const popularCities = [
    { name: 'Barcelona', code: 'BCN' },
    { name: 'Rome', code: 'FCO' },
    { name: 'Paris', code: 'CDG' },
    { name: 'London', code: 'LHR' },
    { name: 'Amsterdam', code: 'AMS' },
    { name: 'Prague', code: 'PRG' },
  ];

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!destination || !startDate || !endDate) return;

    setLoading(true);
    setError(null);
    setRawResponse(null);
    setParsedTrip(null);

    try {
      const result = await planTrip(destination, startDate, endDate);
      setRawResponse(result.response);
      
      if (result.success) {
        // Always try to parse - will return partial data if possible
        const parsed = parseFlexibleFormat(result.response, destination, startDate, endDate);
        setParsedTrip(parsed);
      } else {
        setError(result.response);
      }
    } catch (err) {
      setError('Failed to plan trip. Make sure the API is running.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Travel Planner</h1>
        <p className="text-gray-500 mt-1">AI-powered trip cost estimation</p>
      </div>

      {/* Form */}
      <div className="bg-gradient-to-br from-[#1a1a2e] to-[#16213e] rounded-2xl border border-[#0f3460]/50 p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-gray-400 text-sm mb-2">Destination</label>
            <input
              type="text"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              placeholder="Enter city..."
              className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-blue-500/50"
            />
            <div className="flex gap-2 mt-3 flex-wrap">
              {popularCities.map(city => (
                <button
                  key={city.code}
                  type="button"
                  onClick={() => setDestination(city.name)}
                  className={`px-4 py-2 rounded-xl text-sm transition-all ${
                    destination === city.name
                      ? 'bg-blue-500 text-white'
                      : 'bg-white/5 text-gray-400 hover:bg-white/10'
                  }`}
                >
                  {city.name}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-400 text-sm mb-2">From</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500/50"
              />
            </div>
            <div>
              <label className="block text-gray-400 text-sm mb-2">To</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full bg-black/30 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500/50"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !destination || !startDate || !endDate}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:from-gray-700 disabled:to-gray-700 text-white font-semibold py-4 rounded-xl transition-all"
          >
            {loading ? 'Planning...' : 'Get Trip Estimate'}
          </button>
        </form>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && <LoadingSkeleton />}

      {/* Results */}
      {parsedTrip && (
        <div className="space-y-6 animate-fade-in">
          {/* Header Card */}
          <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-2xl border border-blue-500/30 p-6">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <h2 className="text-3xl font-bold text-white">{parsedTrip.destination || destination}</h2>
                <p className="text-gray-400 mt-1">
                  {parsedTrip.dates || `${startDate} to ${endDate}`}
                  {parsedTrip.nights && ` (${parsedTrip.nights} nights)`}
                </p>
              </div>
              {parsedTrip.totalCost && (
                <div className="text-right">
                  <div className="text-gray-400 text-sm">Total Cost</div>
                  <div className="text-4xl font-bold text-yellow-400">{parsedTrip.totalCost}</div>
                </div>
              )}
            </div>
          </div>

          {/* Cost Breakdown - only show cards with data */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {(parsedTrip.flightsPrice || parsedTrip.flightsInfo) && (
              <CostCard
                icon={<PlaneIcon />}
                title="Flights"
                price={parsedTrip.flightsPrice}
                info={parsedTrip.flightsInfo}
                color="blue"
              />
            )}
            {(parsedTrip.hotelPrice || parsedTrip.hotelInfo) && (
              <CostCard
                icon={<HotelIcon />}
                title="Hotel"
                price={parsedTrip.hotelPrice}
                info={parsedTrip.hotelInfo}
                color="indigo"
              />
            )}
            {(parsedTrip.onsiteTotal || parsedTrip.dailyInfo) && (
              <CostCard
                icon={<WalletIcon />}
                title="On-site"
                price={parsedTrip.onsiteTotal}
                info={parsedTrip.dailyInfo}
                color="purple"
              />
            )}
          </div>

          {/* Weather & Highlights */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Weather */}
            {(parsedTrip.weatherTemp || parsedTrip.weatherInfo) && (
              <div className="bg-[#141414] rounded-xl border border-[#262626] p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-cyan-500/20 rounded-xl flex items-center justify-center">
                    <WeatherIcon className="w-6 h-6 text-cyan-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">Weather</h3>
                    {parsedTrip.weatherTemp && (
                      <p className="text-2xl font-bold text-cyan-400">{parsedTrip.weatherTemp}</p>
                    )}
                  </div>
                </div>
                {parsedTrip.weatherInfo && (
                  <p className="text-gray-400">{parsedTrip.weatherInfo}</p>
                )}
              </div>
            )}

            {/* Highlights */}
            {parsedTrip.highlights.length > 0 && (
              <div className="bg-[#141414] rounded-xl border border-[#262626] p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-amber-500/20 rounded-xl flex items-center justify-center">
                    <StarIcon className="w-6 h-6 text-amber-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-white">Top Attractions</h3>
                </div>
                <div className="grid grid-cols-1 gap-2">
                  {parsedTrip.highlights.map((highlight, i) => (
                    <div key={i} className="flex items-center gap-2 text-gray-300">
                      <span className="w-6 h-6 bg-amber-500/20 rounded-full flex items-center justify-center text-xs text-amber-400 font-bold">
                        {i + 1}
                      </span>
                      {highlight}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Hotels */}
          {parsedTrip.hotelList.length > 0 && (
            <div className="bg-[#141414] rounded-xl border border-[#262626] p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-indigo-500/20 rounded-xl flex items-center justify-center text-indigo-400">
                  <HotelIcon />
                </div>
                <h3 className="text-lg font-semibold text-white">Hotel Options</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {parsedTrip.hotelList.map((hotel, i) => (
                  <span key={i} className="px-4 py-2 bg-indigo-500/10 border border-indigo-500/30 rounded-lg text-indigo-300 text-sm">
                    {hotel}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Recommendation */}
          {parsedTrip.recommendation && (
            <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-xl p-6">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 bg-green-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
                  <CheckIcon className="w-5 h-5 text-green-400" />
                </div>
                <div>
                  <h3 className="text-sm text-green-400 font-medium">Summary</h3>
                  <p className="text-white">{parsedTrip.recommendation}</p>
                </div>
              </div>
            </div>
          )}

          {/* Data Sources */}
          {parsedTrip.dataSources.length > 0 && (
            <div className="bg-[#0d0d0d] rounded-xl border border-[#1a1a1a] p-4">
              <h3 className="text-xs text-gray-500 uppercase tracking-wider mb-3">Data Sources</h3>
              <div className="flex flex-wrap gap-2">
                {parsedTrip.dataSources.map((ds, i) => (
                  <span 
                    key={i} 
                    className={`px-3 py-1.5 rounded-lg text-xs flex items-center gap-1.5 ${
                      ds.isLive 
                        ? 'bg-green-500/10 text-green-400 border border-green-500/20' 
                        : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
                    }`}
                  >
                    <span className={`w-1.5 h-1.5 rounded-full ${ds.isLive ? 'bg-green-400' : 'bg-yellow-400'}`}></span>
                    {ds.name}: {ds.source}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Raw Response (collapsed) */}
          <details className="bg-[#0a0a0a] rounded-xl border border-[#1a1a1a]">
            <summary className="p-4 cursor-pointer text-gray-600 hover:text-gray-400 text-sm">
              View full AI response
            </summary>
            <pre className="p-4 text-xs text-gray-500 whitespace-pre-wrap border-t border-[#1a1a1a] overflow-x-auto">
              {rawResponse}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}

// Flexible parser that extracts what it can from various formats
function parseFlexibleFormat(text: string, defaultDest: string, startDate: string, endDate: string): ParsedTrip {
  const result: ParsedTrip = {
    destination: null,
    dates: null,
    nights: null,
    flightsPrice: null,
    flightsInfo: null,
    hotelPrice: null,
    hotelInfo: null,
    hotelList: [],
    dailyBudget: null,
    dailyInfo: null,
    onsiteTotal: null,
    totalCost: null,
    weatherTemp: null,
    weatherInfo: null,
    highlights: [],
    recommendation: null,
    dataSources: [],
  };

  // Parse DATA SOURCES section (after TRAVEL_RESPONSE_END)
  const dataSourcesMatch = text.match(/DATA SOURCES:\s*([\s\S]*?)(?:$|\n\n)/i);
  if (dataSourcesMatch) {
    const lines = dataSourcesMatch[1].split('\n');
    for (const line of lines) {
      const match = line.match(/^-\s*([^:]+):\s*(.+)$/);
      if (match) {
        const name = match[1].trim();
        const source = match[2].trim();
        const isLive = source.toLowerCase().includes('live');
        result.dataSources.push({ name, source, isLive });
      }
    }
  }

  // Try strict format first
  const strictMatch = text.match(/===TRAVEL_RESPONSE_START===([\s\S]*?)===TRAVEL_RESPONSE_END===/);
  if (strictMatch) {
    const content = strictMatch[1];
    const getField = (name: string): string | null => {
      const regex = new RegExp(`^${name}:\\s*(.+)$`, 'm');
      const m = content.match(regex);
      return m ? m[1].trim() : null;
    };

    result.destination = getField('DESTINATION');
    result.dates = getField('DATES');
    result.nights = getField('NIGHTS');
    result.flightsPrice = getField('FLIGHTS_PRICE');
    result.flightsInfo = getField('FLIGHTS_INFO');
    result.hotelPrice = getField('HOTEL_PRICE');
    result.hotelInfo = getField('HOTEL_INFO');
    result.dailyBudget = getField('DAILY_BUDGET');
    result.dailyInfo = getField('DAILY_INFO');
    result.onsiteTotal = getField('ONSITE_TOTAL');
    result.totalCost = getField('TOTAL_COST');
    result.weatherTemp = getField('WEATHER_TEMP');
    result.weatherInfo = getField('WEATHER_INFO');
    result.recommendation = getField('RECOMMENDATION');

    const hotelListStr = getField('HOTEL_LIST');
    if (hotelListStr) {
      result.hotelList = hotelListStr.split(',').map(h => h.trim()).filter(h => h);
    }

    for (let i = 1; i <= 5; i++) {
      const h = getField(`HIGHLIGHT_${i}`);
      if (h) result.highlights.push(h);
    }

    return result;
  }

  // Fallback: flexible parsing for free-form responses
  
  // Destination from TRIP line
  const tripMatch = text.match(/TRIP:\s*([A-Za-z\s]+)/i);
  result.destination = tripMatch ? tripMatch[1].trim() : defaultDest;

  // Dates
  const datesMatch = text.match(/\((\d{4}-\d{2}-\d{2})\s*to\s*(\d{4}-\d{2}-\d{2})\)/);
  if (datesMatch) {
    result.dates = `${datesMatch[1]} to ${datesMatch[2]}`;
  }

  // Nights
  const nightsMatch = text.match(/(\d+)\s*nights?/i);
  result.nights = nightsMatch ? nightsMatch[1] : null;

  // Flights price - various formats
  const flightsPatterns = [
    /Flights?:?\s*(?:from\s*)?([0-9,.]+)\s*CHF/i,
    /Flights?:?\s*([0-9,.]+)\s*CHF/i,
    /([0-9,.]+)\s*CHF.*(?:flight|round.?trip)/i,
  ];
  for (const pattern of flightsPatterns) {
    const m = text.match(pattern);
    if (m) {
      result.flightsPrice = `${m[1]} CHF`;
      break;
    }
  }

  // Flight info
  const flightInfoMatch = text.match(/Flights?:?[^\n]*\(([^)]+)\)/i);
  result.flightsInfo = flightInfoMatch ? flightInfoMatch[1] : null;

  // Hotel price
  const hotelPricePatterns = [
    /Hotel:?\s*([0-9,.]+)\s*CHF/i,
    /([0-9,.]+)\s*CHF.*hotel/i,
    /hotel.*?([0-9,.]+)\s*CHF/i,
  ];
  for (const pattern of hotelPricePatterns) {
    const m = text.match(pattern);
    if (m) {
      result.hotelPrice = `${m[1]} CHF`;
      break;
    }
  }

  // Hotel info
  const hotelNightMatch = text.match(/(\d+)\s*nights?\s*[x×]\s*([0-9,.]+)\s*CHF/i);
  if (hotelNightMatch) {
    result.hotelInfo = `${hotelNightMatch[2]} CHF/night`;
  }

  // On-site/Daily
  const onsiteMatch = text.match(/On-site:?\s*([0-9,.]+)\s*CHF/i);
  result.onsiteTotal = onsiteMatch ? `${onsiteMatch[1]} CHF` : null;

  const dailyMatch = text.match(/(\d+)\s*days?\s*[x×]\s*([0-9,.]+)\s*CHF/i);
  if (dailyMatch) {
    result.dailyInfo = `${dailyMatch[2]} CHF/day for ${dailyMatch[1]} days`;
  }

  // Total
  const totalPatterns = [
    /TOTAL:?\s*([0-9,.]+)\s*CHF/i,
    /Total.*?([0-9,.]+)\s*CHF/i,
  ];
  for (const pattern of totalPatterns) {
    const m = text.match(pattern);
    if (m) {
      result.totalCost = `${m[1]} CHF`;
      break;
    }
  }

  // Weather temperature
  const tempMatch = text.match(/(\d+)[-–](\d+)\s*°?C/);
  if (tempMatch) {
    result.weatherTemp = `${tempMatch[1]}-${tempMatch[2]}°C`;
  }

  // Weather info
  const weatherInfoMatch = text.match(/(?:partly\s+)?(?:sunny|cloudy|rain|clear|mild)[^.]*\./i);
  result.weatherInfo = weatherInfoMatch ? weatherInfoMatch[0].trim() : null;

  // Hotels - look for hotel names (typically in CAPS or after bullet points)
  const hotelSection = text.match(/HOTEL\s*OPTIONS?:?\s*([\s\S]*?)(?:\n\n|ESTIMATED|WEATHER|HIGHLIGHTS|$)/i);
  if (hotelSection) {
    const hotelLines = hotelSection[1].match(/[-*]\s*([A-Z][A-Z0-9\s-]+)/g);
    if (hotelLines) {
      result.hotelList = hotelLines
        .map(h => h.replace(/^[-*]\s*/, '').trim())
        .filter(h => h.length > 3 && h.length < 50);
    }
  }

  // Highlights - look for attractions after HIGHLIGHTS section
  const highlightsSection = text.match(/HIGHLIGHTS?:?\s*([\s\S]*?)(?:\n\n|---|Let me know|$)/i);
  if (highlightsSection) {
    const highlightLines = highlightsSection[1].match(/[-*]\s*([^(\n]+)/g);
    if (highlightLines) {
      result.highlights = highlightLines
        .map(h => h.replace(/^[-*]\s*/, '').trim())
        .filter(h => h.length > 2 && h.length < 80 && !h.toLowerCase().includes('you may'))
        .slice(0, 5);
    }
  }

  // Recommendation - look for summary text
  const summaryMatch = text.match(/(?:RECOMMENDATION|SUMMARY):?\s*([^\n]+)/i);
  if (summaryMatch) {
    result.recommendation = summaryMatch[1].trim();
  } else {
    // Use the last line before "Let me know" as summary
    const lastSection = text.match(/TOTAL:?[^\n]*\n+([^-\n][^\n]+)/);
    if (lastSection) {
      result.recommendation = lastSection[1].trim();
    }
  }

  return result;
}

function CostCard({ icon, title, price, info, color }: {
  icon: React.ReactNode;
  title: string;
  price: string | null;
  info: string | null;
  color: 'blue' | 'indigo' | 'purple';
}) {
  const colors = {
    blue: 'from-blue-600/30 to-blue-700/15 border-blue-500/50',
    indigo: 'from-indigo-500/25 to-indigo-600/10 border-indigo-500/40',
    purple: 'from-purple-500/25 to-purple-600/10 border-purple-500/40',
  };
  const iconColors = {
    blue: 'bg-blue-500/30 text-blue-400',
    indigo: 'bg-indigo-500/25 text-indigo-400',
    purple: 'bg-purple-500/25 text-purple-400',
  };
  const priceColors = {
    blue: 'text-blue-400',
    indigo: 'text-indigo-400',
    purple: 'text-purple-400',
  };

  return (
    <div className={`bg-gradient-to-br ${colors[color]} rounded-xl border p-6`}>
      <div className="flex items-center gap-3 mb-3">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${iconColors[color]}`}>
          {icon}
        </div>
        <span className="text-gray-400">{title}</span>
      </div>
      <div className={`text-3xl font-bold ${priceColors[color]}`}>{price || '—'}</div>
      {info && <p className="text-gray-500 text-sm mt-1">{info}</p>}
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="bg-[#141414] rounded-2xl h-32"></div>
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-[#141414] rounded-xl h-40"></div>
        <div className="bg-[#141414] rounded-xl h-40"></div>
        <div className="bg-[#141414] rounded-xl h-40"></div>
      </div>
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-[#141414] rounded-xl h-48"></div>
        <div className="bg-[#141414] rounded-xl h-48"></div>
      </div>
    </div>
  );
}

// Icons
function PlaneIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
    </svg>
  );
}

function HotelIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
    </svg>
  );
}

function WalletIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
    </svg>
  );
}

function WeatherIcon({ className }: { className?: string }) {
  return (
    <svg className={className || "w-5 h-5"} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
    </svg>
  );
}

function StarIcon({ className }: { className?: string }) {
  return (
    <svg className={className || "w-5 h-5"} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
    </svg>
  );
}

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg className={className || "w-5 h-5"} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  );
}
