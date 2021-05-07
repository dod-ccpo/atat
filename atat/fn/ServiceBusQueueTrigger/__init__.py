import logging
import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import azure.functions as func
from shared import portfolios_api #(absolute)


def main(msg: func.ServiceBusMessage):
    logging.info('Python ServiceBus queue trigger processed message: %s',
                 msg.get_body().decode('utf-8'))
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=os.environ.get('SERVICE_BUS_CONNECTION_STR'), logging_enable=True)
    with servicebus_client:
        sender = servicebus_client.get_topic_sender(topic_name=os.environ.get("PORTFOLIOS_TOPIC"))
        with sender:
            message = ServiceBusMessage(portfolios_api.get_portfolios(), content_type="application/json")
            sender.send_messages(message)