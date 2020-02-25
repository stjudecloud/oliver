# Azure

Oliver was originally created through the St. Jude Cloud team's close collaboration with the Microsoft Genomics team and, specifically, our the development of [Cromwell on Azure][coa]. As such, we intend to provide first-class support of Cromwell on Azure and common operations like aggregating results and debugging jobs.

The subcommand `oliver azure` currently exists for the community to try, but the guide is still in progress. We will continue to add to this guide as we add functionality. In the meantime, if you use Cromwell on Azure and would like to suggest features or report bugs you encounter, we invite you to do so on the [issues](https://github.com/stjudecloud/oliver/issues) page.

## CosmosDB

When using Cromwell on Azure, [CosmosDB][cosmos] is used as the metadata store for Cromwell. It can be extremely useful to peer into this metadata to understand failures that happen outside of Cromwell (for instance, within Azure Batch). Thus, we have integrated custom commands (such as `oliver cosmos`) to interrogate this database. If you wish to use this functionality, you'll need to set the following configuration parameters.

```bash
oliver config set azure_resource_group "YOUR RESOURCE GROUP NAME"
oliver config set cosmos_account_name "YOUR COSMOSDB ACCOUNT NAME"
```

For more information, see our [configuration guide](../getting-started/configuration.md).

[coa]: https://github.com/microsoft/CromwellOnAzure
[cosmos]: https://azure.microsoft.com/en-us/services/cosmos-db/