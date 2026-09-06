PROPERTY_LAST_INPUT = "prompt_snapshot_last_input"


def _find_workflow_node(extra_pnginfo, unique_id):
    if not isinstance(extra_pnginfo, dict):
        return None

    workflow = extra_pnginfo.get("workflow")
    if not isinstance(workflow, dict):
        return None

    nodes = workflow.get("nodes")
    if not isinstance(nodes, list):
        return None

    for node in nodes:
        if isinstance(node, dict) and str(node.get("id")) == str(unique_id):
            return node

    return None


def _get_last_input(workflow_node):
    if not isinstance(workflow_node, dict):
        return None

    properties = workflow_node.get("properties")
    if not isinstance(properties, dict):
        return None

    value = properties.get(PROPERTY_LAST_INPUT)
    return value if isinstance(value, str) else None


def _store_snapshot_in_workflow(workflow_node, prompt, prompt_in):
    """Update the workflow metadata that will be embedded in the generated image."""
    if not isinstance(workflow_node, dict):
        return

    properties = workflow_node.setdefault("properties", {})
    if isinstance(properties, dict):
        properties[PROPERTY_LAST_INPUT] = prompt_in

    # This node has exactly one visible widget: `prompt`.
    widget_values = workflow_node.get("widgets_values")

    if isinstance(widget_values, list):
        if widget_values:
            widget_values[0] = prompt
        else:
            widget_values.append(prompt)
    elif isinstance(widget_values, dict):
        # Workflow v1 also permits object-form widget values.
        widget_values["prompt"] = prompt
    else:
        workflow_node["widgets_values"] = [prompt]


class PromptSnapshot:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_in": (
                    "STRING",
                    {
                        "forceInput": True,
                        "tooltip": "Translated prompt from the upstream node.",
                    },
                ),
                "prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "dynamicPrompts": False,
                        "tooltip": "Editable prompt used for image generation.",
                    },
                ),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "snapshot"
    CATEGORY = "utils/text"
    DESCRIPTION = (
        "Displays an upstream prompt in an editable multiline field and outputs "
        "the current field value unchanged."
    )

    def snapshot(self, prompt_in, prompt, unique_id=None, extra_pnginfo=None):
        workflow_node = _find_workflow_node(extra_pnginfo, unique_id)
        last_input = _get_last_input(workflow_node)

        # If the upstream translated prompt changed, it becomes the new snapshot.
        # If the upstream prompt did not change, preserve the user's edited text.
        upstream_changed = last_input is None or prompt_in != last_input
        effective_prompt = prompt_in if upstream_changed else prompt

        # Ensure the workflow embedded in the image contains the effective prompt,
        # including on the very first execution before the browser widget is updated.
        _store_snapshot_in_workflow(workflow_node, effective_prompt, prompt_in)

        return {
            "ui": {
                "snapshot_prompt": [effective_prompt],
                "last_input": [prompt_in],
                "sync": [upstream_changed],
            },
            "result": (effective_prompt,),
        }


NODE_CLASS_MAPPINGS = {
    "PromptSnapshot": PromptSnapshot,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptSnapshot": "Prompt Snapshot",
}
