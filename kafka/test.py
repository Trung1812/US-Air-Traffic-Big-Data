from json_producer import setting_up

if __name__=="__main__":
    key = {"flight_id": "12345"}  # Replace with your key structure
    value = {
        "flight_date": "2024-11-22",
        "flight_status": "landed",
        "departure": {
            "airport": "LHR",
            "timezone": "Europe/London",
            "iata": "LHR",
            "icao": "EGLL",
            "terminal": "5",
            "gate": "A10",
            "delay": "10",
            "scheduled": "2024-11-22T14:30:00Z",
            "estimated": "2024-11-22T14:35:00Z",
            "actual": None,
            "estimated_runway": None,
            "actual_runway": None,
        },
        "arrival": {
            "airport": "JFK",
            "timezone": "America/New_York",
            "iata": "JFK",
            "icao": "KJFK",
            "terminal": "4",
            "gate": "B20",
            "baggage": "12",
            "delay": None,
            "scheduled": "2024-11-22T18:30:00Z",
            "estimated": "2024-11-22T18:35:00Z",
            "actual": None,
            "estimated_runway": None,
            "actual_runway": None,
        },
        "airline": {
            "name": "British Airways",
            "iata": "BA",
            "icao": "BAW",
        },
        "flight": {
            "number": "BA123",
            "iata": "BA123",
            "icao": "BAW123",
            "codeshared": {},
        },
    }

    producer = setting_up()
    try:
        producer.send_message(key=key, value=value)
    except Exception as e:
        print(f"Error message: {e}")
    producer.commit()

