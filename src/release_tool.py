import os
import sys
import subprocess
import re

# --- CONFIGURATION ---
RELEASE_REMOTE="backup"
MIN_PYTHON_VERSION = (3, 12)
# Ensures version is numbers only (e.g., 1.0.1), preventing 1.0.1-beta
VERSION_REGEX = r"^\d+\.\d+\.\d+$"


# ---------------------

def check_python_version():
    """Ensures the script is running with the correct Python version."""
    current_ver = sys.version_info[:2]
    if current_ver < MIN_PYTHON_VERSION:
        print(f"❌ Error: Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ is required.")
        print(f"   You are using Python {current_ver[0]}.{current_ver[1]}.")
        sys.exit(1)


def run_command(command):
    """Runs a shell command and returns the output."""
    try:
        result = subprocess.run(
            command, shell=True, check=True, text=True, capture_output=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(e.stderr)
        sys.exit(1)


def get_current_version():
    """Extracts version from pyproject.toml and validates format."""
    version_file = "pyproject.toml"
    if not os.path.exists(version_file):
        print(f"❌ Error: {version_file} not found.")
        sys.exit(1)

    with open(version_file, "r") as f:
        content = f.read()
        match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
        if match:
            version_str = match.group(1)
            # Validate against strict X.X.X regex
            if not re.match(VERSION_REGEX, version_str):
                print(f"❌ Error: Version '{version_str}' in {version_file} is invalid.")
                print(f"   Must match format X.X.X (e.g., 1.0.2). No alphas/betas.")
                sys.exit(1)
            return version_str

    print(f"❌ Error: Could not find 'version' in {version_file}.")
    sys.exit(1)


def check_git_status():
    """Ensures there are no uncommitted changes."""
    status = run_command("git status --porcelain")
    if status:
        print("❌ Error: Your git working directory is not clean.")
        print("   Please commit or stash your changes before releasing.")
        sys.exit(1)


def main():
    print("🚀 Starting Release Workflow...")

    # 1. Enforce Python Version
    check_python_version()

    # 2. Check for clean git state
    check_git_status()

    # 3. Get and validate version format
    version = get_current_version()
    tag_name = f"v{version}"

    # 4. Check if tag already exists
    existing_tags = run_command("git tag")
    if tag_name in existing_tags.split():
        print(f"❌ Error: Tag {tag_name} already exists.")
        print("   Did you forget to bump the version in pyproject.toml?")
        sys.exit(1)

    # 5. Confirmation
    print(f"\n✅ Checks Passed.")
    print(f"   - Python Version: {sys.version.split()[0]} (OK)")
    print(f"   - Version Format: {version} (OK)")
    print(f"   - Git Status: Clean (OK)")
    print(f"\nAction: Create git tag '{tag_name}' and push to '{RELEASE_REMOTE}'.")

    confirm = input("\nProceed? (y/n): ").lower()
    if confirm != 'y':
        print("Aborted.")
        sys.exit(0)

    # 6. Tag and Push
    print(f"\nPushing current branch to tracked branch on '{RELEASE_REMOTE}'...")
    run_command(f"git push {RELEASE_REMOTE}")

    print(f"\nCreating tag {tag_name}...")
    run_command(f"git tag {tag_name}")

    print(f"Pushing tag {tag_name} to '{RELEASE_REMOTE}'...")
    run_command(f"git push {RELEASE_REMOTE} {tag_name}")

    print("\n✅ Done! The CI/CD pipeline should now trigger.")


if __name__ == "__main__":
    main()
