// This file duplicates the config from ../config.json for Metro bundler compatibility

export const config = {
  app: {
    name: 'TFG',
    version: '1.0.0',
    environment: 'development',
  },
  backend: {
    api: {
      host: '127.0.0.1',
      port: 8888,
      url: 'http://localhost:8888',
      docs_url: 'http://localhost:8888/docs',
    },
  },
};

export const API_BASE_URL = config.backend.api.url;
export const API_DOCS_URL = config.backend.api.docs_url;
