# Documentation

Please refer to the guides listed below for more information.

| Guide Name      | Link                             |
| --------------- | -------------------------------- |
| Advanced Usage  | [Link](./ADVANCED_USAGE.md) |
| Configuration   | [Link](./CONFIGURATION.md)  |
| Submitting Jobs | [Link](./SUBMIT.md)         |

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