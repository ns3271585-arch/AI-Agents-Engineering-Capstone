# HR Onboarding & Employee Lifecycle Orchestration Team

A secure, persistent, multi-agent HR onboarding system built with LangGraph, Groq, SQLite checkpointing, human approval, guardrails, structured observability, FastAPI, and Docker.

> **Training program:** Advanced Agentic AI Systems Engineering  
> **Delivered by:** SDAIA Academy via Learning Space  
> **Cohort/session dates:** **[ADD THE EXACT PROGRAM DATES BEFORE SUBMISSION]**

---

## Project Description

The **HR Onboarding & Employee Lifecycle Orchestration System** is a secure, persistent, multi-agent AI application designed to coordinate the main activities required after a job candidate has been officially marked as hired.

Employee onboarding commonly requires several departments to exchange information and complete dependent tasks. Human Resources must review the employee’s information, identify onboarding requirements, prepare training, send employment-related notifications, coordinate with Information Technology, validate the generated documents, and obtain final approval.

When these activities are performed manually, information may be duplicated, required steps may be missed, system access may be granted incorrectly, sensitive information may be exposed, and onboarding may be delayed.

This project addresses that problem through a LangGraph workflow that coordinates specialized HR and IT agents using a shared state. The system does not rely on one prompt pretending to perform every responsibility. Instead, it uses multiple named agents, each with a distinct role, structured outputs, and access to the information produced by earlier agents.

The workflow begins only after the candidate’s employment status is marked as `hired`. Before any onboarding agent or HR tool executes, an input guardrail checks the candidate information and resume for prompt-injection or policy-bypass attempts. The system then checks a persistent employee registry using the candidate ID and normalized email address. Unsafe inputs and existing employees are stopped before onboarding work begins.

For a valid hired candidate, the Onboarding Coordinator Agent creates an ordered plan and retrieves department-specific onboarding requirements through a real function tool. The `StateGraph` then routes execution through specialized agents that analyze the resume, identify skill gaps, generate a personalized training plan, prepare an onboarding notification, and create a simulated IT workspace request.

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

The system uses a **centralized graph-orchestration strategy with shared-state communication**.

The LangGraph `StateGraph` acts as the central orchestrator. It routes execution among specialized agents through predefined and conditional edges. The Onboarding Coordinator Agent creates the onboarding plan and retrieves department-specific requirements, while all agents communicate by reading and updating the shared `OnboardingState`.


### Coordination Strategy

The project uses **centralized graph orchestration**. LangGraph determines which
node executes next through normal and conditional edges. The specialized agents
communicate through the shared `OnboardingState`. The Coordinator Agent creates
the onboarding plan and performs requirements-tool calling, but it does not
dynamically select or invoke the other agents.

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
4. Plan: record the onboarding steps that the `StateGraph` will execute through specialized agent nodes.

The project stores a concise reasoning trace and tool trace without exposing hidden chain-of-thought.

### Reflexion and Self-Critique

The Reviewer Agent evaluates the generated package and returns structured feedback. When a problem is found, the graph routes the workflow back for correction and evaluates it again.

---

## Detailed System Architecture

The project uses **centralized graph orchestration with shared-state communication**.

The LangGraph `StateGraph` is the central orchestrator. It determines which node
executes next through normal and conditional edges. The Onboarding Coordinator
Agent creates an operational plan and performs requirements-tool calling, but it
does not dynamically select the other agents. Specialized agents communicate by
reading from and returning updates to the shared `OnboardingState`.

The complete Mermaid architecture is available in
[`architecture.mmd`](architecture.mmd).

### 1. Nodes

A **node** is one executable stage in the LangGraph workflow.

