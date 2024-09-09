from datetime import datetime


def generate_order_number(pk):
    current_datetime = datetime.now().strftime('%Y%m%d%H%S')
    order_number = current_datetime + str(pk)
    
    return order_number


def generate_transaction_id(order_number):
    current_datetime = datetime.now().strftime('%Y%m')
    transaction_id = current_datetime + str(order_number)
    return transaction_id