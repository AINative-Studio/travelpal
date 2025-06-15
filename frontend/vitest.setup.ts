// Import testing library matchers
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock window.ResizeObserver
class ResizeObserverStub {
  observe() { }
  unobserve() { }
  disconnect() { }
}

window.ResizeObserver = window.ResizeObserver || ResizeObserverStub;

// Mock window.scrollTo
window.scrollTo = vi.fn() as (options?: ScrollToOptions | undefined) => void;

// Mock IntersectionObserver
class IntersectionObserverStub {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
}

window.IntersectionObserver = IntersectionObserverStub as unknown as typeof IntersectionObserver;

// Cleanup after each test case (e.g., clearing jsdom)
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

// Mock next/router
vi.mock('next/router', () => ({
  useRouter: () => ({
    route: '/',
    pathname: '',
    query: {},
    asPath: '',
    push: vi.fn(),
    replace: vi.fn(),
    reload: vi.fn(),
    back: vi.fn(),
    prefetch: vi.fn(),
    beforePopState: vi.fn(),
    events: {
      on: vi.fn(),
      off: vi.fn(),
      emit: vi.fn(),
    },
  }),
}));

// Mock console methods
const consoleError = console.error;
const consoleWarn = console.warn;

beforeAll(() => {
  // Mock console.error to catch and fail tests on React errors
  console.error = (message, ...args) => {
    // Ignore ReactDOM.render deprecation warnings
    if (typeof message === 'string' && message.includes('ReactDOM.render')) {
      return;
    }
    consoleError(message, ...args);
    throw message instanceof Error ? message : new Error(String(message));
  };

  // Mock console.warn to catch and fail tests on warnings
  console.warn = (message, ...args) => {
    // Ignore React 18 hydration warnings in tests
    if (typeof message === 'string' && message.includes('Hydration')) {
      return;
    }
    consoleWarn(message, ...args);
  };
});

afterAll(() => {
  // Restore original console methods
  console.error = consoleError;
  console.warn = consoleWarn;
});
