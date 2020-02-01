def add_loglevel_group(parser, required=False):
    """Adds log level groups to a parser."""

    loglevel_group = parser.add_mutually_exclusive_group(required=required)
    loglevel_group.add_argument(
        "--debug",
        help="Set the log level to DEBUG.",
        default=False,
        action="store_true",
    )
    loglevel_group.add_argument(
        "-v",
        "--verbose",
        help="Set the log level to INFO.",
        default=False,
        action="store_true",
    )


def add_batches_interval_arg(parser):
    parser.add_argument(
        "-x",
        "--batch-interval-mins",
        help="Split batches by any two jobs separated by N minutes.",
        type=int,
    )


def add_batches_group(
    parser, required=False, add_batches_interval_arg_automatically=True
):
    batches = parser.add_mutually_exclusive_group(required=required)
    batches.add_argument(
        "-b",
        "--batches-relative",
        help="Starting with the _most recent_ batch, compute batches separated by `batch-interval-mins`. Any batches not contained in `batches` are filtered.",
        default=None,
        nargs="+",
        type=int,
    )
    batches.add_argument(
        "-B",
        "--batches-absolute",
        help="Starting with the _first batch in time_, compute batches separated by `batch-interval-mins`. Any batches not contained in `batches` are filtered.",
        nargs="+",
        default=None,
        type=int,
    )
    if add_batches_interval_arg_automatically:
        add_batches_interval_arg(parser)


def add_oliver_job_group_args(parser, **kwargs):
    _kwargs = {"help": "Specify the Oliver job group.", "type": str, "default": None}
    _kwargs.update(kwargs)
    parser.add_argument("-g", "--job-group", **_kwargs)


def add_oliver_job_name_args(parser, **kwargs):
    _kwargs = {"help": "Specify the Oliver job name.", "type": str, "default": None}
    _kwargs.update(kwargs)
    parser.add_argument("-j", "--job-name", **_kwargs)
