# API SPECIFICATION

## Base URL

- **Development:** `http://localhost:4000/api`
- **Production:** `https://api.fitness-tracker.com/api`

---

## Authentication

Все защищённые эндпоинты требуют JWT токен в заголовке:

```
Authorization: Bearer <token>
```

---

## Endpoints

### Auth

#### POST /api/auth/register

Регистрация нового пользователя.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepass123",
  "passwordConfirm": "securepass123"
}
```

**Response (201):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid",
    "email": "user@example.com"
  }
}
```

**Errors:**
- `400` — Invalid email/password format
- `409` — Email already exists

---

#### POST /api/auth/login

Аутентификация пользователя.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid",
    "email": "user@example.com"
  }
}
```

**Errors:**
- `400` — Missing fields
- `401` — Invalid credentials

---

#### POST /api/auth/refresh

Обновление JWT токена.

**Request:**
```json
{
  "refreshToken": "refresh-token-value"
}
```

**Response (200):**
```json
{
  "token": "new-jwt-token"
}
```

---

### Workouts

#### GET /api/workouts

Получение списка тренировок пользователя.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `exerciseId` | string | Filter by exercise |
| `from` | string (ISO date) | Start date |
| `to` | string (ISO date) | End date |
| `limit` | number | Max results (default: 100, max: 1000) |
| `offset` | number | Pagination offset |

**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "exerciseId": "uuid",
      "exerciseName": "Squat",
      "weight": 100,
      "reps": 5,
      "sets": 3,
      "rpe": 8,
      "date": "2024-12-20T10:30:00Z",
      "createdAt": "2024-12-20T10:35:00Z"
    }
  ],
  "total": 150,
  "hasMore": true
}
```

---

#### POST /api/workouts

Создание записи о тренировке.

**Request:**
```json
{
  "exerciseId": "uuid",
  "weight": 100,
  "reps": 5,
  "sets": 3,
  "rpe": 8,
  "notes": "Felt strong today"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "exerciseId": "uuid",
  "weight": 100,
  "reps": 5,
  "sets": 3,
  "rpe": 8,
  "date": "2024-12-20T10:30:00Z",
  "createdAt": "2024-12-20T10:35:00Z"
}
```

**Validation Errors (400):**
```json
{
  "error": "Validation failed",
  "details": [
    { "field": "weight", "message": "Weight must be positive" },
    { "field": "reps", "message": "Reps must be between 1 and 100" }
  ]
}
```

---

#### PATCH /api/workouts/:id

Обновление записи о тренировке.

**Request:**
```json
{
  "weight": 105,
  "notes": "Updated"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "weight": 105,
  "notes": "Updated",
  ...
}
```

**Errors:**
- `404` — Workout not found
- `403` — Not owner

---

#### DELETE /api/workouts/:id

Удаление записи о тренировке.

**Response (200):**
```json
{
  "success": true
}
```

---

### Exercises

#### GET /api/exercises

Поиск упражнений.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Search by name |
| `muscleGroup` | string | Filter by muscle group |

**Response (200):**
```json
[
  {
    "id": "uuid",
    "name": "Squat",
    "muscleGroup": "legs",
    "category": "compound"
  },
  {
    "id": "uuid",
    "name": "Leg Press",
    "muscleGroup": "legs",
    "category": "compound"
  }
]
```

---

### Analytics

#### GET /api/analytics/progress

Получение данных прогресса для графика.

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `exerciseId` | string | Yes | Exercise to analyze |
| `from` | string | No | Start date |
| `to` | string | No | End date |
| `granularity` | string | No | `day`, `week`, `month` |

**Response (200):**
```json
{
  "data": [
    {
      "date": "2024-12-01",
      "maxWeight": 100,
      "avgWeight": 95,
      "totalVolume": 1500,
      "workoutCount": 2
    },
    {
      "date": "2024-12-05",
      "maxWeight": 105,
      "avgWeight": 100,
      "totalVolume": 1575,
      "workoutCount": 1
    }
  ],
  "stats": {
    "personalRecord": {
      "weight": 110,
      "date": "2024-12-10"
    },
    "maxWeight": 110,
    "avgWeight": 98,
    "totalWorkouts": 15
  }
}
```

---

#### GET /api/analytics/export

Экспорт данных в CSV/JSON.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `format` | string | `csv` or `json` |
| `from` | string | Start date |
| `to` | string | End date |
| `exerciseId` | string | Filter by exercise |

**Response (200):**
- For `csv`: File download with `Content-Type: text/csv`
- For `json`: Array of workout logs

---

### Templates

#### GET /api/templates

Список шаблонов пользователя.

**Response (200):**
```json
[
  {
    "id": "uuid",
    "name": "PPL Upper",
    "exercises": [
      { "exerciseId": "uuid", "sets": 3, "reps": 5 },
      { "exerciseId": "uuid", "sets": 3, "reps": 8 }
    ]
  }
]
```

---

#### POST /api/templates

Создание шаблона.

**Request:**
```json
{
  "name": "Leg Day",
  "exercises": [
    { "exerciseId": "uuid", "sets": 5, "reps": 5 },
    { "exerciseId": "uuid", "sets": 3, "reps": 10 }
  ]
}
```

---

### Health

#### GET /api/health

Проверка здоровья сервиса.

**Response (200):**
```json
{
  "status": "ok",
  "timestamp": "2024-12-20T10:00:00Z"
}
```

---

## Error Responses

Все ошибки возвращают JSON в формате:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {} // optional
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `201` | Created |
| `400` | Bad Request (validation) |
| `401` | Unauthorized |
| `403` | Forbidden |
| `404` | Not Found |
| `429` | Rate Limit Exceeded |
| `500` | Internal Server Error |

---

## Rate Limiting

- **Authenticated:** 1000 requests/hour
- **Unauthenticated:** 100 requests/hour

Headers в response:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1703073600
```

---

## OpenAPI Schema

```yaml
openapi: 3.0.0
info:
  title: Fitness Tracker API
  version: 1.0.0

components:
  schemas:
    WorkoutLog:
      type: object
      properties:
        id:
          type: string
        exerciseId:
          type: string
        weight:
          type: number
        reps:
          type: integer
        sets:
          type: integer
        date:
          type: string
          format: date-time
        rpe:
          type: number
          nullable: true
      required:
        - id
        - exerciseId
        - weight
        - reps
        - date

    WorkoutInput:
      type: object
      properties:
        exerciseId:
          type: string
        weight:
          type: number
        reps:
          type: integer
        sets:
          type: integer
        rpe:
          type: number
          nullable: true
      required:
        - exerciseId
        - weight
        - reps

    Exercise:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        muscleGroup:
          type: string
        category:
          type: string

    ProgressStats:
      type: object
      properties:
        maxWeight:
          type: number
        avgWeight:
          type: number
        personalRecord:
          type: number
        workoutCount:
          type: integer
```

