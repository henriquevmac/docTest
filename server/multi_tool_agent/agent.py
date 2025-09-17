from datetime import datetime
from google.adk.agents import Agent
import requests

def get_current_date() -> str:
    """Returns the current date in the format YYYY-MM-DDTHH:MM:SSZ.

    Returns:
        str: current date in the format YYYY-MM-DDTHH:MM:SSZ.
    """
    date = datetime.now()
    current_time = date.strftime("%Y-%m-%dT%H:%M:%SZ")
    return current_time


def get_services() -> list:
    """Returns a list of available services.

    Returns:
        list: list of services where each service is a dictionary with the keys "id" and "name", empty list if no services are available.
    """
    response = requests.get("https://api.doc.pt/booking-page/doc/stores/doc/services")
    if response.status_code == 200:
        json_response = response.json()
        services = []
        for service in json_response["data"]:
            service_id = service["id"]
            service_name = service["name"]
            service = {
                    "id": service_id,
                    "name": service_name,
                    }
            services.append(service)
        return services
    else:
        return []

def get_providers(service: int) -> list:
    """Returns a list of providers for a specified service

    Args: 
        service (int): The id of the service for which to retrieve the providers.

    Returns: 
        list: list of providers where each provider is a dictionary with the keys "id" and "name", empty list if no providers are available.
    """
    response = requests.get(f"https://api.doc.pt/booking-page/doc/stores/doc/providers?serviceId={service}")
    if response.status_code == 200:
        json_response = response.json()
        workers = []
        for worker in json_response["data"]:
            worker_id = worker["id"]
            worker_name = worker["name"]
            worker = {
                    "id": worker_id,
                    "name": worker_name,
                    }
            workers.append(worker)
        return workers
    else:
        return []

def get_availability(dateInit: str, dateEnd: str, service: list[int], provider: list[int]) -> list:
    """Returns a list of the availabilities and durations for the specified data range, services and providers.

    Args:
        dateInit (str): The initial date of the availability, int the format YYYY-MM-DDTHH:MM:SSZ.
        dateEnd (str): The final date of the availability, int the format YYYY-MM-DDTHH:MM:SSZ.
        service (list[int]): The ids of the services for which to retrieve the availability, size must be greater than 0.
        provider (list[int]): The ids of the providers for which to retrieve the availability, size must be greater than 0.

    Returns:
        list: list of availability where each availability is a dictionary with the keys "Service_id", "Provider_id", "Day", "startTime", "endTime", "duration", empty list if no availability is available.
    """
    body = {
            "dateInit": dateInit,
            "dateEnd": dateEnd,
            "services": service,
            "providers": provider,
            }
    response = requests.post("https://api.doc.pt/booking-page/doc/stores/doc/availability", json=body)
    if response.status_code == 200:
        json_response = response.json()
        availabilities = []
        for availability in json_response["data"]:
            day = availability["day"]
            for hours in availability["hours"]:
                startTime = hours["start"]
                endTime = hours["end"]
                providers = hours["providers"]
                services = hours["services"]
                durations = hours["durations"]
                for i, provider in enumerate(providers):
                    provider_id = provider
                    service_id = services[i]
                    duration = durations[i]
                    availability = {
                            "Service_id": service_id,
                            "Provider_id": provider_id,
                            "Day": day,
                            "startTime": startTime,
                            "endTime": endTime,
                            "duration": duration,
                            }
                    availabilities.append(availability)
        return availabilities
    else:
        return []

root_agent = Agent(
        name="clinic_booking_agent",
        model="gemini-2.0-flash",
        description=(
            "Agent to answer questions about the services available in a clinic, the providers for each service and the availability for a specified date range."
            ),
        instruction=(
            "You are a helpful agent who can answer user questions about the services available in a clinic, what providers are available for each service and their availabilities in a time frame. "
            "You should not inform the user of the Id's of the services nor for the providers, this is metadata that only you should be able to see to make your job easier. " 
            "You can also get the current date to help you finding dates if the user only uses relative terms such as Tomorrow, end of the month, etc. " 
            "If the user doesn't provide an end date you should assume that the end date is the end of the current month. "
            "If the user doesn't provide a start date you should assume that the start date is the current date. "
            "If the user only provides a date range when asking for availability, you should get the list of all serices and providers and then return their availabilities in the date range provided. "
            "When the user asks for the availability you should return it in the format: Service Name, Provider Name, Day, Start Time, End Time, Duration. "
            ),
        tools=[get_services, get_providers, get_availability, get_current_date],
        )
