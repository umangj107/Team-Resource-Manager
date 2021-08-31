from twilio.rest import Client
import smtplib

# TWILIO_SID = "ACa84276eedd70ed33d9a28dabf709ce8a"
# TWILIO_AUTH_TOKEN = "bef4b5b7adbd698ea0f4c06cf98fed36"
# TWILIO_VIRTUAL_NUMBER = "+16144124154"
# TWILIO_VERIFIED_NUMBER = "+917290914040"

class NotificationManager:
    def __init__(self):
        self.client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    def send_sms(self, message):
        message = self.client.messages.create(
            body = message,
            from_= TWILIO_VIRTUAL_NUMBER,
            to = TWILIO_VERIFIED_NUMBER,
        )
        print(message.sid)

    def send_emails(self, message):
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login("umajain107@gmail.com", "Uj!15111997")
            connection.sendmail(
                from_addr="umajain107@gmail.com",
                to_addrs="umangj107@gmail.com",
                msg=f"Subject:New Low Price Alert!\n\n{message}".encode('utf-8')
            )