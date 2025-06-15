/// <reference types="vite/client" />

// Environment variables for Vite (import.meta.env)
interface ImportMetaEnv {
  // App
  readonly VITE_APP_NAME: string;
  readonly VITE_APP_VERSION: string;
  readonly VITE_APP_ENV: 'development' | 'staging' | 'production';
  
  // API
  readonly VITE_API_URL: string;
  
  // Authentication
  readonly VITE_AUTH0_DOMAIN?: string;
  readonly VITE_AUTH0_CLIENT_ID?: string;
  readonly VITE_AUTH0_AUDIENCE?: string;
  readonly VITE_AUTH0_CALLBACK_URL?: string;
  
  // Feature Flags
  readonly VITE_ENABLE_ANALYTICS: 'true' | 'false';
  readonly VITE_ENABLE_DEBUG_TOOLS: 'true' | 'false';
  
  // Third-party services
  readonly VITE_MAPBOX_ACCESS_TOKEN?: string;
  readonly VITE_SENTRY_DSN?: string;
  readonly VITE_GA_TRACKING_ID?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// Global type declarations
declare namespace NodeJS {
  // Extend ProcessEnv with our environment variables
  interface ProcessEnv extends NodeJS.ProcessEnv, ImportMetaEnv {}
}

// Add type support for SVG imports
declare module '*.svg' {
  import * as React from 'react';
  export const ReactComponent: React.FunctionComponent<React.SVGProps<SVGSVGElement>>;
  const src: string;
  export default src;
}

// Add type support for CSS Modules
declare module '*.module.css' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

declare module '*.module.scss' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

// Add type support for image imports
declare module '*.png';
declare module '*.jpg';
declare module '*.jpeg';
declare module '*.gif';
declare module '*.webp';
declare module '*.avif';

// Add type support for JSON imports
declare module '*.json' {
  const value: Record<string, unknown>;
  export default value;
}
