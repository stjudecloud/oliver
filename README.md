<h1 align="center">Oliver</h1>

<p align="center">
  <a href="https://actions-badge.atrox.dev/stjudecloud/oliver/goto"><img alt="Build Status" src="https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fstjudecloud%2Foliver%2Fbadge&style=flat" />
  </a>
  <a href="https://pypi.org/project/stjudecloud-oliver/" target="_blank">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/stjudecloud-oliver?color=orange">
  </a>
  <a href="https://pypi.org/project/stjudecloud-oliver/" target="_blank">
    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/stjudecloud-oliver?color=orange">
  </a>
  <a href="https://anaconda.org/conda-forge/oliver" target="_blank">
    <img alt="Conda" src="https://img.shields.io/conda/vn/conda-forge/oliver.svg?color=brightgreen">
  </a>
  <a href="https://anaconda.org/conda-forge/oliver" target="_blank">
    <img alt="Conda - Downloads" src="https://img.shields.io/conda/dn/conda-forge/oliver?color=brightgreen">
  </a>
  <a href="https://github.com/stjudecloud/oliver/blob/master/LICENSE.md" target="_blank">
    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-blue.svg" />
  </a>
</p>

![Oliver Example](./docs/oliver-example.gif)

> An opinionated Cromwell orchestration manager.

## Getting Started

## Conda

Oliver is distributed as a package using the community-curated Anaconda repository, [conda-forge](https://conda-forge.org/). We recommend that you first follow [the instructions included in the conda-forge documentation](https://conda-forge.org/docs/user/introduction.html#how-can-i-install-packages-from-conda-forge) to get everything set up!

```bash
conda install oliver -c conda-forge
```

### Python Package Index

You can also install Oliver using the Python Package Index ([PyPI](https://pypi.org/)).

```sh
pip install stjudecloud-oliver
```

Please refer to the guides in the `docs/` folder for more information.

| Guide Name      | Link                             |
| --------------- | -------------------------------- |
| Advanced Usage  | [Link](./docs/ADVANCED_USAGE.md) |
| Configuration   | [Link](./docs/CONFIGURATION.md)  |
| Submitting Jobs | [Link](./docs/SUBMIT.md)         |

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

## Development

If you are interested in contributing to the code, please first review
our [CONTRIBUTING.md](../CONTRIBUTING.md) document. To bootstrap a 
development environment, please use the following commands.

```bash
# Clone the repository
git clone git@github.com:stjudecloud/oliver.git
cd oliver

# Link the package with your current Python environment
python setup.py develop

# Ensure pre-commit is installed to automatically format
# code using `black`.
brew install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

## Tests

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
  --mount type=bind,source=$PWD/scripts,target=/opt/oliver/scripts \
  --mount type=bind,source=$PWD/tests,target=/opt/oliver/tests \
  oliver"

# Seed development environment (make sure Cromwell is live first!)
docker-run-oliver bash seeds/seed.sh http://cromwell:8000 seeds/wdl/hello.wdl
docker-run-oliver pytest
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