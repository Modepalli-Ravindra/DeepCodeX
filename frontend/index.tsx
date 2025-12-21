import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Suppress ResizeObserver loop limit exceeded error
if (typeof window !== 'undefined') {
  const resizeObserverError = 'ResizeObserver loop completed with undelivered notifications';
  const resizeObserverLimitError = 'ResizeObserver loop limit exceeded';
  
  window.addEventListener('error', (e) => {
    if (e.message === resizeObserverError || e.message === resizeObserverLimitError) {
      e.stopImmediatePropagation();
      e.preventDefault();
    }
  });

  window.addEventListener('unhandledrejection', (e) => {
    if (e.reason?.message === resizeObserverError || e.reason?.message === resizeObserverLimitError) {
      e.stopImmediatePropagation();
      e.preventDefault();
    }
  });
}

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);