# SonarQube and Trivy Scan Configuration

This document explains how this Todo application is scanned using SonarQube and Trivy in GitHub Actions.

Application stack:

| Layer | Technology | Main files scanned |
| --- | --- | --- |
| Backend | Python, FastAPI | `backend/app`, `backend/requirements.txt`, `backend/Dockerfile` |
| Frontend | React, JavaScript, Vite | `frontend/src`, `frontend/package.json`, `frontend/Dockerfile` |
| Database | PostgreSQL | `database/init.sql` |
| DevOps | Docker Compose | `docker-compose.yml` |

## Tools Used

| Tool | Main purpose | Account required? | Current workflow usage |
| --- | --- | --- | --- |
| SonarQube | Static code analysis for maintainability, bugs, code smells, vulnerabilities, and security hotspots | Yes | Scans `backend/app` and `frontend/src` |
| Trivy | Open-source vulnerability, dependency, container image, secret, and IaC/misconfiguration scanning | No for normal scans | Scans repo filesystem and built Docker images |

## High-Level Flow

```mermaid
flowchart TD
    A[Developer pushes code to GitHub] --> B[GitHub Actions starts security-scan workflow]

    B --> C[SonarQube Scan Job]
    C --> C1[Checkout repository]
    C1 --> C2[Install and build frontend]
    C2 --> C3[Run SonarQube scanner]
    C3 --> C4[Send analysis result to SonarQube server]
    C4 --> C5[View quality gate, bugs, code smells, vulnerabilities, and hotspots]

    B --> D[Trivy Filesystem Scan Job]
    D --> D1[Checkout repository]
    D1 --> D2[Download Trivy vulnerability database]
    D2 --> D3[Scan source tree, dependency manifests, Dockerfiles, compose file]
    D3 --> D4[Upload SARIF result to GitHub Security tab]

    B --> E[Trivy Backend Image Scan Job]
    E --> E1[Build backend Docker image from backend/Dockerfile]
    E1 --> E2[Download or reuse Trivy vulnerability database]
    E2 --> E3[Inspect image OS packages and Python dependencies]
    E3 --> E4[Compare detected packages with vulnerability advisories]
    E4 --> E5[Fail job if HIGH or CRITICAL issues are found]

    B --> F[Trivy Frontend Image Scan Job]
    F --> F1[Build frontend Docker image from frontend/Dockerfile]
    F1 --> F2[Download or reuse Trivy vulnerability database]
    F2 --> F3[Inspect Node build image and Nginx runtime image packages]
    F3 --> F4[Compare detected packages with vulnerability advisories]
    F4 --> F5[Fail job if HIGH or CRITICAL issues are found]
```

## SonarQube Configuration

The repository uses this file:

```text
sonar-project.properties
```

Current configuration:

```properties
sonar.projectKey=todo-app
sonar.projectName=Todo App
sonar.projectVersion=1.0

sonar.sources=backend/app,frontend/src
sonar.exclusions=**/node_modules/**,**/__pycache__/**,**/dist/**

sonar.python.version=3.12
sonar.sourceEncoding=UTF-8
```

### Required Credentials

SonarQube needs an account and token because the scan results are uploaded to a SonarQube server or SonarQube Cloud project.

Add these GitHub repository secrets:

| Secret | Example | Purpose |
| --- | --- | --- |
| `SONAR_TOKEN` | `sqp_xxxxx` | Authenticates the scanner |
| `SONAR_HOST_URL` | `http://your-sonarqube-server:9000` | SonarQube server URL |

For SonarQube Cloud, use:

```text
SONAR_HOST_URL=https://sonarcloud.io
```

For SonarQube Cloud, also add the organization key to `sonar-project.properties`:

```properties
sonar.organization=your-organization-key
```

### What SonarQube Covers

SonarQube is mainly used for source code quality and secure coding checks.

Important issue types:

| Issue type | Meaning |
| --- | --- |
| Bugs | Code likely to behave incorrectly |
| Vulnerabilities | Security-sensitive coding defects |
| Security hotspots | Security-sensitive code that should be reviewed |
| Code smells | Maintainability problems |
| Duplications | Repeated code blocks |
| Coverage | Test coverage, if reports are provided |

### Languages Supported

SonarQube supports many languages depending on edition and version. For this application, the important supported languages are:

| Language / file type | Used in this app? |
| --- | --- |
| Python | Yes, backend FastAPI code |
| JavaScript / JSX | Yes, React frontend |
| CSS | Yes, frontend styling |
| Dockerfile | Useful for Docker-related analysis where supported |
| YAML | Useful for workflow/config analysis where supported |

## Trivy Configuration

Trivy is configured in:

```text
.github/workflows/security-scan.yml
```

The workflow runs three Trivy scans:

| Job | Target | What it checks |
| --- | --- | --- |
| `trivy-filesystem` | Repository files | Dependencies, IaC/misconfigurations, secrets where enabled by Trivy defaults/action settings |
| `trivy-backend-image` | Built backend Docker image | Python base image packages, OS packages, Python dependencies |
| `trivy-frontend-image` | Built frontend Docker image | Node build image packages, Nginx runtime image packages, npm dependencies when detectable |

### Why Trivy Does Not Need an Account

Trivy runs directly on the GitHub Actions runner. It does not need a Trivy account for normal public vulnerability scanning.

Backend image scan flow:

