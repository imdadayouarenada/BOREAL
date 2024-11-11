import datetime as dt
import argparse as ap
import yaml
import traceback
from typing import Iterator, List
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Emailer:
    """
    class for sending download report emails
    """
    # template of email message content
    _message_template = (
        """
        Hi there,

        The BOREAL Control code ran at {runtime}.
        
        The following errors appeared:
        {error_message}
        
        """
    )

    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        """
        set connection details for emailer
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        
        self.errors = []
        self.server = None
        
    def add_error(self, error: Exception) -> None:
        """
        add an error to the report
        """
        num_error = len(self.errors)+1
        self.errors.append(f"{num_error} - {error}\n")

    def connect(self) -> None:
        """
        setup connection to SMTP server
        """
        ctx = ssl.create_default_context()
        self.server = smtplib.SMTP_SSL(self.host, self.port, context=ctx)
        self.server.login(self.username, self.password)
        return self.server

    def close(self) -> None:
        """
        close connection to server
        """
        self.server.close()

    def __enter__(self) -> None:
        """
        enable use of `with Emailer...`
        """    
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def send(self, to: List[str], cc: List[str]) -> None:
        """
        send the email report
        """
        if not self.errors:
            error_text = "No errors were reported."
        else:
            error_text = "During the download, the following error(s) were reported:\n"
            error_text += "\n".join([str(e) for e in self.errors])
        text = self._message_template.format(
            runtime=dt.datetime.now(),
            error_message=error_text
        )
  
        message = MIMEMultipart('mixed')
        message.attach(MIMEText(text, "plain"))
        message["Subject"] = "Testing Emailer"
        # message["From"] = self.username
        message["From"] = "Irrigation Classification"
        message["To"] = "; ".join(to)
        message["Cc"] = "; ".join(cc)

        self.server.sendmail(self.username, to, message.as_string())
        return message.as_string()
    
def create_parser(desc: str = None) -> ap.ArgumentParser:
    """
    create CLI argument parser
    """
    p = ap.ArgumentParser(description=desc)
    p.add_argument("config", metavar="CONFIG_PATH", type=str, help="configuration file")

    return p

if __name__ == "__main__":
    # read config file
    p = create_parser()
    args = p.parse_args()
    with open(args.config) as f:
        config = yaml.load(f, Loader=yaml.Loader)
    
    #EMAIL setup
    email_config = config["email"]
    host, port   = email_config["server"]
    emailer = Emailer(host, port, email_config["account"], email_config["password"])

    try:
        print(a)
    except Exception as error:
        inf = traceback.format_exc()
        emailer.add_error(str(error) + "\n" + str(inf))

    try:
        x = 1 / 0  # Example of an error
    except Exception as error:
        inf = traceback.format_exc()
        emailer.add_error(str(error) + "\n" + str(inf))

    with emailer as em:
        msg = em.send(email_config["to"], email_config["cc"])
        print(msg)



#### Add to your code: from Emailer import Emailer, create_parser 
#### every time add 
#  try: 
#     what you want to try 
# except Excpetion as error: 
#     inf = traceback.format_exc()
#     emailer.add_error(str(error) + "\n" + str(inf))

# + 


# with emailer as em: 
#     msg = em.send(email_config["to"], email_config["cc"])
#     print(msg)