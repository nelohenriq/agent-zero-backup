---
name: "agent-orchestrator"
description: "Meta-agent skill for orchestrating complex tasks through autonomous sub-agents. Decomposes macro tasks into subtasks, spawns specialized sub-agents with dynamically generated SKILL.md files, coordinates file-based communication, consolidates results, and dissolves agents upon completion."
version: "1.0.0"
author: "Agent Zero"
tags: ["orchestration", "multi-agent", "decomposition", "meta-agent"]
trigger_patterns:
  - "orchestrate"
  - "multi-agent"
  - "decompose task"
  - "spawn agents"
  - "sub-agents"
  - "parallel agents"
  - "agent coordination"
  - "task breakdown"
  - "meta-agent"
  - "agent factory"
  - "delegate tasks"
---

# Agent Orchestrator

Meta-agent skill for orchestrating complex tasks through autonomous sub-agents. Decomposes macro tasks into subtasks, spawns specialized sub-agents with dynamically generated SKILL.md files, coordinates file-based communication, consolidates results, and dissolves agents upon completion.

## Core Workflow

### Phase 1: Task Decomposition
Analyze the macro task and break it into independent, parallelizable subtasks:
1. Identify the end goal and success criteria.
2. List all major components/deliverables required.
3. Determine dependencies between components.
4. Group independent work into parallel subtasks.
5. Create a dependency graph for sequential work.

**Decomposition Principles:**
- Each subtask should be completable in isolation.
- Minimize inter-agent dependencies.

### Phase 2: Agent Spawning & Specialized Skills
For each subtask, generate a specialized SKILL.md and spawn a sub-agent:
1. Define the sub-agent's role and objective.
2. Generate a custom SKILL.md template for the specific subtask.
3. Use call_subordinate to spawn the agent with the generated profile.
4. Ensure sub-agents are instructed to deliver results via the response tool (ending their task) and never attempt orchestration themselves.

### Phase 3: Coordination & Communication
Manage the execution and information flow:
- Use file-based communication (inbox/outbox structure).
- Monitor status.json of sub-agents.
- Handle inter-agent dependencies by passing outputs as inputs.

### Phase 4: Consolidation
Integrate all sub-agent outputs into the final deliverable:
1. Collect all agent outputs from their respective outboxes.
2. Identify overlaps and conflicts.
3. Merge compatible content.
4. Resolve conflicts and document decisions.
5. Validate the integrated output.

## Success Criteria
- All inputs successfully merged.
- Conflicts documented and resolved.
- Integrated output is coherent.
- No data loss.

## Communication Protocol
- Read from: inbox/, other agent outbox/ directories.
- Write to: outbox/.
- Status: status.json.
