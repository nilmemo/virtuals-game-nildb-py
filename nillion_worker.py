from argparse import ArgumentParser
from collections import defaultdict
from dotenv import load_dotenv
from game_sdk.game.worker import Worker
from game_sdk.game.custom_types import (
    Function,
    Argument,
    FunctionResult,
    FunctionResultStatus,
)
from huggingface_hub import InferenceClient
import json
import os
import requests
from typing import Union, Dict, List, Tuple
import uuid

import nilql

from get_nildb_keys import get_nildb_keys

load_dotenv()

GAME_API_KEY = os.environ["GAME_API_KEY"]
HUGGINGFACE_API_KEY = os.environ["HUGGINGFACE_API_KEY"]
PROMPT = """
Write a poem about the beauty of transformation and renewal, drawing inspiration from nature (e.g., seasons, butterflies, or rivers). The poem should follow these criteria:

Structure: Four quatrains (four-line stanzas).
Meter: Iambic tetrameter (four iambic feet per line).
Rhyme Scheme: ABAB for each stanza.
Content Requirements: Include vivid imagery of a natural process of change, such as leaves falling and regrowing, or a river carving a new path. Incorporate themes of hope and resilience.
Tone: Reflective and uplifting, with a focus on the positive aspects of transformation.
The poem should use evocative language and focus on painting a clear mental image for the reader.
"""

'''
parser = ArgumentParser()
parser.add_argument("--prompt", default="generate a short poem about cute animals")
args = parser.parse_args()
value = args.prompt
'''

TASK = "generate a poem, upload poem, judge poems"

JSON_TYPE = Dict[str, Union[str, int, float, bool, None, List, Dict]]

get_nildb_keys()

with open(os.environ.get("NILDB_CONFIG", ".nildb.config.json")) as fh:
    CONFIG = json.load(fh)


class NilDBAPI:
    def __init__(self):
        self.nodes = CONFIG["hosts"]
        self.secret_key = nilql.SecretKey.generate(
            {"nodes": [{}] * len(CONFIG["hosts"])}, {"store": True}
        )

    def download_poems(self) -> Dict:
        """Download all records in the specified node and schema."""
        try:
            shares = defaultdict(list)
            teams = defaultdict(list)
            for idx, node in enumerate(self.nodes):
                headers = {
                    "Authorization": f'Bearer {node["bearer"]}',
                    "Content-Type": "application/json",
                }

                body = {"schema": CONFIG["schema_id"], "filter": {"contest": CONFIG["contest"]}}

                response = requests.post(
                    f"https://{node['url']}/api/v1/data/read",
                    headers=headers,
                    json=body,
                )
                assert (
                    response.status_code == 200
                ), ("upload failed: " + response.content)
                data = response.json().get("data")
                for i, d in enumerate(data):
                    shares[i].append(d["text"]["$share"])
                    teams[i].append(d["team"])
            for i in range(len(teams)):
                assert(teams[i][0] == teams[i][j] for j in range(1, len(teams[i])))
                teams[i] = teams[i][0]
            decrypted = []
            for k in shares:
                decrypted.append(nilql.decrypt(self.secret_key, shares[k]))
            messages = {}
            judged = {"blue": True, "purple": True, "red": True}
            for team, message in zip(teams, decrypted):
                if len(messages) == len(judged):
                    break
                if teams[team] in judged and judged[teams[team]]:
                    messages[teams[team]] = message
                    judged[teams[team]] = False
            return messages
        except Exception as e:
            print(f"Error retrieving records in node: {str(e)}")
            return {}

    def data_download(self) -> JSON_TYPE:
        """Download all records in the specified node and schema."""
        try:
            for idx, node in enumerate(self.nodes):
                headers = {
                    "Authorization": f'Bearer {node["bearer"]}',
                    "Content-Type": "application/json",
                }

                body = {"schema": CONFIG["schema_id"], "filter": {}}

                response = requests.post(
                    f"https://{node['url']}/api/v1/data/read",
                    headers=headers,
                    json=body,
                )
                print(response.content)
                assert (
                    response.status_code == 200
                ), ("upload failed: " + response.content)
            return True

        except Exception as e:
            print(f"Error creating records in node {idx}: {str(e)}")
            return False

    def data_upload(self, payload: JSON_TYPE) -> bool:
        """Create/upload records in the specified node and schema."""
        try:
            print(json.dumps(payload))
            payload["text"] = {
                "$allot": nilql.encrypt(self.secret_key, payload["text"])
            }
            payloads = nilql.allot(payload)
            for idx, shard in enumerate(payloads):
                node = self.nodes[idx]
                headers = {
                    "Authorization": f'Bearer {node["bearer"]}',
                    "Content-Type": "application/json",
                }

                body = {"schema": CONFIG["schema_id"], "data": [shard]}

                response = requests.post(
                    f"https://{node['url']}/api/v1/data/create",
                    headers=headers,
                    json=body,
                )

                assert (
                    response.status_code == 200
                    and response.json().get("data", {}).get("errors", []) == []
                ), ("upload failed: " + response.content)
            return True
        except Exception as e:
            print(f"Error creating records in node {idx}: {str(e)}")
            return False

