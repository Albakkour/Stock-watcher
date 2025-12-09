import { Stock, Alert, Notification } from './types';

export const mockStocks: Stock[] = [
  { symbol: "TSLA", price: 215.45, updated_at: new Date().toISOString() },
  { symbol: "AAPL", price: 178.32, updated_at: new Date().toISOString() },
  { symbol: "MSFT", price: 325.10, updated_at: new Date().toISOString() },
  { symbol: "NVDA", price: 460.15, updated_at: new Date().toISOString() },
  { symbol: "BTC", price: 42050.00, updated_at: new Date().toISOString() },
  { symbol: "GOOGL", price: 138.20, updated_at: new Date().toISOString() },
  { symbol: "AMZN", price: 129.50, updated_at: new Date().toISOString() },
  { symbol: "META", price: 305.25, updated_at: new Date().toISOString() },
];

export const mockAlerts: Alert[] = [
  { id: 1, symbol: "TSLA", direction: "above", threshold: 220, created_at: new Date().toISOString() },
  { id: 2, symbol: "AAPL", direction: "below", threshold: 170, created_at: new Date().toISOString() },
  { id: 3, symbol: "BTC", direction: "above", threshold: 45000, created_at: new Date().toISOString() }
];

export const mockNotifications: Notification[] = [
  { id: 101, symbol: "NVDA", direction: "above", threshold: 450, price: 455.20, triggered_at: new Date(Date.now() - 1000 * 60 * 15).toISOString() },
  { id: 102, symbol: "BTC", direction: "below", threshold: 43000, price: 42900.00, triggered_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString() },
  { id: 103, symbol: "TSLA", direction: "above", threshold: 200, price: 201.50, triggered_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString() }
];