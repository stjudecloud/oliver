from ..config import read_config, write_config

def call(args):
    cromwell_server = input("What is the Cromwell server address? ")
    cromwell_api_version = input("What is the Cromwell API version? ")
    config = {
        "cromwell_server": cromwell_server,
        "cromwell_api_version": cromwell_api_version
    }
    write_config(config)


def register_subparser(subparser):
    subcommand = subparser.add_parser("configure", help="Configure Oliver with default options.")