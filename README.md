# ollama-agent-project
Chat agent for ollama

### create virtual environment
- `virtualenv venv/ollama`
- `source venv/ollama/bin/activate`
- `pip3 freeze > requirements.txt`

### Install dependent packages
- `pip3 --disable-pip-version-check --no-cache-dir install -r requirements.txt` or `pip install -r requirements.txt`
- In case getting error as `ModuleNotFoundError: No module named 'NorenRestApiPy'` use `py -m pip install whl/NorenRestApi-0.0.30-py2.py3-none-any.whl pyotp`