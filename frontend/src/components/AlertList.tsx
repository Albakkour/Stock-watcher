import React from 'react';
import { Alert } from '../types';
import { Activity } from 'lucide-react';

interface AlertListProps {
  alerts: Alert[];
}

export const AlertList: React.FC<AlertListProps> = ({ alerts }) => {
  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div className="section-title" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '1rem', marginBottom: '1rem' }}>
        <div className="flex items-center gap-2">
          <Activity className="text-primary" size={20} />
          <h2 style={{ fontSize: '1.1rem' }}>Active Monitors</h2>
        </div>
        <span style={{ backgroundColor: 'var(--bg-input)', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem' }}>
          {alerts.length}
        </span>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.5rem' }}>
        {alerts.length === 0 ? (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontStyle: 'italic' }}>
            <p>No active alerts configured.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {alerts.map((alert, idx) => (
              <div key={idx} style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between', 
                padding: '0.75rem', 
                backgroundColor: 'rgba(255,255,255,0.03)', 
                borderRadius: '8px',
                border: '1px solid var(--border)'
              }}>
                <div className="flex items-center gap-2">
                  <span style={{ fontWeight: 'bold', minWidth: '3rem' }}>{alert.symbol}</span>
                  <span style={{ 
                    fontSize: '0.7rem', 
                    padding: '0.1rem 0.4rem', 
                    borderRadius: '4px',
                    backgroundColor: alert.direction === 'above' ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                    color: alert.direction === 'above' ? '#4ade80' : '#f87171',
                    textTransform: 'uppercase'
                  }}>
                    {alert.direction}
                  </span>
                </div>
                <span className="font-mono" style={{ color: 'var(--text-main)' }}>
                  ${Number(alert.threshold).toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};