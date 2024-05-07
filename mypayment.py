#!/usr/bin/python3

import payment
import sys
from jinja2 import Environment, FileSystemLoader

import billmgr.logger as logging

from tinkoffApiHandler import TinkoffApiHandler


MODULE = 'payment'
logging.init_logging('mypayment')
logger = logging.get_logger('mypayment')
class TestPaymentCgi(payment.PaymentCgi, TinkoffApiHandler):
    def Process(self):
        logger.info(f"paymethod_params = {self.paymethod_params}")
        logger.info(f"payment_params = {self.payment_params}")

        # Инициализация платежа и логирование его данных
        try:
            init_r = self.initTinkoffPayment()
        except:
            logger.info(f"Ошибка с добавлением модуля TinkoffApiHandler")
            
        logger.info(f"requests = {init_r.json()}")

        redirect_url = init_r.json()["PaymentURL"]

        # Перевод платежа в статус "Оплачивается"
        payment.set_in_pay(self.elid, '', init_r.json()["PaymentId"])
        
        
        # Шаблон Jinja2
        payment_form_env = Environment(loader=FileSystemLoader('billmanager_paymethod/templates'))
        payment_form_template = payment_form_env.get_template('payment_form.html')
        payment_form = payment_form_template.render(redirect_url=redirect_url)

        # Вывод формы
        sys.stdout.write(payment_form)
        
TestPaymentCgi().Process()