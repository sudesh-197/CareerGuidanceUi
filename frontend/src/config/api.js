/**
 * Single source of truth for the backend address.
 * Override with REACT_APP_API_URL in frontend/.env (no trailing slash needed).
 */
export const API_BASE_URL = (process.env.REACT_APP_API_URL || 'http://localhost:5000').replace(/\/+$/, '');
