import React from 'react';
import { Notification } from '../types';
import { BellRing, ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface NotificationLogProps {
  notifications: Notification[];
}

export const NotificationLog: React.FC<NotificationLogProps> = ({ notifications }) => {
  return (
    <div className="card">
      <div className="section-title" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
        <div className="flex items-center gap-2">
          <BellRing className="text-primary" size={20} />
          <h2 style={{ fontSize: '1.1rem' }}>Alert History</h2>
        </div>
      </div>

      <div style={{ maxHeight: '400px', overflowY: 'auto', paddingRight: '0.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {notifications.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
            No alerts have been triggered yet.
          </div>
        ) : (
          notifications.map((n) => {
             const time = new Date(n.triggered_at).toLocaleTimeString();
             const isAbove = n.direction === 'above';
             
             return (
              <div key={n.id} style={{ 
                display: 'flex', 
                flexDirection: 'row', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '1rem', 
                backgroundColor: 'var(--bg-card)', 
                borderLeft: '4px solid var(--primary)',
                borderTop: '1px solid var(--border)',
                borderRight: '1px solid var(--border)',
                borderBottom: '1px solid var(--border)',
                borderRadius: '8px'
              }}>
                <div className="flex items-center gap-2">
                  <div style={{ 
                    padding: '0.5rem', 
                    borderRadius: '50%', 
                    backgroundColor: isAbove ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    color: isAbove ? '#22c55e' : '#ef4444',
                    display: 'flex'
                  }}>
                    {isAbove ? <ArrowUpRight size={18} /> : <ArrowDownRight size={18} />}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{n.symbol}</span>
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>crossed {n.direction}</span>
                      <span className="font-mono" style={{ fontWeight: 'bold' }}>${n.threshold}</span>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                      Trigger Price: <span className="font-mono text-primary">${n.price}</span>
                    </div>
                  </div>
                </div>
                <div className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', backgroundColor: 'rgba(0,0,0,0.3)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                  {time}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};