# pyGarminAPI
pyGarminAPI is a Python library that provides a convenient way to interact with the Garmin API using the Garmin Pull API. With this library, you can easily send signed requests, authenticate with your Garmin API credentials, and fetch activity and health data using Garmin Pull API for your Garmin devices.

The Garmin Pull API allows you to retrieve a wide range of data, including activities such as running, cycling, and swimming, as well as health data like heart rate and step count. By utilizing pyGarminAPI, you can effortlessly integrate Garmin data into your Python applications or scripts.

## Table of Contents

- [Documentation](#documentation)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## Documentation

For detailed instructions on how to use the functions and modules provided by pyGarminAPI, please refer to the [pyGarminAPI Documentation](https://usc-infolab.github.io/pyGarminAPI/).

## Prerequisites

Before using pyGarminAPI, ensure you have the following prerequisites:

- Python 3.8 or higher installed on your system.
- Access to the Garmin API with valid API credentials.
- Database setup with the required tables:
  - A `GARMIN_USER` table with at least `user_id` and `email` columns for each user.
  - An `GARMIN_AUTHORIZATION` table with at least `user_id`, `access_token`, and `token_secret` fields.

If you don't have access to the Garmin API, you can follow these steps to request access and create a Garmin Developer Account:

1. Visit the [Garmin Developer Program](https://developer.garmin.com/gc-developer-program/overview/) page.
2. Click on "Request Now" to access the registration form.
3. Fill in the required information in the registration form and submit your request.
4. Wait for approval from the Garmin Developer Program team. Once approved, you will receive an email with further instructions.
5. Follow the instructions in the email to complete your Garmin Developer Account setup.
6. Once your developer account is set up, log in to the [Garmin Developer Portal](https://developerportal.garmin.com/) and navigate to the "Apps" section.
7. Click on "Create New App" and provide the necessary details for your application.
8. Make sure to specify the appropriate callback URL(s) if needed.
9. After creating your app, you will receive your API credentials, including the Consumer Key and Consumer Secret. Keep these credentials secure, as they are essential for accessing the Garmin API.

Ensure that you have your API credentials ready before using pyGarminAPI.


## Installation
To get started with pyGarminAPI, follow these steps:

1. Clone the pyGarminAPI repository to your local machine:

   ```shell
   git clone https://github.com/NIH-W4H/pyGarminAPI.git
   ```

2. Change into the pyGarminAPI directory:
    ```shell
    cd pyGarminAPI
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Copy the config.yml.example file as config.yml:
    ```shell
    cp config.yml.example config.yml
    ```

5. Edit the config.yml file with your database connection information and table names for the **user** and **authorization** tables.

6. You're now ready to use pyGarminAPI!

## Usage
To use pyGarminAPI in your Python scripts, you can import the necessary functions from the `garmin_api` module. Here's an example:
```python
import pyGarminAPI.garmin_api as garmin_api

# Generate the signature
signatures = garmin_api.generate_signature()
signature = signatures['signature'][0]

# Get the daily summary health data
start_date = datetime(2023, 4, 15)
end_date = start_date + timedelta(days=5)
current_date = start_date

while current_date <= end_date:
    # Generate string for current date
    start_date_str = current_date.strftime('%Y-%m-%d %H:%M:%S')
    end_day_str = (current_date + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    print(start_date_str, end_day_str)
    print(garmin_api.get_daily_summary_health(signature, start_date_str, end_day_str))
    # Increment current date by one day
    current_date += timedelta(days=1)
```
Please note that this is just a basic example. Make sure to adapt it to your specific use case and provide additional instructions, such as error handling and further details on the available functions.

## Features
pyGarminAPI provides the following conveniences:
- Seamless authentication process with your Garmin API credentials.
- Fetch detailed information about activities, including activity type, distance, and duration.
- Retrieve health data such as heart rate and step count.
- Simplified handling of signed requests to the Garmin API.

By leveraging the power of pyGarminAPI, you can create applications that analyze, visualize, or process your Garmin activity and health data in Python. Whether you're building a fitness tracking app, conducting data analysis, or exploring personal health trends, pyGarminAPI provides a robust foundation for working with the Garmin API.

## Contributing
Contributions to pyGarminAPI are welcome! If you find any bugs or have suggestions for new features, please open an issue on the GitHub repository. If you'd like to contribute code, feel free to open a pull request.

## License
This project is licensed under the [MIT License](https://github.com/NIH-W4H/pyGarminAPI/blob/main/LICENSE). Feel free to use and modify this code for your own purposes.
