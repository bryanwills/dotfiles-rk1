# Contributing Guidelines

Contributions are welcome, but high standards are maintained for code quality, portability, and documentation. To avoid having a pull request closed without review, ensure the submission strictly adheres to the following rules.

## Submission Requirements

* **Mandatory Documentation:** Every new script or tool must include a dedicated `README.md` file (or a clear documentation section) explaining its purpose, dependencies, installation steps, and explicit usage instructions with examples.
* **Tested and Functional:** Code must be fully tested in a clean environment prior to submission. Broken, incomplete, or conceptual "vibe-coded" scripts will not be accepted.
* **No AI-Generated Slop:** Low-effort, automated, or untested LLM-generated pull requests will be rejected straight away. If code is generated with assistance, the author must fully understand the logic and verify its stability.
* **Shell Portability:** Scripts utilizing a `#!/bin/sh` shebang must adhere strictly to POSIX standards. Avoid using Bash or Zsh extensions unless explicitly targeting those shells with the correct interpreter.

## Review Process

Pull requests that violate these rules or fail basic execution tests will be closed immediately without a debugging cycle.
