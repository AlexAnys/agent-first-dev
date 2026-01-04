# CS146S: Building a Coding Agent Recap

## 🏛️ The Four Pillars of Coding Agents

| Pillar | Concept | Implementation Detail |
| :--- | :--- | :--- |
| **1. Reasoning 🧠** | The ReAct Loop | A cycle of Thought → Action → Observation that allows the agent to process feedback. |
| **2. Capability 🛠️** | Dynamic Tool Registry | Using `inspect.signature` to automatically tell the LLM what tools are available. |
| **3. Communication 🌉** | The Parsing Bridge | Using Regex to translate the LLM's text into executable Python function calls. |
| **4. Security 🛡️** | Guardrails & Safety | Using sandboxes, "human-in-the-loop," and declarative changes to protect the system. |

## 🔄 The Lifecycle of a Fix

When our agent encounters a bug, it follows a specific sequence within its control loop:

1.  **Analyze**: The agent receives an error (e.g., an `AssertionError`) as an Observation. 🧐
2.  **Act**: It uses `read_file` to see the code and `write_file` to apply a hypothesized fix. ✍️
3.  **Verify**: It uses a tool like `run_command` to execute tests and ensure the fix works without breaking other things. ✅

## 🛡️ Best Practices for Robust Agents

*   **High-Signal Feedback**: Tools should return specific error messages (line numbers, expected vs. actual values) so the agent doesn't get stuck in an infinite loop. 📡
*   **Environment Integrity**: Avoid "Environment Drift" by having the agent modify dependency files (like `requirements.txt`) rather than running raw install commands. 🏗️
*   **Version Control**: Always run agents on a branch or worktree so that changes can be easily reverted if something goes wrong. 🕒

## 🔌 Designing AI-Native APIs (MCP Principles)

"AI-native" APIs are designed for models to understand, call, and orchestrate, moving beyond traditional rigid RPCs meant primarily for human engineers.

### Why AI-Native?
When agents interact with numerous tools within limited context windows, the interface must be **AI-friendly**. Rigid APIs often suffer from fragmented structures, obscure parameter naming, and inconsistent error handling, making it difficult for models to understand or chain them reliably. AI-native design treats the model as the **primary consumer**, significantly reducing the cognitive load for the agent.

### Key Principles for AI-Native Interfaces:

*   **Semantic Tool Descriptions**: Provide clear names, purpose summaries, and specific usage scenarios. Use strict **JSON Schemas** so models can accurately choose tools and populate parameters (standardized in MCP's `tools/list`).
*   **Consistent I/O Formats**: Return structured data with machine-parsable status codes and errors. Avoid "magic strings" or human-only text; where necessary, provide a concise "summary" field to help the model process the result quickly.
*   **Task & Intent-Oriented**: Encapsulate complex multi-step workflows into composable primitives or high-level tasks. This allows the model to chain operations logically without needing to manage low-level plumbing.
*   **Built-in Constraints & Security**: Define explicit rate limits, permission boundaries, and audit logs. Use "dry-run" or rollable operations to enable safe execution and "Human-in-the-Loop" validation.
*   **Streaming & Incremental Support**: Provide progress updates and partial results via SSE or stdio. This allows models to "observe and re-plan" during long tasks rather than waiting indefinitely for a single large response.
*   **Example-Driven Alignment**: Include built-in few-shot examples, common usage patterns, and clear failure/recovery paradigms to align the agent's behavior with the developer's intent.

> **Summary**: Design your interfaces as tools that models can see, safely invoke, and stably combine. The goal is to let the agent spend less time "guessing" and more time completing tasks. **"Design APIs to be AI-native rather than rigid."**