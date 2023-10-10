import requests 
import json
from datetime import datetime, timedelta
import os
from apscheduler.schedulers.blocking import BlockingScheduler

def fetch(city):
    API_key = 'd9840fc70207fcb5360baeb5ebff2764'  # TODO how to store it safely?

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        return data
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch data for city: {city}. Error:{e}")

# Function to get the data for the 3 cities and store them
def ingest():
    cities = ['Paris', 'London', 'Washington']
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    directory = '/app/raw_files'

    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = f"{directory}/{timestamp}.json"

    data = {}

    for city in cities:
        data[city] = fetch(city)
    
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


if __name__=="__main__":

    

    # Create a scheduler
    scheduler = BlockingScheduler()

    # Define the job to run every minute for the next 20 minutes
    end_time = datetime.now() + timedelta(minutes=20)

    # Schedule the job to run every minute
    scheduler.add_job(ingest, 'interval', minutes=1, end_date=end_time)

    # Start the scheduler
    scheduler.start()

    
    
