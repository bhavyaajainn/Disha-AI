from typing import Dict

def select_model(verbose: bool = False) -> str:
    selected = "anthropic.claude-3-haiku-20240307-v1:0"
    if verbose:
        print(f"[Model Selector] Using FAST default: {selected}")
    return selected
