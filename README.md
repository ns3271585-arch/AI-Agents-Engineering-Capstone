# HR Onboarding & Employee Lifecycle Orchestration Team

Advanced Agentic AI Systems Engineering capstone completed under SDAIA Academy,
delivered via Learning Space.

## Problem

Manual onboarding requires HR, training, contract, and IT teams to coordinate
multiple dependent tasks. This project implements a secure, persistent, multi-agent
workflow that generates and reviews an onboarding package after a candidate is hired.

## Architecture

The project uses LangGraph StateGraph with shared `OnboardingState`, named nodes,
normal edges, conditional edges, an IT retry loop, a reviewer revision loop, and a
human approval interrupt.

### Agents

- Onboarding Coordinator Agent
- Resume Analysis Agent
- Training Plan Agent
- Contract Notification Agent
- IT Provisioning Agent
- Reviewer Agent
- Input and Output Guardrail Agents

### Reasoning patterns

- ReAct-style tool use: Thought summary → Action → Observation
- Plan-and-Execute through the Coordinator
- Hierarchical Delegation to specialized agents
- Reflexion/self-critique through the Reviewer

## Security

- Deterministic prompt-injection blocking before agent/tool execution
- PII and credential masking for public output and logs
- Structured JSONL and CSV monitoring

## Persistence and HITL

The graph is compiled with `SqliteSaver`. A stable `thread_id` allows a workflow
to pause at `interrupt()`, survive graph/checkpointer recreation, and resume using
`Command(resume=...)`.

## Setup

```bash
pip install -r requirements.txt
export GROQ_API_KEY=your_key
uvicorn app:app --reload
```

## Environment variables

- `GROQ_API_KEY` — required for the evaluated LLM run
- `GROQ_MODEL` — optional model override
- `LANGSMITH_API_KEY` — optional LangSmith tracing

Never commit API keys.

## Notebook evidence

The executed notebook demonstrates:

1. Blocked prompt injection
2. Not-hired branch
3. Groq agent calls and function tool use
4. Simulated IT failure and retry
5. Reviewer revision loop
6. Human interrupt
7. SQLite restart and state recovery
8. Human resume
9. PII masking
10. Structured metrics and logs
11. FastAPI endpoint tests

## Run with Docker

```bash
docker build -t hr-onboarding-agent .
docker run -p 8000:8000 hr-onboarding-agent
```

## API

- `GET /health`
- `POST /onboard/validate`
- `GET /latest-package`

## Training attribution

Completed for the **Advanced Agentic AI Systems Engineering** training program,
SDAIA Academy, August 2026.

SDAIA Academy: https://github.com/SDAIAAcademy
