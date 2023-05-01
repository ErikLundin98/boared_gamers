# Board game rankings web app

## Installation

You need an environment variable `PASSWORD` set. This can be placed in a `.env` file in the base dir.

Installation with make:
```
make install_unix
make install_windows
```

Alternatively, install manually:
```
python -m venv venv

venv/scripts/activate # Windows
source venv/scripts/activate # Linux/Mac

pip install -r requirements.txt

mkdir db
```

## Running the server

```
python -m app
```