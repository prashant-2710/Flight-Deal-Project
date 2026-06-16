import os
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

class NotificationManager:

    def __init__(self):
        #Twilio setup
        self.client = Client(os.environ['TWILIO_SID'], os.environ['TWILIO_AUTH_TOKEN'])
        self.from_number = os.environ['TWILIO_VIRTUAL_NUMBER']
        self.to_number = os.environ['TWILIO_VERIFIED_NUMBER']

        #Email setup
        self.smtp_server = os.environ["EMAIL_PROVIDER_SMTP"]
        self.smtp_port = int(os.environ["EMAIL_PORT"])
        self.my_email = os.environ["MY_EMAIL"]
        self.my_password = os.environ["MY_APP_PASSWORD"]


    def send_sms(self, flight_data):
        """Formats flight data into a clean text alert and sends it via Twilio SMS."""
        message_body = (
            f"✈️ Low Price Alert! ✈️\n\n"
            f"Only GBP {flight_data.price} to fly from "
            f"{flight_data.origin_airport} to {flight_data.destination_airport}!\n"
            f"📅 Outbound: {flight_data.out_date}\n"
            f"📅 Inbound: {flight_data.return_date}"
        )

        message = self.client.messages.create(
            body=message_body,
            from_=self.from_number,
            to=self.to_number
        )
        
        print(f"Notification sent! Message SID: {message.sid}")
        
    def send_emails(self, email_list, email_body):
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as connection:
                connection.starttls()
                connection.login(self.my_email, self.my_password)

                for customer_email in email_list:
                    # Construct structural MIME message wrapper to safely parse UTF-8 characters like £
                    msg = MIMEText(email_body, "plain", "utf-8")
                    msg["Subject"] = "🔥 New Flight Deal Alert! 🔥"
                    msg["From"] = self.my_email
                    msg["To"] = customer_email
                    
                    connection.sendmail(
                        from_addr=self.my_email,
                        to_addrs=customer_email,
                        msg=msg.as_string()
                    )

            print(f"Success! Bulk promotion dispatched to {len(email_list)} users.")
        except Exception as error:
            print(f"🚨 Email pipeline processing error: {error}")
