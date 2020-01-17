# Configuration

Configuration for `oliver` is stored in the config file as JSON. By default, the
dotfile is location at `~/.oliver_config`.

The following key values pairs can be used to configure `oliver`:

| Key                    | Description                                                                          | Type   | Required | Default                 |
| ---------------------- | ------------------------------------------------------------------------------------ | ------ | -------- | ----------------------- |
| `cromwell_server`      | HTTP/HTTPS root URL for the Cromwell server to use by default.                       | String | True     | `http://localhost:8000` |
| `cromwell_api_version` | Cromwell API version to use by default.                                              | String | True     | `v1`                    |
| `output_prefix`        | Prefix to append to file locations.                                                  | String | False    |                         |
| `azure_resource_group` | If using Cromwell on Azure, resource group associated with your Cromwell instance.   | String | False    |                         |
| `cosmos_account_name`  | If using Cromwell on Azure, name of CosmosDB associated with your Cromwell instance. | String | False    |                         |