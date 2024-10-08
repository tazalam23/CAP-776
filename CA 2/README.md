# CAP776
This is Python mini project  for CA-2 using API
Topic: NASA Data Console Screen with Login and API Integration
Problem Statement
Create a Python-based console application where users need to log in to access space-related data using the NASA API. The user credentials should be stored in a CSV file, and a password reset option should be available. The application should limit tailed login attempts to prevent unauthorized access. Upon successful login, the app will fetch and display data from the NASA API.
Requirements:
1.	Login System:
o	User credentials are stored in a CSV file (regno.csv). The file contains fields like email, password (hashed), and security_question (for password recovery).
o	During login, the system will prompt the user for their email and password.
2.	Input Validation:
o	The email must be in a valid format (e.g., example@domain.com).
o	The password must meet a minimum length of 8 characters, contain at least one special character, and be validated against the stored password (use hashing for comparison).
3.	Forgot Password:
o	If the user chooses to reset their password, they are prompted to enter their registered email.
o	If the email exists in the CSV file, the user must answer a security question correctly. Upon correct answer, they can set a new password.
4.	Login Attempts:
o	The user is allowed up to 5 login attempts. After 5 failed attempts, the user is logged out, and further attempts are denied until the application restarts.
5.	API Integration (NASA API):
Near Earth Object (NEO) Feed
Description: Provides data about asteroids and other near-Earth objects (NEOs) tracked by NASA.
Data Available:
o	Name of the NEO
o	Close approach date
o	Estimated diameter (in meters)
o	Velocity (in km/h)
o	Miss distance (in kilometers)
o	Hazardous status (true/false)
API https://api.nasa.gov/neo/rest/v1/feed?api_key=YOUR_API_KEY
NASA Solar System Dynamics (SSD) API
•	Description: Provides data on planets, moons, comets, asteroids, and other objects in the Solar System.
•	Data Available:
o	Orbital elements (e.g., semi-major axis, eccentricity)
o	Physical parameters (e.g., diameter, mass)
o	Object classification (e.g., planet, dwarf planet)
o	Discovery date
o	Rotation period
API https://ssd-api.jpl.nasa.gov/
6.	Error Handling:
o	Handle cases where the API key is invalid or expired.
o	Handle network errors (e.g., no internet connection).
o	Handle cases where no results are found (e.g., no Mars Rover photos available for the selected date).


