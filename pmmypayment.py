#!/usr/bin/python3

import payment
import billmgr.db
import billmgr.exception

import billmgr.logger as logging

import xml.etree.ElementTree as ET

import hashlib
import requests
import json

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
    

    def CheckPay(self):
        logger.info("run checkpay")
        logger.info()

        # получаем список платежей в статусе оплачивается
        # и которые используют обработчик pmmypayment
        payments = billmgr.db.db_query(f'''
            SELECT p.id, pm.xmlparams, p.externalid FROM payment p
            JOIN paymethod pm
            WHERE module = 'pmmypayment' AND p.status = {payment.PaymentStatus.INPAY.value}
        ''')
        for p in payments:
            logger.info(f"status = {p['id']}")

            p_xml = ET.fromstring(p['xmlparams'])

            # Вычисление Токена для запроса оплаты
            status_data = dict()
            status_data["TerminalKey"] = p_xml.find("terminalkey").text
            status_data["PaymentId"] = p["externalid"]
            # Здесь идёт генерация токена и его запись
            status_data_temp = dict()
            for key, value in status_data.items():
                    if type(value) in [int, float, str, bool]:
                        status_data_temp[key] = value
            status_data_temp.update({"Password": p_xml.find("terminalpsw").text})
            status_data_temp = dict(sorted(status_data_temp.items()))
            concatenated_values = ''.join(list(status_data_temp.values()))
            token = hashlib.sha256(concatenated_values.encode('utf-8')).hexdigest()
            del status_data_temp
            status_data["Token"] = token

            headers = {"Content-Type": "application/json"}

            # Запрос статуса оплаты и его логирование
            status_r = requests.post('https://securepay.tinkoff.ru/v2/GetState', data = json.dumps(status_data), headers=headers) 
            logger.info(f"Payment Success = {status_r.json()}")
            logger.info(f"Payment Status = {status_r.json()}")
            if status_r.json()["Success"] == True:
                # Прочие статусы можно глянуть тут https://www.tinkoff.ru/kassa/dev/payments/#tag/Scenarii-oplaty-po-karte/Statusnaya-model-platezha
                if status_r.json()["Status"] == "CONFIRMED":
                    payment.set_paid(p['id'], '', f"external_{p['id']}")
                elif status_r.json()["Status"] == "CANCELED":
                    payment.set_canceled(p['id'], '', f"external_{p['id']}")
                elif status_r.json()["Status"] == "REJECTED":
                    payment.set_canceled(p['id'], '', f"external_{p['id']}")
                elif status_r.json()["Status"] == "AUTH_FAIL":
                    payment.set_canceled(p['id'], '', f"external_{p['id']}")
                elif status_r.json()["Status"] == "DEADLINE_EXPIRED":
                    payment.set_canceled(p['id'], '', f"external_{p['id']}")
                    
                    

MyPaymentModule().Process()