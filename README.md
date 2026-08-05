# HR Onboarding & Employee Lifecycle Orchestration Team

A secure, persistent, multi-agent HR onboarding system built with LangGraph, Groq, SQLite checkpointing, human approval, guardrails, structured observability, FastAPI, and Docker.

> **Students:** Noura Almuqbil, Moudi Alhomoud, Shahad Alotaish

> **Training program:** Advanced Agentic AI Systems Engineering
  
> **Delivered by:** SDAIA Academy via Learning Space

> **Trainer:** Mohammed Albeladi

> **Cohort/session dates:** **August 2 - August 6**

---

## Project Description

The **HR Onboarding & Employee Lifecycle Orchestration System** is a secure, persistent, multi-agent AI application designed to coordinate the main activities required after a job candidate has been officially marked as hired.

Employee onboarding commonly requires several departments to exchange information and complete dependent tasks. Human Resources must review the employee’s information, identify onboarding requirements, prepare training, send employment-related notifications, coordinate with Information Technology, validate the generated documents, and obtain final approval.

When these activities are performed manually, information may be duplicated, required steps may be missed, system access may be granted incorrectly, sensitive information may be exposed, and onboarding may be delayed.

This project addresses that problem through a LangGraph workflow that coordinates specialized HR and IT agents using a shared state. The system does not rely on one prompt pretending to perform every responsibility. Instead, it uses multiple named agents, each with a distinct role, structured outputs, and access to the information produced by earlier agents.

The workflow begins only after the candidate’s employment status is marked as `hired`. Before any onboarding agent or HR tool executes, an input guardrail checks the candidate information and resume for prompt-injection or policy-bypass attempts. The system then checks a persistent employee registry using the candidate ID and normalized email address. Unsafe inputs and existing employees are stopped before onboarding work begins.

For a valid hired candidate, the Onboarding Coordinator Agent creates an ordered plan and retrieves department-specific onboarding requirements through a real function tool. The workflow then delegates tasks to specialized agents that analyze the resume, identify skill gaps, generate a personalized training plan, prepare an onboarding notification, and create a simulated IT workspace request.

A Reviewer Agent evaluates the complete onboarding package for correctness, completeness, mandatory training coverage, appropriate IT access, and consistency. If deficiencies are detected, the graph follows a revision edge and regenerates the affected outputs. The revision loop is bounded by a maximum revision counter so the workflow cannot continue indefinitely.

Before finalization, the graph pauses at a genuine human-in-the-loop approval node. An HR manager can approve, request revision, or reject the package. Workflow state is persisted using a SQLite LangGraph checkpointer, allowing the process to survive graph or application recreation and resume later using the same thread identifier.

After approval, an output guardrail creates a protected public summary in which sensitive information is masked. Immediately before adding the employee, the registration tool performs a second duplicate check. Only a new employee is written to the persistent registry; a duplicate is routed to a terminating duplicate-employee branch. The system then saves the final onboarding package, generated IT ticket, structured logs, and execution metrics.

For production-readiness evidence, the repository includes a FastAPI application, Dockerfile, dependency file, `.gitignore`, Mermaid architecture diagram, generated artifacts, and an executed Colab notebook containing successful, failure, security, retry, persistence, and human-approval demonstrations.

---

## Problem Statement

Traditional onboarding requires coordination among Human Resources, training teams, hiring managers, and Information Technology. Important information is often transferred manually through emails, documents, and separate systems.

This can lead to:

- Missing mandatory onboarding courses
- Incorrect or excessive system access
- Delayed IT workspace preparation
- Inconsistent employee information across documents
- Unreviewed AI-generated content
- Exposure of personal or confidential information
- Loss of progress when a long-running process is interrupted
- Limited visibility into agent actions, failures, and response times

The project provides one orchestrated workflow that manages these tasks while enforcing security, traceability, persistence, and human oversight.

---

## System Objectives

The system is designed to:

1. Start onboarding only for candidates marked as hired.
2. Detect and block prompt-injection or approval-bypass attempts before tool execution.
3. Prevent duplicate employees by checking candidate ID and email before onboarding.
4. Re-check uniqueness immediately before registration and add the employee only once.
5. Retrieve department-specific onboarding requirements through a real function tool.
6. Analyze the candidate’s resume and identify skills and gaps.
7. Generate a personalized training plan from an approved catalogue.
8. Create a professional onboarding notification using a Jinja2 template.
9. Generate and persist a simulated IT workspace ticket.
10. Review the complete package and request revision when requirements are missing.
11. Pause for a real HR-manager decision before finalization.
12. Persist graph state so interrupted workflows can resume later.
13. Mask sensitive information in public output and monitoring records.
14. Capture structured logs, latency, failures, retries, and revisions.
15. Provide FastAPI and Docker artifacts as deployment evidence.

