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

├── billmgr_mod_mypayment.xml

├── payment.py

├── pmmypayment.py

├── requirements.txt

└── mypayment.py

# Structure of the project
⇨ ./billmgr - general functions for working with BILLmanager, a library that provides basic functionality (working with the database, logging, interacting with the panel via mgrctl)

⇨ ./payment.py - Basic functionality for the implementation of CGI and the module for processing your payment module

⇨ ./pmmypayment.py - The main module of the payment system processor

⇨ ./mypayment.py - CGI to go to the payment system for payment

⇨ ./billmgr_mod_mypayment.xml - XML with fields on the payment method setup form and messages

⇨./requirements.txt - List of libraries for installation via python pip

# Setting the Environment (Installing Dependencies Globally)
apt install python3-pip

cd <PROJECT_DIRECTORY>

pip install -r requirements.txt

# Integration in the BILLmanager structure
cp usr/local/mgr5/<PROJECT_DIRECTORY>/billmgr_mod_mypayment.xml /usr/local/mgr5/etc/xml/

ln -s usr/local/mgr5/<PROJECT_DIRECTORY>/pmmypayment.py /usr/local/mgr5/paymethods/pmmypayment

ln -s usr/local/mgr5/<PROJECT_DIRECTORY>/mypayment.py /usr/local/mgr5/cgi/mypayment
