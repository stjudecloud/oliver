<h1 align="center">Oliver</h1>
<p>
  <a href="https://www.npmjs.com/package/oliver" target="_blank">
    <img alt="Version" src="https://img.shields.io/static/v1?label=version&message=alpha&color=orange">
  </a>
  <a href="https://github.com/stjudecloud/oliver/blob/master/LICENSE.md" target="_blank">
    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg" />
  </a>
</p>

> An opinionated Cromwell orchestration manager.

## Install

```sh
# Developer workstation
python setup.py develop

# Package install
python setup.py install
```

## Usage

```sh
oliver --help
```

Currently, the following commands are supported.

| Command     | Description                                                |
| ----------- | ---------------------------------------------------------- |
| `configure` | Configure Oliver with default options.                     |
| `config`    | Set or get a single config value from Oliver.              |
| `inspect`   | Inspect a workflow.                                        |
| `kill`      | Kill a workflow running on a Cromwell server.              |
| `logs`      | Find all reported logs for a given workflow.               |
| `outputs`   | Find all reported outputs for a given workflow.            |
| `runtime`   | Get the runtime attributes used for a specific call.       |
| `status`    | Report various statistics about a running Cromwell server. |

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