---

## Multi-Agent Architecture

The system uses a **centralized graph orchestration with shared-state handoffs**.

The Onboarding Coordinator Agent acts as the central supervisor. It creates the onboarding plan, invokes the requirements tool, stores the result in shared state, and delegates work to specialized agents.

### Agents and Responsibilities

#### 1. Input Guardrail Agent

Examines the candidate’s resume and onboarding input before the workflow begins.

It detects attempts such as:

- Ignoring previous instructions
- Revealing the system prompt
- Bypassing human approval
- Approving a candidate without review
- Extracting passwords, tokens, or API keys

Unsafe input is routed directly to the blocked end state.

#### 2. Employee Registry Agent

Checks whether a candidate is already present before onboarding begins.

It compares:

- Candidate ID
- Normalized email address

If either value matches an existing employee, the graph routes to a duplicate-employee end node before the Coordinator Agent or onboarding tools run.

After human approval, the same registration tool performs a second uniqueness check immediately before writing the record. This prevents both ordinary duplicate submissions and a duplicate created between the initial check and final registration.

#### 3. Onboarding Coordinator Agent

Acts as the workflow supervisor.

Responsibilities:

- Create the onboarding execution plan
- Apply Plan-and-Execute reasoning
- Call the onboarding-requirements function tool
- Store the tool result in shared state
- Coordinate the specialized agents

#### 4. Resume Analysis Agent

Analyzes the candidate’s supplied resume and returns structured fields:

- Extracted skills
- Missing or onboarding-related skills
- Experience summary

Its output is consumed by the Training Plan Agent.

#### 5. Training Plan Agent

Creates a personalized onboarding training plan.

It:

- Reads missing skills from the Resume Analysis Agent
- Reads mandatory courses from department requirements
- Calls the approved training-catalogue search tool
- Generates a structured training recommendation
- Formats the final plan using Jinja2

#### 6. Contract Notification Agent

Creates the candidate’s onboarding or employment-notification message using:

- Candidate name
- Position
- Department
- Start date
- Approved HR wording
- A reusable Jinja2 template

It does not generate unsupported compensation terms or legal promises.

#### 7. IT Provisioning Agent

Determines the system access and equipment required for the employee’s role.

It applies least-privilege principles and calls a real Python function tool that creates and saves a simulated IT workspace ticket containing:

- Ticket ID
- Candidate ID
- Employee name
- Department
- Position
- Required access
- Required equipment
- Start date
- Submission status

#### 8. Reviewer Agent

Acts as the quality-control and Reflexion agent.

It checks:

- Mandatory training coverage
- Required IT access
- Candidate-name consistency
- Position consistency
- Start-date consistency
- IT-ticket completion
- Overall package completeness

If the quality score is below the threshold, the graph follows a conditional revision edge and returns to the generation stage.

#### 9. Human Approval Node

Pauses the graph before finalization.

The HR manager can provide one of three decisions:

- `approved`
- `revise`
- `rejected`

The graph resumes only after human input is supplied.

#### 10. Output Guardrail Agent

Creates a protected public summary and masks:

- Email addresses
- Phone numbers
- National-ID-like values
- Passwords
- API keys
- Tokens

#### 11. Finalization Agent

Combines the approved outputs into the final onboarding package and persists the result as a JSON artifact.

---

## Agentic Reasoning Patterns

The project explicitly implements several reasoning patterns.

### Plan-and-Execute

The Coordinator Agent first creates an ordered onboarding plan. The graph then executes that plan through specialized nodes.


### ReAct-Style Tool Use

The Coordinator follows a visible operational sequence:

1. Thought summary: determine which onboarding requirements are needed.
2. Action: call the onboarding-requirements tool.
3. Observation: receive the department-specific result.
4. Plan: delegate execution to specialized agents.

The project stores a concise reasoning trace and tool trace without exposing hidden chain-of-thought.

### Reflexion and Self-Critique

