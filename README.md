# avtocod-test-task

## Prepare development environment

Create virtualenv and install dependencies:

```bash
python3 -m venv `PWD`/venv
source venv/bin/activate
pip install -U pip && pip install -r requirements.txt
```

Build services:
```bash
make build
```

## Load

```bash
make load DEPTH=0 ROOT=https://ria.ru
```

