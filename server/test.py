from itertools import product
import requests

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
    availabilities = []
    combinations = list(product(service, provider))
    for combination in combinations:
        body = {
                "dateInit": dateInit,
                "dateEnd": dateEnd,
                "services": [combination[0]],
                "providers": [combination[1]],
                }
        response = requests.post("https://api.doc.pt/booking-page/doc/stores/doc/availability", json=body)
        if response.status_code == 200:
            json_response = response.json()
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
                        avail = {
                                "Service_id": service_id,
                                "Provider_id": provider_id,
                                "Day": day,
                                "startTime": startTime,
                                "endTime": endTime,
                                "duration": duration,
                                }
                        availabilities.append(avail)
        else:
            return []
    return availabilities

availabilities = get_availability("2025-09-17T00:00:00Z", "2025-12-17T23:59:59Z", [18, 19], [14, 15])
for availability in availabilities:
    print(availability)
