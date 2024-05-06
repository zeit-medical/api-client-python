default:
    @just --list

test:
    #!/usr/bin/env bash
    source .venv/bin/activate &&
    pytest tests/

build:
    #!/usr/bin/env bash
    rm -r dist/
    poetry build
    twine upload --repository-url https://pypi.tempzeit.com/ dist/* \
      -u zeit
