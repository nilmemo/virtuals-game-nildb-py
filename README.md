# nildb on virtuals G-A-M-E

```shell
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```
Copy the conig files and update
```shell
cp .env.example .env
cp .nildb.config.json.example .nildb.config.json
```

Run the agent and give it a prompt:
```shell
python nillion_worker.py --prompt "upload a whimsical poem about citizen band radios to nildb"
```

