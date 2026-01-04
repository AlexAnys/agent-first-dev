# Coding Agent Enhancement Design Plan

## Overview

This document outlines the design plan for enhancing `coding_agent_from_scratch_lecture.py` with improved error handling, self-healing capabilities, security guardrails, and API rate limiting. All enhancements will follow **functional programming principles**.

---

## Enhancement Summary

| # | Feature | Purpose |
|---|---------|---------|
| 1 | **Meaningful Extraction Errors** | Provide detailed, actionable error messages when tool invocation parsing fails |
| 2 | **Agent Self-Healing** | Automatically retry with corrective prompts when extraction fails |
| 3 | **Edit File Guardrails** | Prevent modifications to sensitive files (.env, config, system files) |
| 4 | **Max API Control** | Limit API calls to prevent runaway loops and manage costs |
| 5 | **Functional Programming** | Implement all features using pure functions and immutable patterns |

---

## 1. Meaningful Error Extraction

### Current Problem
```python
except Exception:
    continue  # Silent failure - no diagnostic information
```

### Functional Design

#### 1.1 Define Error Types (Using NamedTuple for Immutability)
```python
from typing import NamedTuple, Union
from enum import Enum, auto

class ExtractionErrorType(Enum):
    MISSING_TOOL_PREFIX = auto()
    MISSING_OPENING_PAREN = auto()
    MISSING_CLOSING_PAREN = auto()
    INVALID_JSON_SYNTAX = auto()
    EMPTY_TOOL_NAME = auto()
    UNKNOWN_TOOL_NAME = auto()

class ExtractionError(NamedTuple):
    """Immutable error record for extraction failures."""
    error_type: ExtractionErrorType
    line_number: int
    line_content: str
    details: str

class ToolInvocation(NamedTuple):
    """Immutable successful tool invocation."""
    tool_name: str
    args: Dict[str, Any]
    line_number: int

# Result type using Union (functional Either pattern)
ExtractionResult = Union[ToolInvocation, ExtractionError]
```

#### 1.2 Pure Parsing Functions
```python
def parse_tool_line(line: str, line_number: int, known_tools: frozenset[str]) -> ExtractionResult:
    """
    Pure function to parse a single tool line.
    Returns either ToolInvocation or ExtractionError.
    """
    stripped = line.strip()
    
    # Check for tool prefix
    if not stripped.startswith("tool:"):
        return ExtractionError(
            error_type=ExtractionErrorType.MISSING_TOOL_PREFIX,
            line_number=line_number,
            line_content=line,
            details="Line does not start with 'tool:' prefix"
        )
    
    after_prefix = stripped[len("tool:"):].strip()
    
    # Check for opening parenthesis
    if "(" not in after_prefix:
        return ExtractionError(
            error_type=ExtractionErrorType.MISSING_OPENING_PAREN,
            line_number=line_number,
            line_content=line,
            details=f"Missing '(' in tool invocation: '{after_prefix}'"
        )
    
    name, rest = after_prefix.split("(", 1)
    name = name.strip()
    
    # Check for empty tool name
    if not name:
        return ExtractionError(
            error_type=ExtractionErrorType.EMPTY_TOOL_NAME,
            line_number=line_number,
            line_content=line,
            details="Tool name is empty"
        )
    
    # Check for known tool
    if name not in known_tools:
        return ExtractionError(
            error_type=ExtractionErrorType.UNKNOWN_TOOL_NAME,
            line_number=line_number,
            line_content=line,
            details=f"Unknown tool '{name}'. Available: {sorted(known_tools)}"
        )
    
    # Check for closing parenthesis
    if not rest.endswith(")"):
        return ExtractionError(
            error_type=ExtractionErrorType.MISSING_CLOSING_PAREN,
            line_number=line_number,
            line_content=line,
            details=f"Missing closing ')' in: '{rest}'"
        )
    
    json_str = rest[:-1].strip()
    
    # Parse JSON
    try:
        args = json.loads(json_str)
        return ToolInvocation(tool_name=name, args=args, line_number=line_number)
    except json.JSONDecodeError as e:
        return ExtractionError(
            error_type=ExtractionErrorType.INVALID_JSON_SYNTAX,
            line_number=line_number,
            line_content=line,
            details=f"JSON parse error: {e.msg} at position {e.pos}. JSON: '{json_str}'"
        )


def extract_tool_invocations_with_errors(
    text: str, 
    known_tools: frozenset[str]
) -> Tuple[List[ToolInvocation], List[ExtractionError]]:
    """
    Pure function that extracts tool invocations and collects errors.
    Returns tuple of (successes, errors) - no side effects.
    """
    results = [
        parse_tool_line(line, idx + 1, known_tools)
        for idx, line in enumerate(text.splitlines())
        if line.strip().startswith("tool:")
    ]
    
    successes = [r for r in results if isinstance(r, ToolInvocation)]
    errors = [r for r in results if isinstance(r, ExtractionError)]
    
    return (successes, errors)


def format_extraction_errors(errors: List[ExtractionError]) -> str:
    """Pure function to format errors for display/logging."""
    if not errors:
        return ""
    
    lines = ["Tool Extraction Errors:"]
    for err in errors:
        lines.append(f"  Line {err.line_number}: [{err.error_type.name}]")
        lines.append(f"    Content: {err.line_content[:80]}...")
        lines.append(f"    Details: {err.details}")
    
    return "\n".join(lines)
```

