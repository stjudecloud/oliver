from ..config import read_config, write_config

def call(args):
    cromwell_server = input("What is the Cromwell server address? ")
    config = {
        "cromwell-server": cromwell_server
    }
    write_config(config)


def register_subparser(subparser):
    subcommand = subparser.add_parser("configure", help="Configure Oliver with default options.")