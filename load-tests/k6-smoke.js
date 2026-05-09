import http from 'k6/http';
import { check, sleep } from 'k6';

const baseUrl = __ENV.K6_BASE_URL || 'http://flask-app-service.default.svc.cluster.local';
const vus = Number(__ENV.K6_VUS || 5);
const duration = __ENV.K6_DURATION || '15s';

export const options = {
  vus,
  duration,
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500'],
  },
  summaryTrendStats: ['avg', 'min', 'med', 'p(90)', 'p(95)'],
};

export default function () {
  const homeResponse = http.get(`${baseUrl}/`);
  check(homeResponse, {
    'home endpoint returns 200': (response) => response.status === 200,
    'home page has deployment heading': (response) => response.body.includes('Welcome to My CI/CD Deployed Application!'),
  });

  const healthResponse = http.get(`${baseUrl}/health`);
  check(healthResponse, {
    'health endpoint returns 200': (response) => response.status === 200,
    'health endpoint reports ok': (response) => response.json('status') === 'ok',
  });

  sleep(1);
}