---

## 2. Agent Self-Healing

### Design Philosophy
When extraction fails, the agent should:
1. **Detect** the failure with meaningful error context
2. **Construct** a corrective prompt explaining what went wrong
3. **Retry** the LLM call with the corrective context
4. **Limit** retries to prevent infinite loops

### Functional Design

#### 2.1 Self-Healing Configuration (Immutable)
```python
class SelfHealingConfig(NamedTuple):
    """Immutable configuration for self-healing behavior."""
    max_retries: int = 3
    include_error_details: bool = True
    include_format_reminder: bool = True

DEFAULT_SELF_HEALING_CONFIG = SelfHealingConfig()
```

#### 2.2 Corrective Prompt Generation (Pure Function)
```python
def generate_corrective_prompt(
    errors: List[ExtractionError],
    original_response: str,
    config: SelfHealingConfig
) -> str:
    """
    Pure function to generate a corrective prompt for the LLM.
    """
    prompt_parts = [
        "I could not parse your tool invocation. Please fix the following issues:"
    ]
    
    if config.include_error_details:
        for err in errors:
            prompt_parts.append(f"- {err.error_type.name}: {err.details}")
    
    if config.include_format_reminder:
        prompt_parts.append("")
        prompt_parts.append("Reminder of correct format:")
        prompt_parts.append("  tool: TOOL_NAME({\"param\": \"value\"})")
        prompt_parts.append("")
        prompt_parts.append("Requirements:")
        prompt_parts.append("  - Use compact single-line JSON")
        prompt_parts.append("  - Use double quotes for strings")
        prompt_parts.append("  - Ensure parentheses are balanced")
    
    prompt_parts.append("")
    prompt_parts.append("Please retry your response with the correct format.")
    
    return "\n".join(prompt_parts)
```

