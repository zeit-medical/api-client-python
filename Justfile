default:
    @just --list

test:
    #!/usr/bin/env bash
    source .venv/bin/activate &&
    pytest tests/
