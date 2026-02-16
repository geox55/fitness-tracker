---
name: python-fastapi-developer
description: Guide for creating high-quality backend in Python with FastAPI. Use when building an API backend application in Python with FastAPI.
---

# AI Rules for Python FastAPI

You are an expert in Python, FastAPI, Pydantic, SQLAlchemy.
Your goal is to build robust, performant, and maintainable applications following modern best practices.
You have expert experience with application writing, testing, and running Python applications for production environments.

## Interaction Guidelines

- **User Persona:** Assume the user is familiar with programming concepts but
  may need guidance on Python-specific idioms and async patterns.
- **Explanations:** When generating code, provide explanations for Python-specific
  features like async/await, type hints, context managers, and generators.
- **Clarification:** If a request is ambiguous, ask for clarification on the
  intended functionality and the target module.
- **Dependencies:** When suggesting new dependencies from PyPI, explain their
  benefits and trade-offs.
- **Python project manager:** Use `uv` instead of poetry or pip. 
- **Formatting:** Use `uv run ruff format` to ensure consistent code formatting.
- **Fixes:** Use `uv run ruff check --fix` to automatically fix common errors and
  conform to configured lint rules.
- **Type Checking:** Use `uv run mypy` in strict mode to catch type errors before runtime.

## Project Structure