| Node | Agent or component | Main responsibility | State fields written |
|---|---|---|---|
| `input_guardrail` | Input Guardrail Agent | Detect prompt injection and policy-bypass attempts before tools or HR agents execute | `security_status`, `security_reason`, `workflow_status` |
| `employment_check` | Employment Status Agent | Ensure onboarding starts only when `hired=True` | `workflow_status` |
| `employee_uniqueness_check` | Employee Registry Agent | Check candidate ID and normalized email against the persistent employee registry | `employee_exists`, `duplicate_reason`, `existing_employee` |
| `coordinator` | Onboarding Coordinator Agent | Create the operational plan and call the department-requirements tool | `coordination_plan`, `reasoning_trace`, `tool_trace`, `onboarding_requirements` |
| `resume_analysis` | Resume Analysis Agent | Extract skills, identify gaps, and summarize experience | `extracted_skills`, `missing_skills`, `experience_summary` |
| `training_plan` | Training Plan Agent | Select approved courses and render the personalized plan | `training_plan` |
| `contract_notification` | Contract Notification Agent | Draft and render the onboarding notification | `contract_notification` |
| `it_provisioning` | IT Provisioning Agent | Select least-privilege access/equipment and create an IT ticket | `it_request`, `it_ticket_id`, `it_status`, `it_retry_count` |
| `review` | Reviewer Agent | Validate completeness and consistency; provide Reflexion feedback | `quality_score`, `review_feedback`, `workflow_status` |
| `prepare_revision` | Revision Coordinator | Increment the revision counter before regenerating outputs | `revision_count`, `workflow_status` |
| `human_approval` | HITL approval node | Pause with `interrupt()` and resume with `Command(resume=...)` | `human_decision`, `human_comments` |
| `output_guardrail` | Output Guardrail Agent | Mask email, phone, IDs, API keys, tokens, and passwords in public output | `public_summary` |
| `employee_registration` | Employee Registry Agent | Re-check uniqueness immediately before writing the employee once | `employee_registration`, duplicate fields |
| `finalize` | Finalization Agent | Assemble and persist the approved onboarding package | `final_package`, `workflow_status` |
| `blocked` | Terminal node | End unsafe requests | `errors`, `workflow_status` |
| `not_hired` | Terminal node | End requests for candidates who are not hired | `workflow_status` |
| `duplicate_employee` | Terminal node | Stop duplicate onboarding and prevent a second employee record | `errors`, `workflow_status` |
| `rejected_end` | Terminal node | End a human-rejected onboarding package | `workflow_status` |

### 2. Agents

The system includes distinct named agents with separate responsibilities:

1. **Input Guardrail Agent** — blocks unsafe instructions.
2. **Employment Status Agent** — checks hiring eligibility.
3. **Employee Registry Agent** — prevents duplicate employees and performs one-time registration.
4. **Onboarding Coordinator Agent** — creates the plan and calls the requirements tool.
5. **Resume Analysis Agent** — extracts skills and identifies gaps.
6. **Training Plan Agent** — selects approved training and generates a plan.
7. **Contract Notification Agent** — prepares the onboarding communication.
8. **IT Provisioning Agent** — creates the least-privilege workspace request.
9. **Reviewer Agent** — performs quality review and Reflexion.
10. **Output Guardrail Agent** — protects sensitive public output.
11. **Finalization Agent** — persists the approved package.

Their communication mechanism is the shared `OnboardingState`; they do not use one
prompt that merely imitates several personas.

### 3. Tools

The workflow calls real executable tools:

| Tool | Called by | Purpose | Persistent result |
|---|---|---|---|
| `lookup_onboarding_requirements` | Coordinator Agent | Return mandatory training, default access, and equipment for the department and position | Stored in `onboarding_requirements` |
| `search_training_catalog` | Training Plan Agent | Search the approved local catalogue using department and missing skills | Used to render the training plan |
| `create_it_workspace_request` | IT Provisioning Agent | Create a structured IT ticket | `artifacts/IT-*.json` |
| `check_employee_exists` | Employee Registry Agent | Check candidate ID and email before onboarding | Duplicate decision in shared state |
| `register_employee` | Employee Registry Agent | Re-check uniqueness and write a new employee only once | `data/employee_registry.json` |

The Coordinator’s requirements lookup is demonstrated through model-generated
function calling, while the other tools are invoked through their executable tool interfaces.

### 4. Edges and Conditions

An **edge** determines how execution moves between nodes.

#### Normal edges

