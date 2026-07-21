# Coding Standards & Style Guide

## Overview

To maintain code quality, maintainability, and security across UXOps AI, all developers and AI coding assistants must adhere to the conventions defined in this document.

---

## Python Standards (Backend)

### 1. General Principles
* Python 3.12+ features must be utilized where appropriate (e.g., structural pattern matching, enhanced type hint syntax).
* Code must comply with PEP 8 standards enforced via Black (88 character line limit), Isort, and Ruff.

### 2. Type Hints
* All functions, class methods, and endpoint handlers must include complete type annotations.
```python
# Good
async def get_workspace_by_id(
    db: AsyncSession, workspace_id: UUID
) -> Optional[Workspace]:
    ...


# Bad
def get_workspace_by_id(db, workspace_id):
    ...
```

### 3. Asynchronous Programming
* Endpoint functions, database interactions, and network I/O must be non-blocking using `async` / `await`.
* Do not use blocking calls (e.g., `requests.get` or `time.sleep`) inside async endpoints; use `httpx.AsyncClient` or `asyncio.sleep`.

### 4. Docstrings
* Include docstrings for all public classes, public modules, and non-trivial functions using Google style docstrings:
```python
def calculate_contrast_ratio(fg_color: str, bg_color: str) -> float:
    """Calculates WCAG 2.1 relative contrast ratio between two hex colors.

    Args:
        fg_color: Hex color string (e.g., "#FFFFFF").
        bg_color: Hex color string (e.g., "#000000").

    Returns:
        Float contrast ratio between 1.0 and 21.0.
    """
    ...
```

---

## TypeScript & React Standards (Frontend)

### 1. Strict Type Safety
* Enable strict type checking in `tsconfig.json`.
* Do not use the `any` type. Prefer explicit interfaces, type aliases, generics, or `unknown` with type assertions.

### 2. Component Structure
* Components should be functional and declared with typed props interfaces:
```tsx
interface AuditReportCardProps {
  auditId: string;
  score: number;
  status: 'PENDING' | 'COMPLETED' | 'FAILED';
  onSelect?: (id: string) => void;
}

export const AuditReportCard: React.FC<AuditReportCardProps> = ({
  auditId,
  score,
  status,
  onSelect,
}) => {
  return (
    <div className="audit-card" onClick={() => onSelect?.(auditId)}>
      <h3>Audit #{auditId}</h3>
      <span>Score: {score}/100</span>
    </div>
  );
};
```

### 3. Hook Usage
* Custom hooks must start with `use` (e.g., `useWorkspace`).
* Keep UI components presentational; encapsulate API calls and state management in custom hooks or service layers.

---

## Error Handling & Exception Patterns

### Backend
* Use custom HTTP exceptions raised from FastAPI routes:
```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Workspace not found or access denied",
)
```
* Log exceptions using structured logging before raising or handling.

### Frontend
* Wrap API calls in `try ... catch` blocks and provide user-friendly fallback UI states.

---

## Security Practices

* **Zero Hardcoded Secrets**: Secrets must never be stored in source code. Load configuration from environment variables via Pydantic `BaseSettings`.
* **SQL Injection Prevention**: Use SQLAlchemy ORM parameter binding exclusively. Never construct raw SQL queries via string formatting.
* **Input Validation**: All client payloads must pass validation through Pydantic schemas.
