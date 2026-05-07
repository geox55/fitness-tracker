# Specification: Парсинг PDF InBody-отчёта

**Epic:** E6 — Интеграции
**User Story:** Пользователь должен иметь возможность загрузить PDF, выданный InBody-аппаратом, и приложение само извлечёт ключевые показатели в структурированный замер.
**Related specs:** [003-inbody-measurements.md](003-inbody-measurements.md)

---

## 1. User Goal

Печатать или вводить данные с PDF вручную — это трение. Пользователь хочет «прикрепить файл и забыть»: приложение распарсит, покажет распознанные значения, даст подтвердить или поправить — и сохранит как обычный замер.

---

## 2. Context

InBody-аппараты (модели 270, 370, 570, 770, 970, S10, и т.д.) выдают PDF с относительно стабильной разметкой. Поля, которые нас интересуют (соответствуют ТЗ):
weight_kg, height_cm, sex (на самом PDF может не быть, но обычно есть), muscle_mass_kg, body_fat_percent, body_water_percent, protein_kg, minerals_kg, visceral_fat_level, bmr_kcal, fat_free_mass_kg, bmi.

Парсер не обязан поддерживать все модели — достаточно покрытия 1-2 самых распространённых форматов; для остальных пользователь получит частичный результат и докрутит вручную (см. [003](003-inbody-measurements.md)).

Подход: layout-парсинг через `pdfplumber` или `pymupdf` + регулярки на ключевые слова и числа. ML-распознавание (OCR) — out of scope MVP (PDF от InBody обычно текстовые, не сканированные).

---

## 3. User Scenarios

### Scenario 1 — Успешный парсинг PDF от поддерживаемой модели

**How to test independently**: Загрузить тестовый PDF (InBody 770, образец), проверить что job вернул `status: ready` со всеми полями.

**Acceptance criteria**:

1. **Given** валидный PDF от InBody 270/370/570/770/970/S10 (с текстовым слоем).
   **When** пользователь его загружает (см. [003](003-inbody-measurements.md), Scenario 2).
   **Then** парсер извлекает все обязательные поля (weight_kg, body_fat_percent) и опциональные (если присутствуют), возвращает `status: ready, extracted: {...}, missing_fields: [...]`.

2. **Given** парсер опознал шаблон.
   **When** возвращает результат.
   **Then** также возвращает `template: "inbody_770"` для отладки и аналитики покрытия.

### Scenario 2 — PDF от поддерживаемой модели с пропущенными опциональными полями

**Acceptance criteria**:

1. **Given** PDF, в котором нет visceral_fat_level и protein_kg.
   **When** парсер прошёл.
   **Then** missing_fields = ["visceral_fat_level", "protein_kg"], extracted содержит остальное; пользователь увидит экран превью с пустыми полями.

### Scenario 3 — PDF от неопознанного шаблона

**Acceptance criteria**:

1. **Given** PDF, который не подходит ни под один шаблон.
   **When** парсер пытается извлечь.
   **Then** возвращается `status: partial` с теми полями, которые удалось вытащить через generic regex (хотя бы вес и % жира), либо `status: failed` если ничего не нашлось.

2. **Given** `status: failed`.
   **When** пользователь видит результат.
   **Then** показывается сообщение «Не удалось распознать. Введите вручную?» с CTA на ручной ввод (см. [003](003-inbody-measurements.md)).

### Scenario 4 — PDF не InBody (произвольный документ)

**Acceptance criteria**:

1. **Given** пользователь загрузил, например, счёт за электричество.
   **When** парсер не находит характерных маркеров («InBody», «Body Composition Analysis», «PBF», ...).
   **Then** возвращается `status: not_inbody`; пользователь видит ошибку «Это не похоже на InBody-отчёт».

### Scenario 5 — Зашифрованный или OCR-only PDF

**Acceptance criteria**:

1. **Given** PDF защищён паролем.
   **When** парсер пытается открыть.
   **Then** возвращается `status: encrypted`; ошибка «Файл защищён паролем».

2. **Given** PDF — это скан без текстового слоя.
   **When** парсер не находит текста.
   **Then** возвращается `status: scanned_unsupported`; ошибка «Сканированный файл не поддерживается, введите вручную». OCR — out of scope.

### Scenario 6 — Хранение оригинала

**Acceptance criteria**:

1. **Given** успешный парсинг.
   **When** пользователь подтверждает сохранение.
   **Then** оригинальный файл сохраняется в object storage; путь записывается в `original_pdf_url`. Доступ через signed URL (TTL 5 мин), см. [003](003-inbody-measurements.md).

2. **Given** пользователь отменил подтверждение.
   **When** проходит TTL временного хранилища (1 час).
   **Then** файл и job удаляются.

---

## 4. Functional Requirements

