import csv
import hashlib
import re
import requests
import os
import logging
from getpass import getpass
from datetime import datetime, timedelta

CSV_FILE = 'login_credincial.csv'
LOG_FILE = 'space_data_app.log'
MAX_LOGIN_ATTEMPTS = 5
NASA_API_KEY = 'uq6LhypZNvWCLmfetEPWEgn66XE5JGOagPnhxFOE'

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def create_csv_file():
    if not os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['email', 'password', 'security_question', 'security_answer'])
            logging.info(f"{CSV_FILE} created successfully.")
            print(f"{CSV_FILE} created successfully.")
        except IOError as e:
            logging.error(f"Error creating {CSV_FILE}: {e}")
            print(f"Error creating {CSV_FILE}: {e}")
            exit(1)

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    return len(password) >= 8 and any(char in '!@#$%^&*(),.?":{}|<>' for char in password)

def read_csv_file():
    try:
        with open(CSV_FILE, 'r') as file:
            return list(csv.DictReader(file))
    except FileNotFoundError:
        logging.error(f"Error: {CSV_FILE} not found.")
        print(f"Error: {CSV_FILE} not found. Please restart the application.")
        exit(1)
    except csv.Error as e:
        logging.error(f"Error reading {CSV_FILE}: {e}")
        print(f"Error reading {CSV_FILE}: {e}")
        return []

def write_csv_file(rows):
    try:
        with open(CSV_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['email', 'password', 'security_question', 'security_answer'])
            writer.writeheader()
            writer.writerows(rows)
    except IOError as e:
        logging.error(f"Error writing to {CSV_FILE}: {e}")
        print(f"Error writing to {CSV_FILE}: {e}")

def signup():
    logging.info("User attempting to sign up")
    print("Sign Up")
    while True:
        email = input("Enter your email: ")
        if not validate_email(email):
            logging.warning(f"Invalid email format attempted: {email}")
            print("Invalid email format. Please try again.")
            continue
        
        rows = read_csv_file()
        if any(row['email'] == email for row in rows):
            logging.warning(f"Signup attempted with existing email: {email}")
            print("Email already exists. Please use a different email.")
            continue
        
        while True:
            password = getpass("Enter password (min 8 characters, at least one special character): ")
            if validate_password(password):
                break
            logging.warning("Invalid password format attempted")
            print("Invalid password. Please try again.")
        
        security_question = input("Enter a security question: ")
        security_answer = input("Enter the answer to your security question: ")
        
        new_user = {
            'email': email,
            'password': hash_password(password),
            'security_question': security_question,
            'security_answer': security_answer
        }
        rows.append(new_user)
        write_csv_file(rows)
        logging.info(f"New user signed up: {email}")
        print("Sign up successful!")
        return

def login():
    logging.info("User attempting to log in")
    attempts = 0
    while attempts < MAX_LOGIN_ATTEMPTS:
        email = input("Enter your email: ")
        password = getpass("Enter your password: ")
        
        if not validate_email(email):
            logging.warning(f"Invalid email format attempted: {email}")
            print("Invalid email format. Please try again.")
            continue
        
        rows = read_csv_file()
        for row in rows:
            if row['email'] == email and row['password'] == hash_password(password):
                logging.info(f"User logged in successfully: {email}")
                print("Login successful!")
                return True
        
        logging.warning(f"Failed login attempt for email: {email}")
        print("Invalid credentials. Please try again.")
        attempts += 1
    
    logging.warning(f"Maximum login attempts reached for email: {email}")
    print(f"Maximum login attempts ({MAX_LOGIN_ATTEMPTS}) reached. Please try again later.")
    return False

def forgot_password():
    logging.info("User attempting to reset password")
    email = input("Enter your registered email: ")
    
    rows = read_csv_file()
    for row in rows:
        if row['email'] == email:
            security_answer = input(f"Security Question: {row['security_question']}\nYour answer: ")
            if security_answer.lower() == row['security_answer'].lower():
                while True:
                    new_password = getpass("Enter new password (min 8 characters, at least one special character): ")
                    if validate_password(new_password):
                        row['password'] = hash_password(new_password)
                        write_csv_file(rows)
                        logging.info(f"Password reset successful for email: {email}")
                        print("Password reset successful!")
                        return
                    else:
                        logging.warning("Invalid password format attempted during reset")
                        print("Invalid password format. Please try again.")
            else:
                logging.warning(f"Incorrect security answer for email: {email}")
                print("Incorrect security answer.")
                return
    
    logging.warning(f"Password reset attempted for non-existent email: {email}")
    print("Email not found.")

