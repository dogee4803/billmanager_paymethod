#!/usr/bin/python3

import payment
import requests
import hashlib
import json
import sys
from jinja2 import Environment, FileSystemLoader

import xml.etree.ElementTree as ET

import billmgr.logger as logging

MODULE = 'payment'
logging.init_logging('mypayment')
logger = logging.get_logger('mypayment')

class TestPaymentCgi(payment.PaymentCgi):
    def Process(self):
        # Данные из self.payment_params, self.paymethod_params, self.user_params
        # Вывод параметров метода оплаты (self.paymethod_params) и платежа (self.payment_params) в лог mypayment.log
        logger.info(f"paymethod_params = {self.paymethod_params}")
        logger.info(f"payment_params = {self.payment_params}")

        # Перевод платежа в статус "Оплачивается"
        payment.set_in_pay(self.elid, '', 'external_' + self.elid)
        
        # Запись нужных данных для инициализации платежа
        headers = {"Content-Type": "application/json"}
        data = dict()
        token_data = dict()
        data["TerminalKey"] = self.paymethod_params["terminalkey"]
        data["Amount"] = float(self.payment_params["paymethodamount"]) * 100
        data["OrderId"] = self.elid + "#" + self.payment_params["randomnumber"]

        # Вычисление Токена
        psw = self.paymethod_params["terminalpsw"]
        token_data["TerminalKey"] = data["TerminalKey"]
        token_data["Amount"] = data["Amount"]
        token_data["OrderId"] = data["OrderId"]

        token_data.update({"Password": psw})
        token_data = dict(sorted(token_data.items()))
        logger.info(f"token_data = {token_data}")
        concatenated_values = ''.join(str(token_data.values()))
        hashed_result = hashlib.sha256(concatenated_values.encode('utf-8')).hexdigest()
        data["Token"] = hashed_result


        # Параметры для неудачной попытки запуска скрипта из документации (см. ниже). Может вернусь позже.
        """
        terminal_key = self.paymethod_params["terminalkey"]
        amount = float(self.payment_params["paymethodamount"]) * 100
        order_id = self.elid + "#" + self.payment_params["randomnumber"]
        token = data["Token"]
        """

        # Инициализация платежа и логирование его данных
        r = requests.post('https://securepay.tinkoff.ru/v2/Init', data = json.dumps(data), headers=headers) 
        logger.info(f"data = {data}")
        logger.info(f"requests = {r.json()}")


        # url для перенаправления c cgi на платёжную страницу, а также в зависимости от результатов оплаты на страницы для успеха и провала
        # Страницы возврата реализуются позднее
        redirect_url = r.json()["PaymentURL"]
        success_url = self.success_page
        fail_url = self.fail_page


        # Почему-то генерируется неправильный токен именно для проверки статуса платежа
        """
        # Вычисление Токена для запроса оплаты
        token_status_data = dict()
        psw_status = self.paymethod_params["terminalpsw"]
        token_status_data["TerminalKey"] = self.paymethod_params["terminalkey"]
        token_status_data["PaymentId"] = r.json()["PaymentId"]
        token_status_data.update({"Password": psw_status})
        token_status_data = dict(sorted(token_data.items()))
        concatenated_values = ''.join(str(token_status_data.values()))
        hashed_result = hashlib.sha256(concatenated_values.encode('utf-8')).hexdigest()
        # Запрос оплаты
        status_data = dict()
        status_data["TerminalKey"] = data["TerminalKey"]
        status_data["PaymentId"] = r.json()["PaymentId"]
        status_data["Token"] = hashed_result
        r_status = requests.post('https://securepay.tinkoff.ru/v2/GetState', data = json.dumps(status_data), headers=headers) 
        logger.info(f"status = {r_status.json()}")
        """

        # Формировние html и отправка в stdout для перехода по redirect_url
        # После в планах добавить получение результатов оплаты, а затем сделать страницы возврата
        payment_form_env = Environment(loader=FileSystemLoader('/usr/local/mgr5/mypaymethod/templates'))
        payment_form_template = payment_form_env.get_template('payment_form.html')
        payment_form = payment_form_template.render(redirect_url=redirect_url)

        sys.stdout.write(payment_form)

TestPaymentCgi().Process()