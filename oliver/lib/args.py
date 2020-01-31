def add_loglevel_group(parser):
    """Adds log level groups to a parser."""

    loglevel_group = parser.add_mutually_exclusive_group()
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
