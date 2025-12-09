export interface Stock {
  symbol: string;
  price: number;
  updated_at: string;
}

export interface Alert {
  id: number;
  symbol: string;
  direction: 'above' | 'below';
  threshold: number;
  created_at?: string;
}

export interface Notification {
  id: number;
  symbol: string;
  direction: 'above' | 'below';
  threshold: number;
  price: number;
  triggered_at: string;
}

export interface APIResponse<T> {
  stocks?: T;
  alerts?: T;
  notifications?: T;
}