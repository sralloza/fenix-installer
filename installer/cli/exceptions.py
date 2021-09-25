from click.exceptions import ClickException


class CommandNotImplementedError(ClickException):
    """Raised if a command is not implemented yet."""

    def __init__(self):
        super().__init__("This command is not implemented yet")