The Reviewer Agent evaluates the generated package and returns structured feedback. When a problem is found, the graph routes the workflow back for correction and evaluates it again.

---

## Graph-Based Orchestration

The system is implemented using a real LangGraph `StateGraph`.

The graph includes:

- Named nodes
- Directed edges
- Shared state
- Conditional edges
- Multiple termination paths
- An IT retry loop
- A reviewer revision loop
- A human approval interrupt

### Main Workflow

```text
START
  ↓
Input Guardrail
  ├── Blocked → Blocked End
  └── Safe
        ↓
Employment Status Check
  ├── Not Hired → Not-Hired End
  └── Hired
        ↓
Employee Uniqueness Check
  ├── Existing Employee → Duplicate Employee End
  └── New Employee
        ↓
Onboarding Coordinator Agent
        ↓
Resume Analysis Agent
        ↓
Training Plan Agent
        ↓
Contract Notification Agent
        ↓
IT Provisioning Agent
  ├── Tool Failure → Retry IT Provisioning
  └── Success
        ↓
Reviewer Agent
  ├── Revision Required → Revision Coordinator → Training Plan Agent
  └── Approved
        ↓
Human Approval Interrupt
  ├── Revise → Revision Coordinator
  ├── Reject → Rejected End
  └── Approve
        ↓
Output Guardrail Agent
        ↓
Employee Registration + Second Duplicate Check
  ├── Duplicate Detected → Duplicate Employee End
  └── Registered
        ↓
Finalization Agent
        ↓
END
```

The Mermaid source is also available in [`architecture.mmd`](architecture.mmd).

---

## Shared State

All graph nodes communicate through a shared `OnboardingState`.

The state stores:

- Candidate information
- Security status
- Employee-existence decision
- Duplicate reason and matched employee
- Employee-registration result
- Coordinator plan
- Reasoning and tool traces
- Department requirements
- Resume-analysis results
- Training plan
- Contract notification
- IT request
- Quality score
- Reviewer feedback
- Retry and revision counters
- Human decision
- Final package
- Errors and workflow status

This allows each agent to use outputs produced by earlier agents without requiring the user to repeat information.

---

## Real Tools

The project includes real executable function tools.

### `lookup_onboarding_requirements`

Returns:

- Mandatory training
- Default system access
- Equipment requirements
- Department
- Position

### `search_training_catalog`

Searches the approved local training catalogue using:

- Department
- Missing skills

### `check_employee_exists`

Checks the persistent employee registry by candidate ID and normalized email.

### `register_employee`

Performs a second uniqueness check and writes a new employee record only when no match exists.

### `create_it_workspace_request`

Creates and saves a structured IT workspace ticket as a JSON artifact.

These tools execute through a tool interface and are not represented by hardcoded text outputs.

---

## Security and Guardrails

### Input Security

The deterministic input guardrail blocks known injection and policy-bypass patterns before any HR agent or tool executes.

The executed notebook demonstrates an attack containing instructions to ignore previous rules, reveal the system prompt, and approve the candidate without review. The request is blocked before the requirements tool or Training Plan Agent can run.

### Output and Data Protection

Sensitive values are masked in:

- Public API output
- Public onboarding summaries
- Structured logs
- Monitoring evidence

### Fail-Safe Behavior

Security decisions are deterministic and are not left entirely to an LLM. Required policy checks cannot be overridden by an agent-generated response.

---

## Observability

The system records structured monitoring data in:

```text
artifacts/agent_events.jsonl
artifacts/metrics.csv
```

Captured information includes:

- Timestamp
- Thread ID
- Candidate ID
- Node
- Agent
- Event type
- Status
- Latency
- Tool name
- Revision count
- Retry count
- Error type
- Error message

The executed evidence includes:

- Successful LLM calls
- Function-tool calls
- A simulated IT-service failure
- A successful retry
- Reviewer revision activity
- Human approval
- Output protection
- Finalization

---

## Persistence and Human-in-the-Loop

The graph is compiled with LangGraph `SqliteSaver`.

Each workflow is associated with a stable `thread_id`.

The executed notebook demonstrates that the system can:

1. Run until the human-approval interrupt.
2. Persist candidate data and intermediate outputs.
3. Close the original SQLite connection.
4. Create a new graph and database connection.
5. Recover the same candidate and workflow position.
6. Resume using `Command(resume=...)`.
7. Continue to output protection and finalization.