def get_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    """
    This function will get called at every step of the agent's execution to form the agent's state.
    It will take as input the function result from the previous step.
    """
    # dict containing info about the function result as implemented in the exectuable
    info = function_result.info

    # example of fixed state (function result info is not used to change state) - the first state placed here is the initial state
    init_state = {"objects": []}

    if current_state is None:
        # at the first step, initialise the state with just the init state
        new_state = init_state
    else:
        # do something wiht the current state input and the function result info
        new_state = init_state  # this is just an example where the state is static

    return new_state


def generate_content(plan: str, **kwargs) -> Tuple[FunctionResultStatus, str, dict]:
    """
    Function to generate random phrase or content

    Args:
        plan: Notation of agent action
        **kwargs: Additional arguments that might be passed
    """

    client = InferenceClient(api_key=HUGGINGFACE_API_KEY)

    messages = [
        {
            "role": "user",
            "content": PROMPT
        }
    ]

    stream = client.chat.completions.create(
        model="google/gemma-2-2b-it",
    	messages=messages,
    	max_tokens=500,
    	stream=True
    )

    result = ''.join([chunk.choices[0].delta.content for chunk in stream])

    if result:
        return (
            FunctionResultStatus.DONE,
            f"Successfully generated the poem: {result}",
            {},
        )
    return FunctionResultStatus.FAILED, "No generation", {}


def upload_to_nildb(content: str, **kwargs) -> Tuple[FunctionResultStatus, str, dict]:
    """
    Function to upload content to nildb

    Args:
        content: Text string content to store in nildb
        **kwargs: Additional arguments that might be passed
    """
    if content:
        nildb = NilDBAPI()
        my_id = str(uuid.uuid4())

        if nildb.data_upload( payload={"_id": my_id, "contest": CONFIG["contest"], "team": CONFIG["team"], "text": content}):
            return FunctionResultStatus.DONE, f"Successfully uploaded the {content}", {}
    return FunctionResultStatus.FAILED, "No object specified", {}


def judge_poems(plan: str, **kwargs) -> Tuple[FunctionResultStatus, str, dict]:
    """
    Function to download content from nildb and judge the downloaded poems

    Args:
        plan: Notation of agent action
        **kwargs: Additional arguments that might be passed
    """
    nildb = NilDBAPI()
    my_id = str(uuid.uuid4())

    download = nildb.download_poems()
    if not download:
        return FunctionResultStatus.FAILED, "Download failed", {}

    client = InferenceClient(api_key=HUGGINGFACE_API_KEY)

    messages = [
        {
            "role": "user",
            "content": f"red poem: {download['red']}. blue poem: {download['blue']}. purple poem: {download['purple']}. Do you prefer red or blue or purple? Give a score for each."
        }
    ]

    stream = client.chat.completions.create(
        model="google/gemma-2-2b-it",
    	messages=messages,
    	max_tokens=500,
    	stream=True
    )

    result = ''.join([chunk.choices[0].delta.content for chunk in stream])

    if result:
        return (
            FunctionResultStatus.DONE,
            f"Successfully judged the poems: {result}",
            {},
        )

    return FunctionResultStatus.FAILED, "Could not judge the poems", {}


# Action space with all executables
action_space = [
    Function(
        fn_name="generate",
        fn_description="Generate some creative content",
        args=[
            Argument(
                name="plan", type="task", description="Prompt of reasoning")
            ],
        executable=generate_content,
    ),
    Function(
        fn_name="upload",
        fn_description="Upload to privacy preserving nildb database",
        args=[
            Argument(
                name="content", type="task", description="The source content to upload"
            )
        ],
        executable=upload_to_nildb,
    ),
    Function(
        fn_name="judge_poems",
        fn_description="Judge poems in nildb",
        args=[
            Argument(
                name="plan", type="task", description="Prompt of reasoning")
            ],
        executable=judge_poems,
    ),
]


worker = Worker(
    api_key=GAME_API_KEY,
    description=f"Worker that will {TASK}",
    instruction=TASK,
    get_state_fn=get_state_fn,
    action_space=action_space,
)

# interact and instruct the worker to do something
# worker.run("what would you do to the apple?")
worker.run(TASK)
