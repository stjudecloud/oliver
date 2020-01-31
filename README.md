<h1 align="center">Oliver</h1>
<p align="center">
  <a href="https://actions-badge.atrox.dev/stjudecloud/oliver/goto"><img alt="Build Status" src="https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fstjudecloud%2Foliver%2Fbadge&style=flat" />
  </a>
  <a href="https://www.npmjs.com/package/oliver" target="_blank">
    <img alt="Version" src="https://img.shields.io/static/v1?label=version&message=alpha&color=orange">
  </a>
  <a href="https://github.com/stjudecloud/oliver/blob/master/LICENSE.md" target="_blank">
    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg" />
  </a>
</p>

> An opinionated Cromwell orchestration manager.

![Oliver Example](./docs/oliver-example.gif)

## Getting Started

```sh
# Package install
python setup.py install
```

Please refer to the guides in the `docs/` folder for more information.

| Guide Name     | Link                             |
| -------------- | -------------------------------- |
| Advanced Usage | [Link](./docs/ADVANCED_USAGE.md) |
| Configuration  | [Link](./docs/CONFIGURATION.md)  |
| Development    | [Link](./docs/DEVELOPMENT.md)    |

## Usage

```bash
oliver -h
```

The following subcommands are currently supported.

| Subcommand  | Short Command | Description                                                 |
| ----------- | ------------- | ----------------------------------------------------------- |
| `aws`       |               | All subcommands related to Cromwell on AWS.                 |
| `azure`     |               | All subcommands related to Cromwell on Azure.               |
| `aggregate` | `a`           | Aggregate all results to a local or cloud folder for a run. |
| `batches`   | `b`           | Explore batches of jobs submitted to Cromwell.              |
| `configure` |               | Configure Oliver with default options.                      |
| `config`    |               | Set or get a single config value from Oliver.               |
| `inputs`    |               | Find all reported outputs for a given workflow.             |
| `inspect`   | `i`           | Describe the state of a Cromwell workflow.                  |
| `kill`      | `k`           | Kill a workflow running on a Cromwell server.               |
| `logs`      | `l`           | Find all reported logs for a given workflow.                |
| `outputs`   | `o`           | Find all reported outputs for a given workflow.             |
| `retry`     | `re`          | Resubmit a workflow with the same parameters.               |
| `runtime`   | `ru`          | Get the runtime attributes used for a specific call.        |
| `status`    | `st`          | Report various statistics about a running Cromwell server.  |
| `submit`    | `su`          | Submit a workflow to the Cromwell server.                   |

## Submitting Jobs

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

## Author

👤 **St. Jude Cloud Team**

* Website: https://stjude.cloud
* Twitter: [@StJudeResearch](https://twitter.com/StJudeResearch)
* Github: [@stjudecloud](https://github.com/stjudecloud)

## 🤝 Contributing

Contributions, issues and feature requests are welcome!<br />Feel free to check [issues page](https://github.com/stjudecloud/oliver/issues). You can also take a look at the [contributing guide](https://github.com/stjudecloud/oliver/blob/master/CONTRIBUTING.md).

## 📝 License

Copyright © 2020 [St. Jude Cloud Team](https://github.com/stjudecloud).<br />
This project is [MIT](https://github.com/stjudecloud/oliver/blob/master/LICENSE.md) licensed.