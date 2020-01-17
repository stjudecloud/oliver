# Advanced Usage

Below, you will find some examples of advanced usage supported by `oliver`.

## Advanced Configuration

### Output Prefixing

In some scenarios, it's helpful to modify the output prefixing reported by
Cromwell. For instance, in the case of [Cromwell on Azure][coa], Cromwell mounts
the storage location as a FUSE filesystem. This leads to Cromwell reporting the
location of output files or logs like so:

```
/cromwell-execution/rnaseq_standard/<UUID>/call-multiqc/multiqc_results.tar.gz
```

In general, this location is not ammenable to quickly leveraging in another
script to download the file. In this case, we have chosen to create the
`output_prefix` configuration option that allows prefixing any output locations
with a string. For instance, if the output prefix is `azure://container-name`, the
reported output of the above will be

```
azure://container-name/cromwell-execution/rnaseq_standard/<UUID>/call-multiqc/multiqc_results.tar.gz
```

This string is much more amenable to copying and pasting. You can set this
configuration option by running the following command.

```bash
oliver config set output_prefix "azure://container-name"
```

### CosmosDB

When using [Cromwell on Azure][coa], [CosmosDB][cosmos] is used as the metadata store for Cromwell. It can be extremely useful to peer into this metadata to understand failures that happen outside of Cromwell (for instance, within Azure Batch). Thus, we have integrated custom commands (such as `oliver cosmos`) to interrogate this database. If you wish to use this functionality, you'll need to set the following configuration parameters.

```bash
oliver config set azure_resource_group "YOUR RESOURCE GROUP NAME"
oliver config set cosmos_account_name "YOUR COSMOSDB ACCOUNT NAME"
```
For more information, see our [configuration guide][configuration].

[coa]: https://github.com/microsoft/CromwellOnAzure
[configuration]: ./CONFIGURATION.md
[cosmos]: https://azure.microsoft.com/en-us/services/cosmos-db/