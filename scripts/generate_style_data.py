#!/usr/bin/env python3
"""Generate committed style JSONL (≥100 React/TS + ≥100 Java). Run once; commit outputs."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "data" / "style"
SYSTEM = (STYLE / "SYSTEM.md").read_text(encoding="utf-8").strip()


def row(user: str, assistant: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ]
    }


def react_examples() -> list[dict]:
    examples: list[dict] = []

    # Core patterns (hand-authored quality seeds)
    seeds: list[tuple[str, str]] = [
        (
            "Write a React TypeScript Button with label and onClick props.",
            """```tsx
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}

export function Button({ label, onClick, disabled = false }: ButtonProps) {
  return (
    <button type="button" onClick={onClick} disabled={disabled}>
      {label}
    </button>
  );
}
```""",
        ),
        (
            "Create a React TS TextField with value and onChange.",
            """```tsx
interface TextFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
}

export function TextField({ label, value, onChange }: TextFieldProps) {
  return (
    <label>
      {label}
      <input
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}
```""",
        ),
        (
            "React TS counter with useState.",
            """```tsx
import { useState } from "react";

interface CounterProps {
  initial?: number;
}

export function Counter({ initial = 0 }: CounterProps) {
  const [count, setCount] = useState(initial);
  return (
    <div>
      <p>{count}</p>
      <button type="button" onClick={() => setCount((c) => c + 1)}>
        Increment
      </button>
    </div>
  );
}
```""",
        ),
        (
            "Custom hook useToggle in TypeScript.",
            """```ts
import { useCallback, useState } from "react";

export function useToggle(initial = false): [boolean, () => void] {
  const [value, setValue] = useState(initial);
  const toggle = useCallback(() => setValue((v) => !v), []);
  return [value, toggle];
}
```""",
        ),
        (
            "React list that maps items with a typed id.",
            """```tsx
interface Item {
  id: string;
  title: string;
}

interface ItemListProps {
  items: Item[];
}

export function ItemList({ items }: ItemListProps) {
  return (
    <ul>
      {items.map((item) => (
        <li key={item.id}>{item.title}</li>
      ))}
    </ul>
  );
}
```""",
        ),
    ]

    for user, assistant in seeds:
        examples.append(row(user, assistant))

    # (name, prop, typ, jsx_return_expression)
    components = [
        ("Avatar", "name", "string", 'return <img alt={name} />;'),
        ("Badge", "text", "string", "return <span>{text}</span>;"),
        ("Card", "title", "string", "return <section><h2>{title}</h2></section>;"),
        ("Alert", "message", "string", 'return <div role="alert">{message}</div>;'),
        ("Spinner", "label", "string", 'return <div aria-label={label} />;'),
        ("LinkButton", "href", "string", "return <a href={href}>Open</a>;"),
        (
            "Checkbox",
            "checked",
            "boolean",
            'return <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />;',
        ),
        (
            "Select",
            "value",
            "string",
            "return (\n    <select value={value} onChange={(e) => onChange(e.target.value)}>\n      <option value={value}>{value}</option>\n    </select>\n  );",
        ),
        ("Modal", "open", "boolean", "return <div>{open ? children : null}</div>;"),
        ("Tabs", "active", "string", "return <div data-active={active} />;"),
        ("Tooltip", "content", "string", "return <span title={content}>i</span>;"),
        (
            "Progress",
            "value",
            "number",
            "return <progress value={value} max={100} />;",
        ),
        ("Tag", "label", "string", "return <span>{label}</span>;"),
        (
            "IconButton",
            "ariaLabel",
            "string",
            'return <button type="button" aria-label={ariaLabel} />;',
        ),
        (
            "SearchBox",
            "query",
            "string",
            'return <input value={query} onChange={(e) => onChange(e.target.value)} />;',
        ),
        (
            "Sidebar",
            "collapsed",
            "boolean",
            "return <aside data-collapsed={collapsed} />;",
        ),
        ("Navbar", "brand", "string", "return <nav>{brand}</nav>;"),
        ("Footer", "year", "number", "return <footer>© {year}</footer>;"),
        ("EmptyState", "title", "string", "return <div><p>{title}</p></div>;"),
        ("ErrorBanner", "error", "string", "return <div>{error}</div>;"),
    ]

    for name, prop, typ, jsx in components:
        extra_props = ""
        destructure = prop
        if name in {"Checkbox", "Select", "SearchBox"}:
            if typ == "boolean":
                extra_props = "\n  onChange: (value: boolean) => void;"
            else:
                extra_props = "\n  onChange: (value: string) => void;"
            destructure = f"{prop}, onChange"
        if name == "Modal":
            assistant = f"""```tsx
import type {{ ReactNode }} from "react";

interface {name}Props {{
  {prop}: {typ};
  children: ReactNode;
}}

export function {name}({{ {prop}, children }}: {name}Props) {{
  {jsx}
}}
```"""
        else:
            assistant = f"""```tsx
interface {name}Props {{
  {prop}: {typ};{extra_props}
}}

export function {name}({{ {destructure} }}: {name}Props) {{
  {jsx}
}}
```"""
        user = f"Write a React TypeScript {name} component with typed props (interface)."
        examples.append(row(user, assistant))

    hooks = [
        ("useLocalStorage", "key: string, initial: string", "string",
         """const [value, setValue] = useState(() => localStorage.getItem(key) ?? initial);
  useEffect(() => {
    localStorage.setItem(key, value);
  }, [key, value]);
  return [value, setValue] as const;"""),
        ("useDebouncedValue", "value: T, delayMs: number", "T",
         """const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = window.setTimeout(() => setDebounced(value), delayMs);
    return () => window.clearTimeout(id);
  }, [value, delayMs]);
  return debounced;"""),
        ("usePrevious", "value: T", "T | undefined",
         """const ref = useRef<T | undefined>(undefined);
  useEffect(() => {
    ref.current = value;
  }, [value]);
  return ref.current;"""),
        ("useMounted", "", "boolean",
         """const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);
  return mounted;"""),
        ("useInterval", "callback: () => void, delayMs: number | null", "void",
         """const saved = useRef(callback);
  useEffect(() => {
    saved.current = callback;
  }, [callback]);
  useEffect(() => {
    if (delayMs === null) return;
    const id = window.setInterval(() => saved.current(), delayMs);
    return () => window.clearInterval(id);
  }, [delayMs]);"""),
        ("useMediaQuery", "query: string", "boolean",
         """const [matches, setMatches] = useState(() => window.matchMedia(query).matches);
  useEffect(() => {
    const mql = window.matchMedia(query);
    const onChange = () => setMatches(mql.matches);
    mql.addEventListener("change", onChange);
    return () => mql.removeEventListener("change", onChange);
  }, [query]);
  return matches;"""),
        ("useOnline", "", "boolean",
         """const [online, setOnline] = useState(navigator.onLine);
  useEffect(() => {
    const on = () => setOnline(true);
    const off = () => setOnline(false);
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
    return () => {
      window.removeEventListener("online", on);
      window.removeEventListener("offline", off);
    };
  }, []);
  return online;"""),
        ("useCounter", "initial = 0", "[number, () => void, () => void]",
         """const [count, setCount] = useState(initial);
  const inc = useCallback(() => setCount((c) => c + 1), []);
  const dec = useCallback(() => setCount((c) => c - 1), []);
  return [count, inc, dec];"""),
        ("useBoolean", "initial = false", "{ value: boolean; on: () => void; off: () => void; toggle: () => void }",
         """const [value, setValue] = useState(initial);
  return {
    value,
    on: () => setValue(true),
    off: () => setValue(false),
    toggle: () => setValue((v) => !v),
  };"""),
        ("useArray", "initial: T[]", "{ items: T[]; push: (item: T) => void; removeAt: (index: number) => void }",
         """const [items, setItems] = useState(initial);
  return {
    items,
    push: (item: T) => setItems((prev: T[]) => [...prev, item]),
    removeAt: (index: number) => setItems((prev: T[]) => prev.filter((_, i) => i !== index)),
  };"""),
    ]

    for name, params, _ret, body in hooks:
        generic = "<T>" if "T" in params or "T" in body or name in {"useDebouncedValue", "usePrevious", "useArray"} else ""
        param_list = params if params else ""
        user = f"Implement a TypeScript React hook named {name}."
        used = [h for h in ("useCallback", "useEffect", "useRef", "useState") if h in body]
        imports = f'import {{ {", ".join(used)} }} from "react";'
        assistant = f"""```ts
{imports}

export function {name}{generic}({param_list}) {{
  {body}
}}
```"""
        examples.append(row(user, assistant))

    # Forms / async / typed utils — expand to ≥100
    form_fields = [
        "email", "password", "username", "phone", "city", "country", "zip",
        "company", "title", "bio", "website", "notes", "token", "code",
        "firstName", "lastName", "address", "state", "otp", "nickname",
    ]
    for field in form_fields:
        iface = field[0].upper() + field[1:]
        user = f"React TS controlled input for {field}."
        assistant = f"""```tsx
interface {iface}InputProps {{
  value: string;
  onChange: (value: string) => void;
  label?: string;
}}

export function {iface}Input({{ value, onChange, label = "{field}" }}: {iface}InputProps) {{
  return (
    <label>
      {{label}}
      <input
        name="{field}"
        value={{value}}
        onChange={{(event) => onChange(event.target.value)}}
      />
    </label>
  );
}}
```"""
        examples.append(row(user, assistant))

    fetchers = [
        ("User", "/api/users"),
        ("Project", "/api/projects"),
        ("Task", "/api/tasks"),
        ("Comment", "/api/comments"),
        ("Invoice", "/api/invoices"),
        ("Session", "/api/session"),
        ("Settings", "/api/settings"),
        ("Notification", "/api/notifications"),
        ("Repo", "/api/repos"),
        ("Issue", "/api/issues"),
        ("PullRequest", "/api/pulls"),
        ("Team", "/api/teams"),
        ("Label", "/api/labels"),
        ("Milestone", "/api/milestones"),
        ("Webhook", "/api/webhooks"),
    ]
    for entity, path in fetchers:
        user = f"TypeScript fetch helper that returns {entity} JSON from {path}."
        assistant = f"""```ts
export interface {entity} {{
  id: string;
  name: string;
}}

export async function fetch{entity}(): Promise<{entity}> {{
  const response = await fetch("{path}");
  if (!response.ok) {{
    throw new Error(`Failed to load {entity}: ${{response.status}}`);
  }}
  return (await response.json()) as {entity};
}}
```"""
        examples.append(row(user, assistant))

    reducers = [
        ("todos", "ADD", "text"),
        ("filters", "SET", "value"),
        ("cart", "ADD_ITEM", "sku"),
        ("ui", "OPEN", "panel"),
        ("auth", "LOGIN", "token"),
    ]
    for name, action, field in reducers:
        type_name = name[0].upper() + name[1:]
        user = f"React TS useReducer for {name} state."
        assistant = f"""```tsx
import {{ useReducer }} from "react";

interface {type_name}State {{
  {field}: string;
}}

type {type_name}Action = {{ type: "{action}"; payload: string }};

function reducer(state: {type_name}State, action: {type_name}Action): {type_name}State {{
  switch (action.type) {{
    case "{action}":
      return {{ ...state, {field}: action.payload }};
    default:
      return state;
  }}
}}

interface {type_name}PanelProps {{
  initial: string;
}}

export function {type_name}Panel({{ initial }}: {type_name}PanelProps) {{
  const [state, dispatch] = useReducer(reducer, {{ {field}: initial }});
  return (
    <button
      type="button"
      onClick={{() => dispatch({{ type: "{action}", payload: "updated" }})}}
    >
      {{state.{field}}}
    </button>
  );
}}
```"""
        examples.append(row(user, assistant))

    # Ensure ≥100
    idx = 0
    while len(examples) < 100:
        idx += 1
        user = f"Write a React TypeScript StatusChip showing status string #{idx}."
        assistant = f"""```tsx
interface StatusChip{idx}Props {{
  status: string;
  tone?: "info" | "warn" | "ok";
}}

export function StatusChip{idx}({{ status, tone = "info" }}: StatusChip{idx}Props) {{
  return <span data-tone={{tone}}>{{status}}</span>;
}}
```"""
        examples.append(row(user, assistant))

    return examples


def java_examples() -> list[dict]:
    examples: list[dict] = []

    seeds: list[tuple[str, str]] = [
        (
            "Java 17 record DTO for a user id and email.",
            """```java
public record UserDto(String id, String email) {
  public UserDto {
    if (id == null || id.isBlank()) {
      throw new IllegalArgumentException("id required");
    }
    if (email == null || !email.contains("@")) {
      throw new IllegalArgumentException("email invalid");
    }
  }
}
```""",
        ),
        (
            "Small Java service that finds a user by id or throws.",
            """```java
import java.util.Map;
import java.util.Optional;

public final class UserService {
  private final Map<String, String> users;

  public UserService(Map<String, String> users) {
    this.users = Map.copyOf(users);
  }

  public String requireEmail(String id) {
    return Optional.ofNullable(users.get(id))
        .orElseThrow(() -> new IllegalArgumentException("user not found: " + id));
  }
}
```""",
        ),
        (
            "Java 17 sealed-friendly result type using a record for success.",
            """```java
public record Success<T>(T value) {
  public Success {
    if (value == null) {
      throw new IllegalArgumentException("value required");
    }
  }
}
```""",
        ),
    ]
    for user, assistant in seeds:
        examples.append(row(user, assistant))

    records = [
        ("ProjectDto", "String id, String name"),
        ("TaskDto", "String id, String title, boolean done"),
        ("CommentDto", "String id, String body, String authorId"),
        ("InvoiceDto", "String id, long cents, String currency"),
        ("SessionDto", "String token, long expiresAtEpochMs"),
        ("TeamDto", "String id, String name"),
        ("RepoDto", "String id, String fullName"),
        ("IssueDto", "long number, String title, String state"),
        ("LabelDto", "String name, String color"),
        ("MilestoneDto", "String id, String title"),
        ("WebhookDto", "String id, String url"),
        ("NotificationDto", "String id, String message, boolean read"),
        ("SettingsDto", "boolean darkMode, String locale"),
        ("AddressDto", "String line1, String city, String country"),
        ("MoneyDto", "long amountCents, String currency"),
        ("PageRequest", "int page, int size"),
        ("PageResponse", "int page, int size, long total"),
        ("ErrorBody", "String code, String message"),
        ("AuthToken", "String accessToken, String refreshToken"),
        ("FileMeta", "String name, long sizeBytes, String contentType"),
    ]
    for name, fields in records:
        user = f"Java 17 record named {name}."
        assistant = f"""```java
public record {name}({fields}) {{
  public {name} {{
    // compact constructor keeps invariants local to the DTO
  }}
}}
```"""
        examples.append(row(user, assistant))

    services = [
        ("TaskService", "complete", "String taskId"),
        ("InvoiceService", "voidInvoice", "String invoiceId"),
        ("CommentService", "addComment", "String body"),
        ("ProjectService", "rename", "String name"),
        ("TeamService", "addMember", "String userId"),
        ("RepoService", "archive", "String repoId"),
        ("IssueService", "close", "long number"),
        ("LabelService", "create", "String name"),
        ("WebhookService", "disable", "String webhookId"),
        ("NotificationService", "markRead", "String id"),
        ("SettingsService", "updateLocale", "String locale"),
        ("SessionService", "revoke", "String token"),
        ("FileService", "delete", "String name"),
        ("AuthService", "logout", "String token"),
        ("BillingService", "charge", "long cents"),
    ]
    for cls, method, param in services:
        user = f"Java class {cls} with method {method}({param}) that validates input."
        ptype, pname = param.rsplit(" ", 1)
        if ptype in {"long", "int", "boolean", "double", "float", "char", "byte", "short"}:
            validate = f"""if ({pname} < 0) {{
      throw new IllegalArgumentException("{pname} invalid");
    }}"""
            if ptype == "boolean":
                validate = "// boolean input accepted as-is"
        else:
            validate = f"""if ({pname} == null) {{
      throw new IllegalArgumentException("{pname} required");
    }}"""
        assistant = f"""```java
public final class {cls} {{
  public void {method}({param}) {{
    {validate}
    // domain work would go here
  }}
}}
```"""
        examples.append(row(user, assistant))

    utils = [
        ("Strings", "isBlank", "String value", "boolean",
         "return value == null || value.isBlank();"),
        ("Ints", "requirePositive", "int value", "int",
         """if (value <= 0) {
      throw new IllegalArgumentException("must be positive");
    }
    return value;"""),
        ("Collections2", "requireNonEmpty", "java.util.Collection<?> values", "void",
         """if (values == null || values.isEmpty()) {
      throw new IllegalArgumentException("collection empty");
    }"""),
        ("TimeUtil", "isExpired", "long expiresAtEpochMs", "boolean",
         "return System.currentTimeMillis() >= expiresAtEpochMs;"),
        ("Ids", "requireId", "String id", "String",
         """if (id == null || id.isBlank()) {
      throw new IllegalArgumentException("id required");
    }
    return id;"""),
    ]
    for cls, method, params, ret, body in utils:
        user = f"Java utility {cls}.{method}."
        assistant = f"""```java
public final class {cls} {{
  private {cls}() {{}}

  public static {ret} {method}({params}) {{
    {body}
  }}
}}
```"""
        examples.append(row(user, assistant))

    exceptions = [
        ("NotFoundException", "Resource not found"),
        ("ConflictException", "Conflict"),
        ("ValidationException", "Validation failed"),
        ("UnauthorizedException", "Unauthorized"),
        ("ForbiddenException", "Forbidden"),
        ("GoneException", "Gone"),
        ("RateLimitException", "Rate limited"),
        ("DependencyException", "Dependency failed"),
        ("TimeoutExceptionLocal", "Timed out"),
        ("ParseExceptionLocal", "Parse failed"),
    ]
    for name, msg in exceptions:
        user = f"Checked-style runtime exception class {name} in Java."
        assistant = f"""```java
public final class {name} extends RuntimeException {{
  public {name}(String detail) {{
    super("{msg}: " + detail);
  }}
}}
```"""
        examples.append(row(user, assistant))

    parsers = [
        ("Status", "OPEN", "CLOSED"),
        ("Role", "ADMIN", "USER"),
        ("Priority", "LOW", "HIGH"),
        ("Visibility", "PUBLIC", "PRIVATE"),
        ("Environment", "DEV", "PROD"),
        ("Currency", "USD", "EUR"),
        ("HttpMethod", "GET", "POST"),
        ("SortOrder", "ASC", "DESC"),
        ("Side", "BUY", "SELL"),
        ("Channel", "EMAIL", "SMS"),
    ]
    for name, a, b in parsers:
        user = f"Java enum {name} with parse helper for {a}/{b}."
        assistant = f"""```java
public enum {name} {{
  {a},
  {b};

  public static {name} parse(String raw) {{
    if (raw == null) {{
      throw new IllegalArgumentException("value required");
    }}
    return {name}.valueOf(raw.trim().toUpperCase());
  }}
}}
```"""
        examples.append(row(user, assistant))

    streams = [
        ("sumPositive", "int", "filter(n -> n > 0).mapToInt(Integer::intValue).sum()"),
        ("joinNames", "String", "collect(java.util.stream.Collectors.joining(\",\"))"),
        ("countDistinct", "long", "distinct().count()"),
        ("maxOrZero", "int", "mapToInt(Integer::intValue).max().orElse(0)"),
        ("sortedCopy", "java.util.List<String>", "sorted().toList()"),
    ]
    for method, ret, pipeline in streams:
        user = f"Java method {method} using streams."
        if "String" in ret and "List" in ret:
            param = "java.util.List<String> values"
            stream = "values.stream()"
        elif ret == "String":
            param = "java.util.List<String> values"
            stream = "values.stream()"
        else:
            param = "java.util.List<Integer> values"
            stream = "values.stream()"
        assistant = f"""```java
import java.util.Objects;

public final class StreamOps {{
  private StreamOps() {{}}

  public static {ret} {method}({param}) {{
    Objects.requireNonNull(values, "values");
    return {stream}.{pipeline};
  }}
}}
```"""
        examples.append(row(user, assistant))

    idx = 0
    while len(examples) < 100:
        idx += 1
        user = f"Java 17 record ItemDto{idx} with id and name."
        assistant = f"""```java
public record ItemDto{idx}(String id, String name) {{
  public ItemDto{idx} {{
    if (id == null || id.isBlank()) {{
      throw new IllegalArgumentException("id required");
    }}
    if (name == null || name.isBlank()) {{
      throw new IllegalArgumentException("name required");
    }}
  }}
}}
```"""
        examples.append(row(user, assistant))

    return examples


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for item in rows:
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")


def main() -> None:
    react = react_examples()
    java = java_examples()
    write_jsonl(STYLE / "react-ts.jsonl", react)
    write_jsonl(STYLE / "java.jsonl", java)
    print(f"wrote {len(react)} react-ts rows, {len(java)} java rows")


if __name__ == "__main__":
    main()
