'use client';

import { useEffect, useState } from 'react';
import { getTransactions, getCategories, Transaction, Category } from '@/lib/api';

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<number | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [txData, catData] = await Promise.all([
          getTransactions(100),
          getCategories(),
        ]);
        setTransactions(txData.transactions);
        setCategories(catData.categories);
      } catch (error) {
        console.error('Failed to load transactions:', error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const filteredTransactions = filter
    ? transactions.filter(tx => tx.category_id === filter)
    : transactions;

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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Transactions</h1>
          <p className="text-gray-500 mt-1">{transactions.length} transactions</p>
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setFilter(null)}
          className={`px-4 py-2 rounded-lg text-sm transition-colors ${
            filter === null
              ? 'bg-blue-600 text-white'
              : 'bg-[#1a1a1a] text-gray-400 hover:bg-[#262626]'
          }`}
        >
          All
        </button>
        {categories.map(cat => (
          <button
            key={cat.id}
            onClick={() => setFilter(cat.id)}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              filter === cat.id
                ? 'bg-blue-600 text-white'
                : 'bg-[#1a1a1a] text-gray-400 hover:bg-[#262626]'
            }`}
          >
            {cat.name}
          </button>
        ))}
      </div>

      {/* Transactions Table */}
      <div className="bg-[#141414] rounded-xl border border-[#262626] overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[#262626]">
              <th className="text-left p-4 text-gray-500 font-medium">Date</th>
              <th className="text-left p-4 text-gray-500 font-medium">Description</th>
              <th className="text-left p-4 text-gray-500 font-medium">Category</th>
              <th className="text-left p-4 text-gray-500 font-medium">Merchant</th>
              <th className="text-right p-4 text-gray-500 font-medium">Amount</th>
            </tr>
          </thead>
          <tbody>
            {filteredTransactions.map((tx, index) => (
              <tr
                key={tx.id}
                className="border-b border-[#262626] last:border-0 hover:bg-[#1a1a1a] transition-colors animate-fade-in"
                style={{ animationDelay: `${index * 20}ms` }}
              >
                <td className="p-4 text-gray-400">{tx.date}</td>
                <td className="p-4 text-white">{tx.description}</td>
                <td className="p-4">
                  <span className="px-2 py-1 bg-[#262626] rounded text-sm text-gray-300">
                    {tx.category_name || 'Uncategorized'}
                  </span>
                </td>
                <td className="p-4 text-gray-400">{tx.merchant || '-'}</td>
                <td className={`p-4 text-right font-medium ${
                  tx.amount < 0 ? 'text-red-400' : 'text-green-400'
                }`}>
                  {tx.amount < 0 ? '-' : '+'}CHF {Math.abs(tx.amount).toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

