# Security Policy

LocalAgentBench executes **untrusted model-generated code** inside task workdirs on your machine.

- Always review what an eval run did before reusing its workdirs; treat run outputs as untrusted.
- Run evals as a non-admin user; prefer a VM/container for models you don't trust.
- Never commit API keys or credentials. Report accidentally committed secrets immediately so history can be rotated/purged.
- To report a vulnerability: open a GitHub issue titled `[security]` with minimal reproduction details (no exploit code against third parties).
