# Code Review Report: Последние два MR

**Дата:** 2025-12-19  
**Коммиты:** 
- `3afaf8a` - Инициализация монорепозитория
- `afb9aa9` - Улучшения JWT и обработки ошибок

---

## 📋 Executive Summary

Общий обзор кода показывает хорошую архитектуру и следование лучшим практикам. Однако найдено несколько критических и важных проблем, требующих исправления перед мержем в production.

**Статистика:**
- ✅ Положительных моментов: 12
- ⚠️ Важных проблем: 8
- 🔴 Критических проблем: 3
- 💡 Рекомендаций: 15

---

## ✅ Положительные моменты

### 1. Архитектура
- ✅ Правильное разделение ответственности: Controller → Service → Repository
- ✅ Использование кастомных классов ошибок для типобезопасности
- ✅ Модульная структура с четким разделением слоев
- ✅ Использование prepared statements для защиты от SQL injection

### 2. Безопасность
- ✅ Валидация JWT_SECRET в production окружении
- ✅ Использование bcrypt для хеширования паролей
- ✅ Нормализация email (lowercase) для предотвращения дубликатов
- ✅ Prepared statements защищают от SQL injection

### 3. Обработка ошибок
- ✅ Кастомные классы ошибок с правильными именами
- ✅ Логирование неожиданных ошибок
- ✅ Правильные HTTP статус коды (400, 401, 409, 500)

### 4. Тестирование
- ✅ Хорошее покрытие unit и integration тестами
- ✅ Тесты следуют паттерну AAA (Arrange-Act-Assert)
- ✅ Тесты проверяют нормализацию email

---

## 🔴 Критические проблемы

### 1. Утечка чувствительных данных в логах

**Файл:** `packages/backend/src/api/auth/controller.ts`

**Проблема:**
```typescript
req.log.error({ err }, 'Unexpected error in register endpoint');
```

При логировании объекта `err` могут попасть чувствительные данные (пароли, токены) из стека ошибок или внутренних свойств.

**Риск:** Высокий - утечка паролей/токенов в логи

**Решение:**
```typescript
req.log.error(
  { 
    error: err.message,
    stack: process.env.NODE_ENV === 'development' ? err.stack : undefined,
    name: err.name
  }, 
  'Unexpected error in register endpoint'
);
```

**Приоритет:** 🔴 Критический

---

### 2. Небезопасная обработка ошибок в JWT verifyToken

**Файл:** `packages/backend/src/utils/jwt.ts:40-50`

**Проблема:**
```typescript
export async function verifyToken(token: string): Promise<JWTPayload> {
  try {
    const { payload } = await jwtVerify(token, secretKey);
    return {
      userId: payload.userId as string,
      email: payload.email as string,
    };
  } catch (error) {
    throw new Error('Invalid token'); // ❌ Теряется информация о типе ошибки
  }
}
```

Все ошибки (expired, invalid signature, malformed) обрабатываются одинаково, что усложняет отладку и может скрывать проблемы безопасности.

**Риск:** Средний - потеря контекста ошибок, сложность отладки

**Решение:**
```typescript
export async function verifyToken(token: string): Promise<JWTPayload> {
  try {
    const { payload } = await jwtVerify(token, secretKey);
    return {
      userId: payload.userId as string,
      email: payload.email as string,
    };
  } catch (error) {
    if (error instanceof JWTExpired) {
      throw new InvalidTokenError('Token expired');
    }
    if (error instanceof JWTInvalid) {
      throw new InvalidTokenError('Invalid token signature');
    }
    throw new InvalidTokenError('Token verification failed');
  }
}
```

**Приоритет:** 🔴 Критический

---

### 3. Race condition в регистрации пользователя

**Файл:** `packages/backend/src/services/auth.service.ts:15-47`

**Проблема:**
```typescript
const existingUser = await this.userRepository.findByEmail(normalizedEmail);
if (existingUser) {
  throw new EmailAlreadyExistsError();
}

try {
  const passwordHash = await bcrypt.hash(password, BCRYPT_ROUNDS);
  const user = await this.userRepository.create(normalizedEmail, passwordHash);
  // ...
} catch (error) {
  if (error instanceof Error && error.message === 'Email already exists') {
    throw new EmailAlreadyExistsError();
  }
  throw error;
}
```

Между проверкой `findByEmail` и `create` есть окно для race condition. Два одновременных запроса могут оба пройти проверку и оба попытаться создать пользователя.

**Риск:** Высокий - возможны дубликаты пользователей при конкурентных запросах

**Решение:** 
- Убрать предварительную проверку `findByEmail` (UNIQUE constraint в БД уже защищает)
- Или использовать транзакции с правильной изоляцией

```typescript
async register(email: string, password: string): Promise<AuthResponse> {
  const normalizedEmail = email.toLowerCase().trim();
  
  // Прямо пытаемся создать - UNIQUE constraint защитит
  try {
    const passwordHash = await bcrypt.hash(password, BCRYPT_ROUNDS);
    const user = await this.userRepository.create(normalizedEmail, passwordHash);
    // ...
  } catch (error) {
    if (error instanceof Error && error.message === 'Email already exists') {
      throw new EmailAlreadyExistsError();
    }
    throw error;
  }
}
```

