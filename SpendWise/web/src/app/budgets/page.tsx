'use client';

import { useEffect, useState } from 'react';
import { getBudgets, getBudgetStatus, Budget } from '@/lib/api';

export default function BudgetsPage() {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [status, setStatus] = useState<{
    total_budget: number;
    total_spent: number;
    total_remaining: number;
    overall_usage_percent: number;
  } | null>(null);
  const [weekRange, setWeekRange] = useState({ start: '', end: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [budgetData, statusData] = await Promise.all([
          getBudgets(),
          getBudgetStatus(),
        ]);
        setBudgets(budgetData.budgets);
        setWeekRange({ start: budgetData.week_start, end: budgetData.week_end });
        setStatus(statusData);
      } catch (error) {
        console.error('Failed to load budgets:', error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Budgets</h1>
        <p className="text-gray-500 mt-1">
          Week of {weekRange.start} to {weekRange.end}
        </p>
      </div>

      {/* Overview Card */}
      {status && (
        <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-xl border border-blue-500/30 p-6">
          <div className="grid grid-cols-4 gap-6">
            <div>
              <div className="text-gray-400 text-sm">Total Budget</div>
              <div className="text-2xl font-bold text-white">
                CHF {status.total_budget.toFixed(0)}
              </div>
            </div>
            <div>
              <div className="text-gray-400 text-sm">Spent</div>
              <div className="text-2xl font-bold text-white">
                CHF {status.total_spent.toFixed(0)}
              </div>
            </div>
            <div>
              <div className="text-gray-400 text-sm">Remaining</div>
              <div className={`text-2xl font-bold ${
                status.total_remaining >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                CHF {status.total_remaining.toFixed(0)}
              </div>
            </div>
            <div>
              <div className="text-gray-400 text-sm">Usage</div>
              <div className={`text-2xl font-bold ${
                status.overall_usage_percent >= 100 ? 'text-red-400' :
                status.overall_usage_percent >= 80 ? 'text-yellow-400' :
                'text-green-400'
              }`}>
                {status.overall_usage_percent.toFixed(0)}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Budget Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {budgets.map((budget, index) => (
          <BudgetCard key={budget.id} budget={budget} index={index} />
        ))}
      </div>
    </div>
  );
}

function BudgetCard({ budget, index }: { budget: Budget; index: number }) {
  return (
    <div
      className="bg-[#141414] rounded-xl border border-[#262626] p-6 animate-fade-in"
      style={{ animationDelay: `${index * 100}ms` }}
    >
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          <div
            className="w-4 h-4 rounded-full"
            style={{ backgroundColor: budget.color }}
          />
          <h3 className="text-lg font-semibold text-white">{budget.category_name}</h3>
        </div>
        <StatusBadge status={budget.status} />
      </div>

      <div className="space-y-4">
        <div className="budget-bar h-3">
          <div
            className={`budget-bar-fill ${budget.status}`}
            style={{ width: `${Math.min(budget.usage_percent, 100)}%` }}
          />
        </div>

        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-gray-500 text-xs">Budget</div>
            <div className="text-white font-medium">CHF {budget.budget.toFixed(0)}</div>
          </div>
          <div>
            <div className="text-gray-500 text-xs">Spent</div>
            <div className="text-white font-medium">CHF {budget.spent.toFixed(0)}</div>
          </div>
          <div>
            <div className="text-gray-500 text-xs">Remaining</div>
            <div className={`font-medium ${budget.remaining >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              CHF {budget.remaining.toFixed(0)}
            </div>
          </div>
        </div>

        <div className="text-center">
          <span className={`text-3xl font-bold ${
            budget.status === 'over' ? 'text-red-400' :
            budget.status === 'warning' ? 'text-yellow-400' :
            'text-green-400'
          }`}>
            {budget.usage_percent.toFixed(0)}%
          </span>
          <span className="text-gray-500 ml-2">used</span>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: 'ok' | 'warning' | 'over' }) {
  const styles = {
    ok: 'bg-green-500/20 text-green-400 border-green-500/30',
    warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    over: 'bg-red-500/20 text-red-400 border-red-500/30',
  };

  const labels = {
    ok: 'On Track',
    warning: 'Warning',
    over: 'Over Budget',
  };

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${styles[status]}`}>
      {labels[status]}
    </span>
  );
}

