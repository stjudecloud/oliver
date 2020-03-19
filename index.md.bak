<p align="center">
  <h1 align="center">
    Oliver
  </h1>

  <p align="center">
    <a href="https://actions-badge.atrox.dev/stjudecloud/oliver/goto" target="_blank">
      <img alt="Actions: CI Status"
          src="https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fstjudecloud%2Foliver%2Fbadge&style=flat" />
    </a>
    <a href="https://pypi.org/project/stjudecloud-oliver/" target="_blank">
      <img alt="PyPI"
          src="https://img.shields.io/pypi/v/stjudecloud-oliver?color=orange">
    </a>
    <a href="https://pypi.org/project/stjudecloud-oliver/" target="_blank">
      <img alt="PyPI: Downloads"
          src="https://img.shields.io/pypi/dm/stjudecloud-oliver?color=orange">
    </a>
    <a href="https://anaconda.org/conda-forge/oliver" target="_blank">
      <img alt="Conda"
          src="https://img.shields.io/conda/vn/conda-forge/oliver.svg?color=brightgreen">
    </a>
    <a href="https://anaconda.org/conda-forge/oliver" target="_blank">
      <img alt="Conda: Downloads"
          src="https://img.shields.io/conda/dn/conda-forge/oliver?color=brightgreen">
    </a>
    <a href="https://codecov.io/gh/stjudecloud/oliver" target="_blank">
      <img alt="Code Coverage"
          src="https://codecov.io/gh/stjudecloud/oliver/branch/master/graph/badge.svg" />
    </a>
    <a href="https://github.com/stjudecloud/oliver/blob/master/LICENSE.md" target="_blank">
    <img alt="License: MIT"
          src="https://img.shields.io/badge/License-MIT-blue.svg" />
    </a>
  </p>


  <p align="center">
    An opinionated Cromwell orchestration manager.
    <br />
    <a href="https://stjudecloud.github.io/oliver/"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/stjudecloud/oliver/issues/new?assignees=&labels=&template=feature_request.md&title=Descriptive%20Title&labels=enhancement">Request Feature</a>
    ·
    <a href="https://github.com/stjudecloud/oliver/issues/new?assignees=&labels=&template=bug_report.md&title=Descriptive%20Title&labels=bug">Report Bug</a>
    ·
    ⭐ Consider starring the repo! ⭐
    <br />
  </p>
</p>

<!-- ## 🎨 Demo -->
<br />
<p align="center">
  <img alt="Example of Oliver usage" src="https://stjudecloud.github.io/oliver/images/oliver-example.gif"/>
</p>
<br />

## 🎨 Features


* <b>Workflow Orchestration.</b> Easily submit, inspect, kill, and retry workflows in a Cromwell environment.
* <b>Better Job Tracking.</b> Jobs can be associated with names and job groups to enable better status reporting.
* <b>Dynamic Argument Parsing.</b> Specify inputs and options on the command line rather than editing JSON files.
* <b>Third-party Cloud Integrations.</b> Use the `aws` and `azure` subcommands to explore cloud-specific functionality.

## 📚 Getting Started

### Installation

#### Conda

