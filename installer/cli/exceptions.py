from click import ClickException

from ..models import Service


class CommandNotImplementedError(ClickException):
    """Raised if a command is not implemented yet."""

    def __init__(self):
        super().__init__("This command is not implemented yet")


class SecretsNotFoundError(ClickException):
    """Raised if no secrets were found for service."""

    def __init__(self, service: Service):
        self.service = service
        msg = f"Secrets of service {service.name!r} can't be found"
        super().__init__(msg)


class SecretNotFound(ClickException):
    """Raised if a particular secret is not found for a service."""

    def __init__(self, service: Service, key: str):
        self.service = service
        self.key = key
        msg = f"Service {service.name!r} has no secret named {key!r}"
        super().__init__(msg)


class ServiceNotFoundError(ClickException):
    """Raised if no service was found with a specified name."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        msg = f"No service was found with name {service_name!r}"
        super().__init__(msg)


class ProfileNotFoundError(ClickException):
    """Raised if no profile was found with a specified name."""

    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        msg = f"No profile was found with name {profile_name!r}"
        super().__init__(msg)


class TryAgainError(ClickException):
    """Raised when the client needs to run a command again."""


class DockerNotRunningError(ClickException):
    """Raised when the docker daemon is not running."""

    def __init__(self):
        super().__init__("The docker daemon is not running")
