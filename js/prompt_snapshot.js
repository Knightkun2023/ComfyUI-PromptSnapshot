import { app } from "../../scripts/app.js";

const NODE_CLASS = "PromptSnapshot";
const PROPERTY_LAST_INPUT = "prompt_snapshot_last_input";

function first(value) {
    return Array.isArray(value) ? value[0] : value;
}

app.registerExtension({
    name: "PromptSnapshot.UI",

    async setup() {
        app.api.addEventListener("executed", (event) => {
            const detail = event.detail ?? {};
            const nodeId = detail.node;
            if (nodeId === undefined || nodeId === null) return;

            const node = app.graph?.getNodeById?.(Number(nodeId));
            if (!node || node.comfyClass !== NODE_CLASS) return;

            const output = detail.output ?? {};
            const shouldSync = Boolean(first(output.sync));
            if (!shouldSync) return;

            const snapshotPrompt = first(output.snapshot_prompt) ?? "";
            const lastInput = first(output.last_input) ?? "";

            const promptWidget = node.widgets?.find((widget) => widget.name === "prompt");
            if (promptWidget) {
                promptWidget.value = snapshotPrompt;
            }

            node.properties ??= {};
            node.properties[PROPERTY_LAST_INPUT] = lastInput;

            node.setDirtyCanvas?.(true, true);
        });
    },
});
