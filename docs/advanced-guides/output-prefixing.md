# Output Prefixing

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

[coa]: https://github.com/microsoft/CromwellOnAzure