The project follows a domain-driven modular structure inspired by Netflix's
[Dispatch](https://github.com/Netflix/dispatch):

```
fastapi-project
├── alembic/
├── src
│   ├── auth
│   │   ├── router.py
│   │   ├── schemas.py      # Pydantic models
│   │   ├── models.py       # SQLAlchemy ORM models
│   │   ├── dependencies.py
│   │   ├── config.py       # Module-specific env vars
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── aws
│   │   ├── client.py       # External service client
│   │   ├── schemas.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   └── utils.py
│   └── posts
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── dependencies.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── config.py           # Global configs
│   ├── models.py           # Global/shared models
│   ├── exceptions.py       # Global exceptions
│   ├── pagination.py       # Global utilities
│   ├── database.py         # DB connection setup
│   └── main.py
├── tests/
│   ├── auth/
│   ├── aws/
│   └── posts/
├── .env
├── .gitignore
├── pyproject.toml
├── uv.lock
├── logging.ini
└── alembic.ini
```

### Structure Guidelines

1. **Domain Organization:** Store all domain directories inside `src/` folder.
   - `src/` is the highest level, containing common models, configs, and constants.
   - `src/main.py` is the project root, initializing the FastAPI app.

2. **Module Files:** Each package has its own set of files:
   - `router.py` - Core of each module with all endpoints
   - `schemas.py` - Pydantic models for request/response validation
   - `models.py` - SQLAlchemy ORM models
   - `service.py` - Module-specific business logic
   - `dependencies.py` - FastAPI dependencies for the router
   - `constants.py` - Module-specific constants and error codes
   - `config.py` - Module-specific environment variables
   - `utils.py` - Non-business logic functions (response normalization, etc.)
   - `exceptions.py` - Module-specific exceptions (e.g., `PostNotFound`)

3. **Cross-Module Imports:** Use explicit module names when importing from other packages:

```python
from src.auth import constants as auth_constants
from src.notifications import service as notification_service
from src.posts.constants import ErrorCode as PostsErrorCode
```

## Python Style Guide

### General Principles

- **SOLID Principles:** Apply SOLID principles throughout the codebase.
- **Composition over Inheritance:** Favor composition for building complex logic.
- **Immutability:** Prefer immutable data structures where possible.
- **Single Responsibility:** Each function, class, and module should have one job.
- **Explicit over Implicit:** Be explicit in type hints, imports, and configurations.

### Naming Conventions

- `snake_case` for functions, variables, and module names
- `PascalCase` for classes and type aliases
- `SCREAMING_SNAKE_CASE` for constants
- `_leading_underscore` for private/internal names
- Avoid abbreviations; use meaningful, descriptive names

### Code Quality

- **Line Length:** Lines should be 88 characters or fewer (ruff default).
- **Functions:** Keep functions short with a single purpose (aim for < 20 lines).
- **Docstrings:** Use Google-style docstrings for all public APIs.
- **Comments:** Explain *why*, not *what*. The code should be self-explanatory.
- **No Trailing Comments:** Avoid inline comments at end of lines.

### Type Hints

- **Comprehensive Typing:** Type all function parameters and return values.
- **Modern Syntax:** Use Python 3.11+ syntax (`list[str]` not `List[str]`).
- **Optional Handling:** Use `X | None` instead of `Optional[X]`.
- **TypeAlias:** Use `type` statement for complex type aliases.

```python
# Good: Modern Python 3.11+ type hints
type UserID = int
type UserDict = dict[str, Any]

async def get_user(user_id: UserID) -> User | None:
    ...

# Avoid: Legacy typing module imports
from typing import Optional, List, Dict
def get_user(user_id: int) -> Optional[User]:  # Don't do this
    ...
```

## Async Best Practices

### I/O Operations

FastAPI is async-first. Understand the implications:

```python
import asyncio
from fastapi import APIRouter

router = APIRouter()

# BAD: Blocks the entire event loop
@router.get("/terrible-ping")
async def terrible_ping():
    time.sleep(10)  # Never do this in async routes
    return {"pong": True}

# OK: Runs in threadpool, doesn't block event loop
@router.get("/good-ping")
def good_ping():
    time.sleep(10)  # Sync route runs in threadpool
    return {"pong": True}

# BEST: Non-blocking async operation
@router.get("/perfect-ping")
async def perfect_ping():
    await asyncio.sleep(10)  # Proper async I/O
    return {"pong": True}
```

### Guidelines

- **Async Routes:** Define routes as `async def` only if they perform async I/O.
- **Sync Routes:** Use `def` for routes with blocking operations; FastAPI runs
  them in a threadpool automatically.
- **Never Block Async:** Never call blocking functions (like `time.sleep()`,
  sync HTTP clients, or sync DB operations) in `async def` routes.
- **Sync SDK Workaround:** If you must use a sync library in async context,
  use `run_in_threadpool`:

```python
from fastapi.concurrency import run_in_threadpool

async def call_sync_service():
    result = await run_in_threadpool(sync_client.make_request, data=my_data)
    return result
```

### CPU-Intensive Tasks

- **Don't Await CPU Work:** Awaiting CPU-bound tasks is pointless since CPU
  must complete the work.
- **Don't Use Threads for CPU:** GIL prevents true parallelism in threads.
- **Use Process Pools:** For CPU-intensive work, offload to separate processes
  using `ProcessPoolExecutor` or task queues like Celery/RQ.

## Pydantic Best Practices

### Excessively Use Pydantic

Leverage Pydantic's rich validation features:

```python
from enum import Enum
from pydantic import AnyUrl, BaseModel, EmailStr, Field


class MusicBand(str, Enum):
    AEROSMITH = "AEROSMITH"
    QUEEN = "QUEEN"
    ACDC = "AC/DC"


class UserCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=128)
    username: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9-_]+$")
    email: EmailStr
    age: int = Field(ge=18, default=None)
    favorite_band: MusicBand | None = None
    website: AnyUrl | None = None
```

### Custom Base Model

Create a controllable global base model for app-wide customization:

```python
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict


def datetime_to_gmt_str(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class CustomModel(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: datetime_to_gmt_str},
        populate_by_name=True,
        from_attributes=True,  # Enable ORM mode
    )

    def serializable_dict(self, **kwargs) -> dict:
        """Return a dict with only serializable fields."""
        return jsonable_encoder(self.model_dump())
```

### Decouple BaseSettings

Split settings across modules for maintainability:

```python
# src/auth/config.py
from datetime import timedelta
from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    JWT_ALG: str = "HS256"
    JWT_SECRET: str
    JWT_EXP: int = 5  # minutes
    REFRESH_TOKEN_KEY: str
    REFRESH_TOKEN_EXP: timedelta = timedelta(days=30)
    SECURE_COOKIES: bool = True

    model_config = {"env_prefix": "AUTH_"}


auth_settings = AuthConfig()


# src/config.py
from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings

from src.constants import Environment


class Config(BaseSettings):
    DATABASE_URL: PostgresDsn
    REDIS_URL: RedisDsn
    SITE_DOMAIN: str = "myapp.com"
    ENVIRONMENT: Environment = Environment.PRODUCTION
    CORS_ORIGINS: list[str]
    APP_VERSION: str = "1.0"


settings = Config()
```

### Validation Error Handling

`ValueError` in Pydantic validators becomes a user-friendly validation error:

```python
import re
from pydantic import BaseModel, field_validator

STRONG_PASSWORD_PATTERN = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"


class UserCreate(BaseModel):
    username: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise ValueError(
                "Password must contain at least one lowercase, one uppercase, "
                "one digit, and one special character"
            )
        return password
```

## FastAPI Dependencies

### Beyond Dependency Injection

Use dependencies for request validation against database constraints:

```python
# src/posts/dependencies.py
from typing import Any
from uuid import UUID

from fastapi import Depends

from src.posts import service
from src.posts.exceptions import PostNotFound


async def valid_post_id(post_id: UUID) -> dict[str, Any]:
    post = await service.get_by_id(post_id)
    if not post:
        raise PostNotFound()
    return post


# src/posts/router.py
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/posts/{post_id}")
async def get_post(post: dict[str, Any] = Depends(valid_post_id)):
    return post


@router.put("/posts/{post_id}")
async def update_post(
    update_data: PostUpdate,
    post: dict[str, Any] = Depends(valid_post_id),
):
    return await service.update(id=post["id"], data=update_data)
```

### Chain Dependencies

Dependencies can use other dependencies to avoid code repetition:

```python
# src/auth/dependencies.py
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.auth.config import auth_settings
from src.auth.exceptions import InvalidCredentials


async def parse_jwt_data(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/auth/token"))
) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, auth_settings.JWT_SECRET, algorithms=[auth_settings.JWT_ALG]
        )
    except JWTError:
        raise InvalidCredentials()
    return {"user_id": payload["id"]}


async def valid_owned_post(
    post: dict[str, Any] = Depends(valid_post_id),
    token_data: dict[str, Any] = Depends(parse_jwt_data),
) -> dict[str, Any]:
    if post["creator_id"] != token_data["user_id"]:
        raise UserNotOwner()
    return post
```

### Dependency Caching

Dependencies are cached within a request's scope. If `parse_jwt_data` is called
multiple times in one route (directly or via other dependencies), it executes
only once.

### Prefer Async Dependencies

Always use `async def` for dependencies, even for simple operations. Sync
dependencies run in the threadpool, adding unnecessary overhead:

```python
# Good: Async dependency
async def get_current_user_id(
    token_data: dict[str, Any] = Depends(parse_jwt_data)
) -> int:
    return token_data["user_id"]


# Avoid: Sync dependency (runs in threadpool)
def get_current_user_id(
    token_data: dict[str, Any] = Depends(parse_jwt_data)
) -> int:
    return token_data["user_id"]
```

## SQLAlchemy Async Best Practices

### Database Setup

```python
# src/database.py
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)


engine = create_async_engine(str(settings.DATABASE_URL), echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### Session Management via Dependency Injection

Always inject sessions through FastAPI's DI system:

```python
# src/posts/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.posts import service

router = APIRouter()


@router.get("/posts/{post_id}")
async def get_post(
    post_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    return await service.get_by_id(session, post_id)
```

### Model Definitions

```python
# src/posts/models.py
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Post(Base):
    __tablename__ = "post"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    creator_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(default=None, onupdate=datetime.utcnow)

    creator: Mapped["User"] = relationship(back_populates="posts")
```

### Naming Conventions

1. Use `lower_case_snake` for table and column names
2. Use singular form (`post`, not `posts`)
3. Group similar tables with module prefix (`payment_account`, `payment_bill`)
4. Use `_at` suffix for datetime columns, `_date` suffix for date columns
5. Stay consistent but use concrete names when appropriate (`creator_id` vs `profile_id`)

### SQL-First, Pydantic-Second

Prefer database-level data processing over Python when possible:

```python
# src/posts/service.py
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

async def get_posts_with_creator(
    session: AsyncSession,
    creator_id: UUID,
    limit: int = 10,
    offset: int = 0,
) -> list[Post]:
    query = (
        select(Post)
        .where(Post.creator_id == creator_id)
        .options(selectinload(Post.creator))
        .order_by(desc(Post.created_at))
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    return list(result.scalars().all())
```

## Alembic Migrations

### Configuration

Set human-readable file template in `alembic.ini`:

```ini
# alembic.ini
file_template = %%(year)d-%%(month).2d-%%(day).2d_%%(slug)s
```

### Guidelines

1. **Static Migrations:** Migrations must be static and revertable. If they
   depend on dynamic data, ensure only the data is dynamic, not the structure.
2. **Descriptive Names:** Generate migrations with descriptive slugs explaining
   the changes (e.g., `2024-01-15_add_post_content_index.py`).
3. **Review Generated Code:** Always review auto-generated migrations before
   applying them.
4. **Test Both Directions:** Test both upgrade and downgrade paths.

### Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "add_user_email_index"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Exception Handling

### Module-Specific Exceptions

```python
# src/posts/exceptions.py
from fastapi import HTTPException, status


class PostNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )


class PostPermissionDenied(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this post",
        )
```

### Global Exception Handler

```python
# src/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the exception
    logger.exception("Unhandled exception", exc_info=exc)

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
```

## Testing

### Setup Async Test Client from Day 0

```python
# tests/conftest.py
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.database import Base, get_async_session
from src.main import app

TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session(test_engine) -> AsyncIterator[AsyncSession]:
    async_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    def override_get_session():
        yield session

    app.dependency_overrides[get_async_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()
```

### Test Structure

Follow the Arrange-Act-Assert pattern:

```python
# tests/posts/test_router.py
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_post(client: AsyncClient, authenticated_user):
    # Arrange
    post_data = {"title": "Test Post", "content": "Test content"}

    # Act
    response = await client.post("/posts", json=post_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == post_data["title"]


@pytest.mark.anyio
async def test_get_nonexistent_post(client: AsyncClient):
    # Act
    response = await client.get("/posts/00000000-0000-0000-0000-000000000000")

    # Assert
    assert response.status_code == 404
```

### Testing Best Practices

- **Unit Tests:** Test service layer functions in isolation.
- **Integration Tests:** Test API endpoints with the full request/response cycle.
- **Fixtures:** Use pytest fixtures for common setup (users, database records).
- **Factories:** Consider `factory_boy` for complex test data generation.
- **Mocking:** Prefer fakes/stubs over mocks. Use `unittest.mock` or `pytest-mock`
  when necessary.
- **Coverage:** Aim for high test coverage, especially on business logic.

### Assertions with `pytest`

```python
import pytest


def test_user_validation():
    with pytest.raises(ValueError, match="Password must contain"):
        UserCreate(username="test", password="weak")
```

## Logging

### Use Structured Logging

```python
# src/logging_config.py
import logging
import sys
from typing import Any

import structlog


def setup_logging(log_level: str = "INFO") -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if sys.stderr.isatty()
            else structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
    )
```

### Usage

```python
import structlog

logger = structlog.get_logger()


async def get_user(user_id: UUID) -> User:
    logger.info("fetching_user", user_id=str(user_id))
    try:
        user = await service.get_by_id(user_id)
        logger.info("user_found", user_id=str(user_id))
        return user
    except Exception as e:
        logger.error("user_fetch_failed", user_id=str(user_id), error=str(e))
        raise
```

## Code Quality Tools

- Use `ruff` for linting and formatting. Ruff configuration is in `pyproject.toml` at `[tool.ruff.lint]`.
- Use `ty` for type checking (`ty` is a new fast alternative to mypy and pyright).

## REST API Design

### Follow REST Conventions

Design RESTful APIs for dependency reuse:

```python
# Consistent path parameter names enable dependency chaining
GET /posts/{post_id}
GET /posts/{post_id}/comments
GET /posts/{post_id}/comments/{comment_id}
GET /users/{user_id}/posts
```

### Route Documentation

```python
from fastapi import APIRouter, status

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new post",
    description="Creates a new post for the authenticated user.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Not authenticated"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> PostResponse:
    ...
```

### Hide Docs in Production

```python
# src/main.py
from src.config import settings
from src.constants import Environment

SHOW_DOCS_ENVIRONMENTS = {Environment.LOCAL, Environment.STAGING}

app_configs: dict[str, Any] = {"title": "My API"}
if settings.ENVIRONMENT not in SHOW_DOCS_ENVIRONMENTS:
    app_configs["openapi_url"] = None

app = FastAPI(**app_configs)
```

## Documentation

### Docstring Style (Google)

```python
async def get_posts_by_creator(
    session: AsyncSession,
    creator_id: UUID,
    limit: int = 10,
    offset: int = 0,
) -> list[Post]:
    """Retrieve posts created by a specific user.

    Fetches posts from the database with pagination support,
    ordered by creation date descending.

    Args:
        session: The database session.
        creator_id: The UUID of the post creator.
        limit: Maximum number of posts to return.
        offset: Number of posts to skip.

    Returns:
        A list of Post objects.

    Raises:
        DatabaseError: If the database query fails.
    """
    ...
```

### Documentation Philosophy

- **Comment wisely:** Explain *why*, not *what*.
- **Document for the user:** Write with the reader in mind.
- **No useless documentation:** Don't restate the obvious.
- **Consistency:** Use consistent terminology throughout.

## Package Management

Use pyproject.toml and uv.

- `uv sync` to update the project's environment.
- `uv add` to add a new dependecy. For example `uv add fastapi` or `uv add --dev pytest`.
- `uv run pytest` to run unittests.
- `uv run main.py` to run a script.
- `uv run uvicorn src.main:app` to run FastAPI server in production mode.
- `uv run fastapi dev src/main.py` to run in development mode.

## Security Best Practices

- **Input Validation:** Always validate and sanitize user input via Pydantic.
- **SQL Injection:** Use SQLAlchemy ORM or parameterized queries.
- **Authentication:** Use OAuth2 with JWT tokens; never store plain-text passwords.
- **CORS:** Configure CORS strictly; don't use `allow_origins=["*"]` in production.
- **Secrets:** Never commit secrets; use environment variables or secret managers.
- **HTTPS:** Always use HTTPS in production.
- **Rate Limiting:** Implement rate limiting for public endpoints.

## Performance Considerations

- **Connection Pooling:** Configure SQLAlchemy connection pool appropriately.
- **Pagination:** Always paginate list endpoints.
- **Eager Loading:** Use `selectinload` or `joinedload` to avoid N+1 queries.
- **Caching:** Use Redis for caching frequently accessed data.
- **Background Tasks:** Offload non-critical work to background tasks or queues.
- **Profiling:** Use tools like `py-spy` or `cProfile` to identify bottlenecks.
