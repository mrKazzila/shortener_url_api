# Setup .git hooks (commit-msg, pre-commit, pre-push)
[group('Prepare')]
hooks:
    #!/usr/bin/env bash
    set -euo pipefail

    ROOT="$(git rev-parse --show-toplevel)"
    HOOKS_DIR="$ROOT/.github/hooks"

    if [[ ! -d "$HOOKS_DIR" ]]; then
      echo "❌ Hooks dir not found: $HOOKS_DIR"
      exit 1
    fi

    for f in commit-msg pre-commit pre-push; do
      if [[ ! -f "$HOOKS_DIR/$f" ]]; then
        echo "❌ Hook file not found: $HOOKS_DIR/$f"
        exit 1
      fi
    done

    git config --local core.hooksPath "$HOOKS_DIR"
    chmod +x "$HOOKS_DIR/commit-msg" "$HOOKS_DIR/pre-commit" "$HOOKS_DIR/pre-push"

    echo "✅ Git hooks enabled"
    echo "   core.hooksPath = $(git config --local --get core.hooksPath)"


[group('Prepare')]
hooks-reset:
    #!/usr/bin/env bash
    set -euo pipefail

    git config --local --unset core.hooksPath || true
    echo "✅ Git hooks disabled (core.hooksPath unset)"


[group('Prepare')]
hooks-status:
    #!/usr/bin/env bash
    set -euo pipefail

    echo "core.hooksPath = $(git config --local --get core.hooksPath || echo '<not set>')"
