from ..config import get_default_config, read_config, write_config

QUESTION_MAPPING = {
    "cromwell_server": "What is the Cromwell server address",
    "cromwell_api_version": "What is the Cromwell API version",
}


def ask(question, default):
    return input(f"{question} (default: {default})? ")


def call(args):
    starting_config = get_default_config()
    starting_config.update(read_config())
    final_config = {}

    for k, v in starting_config.items():
        question = "What is the value for '{k}'"
        if k in QUESTION_MAPPING:
            question = QUESTION_MAPPING[k]

        answer = ask(question, v)
        if answer:
            v = answer
        final_config[k] = v

    write_config(final_config)


def register_subparser(subparser):
    subcommand = subparser.add_parser(
        "configure", help="Configure Oliver with default options."
    )