#### 2.3 Self-Healing Loop (Functional with Explicit State)
```python
class HealingAttempt(NamedTuple):
    """Record of a healing attempt."""
    attempt_number: int
    original_response: str
    errors: List[ExtractionError]
    corrective_prompt: str

class HealingResult(NamedTuple):
    """Result of self-healing process."""
    success: bool
    invocations: List[ToolInvocation]
    final_response: str
    attempts: Tuple[HealingAttempt, ...]  # Immutable history


def attempt_extraction_with_healing(
    get_llm_response: Callable[[List[Dict]], str],  # Injected dependency
    conversation: List[Dict[str, Any]],
    known_tools: frozenset[str],
    config: SelfHealingConfig = DEFAULT_SELF_HEALING_CONFIG
) -> HealingResult:
    """
    Functional self-healing extraction with explicit state management.
    Uses recursion instead of mutable loop state.
    """
    
    def heal_recursive(
        current_conversation: List[Dict],
        attempt: int,
        history: Tuple[HealingAttempt, ...]
    ) -> HealingResult:
        # Get LLM response
        response = get_llm_response(current_conversation)
        
        # Attempt extraction
        invocations, errors = extract_tool_invocations_with_errors(response, known_tools)
        
        # Success case: found invocations or no tool lines at all
        if invocations or not any(line.strip().startswith("tool:") for line in response.splitlines()):
            return HealingResult(
                success=True,
                invocations=invocations,
                final_response=response,
                attempts=history
            )
        
        # Failure with retries exhausted
        if attempt >= config.max_retries:
            return HealingResult(
                success=False,
                invocations=[],
                final_response=response,
                attempts=history
            )
        
        # Generate corrective prompt and retry
        corrective_prompt = generate_corrective_prompt(errors, response, config)
        
        new_attempt = HealingAttempt(
            attempt_number=attempt,
            original_response=response,
            errors=errors,
            corrective_prompt=corrective_prompt
        )
        
        # Build new conversation with correction
        updated_conversation = current_conversation + [
            {"role": "assistant", "content": [{"type": "text", "text": response}]},
            {"role": "user", "content": [{"type": "text", "text": corrective_prompt}]}
        ]
        
        # Recursive call - tail-call style
        return heal_recursive(
            updated_conversation,
            attempt + 1,
            history + (new_attempt,)
        )
    
    return heal_recursive(conversation, 0, ())
```

---

## 3. Edit File Guardrails

### Security Threat Model
- **Sensitive Files**: `.env`, `*.pem`, `*.key`, credentials
- **Config Files**: `config.yaml`, `settings.py`, `*.toml` (project config)
- **System Files**: `/etc/*`, `/usr/*`, OS-level configurations

### Functional Design

#### 3.1 Guardrail Rules (Immutable Configuration)
```python
from dataclasses import dataclass
from typing import FrozenSet, Callable

class FileGuardrailRule(NamedTuple):
    """Immutable rule definition."""
    name: str
    description: str
    check: Callable[[Path], bool]  # Returns True if file is BLOCKED

# Define check functions as pure functions
def is_env_file(path: Path) -> bool:
    """Check if file is an environment file."""
    return path.name == ".env" or path.suffix == ".env" or ".env." in path.name

def is_private_key(path: Path) -> bool:
    """Check if file is a private key or certificate."""
    blocked_extensions = frozenset({".pem", ".key", ".p12", ".pfx", ".crt", ".cer"})
    return path.suffix.lower() in blocked_extensions

def is_system_path(path: Path) -> bool:
    """Check if file is in a system directory."""
    system_prefixes = ("/etc", "/usr", "/bin", "/sbin", "/var", "/System", "/Library")
    resolved = str(path.resolve())
    return any(resolved.startswith(prefix) for prefix in system_prefixes)

def is_git_internal(path: Path) -> bool:
    """Check if file is in .git directory."""
    return ".git" in path.parts

def is_sensitive_config(path: Path) -> bool:
    """Check if file is a sensitive configuration file."""
    sensitive_names = frozenset({
        "secrets.yaml", "secrets.yml", "secrets.json",
        "credentials.json", "credentials.yaml",
        ".npmrc", ".pypirc", ".netrc",
        "id_rsa", "id_ed25519", "id_ecdsa"
    })
    return path.name in sensitive_names


# Guardrail rule registry (immutable)
DEFAULT_GUARDRAIL_RULES: Tuple[FileGuardrailRule, ...] = (
    FileGuardrailRule("env_file", "Environment variable files", is_env_file),
    FileGuardrailRule("private_key", "Private keys and certificates", is_private_key),
    FileGuardrailRule("system_path", "System directories", is_system_path),
    FileGuardrailRule("git_internal", "Git internal files", is_git_internal),
    FileGuardrailRule("sensitive_config", "Sensitive configuration files", is_sensitive_config),
)
```

