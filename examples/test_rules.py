import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

api_key = os.getenv("LANGSMITH_API_KEY")
BASE_URL = "https://api.smith.langchain.com"  # adjust if using a different host

def auth_headers():
    return {
        "X-API-Key": api_key
    }

def list_rules(params=None):
    url = f"{BASE_URL}/api/v1/runs/rules"
    resp = requests.get(url, headers=auth_headers(), params=params or {}, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"List rules failed: {resp.status_code} {resp.text}")
    return resp.json()

def get_rule_by_id(rule_id: str):
    """
    The API doesn't provide GET /rules/{id}, so we filter the list endpoint by id.
    The 'id' parameter accepts an array of strings, so we pass [rule_id].
    """
    rules = list_rules(params={"id": [rule_id]})
    if not rules:
        print(f"No rule found with id: {rule_id}")
        return None
    rule = rules[0]
    print("Rule details:\n" + json.dumps(rule, indent=2))
    return rule

def create_prompt_injection_clone():
    url = f"{BASE_URL}/api/v1/runs/rules"

    payload = {
        "display_name": "prompt-injection-2",   # new name
        "session_id": "503e8389-f655-4e5b-90cf-548af7da9875",
        "is_enabled": True,
        "dataset_id": None,
        "sampling_rate": 1.0,
        "filter": "eq(is_root, true)",
        "trace_filter": None,
        "tree_filter": None,
        "use_corrections_dataset": False,
        "num_few_shot_examples": None,
        "extend_only": False,
        "transient": False,
        "add_to_annotation_queue_id": None,
        "add_to_dataset_id": None,
        "add_to_dataset_prefer_correction": False,
        "evaluators": [
            {
                "structured": {
                    "hub_ref": "eval_chat_langchain_v3_prompt_injection_fda713cd:latest",
                    "prompt": None,
                    "template_format": None,
                    "schema": None,
                    "variable_mapping": {
                        "input": "input.messages"
                    },
                    "model": None
                }
            }
        ],
        "code_evaluators": [],
        "alerts": [],
        "webhooks": [],
        "evaluator_version": 3,
        "create_alignment_queue": False,
        "include_extended_stats": False
    }

    resp = requests.post(url, headers=auth_headers(), json=payload, timeout=30)
    if resp.status_code == 200:
        print("✅ Rule created successfully:")
        print(json.dumps(resp.json(), indent=2))
    else:
        print(f"❌ Error {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    print("=== All rules (id :: name) ===")

    params = {
        "name_contains": "prompt-injection"
    }
    for r in list_rules(params=params):
        print(f"{r['id']} :: {r.get('display_name')}")

    rule_id = r['id']
    print("\n=== Selected rule ===")
    get_rule_by_id(rule_id)

    print("\n=== Creating prompt-injection-2 ===")
    # create_prompt_injection_clone()