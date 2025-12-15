import React from 'react';
import { BellPlus } from 'lucide-react';

interface AlertFormProps {
  symbol: string;
  setSymbol: (val: string) => void;
  direction: string;
  setDirection: (val: string) => void;
  threshold: number | string;
  setThreshold: (val: number | string) => void;
  onSubmit: (e: React.FormEvent) => void;
}

export const AlertForm: React.FC<AlertFormProps> = ({
  symbol,
  setSymbol,
  direction,
  setDirection,
  threshold,
  setThreshold,
  onSubmit
}) => {
  return (
    <div className="card" style={{ height: '100%' }}>
      <div className="section-title" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '1rem' }}>
        <div className="flex items-center gap-2">
          <BellPlus className="text-primary" size={20} />
          <h2 style={{ fontSize: '1.1rem' }}>New Watch Alert</h2>
        </div>
      </div>

      <form onSubmit={onSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: '500' }}>Stock Symbol</label>
          <input
            type="text"
            className="input-field"
            placeholder="e.g. TSLA"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            required
            style={{ textTransform: 'uppercase', fontFamily: 'monospace' }}
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: '500' }}>Condition</label>
            <select
              value={direction}
              onChange={(e) => setDirection(e.target.value)}
              className="input-field"
              style={{ cursor: 'pointer' }}
            >
              <option value="above">Above</option>
              <option value="below">Below</option>
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: '500' }}>Price Target ($)</label>
            <input
              type="number"
              className="input-field"
              placeholder="200.00"
              value={threshold}
              onChange={(e) => setThreshold(e.target.value)}
              required
              style={{ fontFamily: 'monospace' }}
            />
          </div>
        </div>

        <button type="submit" className="btn-primary" style={{ marginTop: '0.5rem' }}>
          Set Alert
        </button>
      </form>
    </div>
  );
};