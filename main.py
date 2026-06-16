import requests_cache
from pprint import pprint
from datetime import datetime, timedelta
from data_manager import DataManager
from flight_search import FlightSearch
from flight_data import find_cheapest_flight
from notification_manager import NotificationManager

# Cache setups to preserve plan allocations
requests_cache.install_cache(
    "flight_cache",
    urls_expire_after={
        "*.sheety.co*": requests_cache.DO_NOT_CACHE,
        "*": 3600,
    }
)

data_manager = DataManager()
flight_search = FlightSearch()
notification_manager = NotificationManager()

sheet_data = data_manager.get_destination_data()
customer_emails = data_manager.get_customer_emails()

tomorrow = datetime.now() + timedelta(days=1)
six_month_from_today = datetime.now() + timedelta(days=(6 * 30))

outbound_str = tomorrow.strftime("%Y-%m-%d")
return_str = six_month_from_today.strftime("%Y-%m-%d")

for row in sheet_data:
    city_name = row["city"]
    iata_code = row["iataCode"]
    current_lowest_allowed = row["lowestPrice"]
    row_id = row["id"]

    print(f"\n--- Evaluation Session: {city_name} ({iata_code}) ---")
    print(f"Getting direct flights for {city_name}....")

    # Direct Search
    flights_json = flight_search.check_flights(
        origin_city_code="DEL",
        destination_city_code=iata_code,
        outbound_date=outbound_str,
        return_date=return_str,
        is_direct=True,
    )
    cheapest_flight = find_cheapest_flight(flights_json, return_date=return_str)

    # Indirect Search
    if cheapest_flight.price == "N/A":
        print(f"No direct flight to {city_name}. Looking for indirect flights...")
        flights_json = flight_search.check_flights(
            origin_city_code="DEL",
            destination_city_code=iata_code,
            outbound_date=outbound_str,
            return_date=return_str,
            is_direct=False,
        )
        cheapest_flight = find_cheapest_flight(flights_json, return_date=return_str)
    print(f"Sheet Threshold: GBP {current_lowest_allowed} | Market Best found: GBP {cheapest_flight.price} ({cheapest_flight.stops} stops)")

    # Notification logic
    if cheapest_flight.price != "N/A" and cheapest_flight.price < current_lowest_allowed:
        print(f"🔥 Price match broken! Updating database...")
        data_manager.update_lowest_price(row_id, cheapest_flight.price)
        
        if cheapest_flight.stops == 0:
            custom_message = (
                f"Great News! Low price alert for a Direct flight!\n\n"
                f"Only £{cheapest_flight.price} to fly non-stop from "
                f"{cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}!\n"
                f"📅 Outbound: {cheapest_flight.out_date}\n"
                f"📅 Inbound: {cheapest_flight.return_date}"
            )
        else:
            custom_message = (
                f"Low price alert with layovers found!\n\n"
                f"Only £{cheapest_flight.price} to fly from "
                f"{cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}!\n"
                f"⚠️ Note: This trip has {cheapest_flight.stops} stopover(s).\n"
                f"📅 Outbound: {cheapest_flight.out_date}\n"
                f"📅 Inbound: {cheapest_flight.return_date}"
            )
            
        # Send SMS notification 
        notification_manager.send_sms(cheapest_flight)
        
        # Custom message to all club members
        if customer_emails:
            print(f"Broadcasting email alerts to club membership rows...")
            notification_manager.send_emails(email_list=customer_emails, email_body=custom_message)
    else:
        print(f"No optimization actions required for {city_name}.")