```mermaid
sequenceDiagram
    participant GH as GitHub Actions Runner
    participant Docker as Local Docker Engine
    participant Trivy as Trivy Action
    participant DB as Public Vulnerability Databases
    participant Report as GitHub Security Tab

    GH->>Docker: docker build -t todo-backend:<commit> ./backend
    Docker-->>GH: Backend image exists locally
    GH->>Trivy: Start image scan
    Trivy->>DB: Download latest vulnerability database/advisories
    DB-->>Trivy: Return OS and language package vulnerability data
    Trivy->>Docker: Inspect backend image layers and packages
    Trivy->>Trivy: Match detected packages against known CVEs
    Trivy-->>GH: Produce SARIF report
    GH->>Report: Upload SARIF result
    GH->>GH: Fail job on HIGH or CRITICAL findings
```

### What Trivy Downloads

During a normal scan, Trivy downloads vulnerability databases and advisory data from public sources. It then compares the packages found in this repository or Docker image against known vulnerabilities.

For this backend image:

| Source in image | Example |
| --- | --- |
| Base image OS packages | Debian packages from `python:3.12-slim` |
| Python packages | Packages from `backend/requirements.txt` |
| Application files | Files copied from `backend/app` |

For this frontend image:

| Source in image | Example |
| --- | --- |
| Node build image packages | Packages from `node:22-alpine` build stage |
| Runtime image packages | Packages from `nginx:1.27-alpine` |
| npm packages | React, Vite, and related dependencies |

### What Trivy Covers

Important scan areas:

| Area | Examples |
| --- | --- |
| OS package vulnerabilities | Alpine, Debian, Ubuntu, Red Hat, and other distro packages |
| Language dependency vulnerabilities | Python pip packages, Node.js npm packages, Java Maven packages, Go modules, Ruby gems, Rust crates, .NET NuGet packages, and others |
| Container image vulnerabilities | Vulnerable packages inside Docker images |
| IaC misconfigurations | Dockerfile, Kubernetes, Terraform, Helm, CloudFormation, ARM templates |
| Secrets | Accidentally committed tokens, passwords, and keys |
| SBOM/license support | Can generate and scan SBOM-style inputs depending on configuration |

### Languages and Ecosystems Supported by Trivy

Trivy supports vulnerability scanning for many package ecosystems. Common ones include:

| Ecosystem | Example files |
| --- | --- |
| Python | `requirements.txt`, lock files, installed pip packages |
| Node.js | `package.json`, `package-lock.json`, npm/yarn/pnpm lock files |
| Java | Maven and Gradle dependency files |
| Go | `go.mod`, `go.sum` |
| .NET | NuGet package files |
| PHP | Composer files |
| Ruby | Gemfile and lock files |
| Rust | Cargo files |
| OS packages | `apk`, `dpkg`, `rpm` packages inside images |

## GitHub Actions Workflow Summary

The workflow file is:

```text
.github/workflows/security-scan.yml
```

It runs on:

```yaml
push:
  branches:
    - main
    - master
pull_request:
  branches:
    - main
    - master
workflow_dispatch:
```

The Trivy jobs currently use:

```yaml
severity: HIGH,CRITICAL
ignore-unfixed: true
exit-code: 1
```

Meaning:

| Setting | Meaning |
| --- | --- |
| `severity: HIGH,CRITICAL` | Only fail/report for high-risk findings in this workflow |
| `ignore-unfixed: true` | Ignore issues where no vendor fix is available yet |
| `exit-code: 1` | Fail the GitHub Actions job when matching findings exist |

## When Credentials Are Needed

| Scenario | Credentials needed? | What credential |
| --- | --- | --- |
| SonarQube scan | Yes | `SONAR_TOKEN`, `SONAR_HOST_URL` |
| SonarQube Cloud scan | Yes | `SONAR_TOKEN`, `SONAR_HOST_URL`, usually `sonar.organization` |
| Trivy scan of local repo | No | None |
| Trivy scan of locally built Docker image | No | None |
| Trivy scan of private registry image | Yes | Registry username/password or token |
| Upload SARIF to GitHub Security tab | Usually no custom secret | Uses GitHub Actions token and `security-events: write` permission |

## Local Commands

Run Trivy locally:

```bash
trivy fs .
trivy image todo-backend:local
trivy image todo-frontend:local
```

Build local images first:

```bash
docker build -t todo-backend:local ./backend
docker build -t todo-frontend:local ./frontend
```

Run SonarQube scanner locally after setting credentials:

```bash
sonar-scanner \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.token=<your-token>
```

## Recommended Review Process

1. Pull request opens.
2. GitHub Actions runs SonarQube and Trivy scans.
3. Review SonarQube quality gate for code quality and security hotspots.
4. Review GitHub Security tab for Trivy SARIF findings.
5. Fix `CRITICAL` and `HIGH` findings before merging.
6. Track lower-severity issues separately if they are not blocking.

## References

- SonarQube documentation: https://docs.sonarsource.com/
- SonarQube language overview: https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/languages/overview
- Trivy documentation: https://trivy.dev/
- Trivy vulnerability scanning: https://trivy.dev/docs/latest/scanner/vulnerability/
- Trivy misconfiguration scanning: https://trivy.dev/docs/latest/scanner/misconfiguration/
- Trivy secret scanning: https://trivy.dev/docs/latest/scanner/secret/
