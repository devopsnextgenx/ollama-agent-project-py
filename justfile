default:
    @just --list --unsorted

commit message:
  git add . && git commit -m "{{message}}" && git push

source:
  #!/usr/bin/env bash
  source venv/ollama/bin/activate