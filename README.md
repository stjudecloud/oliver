<h1 align="center">Oliver</h1>
<p align="center">
  <a href="https://www.npmjs.com/package/oliver" target="_blank">
    <img alt="Version" src="https://img.shields.io/static/v1?label=version&message=alpha&color=orange">
  </a>
  <a href="https://github.com/stjudecloud/oliver/blob/master/LICENSE.md" target="_blank">
    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg" />
  </a>
</p>

> An opinionated Cromwell orchestration manager.

![Oliver Example](./docs/oliver-example.gif)

## Install

```sh
# Package install
python setup.py install
```

## Development

```sh
# Clone the repository
git clone git@github.com:stjudecloud/oliver.git
cd oliver

# Link the package with your current Python environment
python setup.py develop

# Ensure pre-commit is installed to automatically format
# code using `black`.
brew install pre-commit
pre-commit install
```

## Usage

```text
oliver --help

usage: oliver [-h] [--cromwell-server CROMWELL_SERVER]
              [--cromwell-api-version CROMWELL_API_VERSION] [-v]
              {aggregate,a,configure,config,cosmos,inputs,inspect,i,kill,k,logs,l,outputs,o,retry,re,runtime,ru,status,st,submit,su}
              ...

An opinionated Cromwell orchestration system.

positional arguments:
  {aggregate,a,configure,config,cosmos,inputs,inspect,i,kill,k,logs,l,outputs,o,retry,re,runtime,ru,status,st,submit,su}
    aggregate (a)       Aggregate all results to a local or cloud folder for a
                        run.
    configure           Configure Oliver with default options.
    config              Set or get a single config value from Oliver.
    cosmos              Get cosmos DB entries for a workflow.
    inputs              Find all reported outputs for a given workflow.
    inspect (i)         Describe the state of a Cromwell workflow.
    kill (k)            Kill a workflow running on a Cromwell server.
    logs (l)            Find all reported logs for a given workflow.
    outputs (o)         Find all reported outputs for a given workflow.
    retry (re)          Resubmit a workflow with the same parameters.
    runtime (ru)        Get the runtime attributes used for a specific call.
    status (st)         Report various statistics about a running Cromwell
                        server.
    submit (su)         Submit a workflow to the Cromwell server.

optional arguments:
  -h, --help            show this help message and exit
  --cromwell-server CROMWELL_SERVER
                        Cromwell host location.
  --cromwell-api-version CROMWELL_API_VERSION
                        Cromwell API version.
  -v, --verbose         Print verbose output.
  ```

## Documentation

Please refer to the guides in the `docs/` folder for more in-depth
documentation.

| Guide Name     | Link                             |
| -------------- | -------------------------------- |
| Advanced Usage | [Link](./docs/ADVANCED_USAGE.md) |
| Configuration  | [Link](./docs/CONFIGURATION.md)  |

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