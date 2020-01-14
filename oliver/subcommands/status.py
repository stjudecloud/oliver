def call(args):
    print(f"What is N? {args.n}!")

def register_subparser(subparser):
    subcommand = subparser.add_parser("status", help="Report various statistics about a running Cromwell server.")
    subcommand.add_argument("-n", default=42)