```text
coordinator
→ resume_analysis
→ training_plan
→ contract_notification
→ it_provisioning
→ review
```

#### Conditional edges

| Source node | Condition | Destination |
|---|---|---|
| `input_guardrail` | Input is safe | `employment_check` |
| `input_guardrail` | Prompt injection detected | `blocked` |
| `employment_check` | `hired=True` | `employee_uniqueness_check` |
| `employment_check` | `hired=False` | `not_hired` |
| `employee_uniqueness_check` | No matching candidate ID/email | `coordinator` |
| `employee_uniqueness_check` | Existing employee found | `duplicate_employee` |
| `it_provisioning` | Ticket submitted | `review` |
| `it_provisioning` | Failure and retry limit not exceeded | `it_provisioning` |
| `review` | Score passes and package is approved | `human_approval` |
| `review` | Revision needed and revision limit not exceeded | `prepare_revision` |
| `human_approval` | Human approves | `output_guardrail` |
| `human_approval` | Human requests revision | `prepare_revision` |
| `human_approval` | Human rejects | `rejected_end` |
| `employee_registration` | Second uniqueness check passes | `finalize` |
| `employee_registration` | Duplicate detected before write | `duplicate_employee` |

### 5. Loops

The graph contains two genuine bounded loops:

- **IT retry loop:** `it_provisioning → it_provisioning` while
  `it_retry_count <= max_it_retries`.
- **Reviewer revision loop:** `review → prepare_revision → training_plan` while
  `revision_count < max_revisions`.

Both loops terminate through explicit state conditions.

### 6. Shared State

`OnboardingState` is the workflow’s shared short-term memory. It carries:

- Candidate inputs
- Guardrail decisions
- Employee-existence results
- Coordinator plan and tool observations
- Resume analysis
- Training plan
- Contract notification
- IT request and retry counters
- Reviewer score and feedback
- Human decision
- Registration result
- Final package and errors

Every node reads the state and returns only the fields it updates.

### 7. Persistence and HITL

The graph is compiled with `SqliteSaver` and a stable `thread_id`.

The `human_approval` node calls `interrupt()`. The notebook demonstrates:

1. Pausing before approval
2. Closing the original SQLite connection
3. Recreating the graph and checkpointer
4. Recovering the same state and next node
5. Resuming through `Command(resume=...)`

### 8. Guardrails and Observability

- The input guardrail blocks prompt injection before tools and HR agents execute.
- The output guardrail masks PII and credentials.
- `log_event()` writes structured events to `agent_events.jsonl`.
- Metrics including latency, tool calls, retries, revisions, failures, and errors
  are written to `metrics.csv`.

### 9. Generated Outputs and Deployment

The workflow generates:

- Personalized training plan
- Contract/onboarding notification
- IT ticket JSON
- Employee-registry record
- Final onboarding package
- JSONL event logs
- CSV metrics

The repository also includes FastAPI endpoints, a Dockerfile, and a dependency
file as production/deployment artifacts.


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
git clone <YOUR_REPOSITORY_URL>
cd HR-Onboarding-Agentic-System
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

Replace the placeholders below with the team members’ names before submission.

| Team Member | Main Responsibilities |
|---|---|
| **[TEAM MEMBER 1 NAME]** | Agentic reasoning, shared state, LangGraph nodes, edges, conditional routing, retry and revision loops |
| **[TEAM MEMBER 2 NAME]** | Specialized HR agents, function tools, templates, guardrails, and observability |
| **[TEAM MEMBER 3 NAME]** | SQLite persistence, human-in-the-loop approval, FastAPI, Docker, GitHub integration, and final execution evidence |

---

## Training Attribution

This project was completed as part of the:

**Advanced Agentic AI Systems Engineering Program**  
**SDAIA Academy, delivered via Learning Space**  
**Cohort/session dates:** **[ADD THE EXACT PROGRAM DATES BEFORE SUBMISSION]**

SDAIA Academy GitHub: <https://github.com/SDAIAAcademy>

---

## License and Usage

This repository was created for educational and capstone-evaluation purposes. Review all generated HR content before using it in a real organization.
