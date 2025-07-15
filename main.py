import logging
import requests # Keep import for payload structure, even if not used for actual request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import json # Import json for pretty printing the payload in email
import pytz # Import pytz for timezone handling
import sys # Import sys for command-line arguments

# Configure logging for better output in a standard script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_email_notification(subject, body, recipient_email):
    """
    Sends an email notification using Gmail's SMTP server.
    Requires the GMAIL_APP_PASSWORD environment variable to be set.
    """
    sender_email = "yanhongnanbk@gmail.com"
    sender_password = os.environ.get("GMAIL_APP_PASSWORD")
    # sender_password = "relz lzch vlqv tkzp"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    if not sender_password:
        logging.error("Error: GMAIL_APP_PASSWORD environment variable not set. Cannot send email.")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        logging.info(f"Email notification sent successfully to {recipient_email}")
    except Exception as e:
        logging.error(f"Failed to send email notification: {e}")

def simulate_employee_status_update(status_code: str):
    """
    This function simulates updating employee status by constructing the
    payload and intended headers, and then sending them via email for validation.
    It does NOT make an actual HTTP POST request to the API.

    Args:
        status_code (str): The code representing the desired employee status
                           (e.g., "01", "02", "03", "10").
    """
    logging.info(f'Starting the employee status simulation process for status code: {status_code}.')

    # --- Configuration ---
    api_url = "https://agentportal.monetwfo-eu.com/APApi/api/DataCollector/InsertRawAgentState" # Still define for context
    recipient_email = "nikolasyubikey@mngenvmcap461413.onmicrosoft.com"
    
    # Retrieve the bearer token from environment variables.
    # It will default to an empty string if not set, allowing the simulation to proceed.
    # For actual API calls, this would be a required environment variable.
    bearer_token = os.environ.get("AGENT_API_BEARER_TOKEN", "BEARER_TOKEN_NOT_SET_FOR_SIMULATION")

    # Define status mappings
    status_map = {
        "01": "01. Available/Case Work",
        "02": "02. Break",
        "03": "03. Lunch",
        "10": "10. End of shift"
    }

    # Get the corresponding status string
    status_string = status_map.get(status_code)
    if not status_string:
        error_message = f"Invalid status code provided: {status_code}. Valid codes are {list(status_map.keys())}"
        logging.error(error_message)
        send_email_notification(
            "Employee Status Simulation Failed: Invalid Status Code",
            error_message,
            recipient_email
        )
        return

    # Generate dynamic timestamp (YYYY-mm-dd HH:MM:SS) in UTC+7
    # Define the UTC+7 timezone. Using 'Asia/Bangkok' as a common representative for UTC+7.
    # Other options could be 'Asia/Ho_Chi_Minh' or 'Asia/Jakarta'.
    utc_plus_7_tz = pytz.timezone('Asia/Bangkok')

    # Get current UTC time (timezone-aware)
    now_utc = datetime.now(pytz.utc)
    
    # Convert UTC time to UTC+7 timezone
    now_utc_plus_7 = now_utc.astimezone(utc_plus_7_tz)

    # Format the datetime string for the payload (YYYY-mm-dd HH:MM:SS)
    current_datetime_str = now_utc_plus_7.strftime("%Y-%m-%d %H:%M:%S")

    # Format the date string for the email subject (YYYY-mm-dd)
    current_date_for_subject = now_utc_plus_7.strftime("%Y-%m-%d")

    # Construct the payload
    payload = {
        "ClientID": "118",
        "AgentID": "TV2034",
        "Status": status_string,
        "DateStamp": current_datetime_str,
        "UpdatedOn": current_datetime_str,
        "RawAgentStateUpdated": True
    }

    # Define headers with the Bearer token (will show placeholder if not set)
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    # Updated email subject to include the current date in UTC+7
    email_subject = f"Nikolas Monet Cron Job {current_date_for_subject}"
    email_body = (
        f"This is a simulation of the API call to {api_url} for status '{status_string}'.\n\n"
        f"--- Intended Request Details ---\n\n"
        f"API Endpoint: {api_url}\n"
        f"Method: POST\n\n"
        f"Headers:\n{json.dumps(headers, indent=2)}\n\n" # Pretty print headers
        f"Payload:\n{json.dumps(payload, indent=2)}\n\n" # Pretty print payload
        f"--- End of Request Details ---"
    )

    # Send the email notification with the payload and token details
    send_email_notification(email_subject, email_body, recipient_email)

    logging.info("API call simulation and email notification process completed.")

if __name__ == "__main__":
    # This block allows you to run the script directly.
    # When triggered by GitHub Actions, you will pass the status_code as an argument.
    
    # Example: If you run 'python your_script.py 01'
    if len(sys.argv) > 1:
        status_to_simulate = sys.argv[1]
        simulate_employee_status_update(status_to_simulate)
    else:
        # Default behavior if no argument is provided (e.g., for local testing without arguments)
        logging.warning("No status code provided as a command-line argument. Running with default status '10'.")
        simulate_employee_status_update("10")