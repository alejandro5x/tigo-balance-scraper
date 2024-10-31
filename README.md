# Tigo Panama Balance Scraper

This script uses Python, Playwright, and MQTT to log into the Tigo Panama website, retrieve the account balance, and send the balance (or an error message) to an MQTT broker. It's designed for automated monitoring and integration with MQTT-based IoT or automation platforms.

## Prerequisites

- Python 3.7+
- A Tigo Panama account (with credentials)
- MQTT broker details (username, password, server, port)
- Environment variables configured using a `.env` file

## Installation

1. Clone the repository and navigate to the project directory:

    ```bash
    git clone https://github.com/alejandro5x/tigo-balance-scraper.git
    cd tigo-balance-scraper
    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up a `.env` file in the project directory with the following environment variables:

    ```plaintext
    TIGO_NUMBER=<your_tigo_email>
    TIGO_PASSWORD=<your_tigo_password>
    MQTT_USER=<mqtt_username>
    MQTT_PASSWORD=<mqtt_password>
    MQTT_BROKER=<mqtt_broker_url>
    MQTT_PORT=<mqtt_port_number>
    TIGO_MQTT_TOPIC=<mqtt_topic_for_balance>
    TIGO_MQTT_ERROR_TOPIC=<mqtt_topic_for_errors>
    ```

## Usage

To run the script, simply execute:

```bash
python tigo_balance.py
```

The script performs the following tasks:

1. Logs in to the Tigo Panama website.
2. Retrieves the current balance.
3. Publishes the balance to the specified MQTT topic.
4. If an error occurs, sends an error message to a separate MQTT topic.

## Functions

- **`run()`**: Main function to control Playwright browser actions and log in to Tigo's portal.
- **`send_mqtt_data()`**: Sends the balance information to the MQTT broker.
- **`send_mqtt_error()`**: Sends any encountered error messages to a designated MQTT topic.

## Error Handling

The script handles login and timeout errors by publishing a relevant error message to the `TIGO_MQTT_ERROR_TOPIC`.

## Example MQTT Message Payloads

**Balance Message**:
```json
{
    "state": "10.00",
    "updated_ts": "1690483200",
    "updated_dt": "2024-08-26T12:00:00"
}
```

**Error Message**:
```json
{
    "error": "Error getting balance: TimeoutError",
    "updated_ts": "1690483200",
    "updated_dt": "2024-08-26T12:00:00"
}
```

