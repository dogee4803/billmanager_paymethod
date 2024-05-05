#!/usr/bin/python3

import payment
import billmgr.db
import billmgr.exception

import billmgr.logger as logging

import xml.etree.ElementTree as ET

MODULE = 'payment'
logging.init_logging('pmmypayment')
logger = logging.get_logger('pmmypayment')

class MyPaymentModule(payment.PaymentModule):
    def __init__(self):
        super().__init__()

        self.features[payment.FEATURE_CHECKPAY] = True
        self.features[payment.FEATURE_REDIRECT] = True
        self.features[payment.FEATURE_NOT_PROFILE] = True
        self.features[payment.FEATURE_PMVALIDATE] = True

        self.params[payment.PAYMENT_PARAM_PAYMENT_SCRIPT] = "/mancgi/mypayment"

    
    def PM_Validate(self, xml : ET.ElementTree):
        logger.info("run pmvalidate")

        # мы всегда можем вывести xml в лог, чтобы изучить, что приходит :)
        logger.info(f"xml input: {ET.tostring(xml.getroot(), encoding='unicode')}")

        terminalkey_node = xml.find('./terminalkey')
        terminalpsw_node = xml.find('./terminalpsw')
        minamount_node = xml.find('.//paymethod/minamount')
        terminalkey = terminalkey_node.text if terminalkey_node is not None else ''
        terminalpsw = terminalpsw_node.text if terminalpsw_node is not None else ''
        minamount = float(minamount_node.text) if minamount_node is not None else 0

        # Заменям условие проверки для тестового подключения к Tinkoff, а также добавляем ограничение по минимальному платежу в размере 100 рублей
        if terminalkey != 'TinkoffBankTest' or terminalpsw != 'TinkoffBankTest':
            raise billmgr.exception.XmlException('wrong_terminal_info')
        if minamount < 100:
            raise billmgr.exception.XmlException('too_small_min_amount')

        # Здесь условия уже для реального подключения, а не проверки
        '''
        if len(terminalkey) != 20 or len(terminalpsw) != 20:
            raise billmgr.exception.XmlException('wrong_terminal_info')
        '''
    

    # в тестовом примере получаем необходимые платежи
    # и переводим их все в статус 'оплачен'
    def CheckPay(self):
        logger.info("run checkpay")

        # получаем список платежей в статусе оплачивается
        # и которые используют обработчик pmmypayment
        payments = billmgr.db.db_query(f'''
            SELECT p.id FROM payment p
            JOIN paymethod pm
            WHERE module = 'pmmypayment' AND p.status = {payment.PaymentStatus.INPAY.value}
        ''')

        for p in payments:
            logger.info(f"change status for payment {p['id']}")
            payment.set_paid(p['id'], '', f"external_{p['id']}")


MyPaymentModule().Process()
