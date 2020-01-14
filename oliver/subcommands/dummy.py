def call(args):
    print(f"What is N? {args.n}!")

def register_subparser(subparser):
    subcommand = subparser.add_parser("dummy")
    subcommand.add_argument("-n", default=42)