This proves the workflow does not depend only on in-memory state.

---

## Production and Deployment Artifacts

The repository contains:

```text
Master_Final_HR_Onboarding.ipynb
README.md
app.py
Dockerfile
requirements.txt
.gitignore
architecture.mmd
data/
templates/
artifacts/
```

### FastAPI Endpoints

The API includes:

- `GET /health`
- `POST /onboard/validate`
- `GET /latest-package`

The executed notebook demonstrates:

- A successful health check
- Acceptance of a safe onboarding request
- Rejection of a prompt-injection request
- Retrieval of the latest onboarding package

---

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/ns3271585-arch/AI-Agents-Engineering-Capstone.git
cd AI-Agents-Engineering-Capstone
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

The main evaluated notebook uses Colab Secrets.

Add:

```text
GROQ_API_KEY
```

Optional variables:

```text
GROQ_MODEL
LANGSMITH_API_KEY
```

Never commit API keys or secrets to GitHub.

### 4. Run the notebook

Open:

```text
Master_Final_HR_Onboarding.ipynb
```

Run all cells from top to bottom.

The final evaluated run should display:

```text
LLM_MODE: True
```

### 5. Run the FastAPI application

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000/docs
```

---

## Docker

Build the image:

```bash
docker build -t hr-onboarding-agent .
```

Run the container:

```bash
docker run -p 8000:8000 hr-onboarding-agent
```

The API will be available at:

```text
http://localhost:8000
```

---

## Repository Structure

```text
HR-Onboarding-Agentic-System/
├── Master_Final_HR_Onboarding.ipynb
├── README.md
├── app.py
├── Dockerfile
├── requirements.txt
├── .gitignore
├── architecture.mmd
│
├── data/
│   ├── training_catalog.json
│   └── employee_registry.json
│
├── templates/
│   ├── contract_notification.j2
│   └── training_plan.j2
│
└── artifacts/
    ├── agent_events.jsonl
    ├── metrics.csv
    ├── final_onboarding_package.json
    └── IT-*.json
```

---

## Project Scope

The implemented capstone focuses on the onboarding phase that begins after a candidate has been marked as hired.

### Included Scope

- Candidate validation
- Duplicate-employee prevention
- Persistent employee registration
- Resume analysis
- Training recommendations
- Contract/onboarding notification
- IT provisioning request
- Automated review
- Revision loops
- Human approval
- Persistent workflow state
- Security and monitoring
- API and Docker artifacts

### Future Extension Opportunities

The architecture can later be extended with new graph nodes for:

- Probation review
- Role transfer
- Promotion
- Access modification
- Offboarding

These later lifecycle processes are future extensions and are not claimed as part of the currently executed capstone.

---

## Evidence of Execution

The executed notebook includes:

1. Graph visualization
2. Blocked prompt-injection attempt
3. Not-hired conditional branch
4. Groq-backed agent execution
5. Model-generated function call
6. IT failure and retry
7. Reviewer revision loop
8. Human interrupt
9. SQLite restart and recovery
10. Human approval and resume
11. PII masking
12. JSONL and CSV monitoring
13. FastAPI endpoint tests
14. Final generated onboarding package

---

## Limitations

This project is an educational capstone and uses simulated enterprise services.

- The IT workspace tool creates local JSON tickets rather than connecting to a real corporate IT service.
- The training catalogue is a controlled local dataset.
- The contract notification is an onboarding communication template, not a legally binding employment contract.
- The system does not replace legal, HR, security, or managerial judgment.
- Human approval remains mandatory before finalization.

---

## Team Responsibilities


| Team Member | Main Responsibilities |
|---|---|
| **Moudi Alhomoud** | Agentic reasoning, shared state, LangGraph nodes, edges, conditional routing, retry and revision loops |
| **Shahad Alotaish** | Specialized HR agents, function tools, templates, guardrails, and observability |
| **Noura Almuqbil** | SQLite persistence, human-in-the-loop approval, FastAPI, Docker, GitHub integration, and final execution evidence |

---

## Training Attribution

This project was completed as part of the:

**Advanced Agentic AI Systems Engineering Program**  
**SDAIA Academy, delivered via Learning Space**  

SDAIA Academy GitHub: <https://github.com/SDAIAAcademy>

---

## License and Usage

This repository was created for educational and capstone-evaluation purposes. Review all generated HR content before using it in a real organization.
