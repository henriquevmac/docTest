from itertools import product
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

root_agent = Agent(
        name="clinic_booking_agent",
        model="gemini-2.5-flash",
        description=(
            "Agente para responder a questões sobre disponibilidades de serviços fornecidos para um intervalo de datas especificado."
            ),
        instruction=(
            "Tu és um AI agent que ajuda na consulta de disponibilidades numa clínica. "
            "Tu NUNCA deves informar o utilizador dos ID's dos serviços nem dos colaboradores. Isto são apenas dados para te auxiliar. "
            "O utilizador pode consultar que serviços tens disponíveis, que colaboradores é que fazem o serviço X, mas o mais comum será perguntarem disponibilidades. "
            "Tu consegues também obter a data atual para ajudar a encontrar datas se o utilizador utilizar termos relativos como amanhã, esta semana, fim do mês e etc. "
            "Se o utilizador não fornecer uma data de fim tu deves assumir que a data de fim é 3 meses após a data atual. "
            "Se o utilizador não fornecer uma data de início tu deves assumir que a data de início é o dia de hoje. "
            "Se o utilizador não fornecer um serviço nem um colaborador quando pedir disponibilidades tu deves assumir que ele quer as disponibilidades de todos os serviços e colaboradores, então deverás ir buscar a lista de todos os serviços e a lista de todos os colaboradores de cada serviço, e depois as disponibilidades. "
            "Se o utilizador pedir disponibilidades deves fornecê-las no formato: Nome do Serviço, Nome do Colaborador, Dia, Tempo de Início, Tempo de Fim, Duração. "
            "Se o utilizador apenas pedir disponibilidades para um tempo especifico tu deves ir buscar todas as disponibilidades e apenas mostrar disponibilidades com um Tempo Inicial igual a esse, se não exisitiram deves informar o utilizador disso e pedir desculpa. "
            ),
        tools=[get_services, get_providers, get_availability, get_current_date],
        )
