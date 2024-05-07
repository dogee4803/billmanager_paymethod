import requests
import json
import hashlib
import http.client

import billmgr.logger as logging

import xml.etree.ElementTree as ET

MODULE = 'payment'


headers = {"Content-Type": "application/json"}

logging.init_logging('tinkoffApiHandler')
logger = logging.get_logger('tinkoffApiHandler')

class TinkoffApiHandler():

    def initTinkoffPayment(self):
        
        init_data = dict()
        init_data["TerminalKey"] = self.paymethod_params["terminalkey"]
        init_data["Amount"] = str(float(self.payment_params["paymethodamount"]) * 100)
        init_data["OrderId"] = self.elid + "#" + self.payment_params["randomnumber"]
        init_data["Token"] = genToken(init_data, self.paymethod_params["terminalpsw"])
        init_data["SuccessURL"] = self.success_page
        init_data["FailURL"] = self.fail_page
        logger.info(f"tinkoffInit_data = {init_data}")

        # https://www.tinkoff.ru/kassa/dev/payments/#tag/Standartnyj-platyozh/paths/~1v2~1Init/post
        return requests.post('https://securepay.tinkoff.ru/v2/Init', data = json.dumps(init_data), headers=headers) 
    

    def checkStatusPayment(self, payment):
        logger.info(f"status = {payment['id']}")

        payment_xml = ET.fromstring(payment['xmlparams'])
        logger.info(f"p['xmlparams'] {payment_xml.text}")

        status_data = dict()
        status_data["TerminalKey"] = payment_xml.find("terminalkey").text

        logger.info(f"payment_id {payment['externalid']}")

        status_data["PaymentId"] = payment["externalid"]
        status_data["Token"] = genToken(status_data, payment_xml.find("terminalpsw").text)

        logger.info(f"getStatus_data = {status_data}")

        # https://www.tinkoff.ru/kassa/dev/payments/#tag/Standartnyj-platyozh/paths/~1v2~1GetState/post
        return requests.post('https://securepay.tinkoff.ru/v2/GetState', data = json.dumps(status_data), headers=headers)


    
    def getTerminalList(self, bearerToken):
        conn = http.client.HTTPSConnection("business.tinkoff.ru")
        payload = ''
        headers = {'Accept': 'application/json', 'Authorization': bearerToken}
        # https://developer.tinkoff.ru/docs/api/get-api-v-1-tacq-terminals
        conn.request("GET", "/openapi/api/v1/tacq/terminals?page=null&size=null", payload, headers)
        res = conn.getresponse()
        data = res.read()
        json_data = json.loads(data.decode("utf-8"))
        terminals = json_data["terminals"]
        logging.info(f"terminalVal{terminals}")
        terminalkeys = []
        for terminal in terminals:
            terminalkeys.append(terminal["key"])
        return terminalkeys
    

def genToken(data, secretKey):
    data_temp = dict()
    for key, value in data.items():
        if type(value) in [int, float, str, bool]:
            data_temp[key] = value
    data_temp.update({"Password": secretKey})
    data_temp = dict(sorted(data_temp.items()))
    concatenated_values = ''.join(list(data_temp.values()))
    return hashlib.sha256(concatenated_values.encode('utf-8')).hexdigest()