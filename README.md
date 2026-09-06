# ComfyUI-PromptSnapshot

Minimal ComfyUI custom node for an editable prompt snapshot.

## Install

Copy this directory to:

`ComfyUI/custom_nodes/ComfyUI-PromptSnapshot/`

Then restart ComfyUI and reload the browser.

## Node

`utils/text -> Prompt Snapshot`

- `prompt_in`: connect the translated English prompt.
- `prompt`: editable multiline text field.
- output `prompt`: connect to your image-generation text-encoding node.

### Behavior

1. When the upstream translated prompt changes, `prompt` is updated with that value.
2. If only the `prompt` field is edited, the edited text is output on the next workflow execution.
3. The edited prompt is stored in the workflow metadata embedded in generated images when metadata saving is enabled.
