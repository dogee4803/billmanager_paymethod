[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/dogee4803/billmanager_paymethod/blob/main/README.en.md)
[![ru](https://img.shields.io/badge/lang-ru-blue.svg)](https://github.com/dogee4803/billmanager_paymethod/blob/main/README.md)

# billmanager_paymethod
Creating a Tinkoff payment method for billmanager


# File Structure
.

├── billmgr

│   ├── __init__.py

│   ├── config.py

│   ├── db.py

│   ├── exception.py

│   ├── logger.py

│   └── misc.py

├── templates

├── billmgr_mod_mypayment.xml

├── payment.py

├── pmmypayment.py

├── requirements.txt

├── tinkoffApiHandler.py

└── mypayment.py


# Structure of the project
⇨ ./billmgr - General functions for working with BILLmanager, a library that provides basic functionality (working with the database, logging, interacting with the panel via mgrctl).

⇨ ./templates - Folder with forms templates for sending data to bank payment system.

⇨ ./payment.py - Basic functionality for the implementation of CGI and the module for processing your payment module.

⇨ ./pmmypayment.py - The main module of the payment system processor.

⇨ ./mypayment.py - CGI to go to the payment system for payment.

⇨ ./tinkoffApiHandler.py - The module for working with Tinkoff API

⇨ ./billmgr_mod_mypayment.xml - XML with fields on the payment method setup form and messages.

⇨./requirements.txt - List of libraries for installation via python pip.


# Setting the Environment (Installing Dependencies Globally)
apt install python3-pip

cd <PROJECT_DIRECTORY>

pip install -r requirements.txt


# Integration in the BILLmanager structure
cp /usr/local/mgr5/<PROJECT_DIRECTORY>/billmgr_mod_XXXpayment.xml /usr/local/mgr5/etc/xml/

ln -s /usr/local/mgr5/<PROJECT_DIRECTORY>/pXXXypayment.py /usr/local/mgr5/paymethods/pmXXXpayment

ln -s /usr/local/mgr5/<PROJECT_DIRECTORY>/XXXpayment.py /usr/local/mgr5/cgi/XXXpayment