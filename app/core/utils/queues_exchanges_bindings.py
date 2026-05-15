from app.core.schemas.rabbitmq_schemas import RabbitMQExchange, RabbitMQQueue, RabbitMQQueueBinding


class NotificationRoutingKeys:
    """Constants for notification routing keys."""

    SMS = "notification.sms"
    EMAIL = "notification.email"
    PUSH = "notification.push"


#######################################################################################
#                                                                                     #
#                                      QUEUES                                         #
#                                                                                     #
#######################################################################################
sms_notifications_queue = RabbitMQQueue(name="sms_notifications_queue", queue_type="quorum")

email_notifications_queue = RabbitMQQueue(name="email_notifications_queue", queue_type="quorum")

push_notifications_queue = RabbitMQQueue(name="push_notifications_queue", queue_type="quorum")


#######################################################################################
#                                                                                     #
#                                   EXCHANGES                                         #
#                                                                                     #
#######################################################################################
notifications_exchange = RabbitMQExchange(name="notification_exchange", type="topic")


#######################################################################################
#                                                                                     #
#                                    BINDINGS                                         #
#                                                                                     #
#######################################################################################
sms_notifications_queue_binding = RabbitMQQueueBinding(
    queue_name=sms_notifications_queue.name,
    exchange_name=notifications_exchange.name,
    routing_key=NotificationRoutingKeys.SMS,
)

email_notifications_queue_binding = RabbitMQQueueBinding(
    queue_name=email_notifications_queue.name,
    exchange_name=notifications_exchange.name,
    routing_key=NotificationRoutingKeys.EMAIL,
)

push_notifications_queue_binding = RabbitMQQueueBinding(
    queue_name=push_notifications_queue.name,
    exchange_name=notifications_exchange.name,
    routing_key=NotificationRoutingKeys.PUSH,
)


queues = [sms_notifications_queue, email_notifications_queue, push_notifications_queue]

exchanges = [notifications_exchange]

queue_bindings = [sms_notifications_queue_binding, email_notifications_queue_binding, push_notifications_queue_binding]
