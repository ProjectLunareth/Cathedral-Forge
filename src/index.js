import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

/**
 * The main entry point for the React application.
 * 1. It finds the root DOM element with the ID 'root'.
 * 2. It creates a React root to manage rendering inside that element.
 * 3. It renders the main App component, wrapped in StrictMode for development checks.
 */
const rootElement = document.getElementById('root');
const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
