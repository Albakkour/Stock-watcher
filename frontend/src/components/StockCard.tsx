import React from 'react';
import { Stock } from '../types';
import { TrendingUp, Clock } from 'lucide-react';

interface StockCardProps {
  stock: Stock;
}

export const StockCard: React.FC<StockCardProps> = ({ stock }) => {
  const formattedTime = new Date(stock.updated_at).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: 0 }}>{stock.symbol}</h3>
          <span className="section-tag" style={{ fontSize: '0.65rem' }}>Market Data</span>
        </div>
        <div style={{ color: 'var(--primary)' }}>
          <TrendingUp size={24} />
        </div>
      </div>
      
      <div className="flex flex-col">
        <span className="font-mono" style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
          ${Number(stock.price).toFixed(2)}
        </span>
        <div className="flex items-center gap-2" style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
          <Clock size={12} />
          <span>Updated: {formattedTime}</span>
        </div>
      </div>
    </div>
  );
};