import mysql.connector
import random
from datetime import datetime

# Connect to the database
database = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='sanket1234',
    database='bus_ticketing'
)

connection = database.cursor()

# Create the table if it doesn't exist
create_table_query = '''
CREATE TABLE IF NOT EXISTS bookings (
    Passenger_Id INT PRIMARY KEY,
    Passenger_Name VARCHAR(255),
    Passenger_Age INT,
    No_of_passengers INT,
    Date_of_travel DATE,
    Price FLOAT
)
'''
connection.execute(create_table_query)

TOTAL_SEATS = 40


def display_menu():
    print("1. Seat Availability")
    print("2. Booking")
    print("3. Show all bookings")
    print("4. Update Booking Details")
    print("5. Cancel Booking")
    print("6. Exit Application")


# Validate date format (YYYY-MM-DD)
def validate_date(input_date):
    try:
        date = datetime.strptime(input_date, '%Y-%m-%d')
        return date.strftime('%Y-%m-%d')  # Return date in the correct format
    except ValueError:
        print("Invalid date format. Please enter in YYYY-MM-DD format.")
        return None


# Validate integer input (like age, number of passengers)
def validate_int_input(prompt):
    try:
        return int(input(prompt))
    except ValueError:
        print("Invalid input. Please enter a valid integer.")
        return None


# Generate a random six-digit Passenger ID
def generate_passenger_id():
    return random.randint(100000, 999999)


# Generalized function for executing MySQL queries
def execute_query(query, values=None):
    try:
        if values:
            connection.execute(query, values)
        else:
            connection.execute(query)
        database.commit()
    except mysql.connector.Error as err:
        print(f"Database error: {err}")


# Check seat availability for a specific travel date
def check_seat_availability(date_of_travel):
    query = "SELECT SUM(No_of_passengers) FROM bookings WHERE Date_of_travel = %s"
    execute_query(query, (date_of_travel,))
    booked_seats = connection.fetchone()[0]
    booked_seats = booked_seats if booked_seats is not None else 0
    available_seats = TOTAL_SEATS - booked_seats
    print(f"Total seats booked on {date_of_travel}: {booked_seats}")
    print(f"Seats available on {date_of_travel}: {available_seats}")
    return available_seats


# Book seats for passengers
def book_seat():
    date_of_travel = input("Enter Date of Travel (YYYY-MM-DD): ")
    date_of_travel = validate_date(date_of_travel)
    if date_of_travel is None:
        return

    available_seats = check_seat_availability(date_of_travel)

    if available_seats > 0:
        name = input("Enter Passenger Name: ")
        age = validate_int_input("Enter Passenger Age: ")
        if age is None:
            return

        num_passengers = validate_int_input("Enter Number of Passengers: ")
        if num_passengers is None or num_passengers > available_seats:
            print(f"Only {available_seats} seats are available.")
            return

        price = float(input("Enter Price: "))
        passenger_id = generate_passenger_id()

        query = '''
        INSERT INTO bookings (Passenger_Id, Passenger_Name, Passenger_Age, No_of_passengers, Date_of_travel, Price)
        VALUES (%s, %s, %s, %s, %s, %s)
        '''
        values = (passenger_id, name, age, num_passengers, date_of_travel, price)
        execute_query(query, values)
        print(f"Booking successful! Your Passenger ID is {passenger_id}")
    else:
        print("No seats available for the selected date.")


# Show all bookings in the system
def show_all_bookings():
    query = "SELECT * FROM bookings"
    execute_query(query)
    results = connection.fetchall()
    for row in results:
        passenger_id, passenger_name, passenger_age, no_of_passengers, date_of_travel, price = row
        date_of_travel = date_of_travel.strftime('%Y-%m-%d')
        print((passenger_id, passenger_name, passenger_age, no_of_passengers, date_of_travel, price))


# Update existing booking details
def update_booking_details():
    passenger_id = validate_int_input("Enter Passenger ID to update: ")
    if passenger_id is None:
        return

    name = input("Enter new Passenger Name: ")
    age = validate_int_input("Enter new Passenger Age: ")
    if age is None:
        return

    num_passengers = validate_int_input("Enter new Number of Passengers: ")
    if num_passengers is None:
        return

    date_of_travel = input("Enter new Date of Travel (YYYY-MM-DD): ")
    date_of_travel = validate_date(date_of_travel)
    if date_of_travel is None:
        return

    price = float(input("Enter new Price: "))

    query = '''
    UPDATE bookings
    SET Passenger_Name = %s, Passenger_Age = %s, No_of_passengers = %s, Date_of_travel = %s, Price = %s
    WHERE Passenger_Id = %s
    '''
    values = (name, age, num_passengers, date_of_travel, price, passenger_id)
    execute_query(query, values)
    print("Booking updated successfully!")


# Cancel a booking by Passenger ID
def cancel_booking():
    passenger_id = validate_int_input("Enter Passenger ID to cancel: ")
    if passenger_id is None:
        return

    query = "DELETE FROM bookings WHERE Passenger_Id = %s"
    execute_query(query, (passenger_id,))
    print("Booking cancelled successfully!")


# Close resources properly
def close_resources():
    try:
        if connection:
            connection.close()
        if database:
            database.close()
    except mysql.connector.Error as err:
        print(f"Error closing connection: {err}")


# Main application loop
while True:
    display_menu()
    choice = validate_int_input("Enter your choice: ")

    if choice == 1:
        date_of_travel = input("Enter Date of Travel (YYYY-MM-DD) to check availability: ")
        date_of_travel = validate_date(date_of_travel)
        if date_of_travel:
            check_seat_availability(date_of_travel)
    elif choice == 2:
        book_seat()
    elif choice == 3:
        show_all_bookings()
    elif choice == 4:
        update_booking_details()
    elif choice == 5:
        cancel_booking()
    elif choice == 6:
        print("Exiting application.")
        close_resources()
        break
    else:
        print("Invalid choice. Please try again.")
