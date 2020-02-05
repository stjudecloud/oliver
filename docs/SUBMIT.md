# Submitting Jobs

One of the novel features of `oliver` is the ease in which workflow
parameters can be set on the command line. Typically when submitting a workflow, 
one must specify a `workflowInputs` (could be one of many), `workflowOptions`,
and `labels` JSON file to Cromwell.

When you use `oliver submit`, you can easily specify files or individual key-value 
pairs to be included in the parameters above. For instance, passing `inputs.json` on 
the command line will read all key-value pairs from `inputs.json` and add them to 
the inputs dictionary. Individual key-value pairs can be passed like `key=value`.
Values passed later are processed sequentially, meaning that later arguments
overwrite any key-value pairs set by previous ones.

Additionally, argument passed on the command line can encode each the
different parameter types for a Cromwell workflow:

| Parameter Type | Prefix   | Example      |
| -------------- | -------- | ------------ |
| Input          | `<none>` | `key=value`  |
| Option         | `@`      | `@key=value` |
| Label          | `%`      | `%key=value` |

For example, consider the following command:

```bash
oliver submit workflow.wdl \
    default-inputs.json \      # loads all values in the JSON file to the inputs object.
    @default-options.json \    # loads all values in the JSON file to the options object.
    %default-labels.json \     # loads all values in the JSON file to the labels object.
    input_key=value \          # adds `input_key=value` to the inputs object (overwrites the value if `input_key` set in default-inputs.json).
    @option_key=value \        # adds `option_key=value` to the options object (overwrites the value if `option_key` set in default-options.json).
    %label_key=value \         # adds `label_key=value` to the labels object (overwrites the value if `label_key` set in default-labels.json).
```