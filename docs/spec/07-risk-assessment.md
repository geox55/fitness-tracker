# RISK ASSESSMENT & MITIGATION

## Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **SQLite concurrency limit** | HIGH | HIGH | WAL mode, connection pooling, queue for writes |
| **Chart rendering slow** | MEDIUM | MEDIUM | Virtual scroll, reduce data points, client aggregation |
| **Offline sync conflicts** | MEDIUM | MEDIUM | Last-write-wins, timestamp reconciliation |
| **Database size growth** | MEDIUM | MEDIUM | Archival strategy, partition old data |
| **API rate limiting issues** | MEDIUM | LOW | Backoff strategy, client queue, rate limit headers |
| **Mobile browser compatibility** | LOW | MEDIUM | Test iOS Safari, Android Chrome, PWA caching |
| **Data export latency** | MEDIUM | LOW | Stream response, background job |
| **JWT token expiration UX** | MEDIUM | MEDIUM | Auto-refresh with refresh token |

---

## Testing Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **Tests not matching reality** | HIGH | HIGH | Write tests AFTER architecture, BEFORE code |
| **Tests become outdated** | MEDIUM | MEDIUM | Maintain tests as living document |
| **Offline test coverage gaps** | MEDIUM | HIGH | Dedicated offline test suite |
| **API contract neglect** | MEDIUM | MEDIUM | OpenAPI spec first, generate client |
| **Database state pollution** | MEDIUM | MEDIUM | Test fixtures, DB reset between tests |

---

## Performance Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **N+1 queries** | MEDIUM | HIGH | JOIN queries, eager loading |
| **Memory leak in React** | LOW | HIGH | React DevTools, memory leak tests |
| **Large file export timeout** | MEDIUM | MEDIUM | Stream CSV, async export |
| **Bundle size bloat** | MEDIUM | MEDIUM | Tree-shaking, code splitting |
| **Chart for large data** | MEDIUM | MEDIUM | Limit to 6 months, aggregate points |

---

## Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **Low user adoption** | MEDIUM | HIGH | Focus UX, fast onboarding, viral features |
| **Competitor advantage** | HIGH | HIGH | Differentiate: API-first, open source |
| **Data privacy concerns** | MEDIUM | HIGH | Clear privacy policy, self-hosted option |
| **API abuse** | MEDIUM | MEDIUM | Rate limiting, API keys, monitoring |

---

## Mitigation Strategies

### SQLite Concurrency

```typescript
// WAL mode для better concurrency
db.pragma('journal_mode = WAL');
db.pragma('busy_timeout = 5000');

// Connection pooling (если нужно)
const pool = new DatabasePool({
  filename: process.env.DATABASE_PATH,
  maxConnections: 5
});
```

### Offline Sync Conflicts

```typescript
// Last-write-wins с timestamp
interface SyncableLog {
  id: string;
  localUpdatedAt: string;  // Client timestamp
  serverUpdatedAt?: string; // Server timestamp
}

const resolveConflict = (local: SyncableLog, server: SyncableLog) => {
  // Server wins if newer
  if (server.serverUpdatedAt > local.localUpdatedAt) {
    return server;
  }
  return local;
};
```

### Chart Performance

```typescript
// Агрегация данных для больших периодов
const aggregateForChart = (logs: WorkoutLog[], period: 'day' | 'week' | 'month') => {
  const grouped = groupBy(logs, log => {
    const date = new Date(log.date);
    if (period === 'week') return getWeekStart(date);
    if (period === 'month') return getMonthStart(date);
    return log.date.split('T')[0];
  });
  
  return Object.entries(grouped).map(([date, logs]) => ({
    date,
    maxWeight: Math.max(...logs.map(l => l.weight)),
    avgWeight: average(logs.map(l => l.weight))
  }));
};
```

### Rate Limiting

```typescript
// Fastify plugin
import rateLimit from '@fastify/rate-limit';

await app.register(rateLimit, {
  max: 1000, // requests
  timeWindow: '1 hour',
  errorResponseBuilder: (request, context) => ({
    error: 'Too many requests, please try again later',
    retryAfter: context.ttl
  })
});

// Apply to specific routes
await app.register(rateLimit, {
  max: 100,
  timeWindow: '1 minute'
}, { prefix: '/api/auth' });
```

### Bundle Size

```typescript
// Dynamic imports для тяжёлых компонентов
const ProgressChart = dynamic(
  () => import('@/features/progress-analytics/ui/ProgressChart'),
  { 
    loading: () => <ChartSkeleton />,
    ssr: false // Recharts не нужен на сервере
  }
);
```

---

## Monitoring & Alerts

### Key Metrics to Monitor

| Metric | Threshold | Alert |
|--------|-----------|-------|
| API Response Time (p95) | > 500ms | Warning |
| API Response Time (p99) | > 1000ms | Critical |
| Error Rate | > 1% | Warning |
| Error Rate | > 5% | Critical |
| Database Query Time | > 200ms | Warning |
| Memory Usage | > 80% | Warning |

### Implementation

```typescript
// Simple metrics logging (Fastify hook)
app.addHook('onRequest', async (request, reply) => {
  request.startTime = Date.now();
});

app.addHook('onResponse', async (request, reply) => {
  const duration = Date.now() - request.startTime;
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    method: request.method,
    path: request.url,
    statusCode: reply.statusCode,
    duration,
    userId: request.user?.id
  }));
});
```

---

## Contingency Plans

### Database Corruption

1. Stop application
2. Check database integrity: `PRAGMA integrity_check`
3. Restore from backup
4. Replay WAL if possible

### API Outage

1. Enable maintenance mode
2. Check logs for root cause
3. Rollback if deployment issue
4. Communicate to users

### Data Breach

1. Immediately revoke all JWT tokens
2. Force password reset
3. Investigate and document
4. Notify affected users