**Приоритет:** 🔴 Критический

---

## ⚠️ Важные проблемы

### 4. Использование `any` типа в обработке ошибок

**Файл:** `packages/backend/src/api/auth/controller.ts:21, 47`

**Проблема:**
```typescript
if (err instanceof ZodError || (err as any)?.name === 'ZodError') {
```

Использование `any` нарушает правила проекта (`.cursor/rules/backend-development.mdc`):
> "Avoid using `any` - create necessary types instead"

**Решение:**
```typescript
interface ErrorWithName extends Error {
  name: string;
}

function isZodError(err: unknown): err is ZodError {
  return err instanceof ZodError || 
    (err !== null && typeof err === 'object' && 'name' in err && (err as ErrorWithName).name === 'ZodError');
}

// Использование:
if (isZodError(err)) {
  return reply.status(400).send({
    error: 'Validation failed',
    details: err.errors,
  });
}
```

**Приоритет:** ⚠️ Важный

---

### 5. Неполная валидация JWT_SECRET при старте

**Файл:** `packages/backend/src/utils/jwt.ts:7-20`

**Проблема:**
Валидация JWT_SECRET выполняется только при импорте модуля, но не проверяется при каждом использовании. Если переменная окружения изменится во время работы, валидация не сработает.

**Решение:**
Добавить проверку при каждом использовании или использовать валидацию через конфигурационный объект, который инициализируется при старте приложения.

**Приоритет:** ⚠️ Важный

---

### 6. Отсутствие валидации типов в mapRowToUser

**Файл:** `packages/backend/src/repositories/user.repository.ts:36-50`

**Проблема:**
Метод `mapRowToUser` принимает объект с типом, но не валидирует, что данные действительно соответствуют ожидаемому формату. Если БД вернет неожиданные данные, ошибка проявится позже.

**Решение:**
Добавить runtime валидацию с использованием Zod или проверку типов:

```typescript
private mapRowToUser(row: unknown): User {
  if (!row || typeof row !== 'object') {
    throw new Error('Invalid row data');
  }
  const r = row as Record<string, unknown>;
  
  if (!r.id || !r.email || !r.passwordHash || !r.createdAt || !r.updatedAt) {
    throw new Error('Missing required user fields');
  }
  
  return {
    id: String(r.id),
    email: String(r.email),
    passwordHash: String(r.passwordHash),
    createdAt: String(r.createdAt),
    updatedAt: String(r.updatedAt),
  };
}
```

**Приоритет:** ⚠️ Важный

---

### 7. Непоследовательная обработка ошибок БД

**Файл:** `packages/backend/src/repositories/user.repository.ts:52-79, 81-108`

**Проблема:**
В `findByEmail` и `findById` при отсутствии таблицы возвращается `null`, что скрывает проблему конфигурации. Это может привести к тихим ошибкам.

**Решение:**
Бросить специальную ошибку для проблем конфигурации:

```typescript
if (error?.message?.includes('no such table')) {
  throw new Error('Database not initialized. Run migrations first.');
}
```

**Приоритет:** ⚠️ Важный

---

### 8. Отсутствие очистки тестовых данных

**Файл:** `packages/backend/tests/unit/auth.service.test.ts`, `packages/backend/tests/integration/auth.test.ts`

**Проблема:**
Тесты создают пользователей в БД, но не очищают их после выполнения. Это может привести к:
- Загрязнению тестовой БД
- Взаимному влиянию тестов
- Проблемам при параллельном запуске

**Решение:**
Добавить `afterEach` для очистки данных или использовать транзакции с rollback:

```typescript
afterEach(async () => {
  const db = DatabaseManager.getInstance();
  db.prepare('DELETE FROM users').run();
});
```

**Приоритет:** ⚠️ Важный

---

### 9. Магическое число в тестах

**Файл:** `packages/backend/tests/integration/auth.test.ts:54`

**Проблема:**
```typescript
expect(body.user.email).toBe(email);
```

Тест ожидает, что email будет в том же регистре, что и входные данные, но сервис нормализует email в lowercase. Тест должен проверять `email.toLowerCase()`.

**Решение:**
```typescript
expect(body.user.email).toBe(email.toLowerCase());
```

**Приоритет:** ⚠️ Важный

---

### 10. Отсутствие JSDoc документации

**Файл:** Все публичные методы в сервисах и контроллерах

**Проблема:**
Согласно правилам проекта:
> "Use JSDoc to document public classes and methods"

Отсутствует документация для публичных методов.

**Решение:**
Добавить JSDoc комментарии:

```typescript
/**
 * Registers a new user with email and password
 * @param email - User email address (will be normalized to lowercase)
 * @param password - User password (min 8 characters)
 * @returns Authentication response with JWT token and user data
 * @throws {EmailAlreadyExistsError} If email is already registered
 * @throws {Error} For other registration failures
 */
async register(email: string, password: string): Promise<AuthResponse> {
  // ...
}
```

