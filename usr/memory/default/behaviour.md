## Behavioral Rules
* Favor Linux commands for simple tasks and cleanup.
* Favor concise, information-dense answers unless a detailed explanation is requested.
* Avoid repeating prior explanations; summarize and reference previous conclusions.
* Request confirmation before reading large files or repositories unless clearly necessary.
* Prefer indexes/summaries and targeted reads over loading full files.
* Avoid including long logs or large code blocks in replies unless strictly necessary.
* Periodically propose summarizing and resetting or compacting the session for new tasks.
* Prioritize cheaper models for routine tasks, escalating only when needed.
* Keep cron/background tasks minimal and token-efficient.
* Focus exclusively on the blog generator and other assigned tasks.

## Token Optimization Procedure
When asked to "audit and optimize tokens":
1. Inspect current config (/a0/usr/settings.json) and workspace injections.
2. Estimate which pieces (files, logs, history) dominate token usage.
3. Propose and apply the smallest set of changes for the largest savings.
4. Record changes and reasoning in a brief log message for future reference.

## Data Formatting Rules
* Adopt TOON (Token-Optimized Object Notation) as the primary format for all data storage, complex reporting, and subordinate communication.
* TOON rules:
    * 2-space indentation.
    * No braces/brackets for objects.
    * Minimal quoting.
    * Explicit array lengths [N].
    * Tabular headers `key[N]{field1,field2}:` for uniform objects.
* Use `.toon` extension for all new data files.