Oliver is distributed as a package using the community-curated Anaconda repository, [conda-forge](https://conda-forge.org/). You'll need to [install conda][conda-install], and we recommend that you first follow [the instructions included in the conda-forge documentation][conda-forge-setup] to get everything set up!

```bash
conda install oliver -c conda-forge
```

#### Python Package Index

You can also install Oliver using the Python Package Index ([PyPI](https://pypi.org/)).

```bash
pip install stjudecloud-oliver
```

### Configuring

Next, we recommend that you configure oliver so that common arguments can be saved. By default, Oliver will prompt you for the answers interactively.

```bash
oliver configure
```

If you are setting up Oliver programmatically, you can accept a default configuration (`oliver configure --defaults`) and edit from there using `oliver config`.

## 🚌 A Quick Tour

At its foundation, Oliver is an opinionated job orchestrator for Cromwell. Commonly, you will want to use it to submit a job, inspect a job's status, kill a job, retry a job (possibly with different parameters), and organize job results.

If you're interested in a complete overview of Oliver's capabilities, please see [**the documentation pages**](https://stjudecloud.github.io/oliver/)</a>.

#### Submit a Job

The simplest possible job submission is one which submits a simple workflow with one or more input JSON file(s) and/or key-value pair(s).

```bash
oliver submit workflow.wdl inputs.json input_key=input_value
```

You can similarly set workflow options and labels by prepending arguments with `@` and `%` respectively.

```bash
# works for files too!
oliver submit workflow.wdl @option=foo %label=bar
```

Please [**see the docs**](https://stjudecloud.github.io/oliver/getting-started/submit-jobs/) for more details on job submission.

#### Inspect a Job

Once a job is submitted, you can interrogate the Cromwell server about its status.

```bash
oliver inspect workflow-id
```

If you aren't sure what workflow identifier was given to your job, you can easily track it down using the `status` subcommand.

```bash
# detailed view, which shows individual workflow statuses
oliver status -d
```

#### Kill a Job

If, for whatever reason, you'd like to stop a job, you can use Oliver to instruct Cromwell to do so.

```bash
oliver kill workflow-id
```

#### Retry a Job

Retrying a workflow is similarly easy: even if you need to override previously set parameters (e.g. increase the memory capacity for a task).

```bash
# override previous inputs by specifying arguments (the same way as you would for `submit`).
oliver retry workflow-id
```

## 🖥️ Development

If you are interested in contributing to the code, please first review
our [CONTRIBUTING.md][contributing-md] document. To bootstrap a
development environment, please use the following commands.

```bash
# Clone the repository
git clone git@github.com:stjudecloud/oliver.git
cd oliver

# Install the project using poetry
poetry install

# Ensure pre-commit is installed to automatically format
# code using `black`.
brew install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

## 🚧️ Tests

Oliver provides a (currently patchy) set of tests — both unit and end-to-end. To get started with testing, you'll
need to bootstrap a Docker test environment (one-time operation).

```bash
# Start development environment
docker image build --tag oliver .
docker-compose up --build  -d

alias docker-run-oliver="docker container run \
  -it \
  --rm \
  --network oliver_default \
  --mount type=bind,source=$PWD/seeds,target=/opt/oliver/seeds \
  --mount type=bind,source=$PWD/oliver,target=/opt/oliver/oliver \
  --mount type=bind,source=$PWD/tests,target=/opt/oliver/tests \
  --entrypoint '' \
  oliver:latest"

# Seed development environment (make sure Cromwell is live first!)
docker-run-oliver bash seeds/seed.sh http://cromwell:8000 seeds/wdl/hello.wdl
docker-run-oliver pytest --cov=./ --cov-report=xml
```

To reset your entire docker-compose environment, you can run the following:

```bash
docker-compose down

docker image rm oliver:latest
docker image rm oliver_cromwell:latest
docker image rm mysql:5.7
docker volume rm oliver_mysql_data
docker network rm oliver_default

docker image build --tag oliver .
docker-compose up --build -d
```

## 🤝 Contributing

Contributions, issues and feature requests are welcome!<br />Feel free to check [issues page](https://github.com/stjudecloud/oliver/issues). You can also take a look at the [contributing guide][contributing-md].

## 📝 License

Copyright © 2020 [St. Jude Cloud Team](https://github.com/stjudecloud).<br />
This project is [MIT][license-md] licensed.

[conda-install]: https://docs.anaconda.com/anaconda/install/
[conda-forge-setup]: https://conda-forge.org/docs/user/introduction.html#how-can-i-install-packages-from-conda-forge
[contributing-md]: https://github.com/stjudecloud/oliver/blob/master/CONTRIBUTING.md
[license-md]: https://github.com/stjudecloud/oliver/blob/master/LICENSE.md