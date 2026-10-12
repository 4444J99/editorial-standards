# Supported hosted runner contract repair

Owner: @4444J99. Codex implementation lane. Trigger: PR #16 run 38272536473 tests Ubuntu 24.04, while the editorial validator hardcodes ubuntu-latest. The default workflow at this repair's base still uses ubuntu-latest; the observed failure is on the PR merge revision, not proof of failed default CI.

Allow exactly ubuntu-latest and ubuntu-24.04. Preserve the exact job/step inventory, protected commands and all rejection of execution bypasses. New regressions accept the pinned supported image and reject self-hosted, Windows, old Ubuntu and expression-selected runners. No generated instruction outputs, existing PR branch or settings changed. This additive compatibility repair can land independently before the existing runner-pin PR is retested.

Validation: Python 3.12, pinned PyYAML 6.0.3; 155 unit tests pass (49.251s). Native validator passes (6 publication and 7 reader-mode templates). git diff --check passes. The initial system-interpreter probe lacked PyYAML and is not reported as a source failure. Remote CI/review/default acceptance remains separate; no failed hosted run was rerun without changed source.

Bounded pilot authorization covers this repair and staged advisory controls; required-check activation and portfolio expansion are excluded. Reader-mode issue #13's independent acceptance gates remain open. Rollback: revert this isolated repair through a reviewed PR; retaining ubuntu-latest keeps current default behavior available without weakening any protected execution control.
