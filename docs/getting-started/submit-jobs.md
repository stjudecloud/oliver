# Submitting Jobs

One of the novel features provided by Oliver is the ease with which workflow
inputs, options, and labels can be set dynamically on the command line.
Typically when submitting a workflow, one must craft and POST one or more `workflowInputs`,
`workflowOptions`, and `labels` JSON files to Cromwell. This can be cumbersome
— especially when you have thousands of workflows to run.

## Dynamic Parameter Parsing

Oliver provides an improvement over this experience for a few keys reasons:

* Inputs, options, and labels can be loaded from files _or_ as key-value pairs on the command line.
* Inputs, options, and labels are processed sequentially and overwrite arguments that were provided earlier on the command line.
* Oliver distinguishes between inputs, options, and labels based on the prefix provided.

For instance, consider the following command:

```bash
oliver submit workflow.wdl defaults.json sample_name=SJBALL101_D
```

Here, Oliver loads `workflow.wdl` and begins preparing the `workflowInputs` (inputs), `workflowOptions` (options), and `labels` (labels) JSON objects — all of which are initialized as `{}`.

1. Oliver loads the JSON object defined in `defaults.json`. For each key-value in that object, it adds the pair to `workflowInputs`, overwriting the pair if it already exists. In this case, the JSON object is empty, so `workflowInputs` now mirrors what was contained in `defaults.json`.
2. Oliver recognizes that you have provided `sample_name=SJBALL101_D` as a key value pair and adds this pair to `workflowInputs`, overwriting the key if it existed.

In this way, you can dynamically set and overwrite inputs with ease to satisfy your use case.

### Prefixes

This process works similarly for all parameter types (inputs, options, or labels). To distinguish them to Oliver, you need to use the following prefixes:

| Parameter Type | Prefix   | Example      |
| -------------- | -------- | ------------ |
| Input          | `<none>` | `key=value`  |
| Option         | `@`      | `@key=value` |
| Label          | `%`      | `%key=value` |

For example, consider the following command and note the process Oliver follows in the comments:

```bash
oliver submit workflow.wdl \
    default-inputs.json \      # loads all values in the JSON file to the inputs object.
    @default-options.json \    # loads all values in the JSON file to the options object.
    %default-labels.json \     # loads all values in the JSON file to the labels object.
    input_key=value \          # adds `input_key=value` to the inputs object (overwrites the value if `input_key` set in default-inputs.json).
    @option_key=value \        # adds `option_key=value` to the options object (overwrites the value if `option_key` set in default-options.json).
    %label_key=value \         # adds `label_key=value` to the labels object (overwrites the value if `label_key` set in default-labels.json).
```

### Inspecting Parameters with Dry Runs

Often, it can be useful to inspect how Oliver is parsing the parameters you are passing on the command line. You can easily do so by specifying the dry-run argument.

```bash
oliver submit workflow.wdl defaults.json sample_name=SJBALL101_D --dry-run
```

## Job Names and Groups

You can submit jobs with a "Oliver Job Name" (`-j`) and "Oliver Job Group" (`-g`) to mimic the capabilities of an HPC. Under the hood, Oliver adds these as labels to the workflow. In most Oliver commands, you can then specify these options to restrict results.

For instance, if you wished to submit a group of samples with the same job name and then track their status:

```
# Submit jobs
for SAMPLE in $SAMPLES; do
  echo oliver submit $WORKFLOW_URL $DEFAULT_INPUTS_FILE \
                     input_bam=${SAMPLE}.bam \
                     output_prefix=${SAMPLE}. \
                     -j ${SAMPLE} -g CohortAlpha
done

# Check status of this job group
oliver status -g CohortAlpha
```