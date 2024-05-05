#!/usr/bin/python3

import payment
import sys
import requests
import hashlib
import json

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
        payment_form =  "<html>\n";
        payment_form += "<head><meta http-equiv='Content-Type' content='text/html; charset=UTF-8'>\n"
        payment_form += "<link rel='shortcut icon' href='billmgr.ico' type='image/x-icon' />"
        payment_form += "  <script language='JavaScript'>\n"
        payment_form += "    function DoSubmit() {\n"
        payment_form += "      window.location.assign('" + redirect_url + "');\n"
        payment_form += "    }\n"
        payment_form += "  </script>\n"
        payment_form += "</head>\n"
        # Проверка результатов оплаты. Пока не сделал реализацию запроса после заполнения формы. Как идёт запрос на след. строке
        #r_status = requests.post('https://securepay.tinkoff.ru/v2/GetState', data = json.dumps(status_data), headers=headers) 
        payment_form += "<body onload='DoSubmit()'>\n"
        payment_form += "  <script>\n"
        #payment_form += "    function handlePaymentResult(success) {\n"
        #payment_form += "      if (success) {\n"
        #payment_form += "        window.location.assign('" + success_url + "');\n"
        #payment_form += "      } else {\n"
        #payment_form += "        window.location.assign('" + fail_url + "');\n"
        #payment_form += "      }\n"
        #payment_form += "    }\n"
        #payment_form += "    var urlParams = new URLSearchParams(window.location.search);\n"
        #payment_form += "    var paymentSuccess = urlParams.get('paymentSuccess') === 'true';\n"
        #payment_form += "    handlePaymentResult(paymentSuccess);\n"
        payment_form += "  </script>\n"
        payment_form += "</body>\n"
        payment_form += "</html>\n";

        sys.stdout.write(payment_form)

        # Попытка сделать через скрипт из документации. Может вернусь позже.
        
        """
        payment_form = "<html>\n"
        payment_form += "<head><meta http-equiv='Content-Type' content='text/html; charset=UTF-8' />\n"
        payment_form += "<link rel='shortcut icon' href='billmgr.ico' type='image/x-icon' />\n"
        payment_form += "   <script language='JavaScript'>\n"
        payment_form += "       function submit() {\n"
        payment_form += "           document.frm.submit();\n"
        payment_form += "       }\n"
        payment_form += "   </script>\n"
        payment_form += "</head>\n"
        payment_form += "<body onload='submit()'>\n"
        payment_form += "   <form name='frm' action='https://securepay.tinkoff.ru/v2/Init' method='post'>\n"
        payment_form += "       <input type='hidden' name='TerminalKey' value='" + terminal_key + "'>\n"
        payment_form += "       <input type='hidden' name='Amount' value='" + amount + "'>\n"
        payment_form += "       <input type='hidden' name='OrderId' value='" + order_id + "'>\n"
        payment_form += "       <input type='hidden' name='Token' value='" + token + "'>\n"
        payment_form += "   </form>\n"
        payment_form += "</body>\n"
        payment_form += "</html>\n";

        """
TestPaymentCgi().Process()