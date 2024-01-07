from datetime import datetime

# Given date string
given_date_string = 'December 16, 2023'

# Convert the given date string to a datetime object
given_date = datetime.strptime(given_date_string, '%B %d, %Y')

# Get today's date
today_date = datetime.today()

# Compare the dates
if given_date < today_date:
    print(f"The date {given_date_string} is before today's date.")
else:
    print(f"The date {given_date_string} is on or after today's date.")
