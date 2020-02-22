# Configuration

Configuration for Oliver is stored in the config file as JSON. By default, the
dotfile is location at `~/.oliver_config`. One of the benefits of using Oliver is the "set and forget" nature of configuration. For instance, a common configuration option that you might want to set rather than providing on the command line is the URL to your Cromwell server.

## Basics

Before using Oliver, you should run the configuration quickstart wizard:

```bash
oliver configure
```

If you just want to accept the defaults, or if you are using Oliver in a non interactive environment like CI, you can just start with the default configuration.

```bash
oliver configure --defaults
```

Similarly, you can use the `oliver config` subcommand to display current config values, get specific key-value pairs, or set new values for configuration options.

```bash
# list all config values
oliver config list

# get a particular key
oliver config get cromwell_server

# set a particular key's value
oliver config set cromwell_server http://foo:8000
```

## Commonly Used Options

The following key values pairs are commonly used to configure Oliver. Note that any key in the `argparse` parser can be specified in the configuration — if you would like to set any of these options and don't mind looking through Python code, you can do so (we do not exhaustively list all possible config options here).

| Key                    | Description                                                           | Type   | Default                 |
| ---------------------- | --------------------------------------------------------------------- | ------ | ----------------------- |  |
| `cromwell_server`      | HTTP/HTTPS root URL for the Cromwell server to use by default.        | String | `http://localhost:8000` |
| `cromwell_api_version` | Cromwell API version to use by default.                               | String | `v1`                    |
| `batch_interval_mins`  | When inferring batches, how many minutes should separate two batches? | Int    | 2                       |
| `output_prefix`        | Prefix to append to file locations.                                   | String | None                    |

### Cromwell on Azure Specific

| Key                    | Description                                                                          | Type   | Default |
| ---------------------- | ------------------------------------------------------------------------------------ | ------ | ------- | ---- |
| `azure_resource_group` | If using Cromwell on Azure, resource group associated with your Cromwell instance.   | String |         | None |
| `cosmos_account_name`  | If using Cromwell on Azure, name of CosmosDB associated with your Cromwell instance. | String |         | None |