def fetch_api_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.HTTPError):
            if e.response.status_code == 403:
                logging.error("Invalid or expired API key")
                print("Error: Invalid or expired API key.")
            elif e.response.status_code == 404:
                logging.error("Requested resource not found")
                print("Error: Requested resource not found.")
            else:
                logging.error(f"HTTP Error: {e}")
                print(f"HTTP Error: {e}")
        elif isinstance(e, requests.exceptions.ConnectionError):
            logging.error("No internet connection")
            print("Error: No internet connection.")
        elif isinstance(e, requests.exceptions.Timeout):
            logging.error("Request timed out")
            print("Error: Request timed out.")
        else:
            logging.error(f"Error fetching data: {e}")
            print(f"Error fetching data: {e}")
        return None

def fetch_neo_data():
    logging.info("Fetching NEO data")
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={NASA_API_KEY}"
    data = fetch_api_data(url)
    if data:
        print("Near Earth Object (NEO) Data:")
        neo_count = 0
        for date, neo_list in data['near_earth_objects'].items():
            for neo in neo_list:
                neo_count += 1
                print(f"\nNEO #{neo_count}:")
                print(f"Name: {neo['name']}")
                print(f"Close Approach Date: {neo['close_approach_data'][0]['close_approach_date']}")
                print(f"Estimated Diameter: {neo['estimated_diameter']['meters']['estimated_diameter_min']:.2f} - {neo['estimated_diameter']['meters']['estimated_diameter_max']:.2f} meters")
                print(f"Velocity: {float(neo['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']):.2f} km/h")
                print(f"Miss Distance: {float(neo['close_approach_data'][0]['miss_distance']['kilometers']):.2f} km")
                print(f"Potentially Hazardous: {'Yes' if neo['is_potentially_hazardous_asteroid'] else 'No'}")
        
        if neo_count == 0:
            logging.info("No NEOs found for the given date range")
            print("No Near Earth Objects found for the given date range.")
    else:
        logging.error("Failed to fetch NEO data")
        print("Failed to fetch NEO data. Please try again later.")

def fetch_ssd_data():
    object_name = input("Enter the name or ID of a celestial object (e.g., 'mars', '433', 'halley'): ").lower()
    logging.info(f"Fetching SSD data for object: {object_name}")
    url = f"https://api.le-systeme-solaire.net/rest/bodies/{object_name}"
    data = fetch_api_data(url)
    
    if data:
        print("\nSolar System Dynamics Data:")
        
        print(f"Name: {data.get('englishName', 'N/A')}")
        print(f"Object Type: {data.get('bodyType', 'N/A')}")
        
        if 'semimajorAxis' in data:
            print("\nOrbital Elements:")
            print(f"Semi-major axis: {data.get('semimajorAxis', 'N/A')} km")
            print(f"Eccentricity: {data.get('eccentricity', 'N/A')}")
            print(f"Inclination: {data.get('inclination', 'N/A')} degrees")
            print(f"Orbital period: {data.get('sideralOrbit', 'N/A')} days")
        
        print("\nPhysical Parameters:")
        print(f"Diameter: {data.get('meanRadius', 'N/A')} km")
        print(f"Mass: {data.get('mass', {}).get('massValue', 'N/A')} x 10^{data.get('mass', {}).get('massExponent', 'N/A')} kg")
        print(f"Density: {data.get('density', 'N/A')} g/cm³")
        
        print(f"Rotation period: {data.get('sideralRotation', 'N/A')} hours")
        
        if data.get('discoveredBy') or data.get('discoveryDate'):
            print("\nDiscovery Information:")
            print(f"Discovered by: {data.get('discoveredBy', 'N/A')}")
            print(f"Discovery date: {data.get('discoveryDate', 'N/A')}")
        
    else:
        logging.warning(f"No data found for the object: {object_name}")
        print(f"No data found for the object: {object_name}")


def main():
    logging.info("Space Data Application started")
    print("Welcome to the Space Data Application!")
    create_csv_file() 
    while True:
        try:
            choice = input("1. Sign Up\n2. Log In\n3. Forgot Password\n4. Exit\nEnter your choice: ")
            if choice == '1':
                signup()
            elif choice == '2':
                if login():
                    while True:
                        data_choice = input("1. Fetch NEO Data\n2. Fetch SSD Data\n3. Logout\nEnter your choice: ")
                        if data_choice == '1':
                            fetch_neo_data()
                        elif data_choice == '2':
                            fetch_ssd_data()
                        elif data_choice == '3':
                            logging.info("User logged out")
                            print("Logging out...")
                            break
                        else:
                            print("Invalid choice. Please try again.")
            elif choice == '3':
                forgot_password()
            elif choice == '4':
                logging.info("Space Data Application exited")
                print("Thank you for using the Space Data Application. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
        except KeyboardInterrupt:
            logging.info("Program interrupted by user")
            print("\nProgram interrupted. Exiting...")
            break
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            print(f"An unexpected error occurred: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()