| #      | Requirement                                                                                                |
|--------|------------------------------------------------------------------------------------------------------------|
| REQ-01 | Поддержка асинхронного flow: upload → job_id → poll/get result                                              |
| REQ-02 | Поддержка минимум 2 шаблонов InBody (например, 770 и 270)                                                   |
| REQ-03 | Generic-fallback регулярки на ключевые поля (weight, %fat) для неизвестных шаблонов                         |
| REQ-04 | Возврат extracted-полей с указанием уверенности (высокая = из шаблона, средняя = из generic)                |
| REQ-05 | Пометка missing_fields для полей, которых не нашлось                                                        |
| REQ-06 | Опознание не-InBody документов и зашифрованных PDF                                                          |
| REQ-07 | Хранение оригинального PDF в object storage только после подтверждения пользователем                        |
| REQ-08 | Очистка временных загрузок без подтверждения через 1 час                                                    |
| REQ-09 | Логирование статистики: какой шаблон распознан / какие поля пропущены, для итеративного улучшения парсера |
| REQ-10 | Лимит размера файла: 10 MB                                                                                  |
| REQ-11 | Аудит: пользователь видит, что именно распознано (highlight на превью PDF — опц., в фазе 2)                 |

---

## 5. Non-functional Requirements

| #      | Requirement                                                                | Category    |
|--------|----------------------------------------------------------------------------|-------------|
| NFR-01 | Парсинг ≤5 секунд на 95-перцентиле для PDF ≤2 MB                           | Performance |
| NFR-02 | Парсер работает в изолированном sandbox (защита от malicious PDF)          | Security    |
| NFR-03 | Никогда не блокирует основной API (асинхронный воркер)                     | Architecture |
| NFR-04 | Все загруженные PDF шифруются at-rest                                      | Security    |
| NFR-05 | Точность распознавания ≥95% для поддерживаемых шаблонов на тестовом наборе | Quality     |

---

## 6. Data Model

**Entity: PdfImportJob**

| Field          | Type      | Constraints                                                            | Description                                            |
|----------------|-----------|------------------------------------------------------------------------|--------------------------------------------------------|
| id             | UUID      | PK                                                                     |                                                        |
| user_id        | UUID      | FK → User, required                                                    |                                                        |
| status         | Enum      | `parsing` \| `ready` \| `partial` \| `failed` \| `not_inbody` \| `encrypted` \| `scanned_unsupported` |                                |
| template       | String    | Optional                                                               | `inbody_770`, `inbody_270`, `generic`, или null         |
| extracted      | JSON      | Optional                                                               | поле → значение                                        |
| confidence     | JSON      | Optional                                                               | поле → `high`/`medium`/`low`                           |
| missing_fields | String[]  | Optional                                                               |                                                        |
| temp_pdf_path  | String    | Required                                                               | Временный путь, удаляется через 1 час без подтверждения |
| created_at     | Timestamp | Required                                                               |                                                        |
| confirmed_at   | Timestamp | Optional                                                               | Когда пользователь сохранил                            |

После подтверждения создаётся `InBodyMeasurement` (см. [003](003-inbody-measurements.md)) с `source = pdf` и `original_pdf_url`, ссылающимся на постоянное хранилище.

---

## 7. Screens

Здесь UI описан только в части превью (полная картина — в [003](003-inbody-measurements.md)).

### Screen: Превью PDF

**Elements**:
- Превью документа (первая страница PDF)
- Распознанные поля справа: имя поля, значение, бейдж уверенности (high/medium/low)
- Пропущенные поля помечены красным с возможностью ввести вручную
- Кнопки «Сохранить» / «Отменить»

**States**:
- `parsing`: спиннер «обрабатываем»
- `ready` / `partial`: превью с полями
- `failed`/`not_inbody`/`encrypted`/`scanned_unsupported`: ошибка с кнопкой «Ввести вручную»

---

## 9. API Endpoints

См. эндпоинты в [003-inbody-measurements.md](003-inbody-measurements.md):
- `POST /api/v1/inbody/measurements/from-pdf` — старт job
- `GET /api/v1/inbody/measurements/from-pdf/{job_id}` — опрос статуса
- `POST /api/v1/inbody/measurements/from-pdf/{job_id}/confirm` — подтверждение

Дополнительно для отладки:
```
GET /internal/v1/inbody-pdf/templates/stats
```
**Response 200**:
```json
{
  "templates_recognized": { "inbody_770": 142, "inbody_270": 35, "generic": 18, "unknown": 9 }
}
```

---

## 10. Edge Cases

- PDF в кириллице vs латинице (русско- vs англоязычные шаблоны InBody) → поддерживаются оба, парсер пробует оба регекса.
- В одном PDF несколько страниц с замерами разных людей → берётся первая страница; в фазе 2 — выбор страницы.
- Дробные значения с запятой («18,2») vs точкой («18.2») → нормализуется к точке.
- Пользователь загрузил PDF, но не подтвердил выбор → temp_pdf_path удаляется через 1 час (cleanup job).
- Пользователь подтвердил, но отдельные поля содержат явный outlier (например, `weight_kg = 350`) → предупреждение «значение выглядит подозрительным», но сохранение разрешено.

---

## 11. Out of Scope

- OCR для сканированных PDF
- Распознавание изображений (фото распечатанного отчёта) — отдельный эпик
- Поддержка экзотических моделей InBody (S10, M20) сверх 2 базовых шаблонов в MVP
- Парсинг отчётов от других производителей (Tanita, Omron, и т.д.)
- Bulk-загрузка нескольких PDF сразу
- Возврат «highlighted PDF» с подсветкой распознанных полей (фаза 2)