#### 3.2 Guardrail Validation (Pure Functions)
```python
class GuardrailViolation(NamedTuple):
    """Record of a guardrail violation."""
    rule_name: str
    rule_description: str
    file_path: str
    message: str

class GuardrailResult(NamedTuple):
    """Result of guardrail check."""
    allowed: bool
    violations: Tuple[GuardrailViolation, ...]


def check_file_guardrails(
    path: Path,
    rules: Tuple[FileGuardrailRule, ...] = DEFAULT_GUARDRAIL_RULES
) -> GuardrailResult:
    """
    Pure function to check if file edit is allowed.
    Returns GuardrailResult with allowed status and any violations.
    """
    violations = tuple(
        GuardrailViolation(
            rule_name=rule.name,
            rule_description=rule.description,
            file_path=str(path),
            message=f"Blocked by rule '{rule.name}': {rule.description}"
        )
        for rule in rules
        if rule.check(path)
    )
    
    return GuardrailResult(
        allowed=len(violations) == 0,
        violations=violations
    )


def format_guardrail_violations(result: GuardrailResult) -> str:
    """Pure function to format violations for display."""
    if result.allowed:
        return ""
    
    lines = ["⛔ FILE EDIT BLOCKED - Security Guardrail Triggered:"]
    for v in result.violations:
        lines.append(f"  Rule: {v.rule_name}")
        lines.append(f"  Reason: {v.rule_description}")
        lines.append(f"  Path: {v.file_path}")
    
    return "\n".join(lines)
```

#### 3.3 Protected Edit File Tool (Wrapper Pattern)
```python
def create_protected_edit_file_tool(
    base_tool: Callable,
    rules: Tuple[FileGuardrailRule, ...] = DEFAULT_GUARDRAIL_RULES
) -> Callable:
    """
    Higher-order function that wraps edit_file with guardrails.
    Returns a new function - does not mutate the original.
    """
    def protected_edit_file(path: str, old_str: str, new_str: str) -> dict[str, Any]:
        resolved_path = resolve_abs_path(path)
        
        # Check guardrails
        guardrail_result = check_file_guardrails(resolved_path, rules)
        
        if not guardrail_result.allowed:
            return {
                "path": str(resolved_path),
                "action": "blocked",
                "reason": "security_guardrail",
                "violations": [
                    {"rule": v.rule_name, "description": v.rule_description}
                    for v in guardrail_result.violations
                ]
            }
        
        # Delegate to base tool
        return base_tool(path, old_str, new_str)
    
    # Preserve docstring for tool representation
    protected_edit_file.__doc__ = base_tool.__doc__ + """
    
    SECURITY: This tool has guardrails that prevent editing:
    - Environment files (.env)
    - Private keys and certificates (.pem, .key)
    - System directories (/etc, /usr, etc.)
    - Git internal files (.git/)
    - Sensitive configuration files (secrets.yaml, credentials.json)
    """
    
    return protected_edit_file
```

---

## 4. Max API Control

### Goals
- **Prevent Runaway Loops**: Limit total API calls per session
- **Cost Management**: Track and limit token usage
- **Graceful Degradation**: Inform user when limits are reached

### Functional Design

#### 4.1 API Usage State (Immutable)
```python
class APIUsageStats(NamedTuple):
    """Immutable record of API usage."""
    total_calls: int
    total_input_tokens: int
    total_output_tokens: int
    calls_in_current_turn: int

class APILimits(NamedTuple):
    """Immutable API limit configuration."""
    max_calls_per_session: int = 100
    max_calls_per_turn: int = 10
    max_input_tokens_per_session: int = 100_000
    max_output_tokens_per_session: int = 50_000

DEFAULT_API_LIMITS = APILimits()
INITIAL_API_USAGE = APIUsageStats(
    total_calls=0,
    total_input_tokens=0,
    total_output_tokens=0,
    calls_in_current_turn=0
)
```

