# Monitoring Jobs

Another major feature of Oliver is the ease with which you can interrogate workflow status(es). In the simplest case, you can use the `oliver status` subcommand to get a summary of running jobs much like an HPC environment.

```bash
oliver status
```

To see individual workflows, you can use the `-d`/`--detail-view` parameter to show a "detailed" view.

```bash
oliver status -d
```

You also might be interested in a summary of the status of what steps each workflow in on. For this, you can use the `-z`/`--steps-view` parameter to show the "steps" view.

```bash
oliver status -z
```

By default, Oliver only shows all statuses. You can use the `-r` (Running), `-s` (Succeeded), `-f` (Failed), and `-a` (Aborted) flags to select a subset of these.

```bash
# only show failed and aborted jobs
oliver status -fa
```

## Batching

If you run hundreds or thousands of workflows, Oliver's response time might become slow because it needs to retrieve information about every workflow Cromwell has ever run. In this case, it's typically useful to think of your job runs as self-contained groups of jobs separated by time called **batches**.

Oliver has facilities baked in to compute batches automatically (meaning you don't need to specify the batch number at submit time). Just ensure the `batch_interval_mins` configuration variable is set and try `oliver batches`.

```bash
oliver batches
```

You can restrict `oliver status` to only report only a subset of batches. For instance, you can report on the first batch ever run (`-B`/`--batches-absolute`).

```bash
oliver status -B 0
```

Or, more commonly, you are interested in the last batch run (`-b`/`--batches-relative`).

```bash
oliver status -b 0
```

## Job Names and Groups

If you have submitted jobs with an Oliver Job Name or Oliver Job Group, you can restrict results to only workflows assigned to that name/group.

```bash
oliver status -g CohortName
```