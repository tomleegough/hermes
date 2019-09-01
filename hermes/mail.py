from flask import Blueprint, request

bp = Blueprint('mail', __name__)

"""
This call sends a message to one recipient.
"""
from mailjet_rest import Client

# TODO: Generalise mailjet credentials to allow open source
def send_verification_email(recipient, user_activate_url):
    api_key = '82008b39bbf82b502c360991ab7285ae'
    api_secret = 'c256ddbd33c9cdca18df3c2cf963d7b5'
    mailjet = Client(
        auth=(
            api_key,
            api_secret
        ),
        version='v3.1'
    )

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
                "TextPart": "Please verify your Hermes Accounting Login to use the app.",
                "HTMLPart":
                    """
                        <h1>Welcome to Hermes Accounting!</h1>
                        <p>Welcome to Hermes Accounting! Before you can log in with your newly created account. You will need to verify your email address.
                    </p>
                        <p>To activate your account, follow this link <a href="{}auth/activate">{}auth/activate</a> and enter your email and activation code, included in this email</p>
                        <p><b>Activation Code:</b> {} </p>
                        <p>Thank you for creating your account</p>
                    """.format(
                            request.url_root,
                            request.url_root,
                            user_activate_url
                    )
            }
        ]
    }

    mailjet.send.create(data=data)
    # print(result.status_code )
    # print(result.json() )

def send_password_reset(recipient, user_reset_url):
    api_key = '82008b39bbf82b502c360991ab7285ae'
    api_secret = 'c256ddbd33c9cdca18df3c2cf963d7b5'
    mailjet = Client(
        auth=(
            api_key,
            api_secret
        ),
        version='v3.1'
    )

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

                "Subject": "Reset your Hermes Account Password",
                "HTMLPart":
                    """
                        <h1>Reset your Hermes Accounting Password</h1>
                        <p>To reset your password, follow this link <a href="{}auth/reset">{}auth/reset</a> use the temporary password in this email.</p>
                        <p><b>Temporary Password:</b> {} </p>
                    """.format(
                            request.url_root,
                            request.url_root,
                            user_reset_url
                    )
            }
        ]
    }

    mailjet.send.create(data=data)