#### 4.2 Limit Check Functions (Pure)
```python
class LimitExceeded(NamedTuple):
    """Record of which limit was exceeded."""
    limit_name: str
    current_value: int
    max_value: int
    message: str

class LimitCheckResult(NamedTuple):
    """Result of limit check."""
    allowed: bool
    exceeded: Optional[LimitExceeded]


def check_api_limits(
    usage: APIUsageStats,
    limits: APILimits = DEFAULT_API_LIMITS
) -> LimitCheckResult:
    """
    Pure function to check if API call is allowed.
    """
    checks = [
        ("max_calls_per_session", usage.total_calls, limits.max_calls_per_session),
        ("max_calls_per_turn", usage.calls_in_current_turn, limits.max_calls_per_turn),
        ("max_input_tokens_per_session", usage.total_input_tokens, limits.max_input_tokens_per_session),
        ("max_output_tokens_per_session", usage.total_output_tokens, limits.max_output_tokens_per_session),
    ]
    
    for limit_name, current, maximum in checks:
        if current >= maximum:
            return LimitCheckResult(
                allowed=False,
                exceeded=LimitExceeded(
                    limit_name=limit_name,
                    current_value=current,
                    max_value=maximum,
                    message=f"Limit '{limit_name}' exceeded: {current}/{maximum}"
                )
            )
    
    return LimitCheckResult(allowed=True, exceeded=None)
```

#### 4.3 Usage Tracking (Functional State Updates)
```python
def update_usage_after_call(
    usage: APIUsageStats,
    input_tokens: int,
    output_tokens: int
) -> APIUsageStats:
    """
    Pure function that returns NEW usage stats after an API call.
    Does not mutate the input.
    """
    return APIUsageStats(
        total_calls=usage.total_calls + 1,
        total_input_tokens=usage.total_input_tokens + input_tokens,
        total_output_tokens=usage.total_output_tokens + output_tokens,
        calls_in_current_turn=usage.calls_in_current_turn + 1
    )


def reset_turn_usage(usage: APIUsageStats) -> APIUsageStats:
    """
    Pure function to reset per-turn counters.
    Called when starting a new user turn.
    """
    return APIUsageStats(
        total_calls=usage.total_calls,
        total_input_tokens=usage.total_input_tokens,
        total_output_tokens=usage.total_output_tokens,
        calls_in_current_turn=0
    )


def format_usage_stats(usage: APIUsageStats, limits: APILimits) -> str:
    """Pure function to format usage for display."""
    return f"""
API Usage Stats:
  Calls: {usage.total_calls}/{limits.max_calls_per_session}
  Turn Calls: {usage.calls_in_current_turn}/{limits.max_calls_per_turn}
  Input Tokens: {usage.total_input_tokens}/{limits.max_input_tokens_per_session}
  Output Tokens: {usage.total_output_tokens}/{limits.max_output_tokens_per_session}
""".strip()
```

