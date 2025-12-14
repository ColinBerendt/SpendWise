'use client';

import { useEffect, useState } from 'react';
import { getBudgets, getTransactions, getTransactionSummary, Budget, Transaction } from '@/lib/api';

export default function Dashboard() {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [summary, setSummary] = useState<{ income: number; expenses: number; net: number } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [budgetData, txData, summaryData] = await Promise.all([
          getBudgets(),
          getTransactions(5),
          getTransactionSummary('week'),
        ]);
        setBudgets(budgetData.budgets);
        setTransactions(txData.transactions);
        setSummary(summaryData);
      } catch (error) {
        console.error('Failed to load data:', error);
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

  const warningCount = budgets.filter(b => b.status === 'warning').length;
  const overCount = budgets.filter(b => b.status === 'over').length;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-gray-500 mt-1">Your financial overview</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="Balance"
          value={`CHF ${summary?.net.toLocaleString() || 0}`}
          subtitle="This week"
          color="blue"
        />
        <StatCard
          title="Expenses"
          value={`CHF ${summary?.expenses.toLocaleString() || 0}`}
          subtitle="This week"
          color="red"
        />
        <StatCard
          title="Budget Alerts"
          value={`${warningCount + overCount}`}
          subtitle={`${overCount} over, ${warningCount} warning`}
          color={overCount > 0 ? 'red' : warningCount > 0 ? 'yellow' : 'green'}
        />
      </div>

      {/* Budget Status */}
      <div className="bg-[#141414] rounded-xl border border-[#262626] p-6">
        <h2 className="text-xl font-semibold text-white mb-6">Budget Status</h2>
        <div className="space-y-4">
          {budgets.map((budget, index) => (
            <div
              key={budget.id}
              className="animate-fade-in"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center gap-3">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: budget.color }}
                  />
                  <span className="text-white">{budget.category_name}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-gray-400 text-sm">
                    CHF {budget.spent.toFixed(0)} / {budget.budget.toFixed(0)}
                  </span>
                  <span className={`text-sm font-medium ${
                    budget.status === 'over' ? 'text-red-500' :
                    budget.status === 'warning' ? 'text-yellow-500' :
                    'text-green-500'
                  }`}>
                    {budget.usage_percent.toFixed(0)}%
                  </span>
                  <StatusIcon status={budget.status} />
                </div>
              </div>
              <div className="budget-bar">
                <div
                  className={`budget-bar-fill ${budget.status}`}
                  style={{ width: `${Math.min(budget.usage_percent, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="bg-[#141414] rounded-xl border border-[#262626] p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-white">Recent Transactions</h2>
          <a href="/transactions" className="text-blue-500 text-sm hover:underline">
            View all
          </a>
        </div>
        <div className="space-y-3">
          {transactions.map((tx, index) => (
            <div
              key={tx.id}
              className="flex justify-between items-center py-3 border-b border-[#262626] last:border-0 animate-fade-in"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div>
                <div className="text-white">{tx.description}</div>
                <div className="text-gray-500 text-sm">
                  {tx.category_name} &middot; {tx.date}
                </div>
              </div>
              <div className={`font-medium ${tx.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                {tx.amount < 0 ? '-' : '+'}CHF {Math.abs(tx.amount).toFixed(2)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, subtitle, color }: {
  title: string;
  value: string;
  subtitle: string;
  color: 'blue' | 'red' | 'green' | 'yellow';
}) {
  const colorClasses = {
    blue: 'border-blue-500/30 bg-blue-500/5',
    red: 'border-red-500/30 bg-red-500/5',
    green: 'border-green-500/30 bg-green-500/5',
    yellow: 'border-yellow-500/30 bg-yellow-500/5',
  };

  return (
    <div className={`rounded-xl border p-6 ${colorClasses[color]}`}>
      <div className="text-gray-400 text-sm">{title}</div>
      <div className="text-2xl font-bold text-white mt-1">{value}</div>
      <div className="text-gray-500 text-sm mt-1">{subtitle}</div>
    </div>
  );
}

function StatusIcon({ status }: { status: 'ok' | 'warning' | 'over' }) {
  if (status === 'ok') {
    return <span className="text-green-500">&#10003;</span>;
  }
  if (status === 'warning') {
    return <span className="text-yellow-500">&#9888;</span>;
  }
  return <span className="text-red-500">&#10060;</span>;
}
