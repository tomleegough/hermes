from flask import Blueprint

bp = Blueprint('mail', __name__)

"""
This call sends a message to one recipient.
"""
from mailjet_rest import Client


def send_verification_email(recipient, user_activate_url):
    api_key = '82008b39bbf82b502c360991ab7285ae'
    api_secret = 'c256ddbd33c9cdca18df3c2cf963d7b5'
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')

    data = {
        'Messages': [
            {
                "From": {
                    "Email": "tom@tlg-accounting.co.uk",
                    "Name": "Hermes Mailbot"
                },

                "To": [
                    {
                        "Email": recipient
                    }
                ],

                "Subject": "Verify your Hermes Account",
                "TextPart": "Please verify your Herming Accounting Login to use the app.",
                "HTMLPart": "<a href='https://hermes.tlg-accounting.co.uk/auth/" + user_activate_url +"'>link</a>"
            }
        ]
    }

    result = mailjet.send.create(data=data)
    # print(result.status_code )
    # print(result.json() )
