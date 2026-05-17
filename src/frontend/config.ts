// This file duplicates the config from ../config.json for Metro bundler compatibility

export const config = {
  app: {
    name: 'TFG',
    version: '1.0.0',
    environment: 'development',
  },
  backend: {
    api: {
      host: '172.20.10.2',
      port: 8888,
      url: 'http://172.20.10.2:8888',
      docs_url: 'http://172.20.10.2:8888/docs',
    },
    ws: {
      url: 'ws://172.20.10.2:8888',
    },
  },
};

export const API_BASE_URL = config.backend.api.url;
export const API_DOCS_URL = config.backend.api.docs_url;