**Приоритет:** ⚠️ Важный

---

## 💡 Рекомендации по улучшению

### 11. Константы вместо магических значений

**Файл:** `packages/backend/src/utils/jwt.ts:4-5`

```typescript
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret';
const JWT_EXPIRY = process.env.JWT_EXPIRY || '7d';
```

Рекомендация: Вынести дефолтные значения в константы:

```typescript
const DEFAULT_JWT_SECRET = 'dev-secret';
const DEFAULT_JWT_EXPIRY = '7d';
```

---

### 12. Улучшение обработки ошибок в refresh endpoint

**Файл:** `packages/backend/src/api/auth/controller.ts:66-88`

Рекомендация: Добавить валидацию схемы для `refreshToken`:

```typescript
const refreshTokenSchema = z.object({
  refreshToken: z.string().min(1, 'refreshToken is required'),
});

async refresh(req: FastifyRequest, reply: FastifyReply) {
  try {
    const validated = refreshTokenSchema.parse(req.body || {});
    const result = await this.service.refresh(validated.refreshToken);
    return reply.status(200).send(result);
  } catch (err) {
    // ...
  }
}
```

---

### 13. Типизация ошибок в catch блоках

**Файл:** `packages/backend/src/repositories/user.repository.ts:26, 72, 101`

Рекомендация: Использовать более строгую типизацию вместо `any`:

```typescript
catch (error: unknown) {
  if (error instanceof Error) {
    // Handle Error
  }
  // Handle unknown error type
}
```

---

### 14. Добавление rate limiting

**Файл:** `packages/backend/src/api/auth/routes.ts`

Рекомендация: Добавить rate limiting для защиты от brute force атак на `/login` и `/register` endpoints согласно API спецификации (100 req/hour для unauthenticated).

---

### 15. Улучшение тестов для edge cases

**Рекомендация:** Добавить тесты для:
- Очень длинных email адресов
- Email с пробелами (должны обрезаться)
- Специальных символов в email
- Одновременных запросов на регистрацию (race condition)

---

### 16. Использование транзакций для атомарности

**Файл:** `packages/backend/src/repositories/user.repository.ts`

Рекомендация: Для операций, которые должны быть атомарными, использовать транзакции:

```typescript
async create(email: string, passwordHash: string): Promise<User> {
  return this.db.transaction(() => {
    // Create user logic
  })();
}
```

---

### 17. Добавление индексов в БД

**Рекомендация:** Убедиться, что в миграциях есть индексы на `email` (уже есть UNIQUE constraint) и `user_id` для будущих таблиц workout_logs.

---

### 18. Улучшение сообщений об ошибках

**Файл:** `packages/backend/src/utils/jwt.ts:48`

Рекомендация: Более информативные сообщения об ошибках для разработки:

```typescript
catch (error) {
  const message = process.env.NODE_ENV === 'development' 
    ? `Token verification failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    : 'Invalid token';
  throw new InvalidTokenError(message);
}
```

---

### 19. Валидация входных данных в сервисе

**Файл:** `packages/backend/src/services/auth.service.ts:49`

Рекомендация: Убрать неиспользуемую валидацию:

```typescript
async login(email: string, password: string): Promise<AuthResponse> {
  // loginSchema.parse уже вызывается в контроллере
  // Убрать дублирующую валидацию если она есть
```

---

### 20. Добавление метрик и мониторинга

**Рекомендация:** Добавить логирование успешных операций для мониторинга:

```typescript
req.log.info({ userId: result.user.id }, 'User registered successfully');
```

---

## 📊 Соответствие правилам проекта

### ✅ Соответствует:
- Использование TypeScript с типами
- Модульная архитектура
- Prepared statements для БД
- Кастомные классы ошибок
- Правильные HTTP статус коды

### ❌ Не соответствует:
- Использование `any` типа (нарушает правило "Avoid using `any`")
- Отсутствие JSDoc документации (нарушает правило "Use JSDoc to document public classes and methods")
- Некоторые функции длиннее 20 инструкций (нарушает правило "Write short functions with a single purpose")

---

## 🎯 Приоритеты исправлений

### Немедленно (перед мержем):
1. 🔴 Утечка чувствительных данных в логах (#1)
2. 🔴 Race condition в регистрации (#3)
3. 🔴 Небезопасная обработка ошибок JWT (#2)

### В ближайшее время:
4. ⚠️ Использование `any` типа (#4)
5. ⚠️ Отсутствие очистки тестовых данных (#8)
6. ⚠️ Непоследовательная обработка ошибок БД (#7)

### Желательно:
7. 💡 JSDoc документация (#10)
8. 💡 Rate limiting (#14)
9. 💡 Улучшение тестов (#15)

---

## 📝 Заключение

Код демонстрирует хорошее понимание архитектуры и лучших практик. Основные проблемы связаны с безопасностью и обработкой ошибок. После исправления критических проблем код будет готов к production.

**Общая оценка:** 7.5/10

**Рекомендация:** Исправить критические проблемы перед мержем, остальные можно исправить в следующих итерациях.

