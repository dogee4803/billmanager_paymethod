#!/usr/bin/python3

import payment
import billmgr.db
import billmgr.exception

import billmgr.logger as logging

import xml.etree.ElementTree as ET

from tinkoffApiHandler import TinkoffApiHandler

MODULE = 'payment'
logging.init_logging('pmmypayment')
logger = logging.get_logger('pmmypayment')

class MyPaymentModule(payment.PaymentModule, TinkoffApiHandler):
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
        terminalkeys = self.getTerminalList(<Ваш Bearer Token>)
        if terminalkey not in terminalkeys or len(terminalpsw) > 20:
            raise billmgr.exception.XmlException('wrong_terminal_info')
        '''
    

    def CheckPay(self):
        logger.info("run checkpay")

        # получаем список платежей в статусе оплачивается
        # и которые используют обработчик pmmypayment
        payments = billmgr.db.db_query(f'''
            SELECT p.id, pm.xmlparams, p.externalid FROM payment p
            JOIN paymethod pm
            WHERE module = 'pmmypayment' AND p.status = {payment.PaymentStatus.INPAY.value}
        ''')
        logger.info(f"payments {payments}")
        for p in payments:
            try:
                try:
                    status_r = self.checkStatusPayment(p)
                    logger.info(f"Статус оплаты: {status_r}")
                except:
                    logger.info(f"Ошибка с добавлением модуля TinkoffApiHandler")
                if status_r.json()["Success"] == True:
                    # Прочие статусы https://www.tinkoff.ru/kassa/dev/payments/#tag/Scenarii-oplaty-po-karte/Statusnaya-model-platezha
                    successful_statuses = ["CONFIRMED"]
                    failed_statuses = ["CANCELED", "REJECTED", "AUTH_FAIL", "DEADLINE_EXPIRED"]
                    if status_r.json()["Status"] in successful_statuses:
                        payment.set_paid(p['id'], '', f"external_{p['id']}")
                    elif status_r.json()["Status"] in failed_statuses:
                        logger.info(f"Payment {p['id']} отменён т.к статус - {status_r.json()['Status']}")
                        payment.set_canceled(p['id'], '', f"external_{p['id']}")
                    else:
                        logger.info(f"Неизвестный статус платежа {p['id']}. Статус - {status_r.json()['Status']}")

            except:
                logger.info(f"Incorrect payment{p['id']}")
                    

MyPaymentModule().Process()