#### 4.4 Rate-Limited LLM Caller (Higher-Order Function)
```python
def create_rate_limited_llm_caller(
    base_caller: Callable[[List[Dict]], Any],  # Returns full response object
    limits: APILimits = DEFAULT_API_LIMITS
) -> Callable:
    """
    Higher-order function that wraps LLM caller with rate limiting.
    Uses closure to maintain usage state (functional approach with managed side-effect).
    """
    # Use a mutable container for state (functional approach to managed state)
    state = {"usage": INITIAL_API_USAGE}
    
    def rate_limited_call(conversation: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Check limits before call
        limit_result = check_api_limits(state["usage"], limits)
        
        if not limit_result.allowed:
            return {
                "success": False,
                "error": "rate_limit_exceeded",
                "content": None,
                "details": limit_result.exceeded._asdict() if limit_result.exceeded else {}
            }
        
        # Make the actual call
        try:
            response = base_caller(conversation)
            
            # Extract token usage from response
            input_tokens = getattr(response.usage, 'prompt_tokens', 0)
            output_tokens = getattr(response.usage, 'completion_tokens', 0)
            content = response.choices[0].message.content
            
            # Update usage state (functional update)
            state["usage"] = update_usage_after_call(
                state["usage"],
                input_tokens,
                output_tokens
            )
            
            return {
                "success": True,
                "error": None,
                "content": content,
                "usage": state["usage"]._asdict()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": "api_error",
                "content": None,
                "details": str(e)
            }
    
    def reset_turn():
        """Reset per-turn counters."""
        state["usage"] = reset_turn_usage(state["usage"])
    
    def get_usage() -> APIUsageStats:
        """Get current usage stats."""
        return state["usage"]
    
    # Attach helper functions
    rate_limited_call.reset_turn = reset_turn
    rate_limited_call.get_usage = get_usage
    
    return rate_limited_call
```

---

## 5. Functional Programming Principles Applied

### 5.1 Core Principles Used

| Principle | Application |
|-----------|-------------|
| **Immutability** | All data structures use `NamedTuple` or `frozenset` |
| **Pure Functions** | All parsing, checking, formatting functions have no side effects |
| **Higher-Order Functions** | `create_protected_edit_file_tool`, `create_rate_limited_llm_caller` |
| **Function Composition** | Building complex behavior from simple, composable functions |
| **Explicit State** | State changes return new objects, not mutations |
| **Type Safety** | Using `Union` types for Result patterns (success/error) |

### 5.2 Module Organization

```
lectures/week2/
├── coding_agent_from_scratch_lecture.py  # Main agent (enhanced)
├── extraction/
│   ├── __init__.py
│   ├── types.py           # ExtractionError, ToolInvocation types
│   ├── parser.py          # parse_tool_line, extract_tool_invocations_with_errors
│   └── formatter.py       # format_extraction_errors
├── self_healing/
│   ├── __init__.py
│   ├── types.py           # HealingAttempt, HealingResult, SelfHealingConfig
│   ├── prompts.py         # generate_corrective_prompt
│   └── healer.py          # attempt_extraction_with_healing
├── guardrails/
│   ├── __init__.py
│   ├── types.py           # GuardrailViolation, GuardrailResult, FileGuardrailRule
│   ├── rules.py           # DEFAULT_GUARDRAIL_RULES, check functions
│   ├── checker.py         # check_file_guardrails
│   └── wrapper.py         # create_protected_edit_file_tool
└── rate_limiting/
    ├── __init__.py
    ├── types.py           # APIUsageStats, APILimits, LimitExceeded
    ├── checker.py         # check_api_limits
    ├── tracker.py         # update_usage_after_call, reset_turn_usage
    └── wrapper.py         # create_rate_limited_llm_caller
```

---

## 6. Integration Example

