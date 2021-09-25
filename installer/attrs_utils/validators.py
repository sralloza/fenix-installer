SERVICES_NEEDED = ["default", "traefik"]


def validate_required_services(service, attribute, value):
    if service.name in SERVICES_NEEDED and value is False:
        raise ValueError(f"Can't disable service {service.name} as it is required.")
