"""Knowledge base - project scanning and patterns."""
import json
from pathlib import Path

from . import db

IGNORE_DIRS = {".git", ".agent", "__pycache__", "node_modules", ".venv", "venv", ".tox", "dist", "build", ".eggs"}
IGNORE_FILES = {".DS_Store", "Thumbs.db"}

def scan_project(project_path: Path = None) -> dict:
    """Scan project structure."""
    root = project_path or Path.cwd()
    result = {
        "files": [],
        "dirs": [],
        "languages": set(),
        "frameworks": [],
        "test_framework": None,
        "has_git": False,
    }

    # Check git
    if (root / ".git").exists():
        result["has_git"] = True

    # Scan files
    for item in root.rglob("*"):
        rel = item.relative_to(root)

        # Skip ignored
        if any(p in IGNORE_DIRS for p in rel.parts):
            continue
        if item.name in IGNORE_FILES:
            continue

        if item.is_file():
            result["files"].append(str(rel))
            _detect_language(item, result)
        elif item.is_dir():
            result["dirs"].append(str(rel))

    # Detect frameworks/tools
    _detect_frameworks(root, result)
    _detect_test_framework(root, result)

    result["languages"] = list(result["languages"])
    return result

def _detect_language(path: Path, result: dict):
    """Detect language from file extension."""
    ext_map = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".go": "go", ".rs": "rust", ".java": "java",
        ".rb": "ruby", ".php": "php", ".c": "c", ".cpp": "cpp",
        ".cs": "csharp", ".swift": "swift", ".kt": "kotlin",
    }
    ext = path.suffix.lower()
    if ext in ext_map:
        result["languages"].add(ext_map[ext])

def _detect_frameworks(root: Path, result: dict):
    """Detect frameworks from config files."""
    checks = [
        ("pyproject.toml", "python-project"),
        ("package.json", "node"),
        ("Cargo.toml", "rust"),
        ("go.mod", "go"),
        ("Gemfile", "ruby"),
        ("composer.json", "php"),
        ("pom.xml", "maven"),
        ("build.gradle", "gradle"),
        ("CMakeLists.txt", "cmake"),
        ("Makefile", "make"),
        ("Dockerfile", "docker"),
        ("docker-compose.yml", "docker-compose"),
        (".github/workflows", "github-actions"),
    ]
    for check, framework in checks:
        if (root / check).exists():
            result["frameworks"].append(framework)

def _detect_test_framework(root: Path, result: dict):
    """Detect test framework."""
    # Python
    if "python" in result["languages"]:
        if (root / "pytest.ini").exists() or (root / "conftest.py").exists():
            result["test_framework"] = "pytest"
        elif (root / "setup.cfg").exists():
            result["test_framework"] = "pytest"  # assume pytest
        elif any(f.startswith("test_") for f in result["files"]):
            result["test_framework"] = "pytest"

    # Node
    if "javascript" in result["languages"] or "typescript" in result["languages"]:
        pkg = root / "package.json"
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text())
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "jest" in deps:
                    result["test_framework"] = "jest"
                elif "mocha" in deps:
                    result["test_framework"] = "mocha"
                elif "vitest" in deps:
                    result["test_framework"] = "vitest"
            except Exception:
                pass

    # Go
    if "go" in result["languages"]:
        if any(f.endswith("_test.go") for f in result["files"]):
            result["test_framework"] = "go-test"

    # Rust
    if "rust" in result["languages"]:
        result["test_framework"] = "cargo-test"

def store_knowledge(scan_result: dict, project_path: Path = None):
    """Store scan results in knowledge base."""
    db.init_db(project_path)

    # Store summary
    db.set_knowledge("languages", json.dumps(scan_result["languages"]), "structure", project_path)
    db.set_knowledge("frameworks", json.dumps(scan_result["frameworks"]), "structure", project_path)
    db.set_knowledge("test_framework", scan_result["test_framework"] or "", "structure", project_path)
    db.set_knowledge("has_git", str(scan_result["has_git"]), "structure", project_path)
    db.set_knowledge("file_count", str(len(scan_result["files"])), "structure", project_path)

    # Store file list (truncated for large projects)
    files = scan_result["files"][:500]  # limit
    db.set_knowledge("files", json.dumps(files), "structure", project_path)

def get_project_summary(project_path: Path = None) -> dict:
    """Get project summary from knowledge base."""
    entries = db.get_knowledge(category="structure", project_path=project_path)
    result = {}
    for e in entries:
        key, val = e["key"], e["value"]
        if key in ("languages", "frameworks", "files"):
            result[key] = json.loads(val) if val else []
        elif key == "has_git":
            result[key] = val == "True"
        elif key == "file_count":
            result[key] = int(val) if val else 0
        else:
            result[key] = val
    return result

def init_project(project_path: Path = None) -> dict:
    """Full init: scan and store."""
    result = scan_project(project_path)
    store_knowledge(result, project_path)
    return result
