import requests

def get_availability(dateInit: str, dateEnd: str, service: list[int], provider: list[int]) -> list:
    """Returns a list of the availability for the specified data range and services and providers.

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
    print(response.status_code)
    print(response.text)
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
                    avail = {
                            "Service_id": service_id,
                            "Provider_id": provider_id,
                            "Day": day,
                            "startTime": startTime,
                            "endTime": endTime,
                            "duration": duration,
                            }
                    availabilities.append(avail)
        return availabilities
    else:
        return []

print(get_availability("2025-09-01T00:00:00Z", "2025-09-30T23:59:59Z", [18, 19], [14, 15]))
