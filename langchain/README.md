# Langchain
Framework to create AI harness and Agent.

## Conventions
- `agents` folder contains different agents by use case.
- `utils` folder cantains scripts and programs that can be imported and used by agents.
- `.env` file contains all ENV vars that can be used by agents. Must be imported using `utils/import_env.py`
- `requirements.txt` all the python packages used by this project. For a 1-time initial install, run `python -m pip install -r requirements.txt`.

## Workflow
### Run example agent
- Install all packages `python -m pip install -r requirements.txt`.
- Run an agent: `python -m agents.weather`