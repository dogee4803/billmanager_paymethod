#!/usr/bin/python3

import payment
import requests
import hashlib
import json
import sys
from jinja2 import Environment, FileSystemLoader

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

        # Функция генерации токена
        def gen_token(data, secretkey):
            # Генерирует токен с использованием алгоритма хеширования SHA-256
            secret_data = dict()
            for key, value in data.items():
                if type(value) in [int, float, str, bool]:
                    secret_data[key] = value
            secret_data.update({"Password": secretkey})
            secret_data = dict(sorted(secret_data.items()))
            concatenated_values = ''.join(list(secret_data.values()))
            token = hashlib.sha256(concatenated_values.encode('utf-8')).hexdigest()
            return token
        
        # Перевод платежа в статус "Оплачивается"
        payment.set_in_pay(self.elid, '', 'external_' + self.elid)
        
        # Запись нужных данных для инициализации платежа
        headers = {"Content-Type": "application/json"}
        init_data = dict()
        init_data["TerminalKey"] = self.paymethod_params["terminalkey"]
        init_data["Amount"] = str(float(self.payment_params["paymethodamount"]) * 100)
        init_data["OrderId"] = self.elid + "#" + self.payment_params["randomnumber"]
        # Здесь идёт генерация токена и его запись
        init_data_temp = dict()
        for key, value in init_data.items():
                if type(value) in [int, float, str, bool]:
                    init_data_temp[key] = value
        init_data_temp.update({"Password": self.paymethod_params["terminalpsw"]})
        init_data_temp = dict(sorted(init_data_temp.items()))
        concatenated_values = ''.join(list(init_data_temp.values()))
        token = hashlib.sha256(concatenated_values.encode('utf-8')).hexdigest()
        del init_data_temp
        init_data["Token"] = token
        # Затем запись страниц возврата
        init_data["SuccessURL"] = self.success_page
        init_data["FailURL"] = self.fail_page


        # Инициализация платежа и логирование его данных
        init_r = requests.post('https://securepay.tinkoff.ru/v2/Init', data = json.dumps(init_data), headers=headers) 
        logger.info(f"data = {init_data}")
        logger.info(f"requests = {init_r.json()}")


        # url для перенаправления c cgi на платёжную страницу, а также в зависимости от результатов оплаты на страницы для успеха и провала
        redirect_url = init_r.json()["PaymentURL"]
        
        # Формирование html и отправка в stdout для перехода по redirect_url
        
        # Создание окружения для Jinja2
        payment_form_env = Environment(loader=FileSystemLoader('/usr/local/mgr5/mypaymethod/templates'))
        # Загрузка шаблона из файла
        payment_form_template = payment_form_env.get_template('payment_form.html')
        # Создание объекта шаблона
        payment_form = payment_form_template.render(redirect_url=redirect_url)

        # Вывод формы
        sys.stdout.write(payment_form)
        
TestPaymentCgi().Process()