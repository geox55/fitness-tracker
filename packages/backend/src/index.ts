import Fastify from 'fastify';
import cors from '@fastify/cors';

const app = Fastify({ logger: true });

// CORS
await app.register(cors, {
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true,
});

// Health check
app.get('/api/health', async () => {
  return { status: 'ok' };
});

// Register routes
import authRoutes from './api/auth/routes.js';
import workoutRoutes from './api/workouts/routes.js';
import exerciseRoutes from './api/exercises/routes.js';
import workoutSessionRoutes from './api/workout-sessions/routes.js';
import supersetRoutes from './api/supersets/routes.js';
await app.register(authRoutes, { prefix: '/api/auth' });
await app.register(workoutRoutes, { prefix: '/api/workouts' });
await app.register(exerciseRoutes, { prefix: '/api/exercises' });
await app.register(workoutSessionRoutes, { prefix: '/api/workout-sessions' });
await app.register(supersetRoutes, { prefix: '/api/workout-sessions' });

const PORT = Number(process.env.PORT) || 4000;
const HOST = process.env.HOST || '0.0.0.0';

try {
  await app.listen({ port: PORT, host: HOST });
  console.log(`🚀 Server running on http://${HOST}:${PORT}`);
} catch (err) {
  app.log.error(err);
  process.exit(1);
}