### Enhanced Agent Loop
```python
def run_enhanced_coding_agent_loop():
    """
    Enhanced agent loop with all features integrated.
    """
    # Setup guardrails
    protected_edit_tool = create_protected_edit_file_tool(edit_file_tool)
    
    enhanced_tool_registry = {
        "read_file": read_file_tool,
        "list_files": list_files_tool,
        "edit_file": protected_edit_tool  # Wrapped with guardrails
    }
    known_tools = frozenset(enhanced_tool_registry.keys())
    
    # Setup rate limiting
    def base_llm_caller(conversation):
        return openai_client.chat.completions.create(
            model="gpt-4",
            messages=conversation,
            max_completion_tokens=2000
        )
    
    rate_limited_caller = create_rate_limited_llm_caller(base_llm_caller)
    
    # Self-healing config
    healing_config = SelfHealingConfig(max_retries=3)
    
    # Build system prompt
    system_prompt = get_full_system_prompt()
    conversation = [{"role": "system", "content": [{"type": "text", "text": system_prompt}]}]
    
    while True:
        try:
            user_input = input(f"{YOU_COLOR}You:{RESET_COLOR} ")
        except (KeyboardInterrupt, EOFError):
            print(f"\n{format_usage_stats(rate_limited_caller.get_usage(), DEFAULT_API_LIMITS)}")
            break
        
        # Reset turn counters
        rate_limited_caller.reset_turn()
        
        conversation.append({
            "role": "user",
            "content": [{"type": "text", "text": user_input.strip()}]
        })
        
        # Inner agent loop with self-healing
        while True:
            # Use self-healing extraction
            healing_result = attempt_extraction_with_healing(
                lambda conv: rate_limited_caller(conv)["content"],
                conversation,
                known_tools,
                healing_config
            )
            
            if not healing_result.success:
                print(f"{ASSISTANT_COLOR}[Self-healing exhausted]{RESET_COLOR}")
                print(healing_result.final_response)
                break
            
            if not healing_result.invocations:
                # No tool calls - regular response
                print(f"{ASSISTANT_COLOR}Assistant:{RESET_COLOR}")
                print(healing_result.final_response)
                conversation.append({
                    "role": "assistant",
                    "content": [{"type": "text", "text": healing_result.final_response}]
                })
                break
            
            # Execute tools
            for invocation in healing_result.invocations:
                tool = enhanced_tool_registry[invocation.tool_name]
                result = execute_tool(tool, invocation.tool_name, invocation.args)
                
                conversation.append({
                    "role": "user",
                    "content": [{"type": "text", "text": f"tool_result({json.dumps(result)})"}]
                })
```

---

## 7. Testing Strategy

### Unit Tests (Pure Functions)
```python
def test_parse_tool_line_valid():
    result = parse_tool_line(
        'tool: read_file({"filename": "test.py"})', 
        1, 
        frozenset({"read_file"})
    )
    assert isinstance(result, ToolInvocation)
    assert result.tool_name == "read_file"
    assert result.args == {"filename": "test.py"}

def test_parse_tool_line_invalid_json():
    result = parse_tool_line(
        'tool: read_file({filename: "test.py"})',  # Missing quotes
        1,
        frozenset({"read_file"})
    )
    assert isinstance(result, ExtractionError)
    assert result.error_type == ExtractionErrorType.INVALID_JSON_SYNTAX

def test_guardrail_blocks_env_file():
    result = check_file_guardrails(Path("/project/.env"))
    assert not result.allowed
    assert any(v.rule_name == "env_file" for v in result.violations)

def test_api_limits_exceeded():
    usage = APIUsageStats(100, 0, 0, 0)  # At max calls
    result = check_api_limits(usage, APILimits(max_calls_per_session=100))
    assert not result.allowed
```

---

## 8. Implementation Order

1. **Phase 1**: Extraction Types & Parser (1 day)
   - Define `NamedTuple` types
   - Implement `parse_tool_line` and `extract_tool_invocations_with_errors`
   - Add unit tests

2. **Phase 2**: Self-Healing (1 day)
   - Implement `generate_corrective_prompt`
   - Implement `attempt_extraction_with_healing`
   - Integration test with mock LLM

3. **Phase 3**: Guardrails (0.5 day)
   - Define rules
   - Implement `check_file_guardrails`
   - Create `create_protected_edit_file_tool` wrapper

4. **Phase 4**: Rate Limiting (0.5 day)
   - Define usage types
   - Implement `check_api_limits` and tracking functions
   - Create `create_rate_limited_llm_caller`

5. **Phase 5**: Integration (0.5 day)
   - Update main agent loop
   - End-to-end testing
   - Documentation

---

## 9. Success Criteria

- [ ] All extraction failures produce actionable error messages
- [ ] Agent successfully self-heals from malformed tool responses (up to 3 retries)
- [ ] `.env` and other sensitive files are blocked from editing
- [ ] API calls are limited and usage is tracked
- [ ] All new code follows functional programming principles
- [ ] Unit test coverage > 90% for new pure functions
