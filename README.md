[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/dogee4803/billmanager_paymethod/blob/main/README.en.md)
[![ru](https://img.shields.io/badge/lang-ru-blue.svg)](https://github.com/dogee4803/billmanager_paymethod/blob/main/README.md)

# billmanager_paymethod
Создание метода оплаты Tinkoff для billmanager 


# Структура по файлам
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


# Структура проекта
⇨ ./billmgr - общие функции для работы с BILLmanager, библиотека, предоставляющая базовую функциональность (работа с бд, вывод в лог, взаимодействие с панелью через mgrctl).

⇨ ./templates - Папка с шаблонами форм для отправки данных в платёжную систему.

⇨ ./payment.py - базовая функциональность для реализации cgi и модуля обработки собственного платежного модуля.

⇨ ./pmmypayment.py - основной модуль обработчика платежной системы.

⇨ ./mypayment.py - cgi для перехода в платежную систему для оплаты.

⇨ ./tinkoffApiHandler.py - модуль работы с api Tinkoff.

⇨ ./billmgr_mod_mypayment.xml - xml с полями на форме настройки метода оплаты и сообщениями.

⇨./requirements.txt - используемые сторонние библиотеки (для pip).


# Установка окружения (установка зависимостей глобально)
apt install python3-pip

cd <ДИРЕКТОРИЯ_ПРОЕКТА>

pip install -r requirements.txt


# Размещение в структуре BILLmanager
cp /usr/local/mgr5/<ДИРЕКТОРИЯ_ПРОЕКТА>/billmgr_mod_XXXpayment.xml /usr/local/mgr5/etc/xml/

ln -s /usr/local/mgr5/<ДИРЕКТОРИЯ_ПРОЕКТА>/pmXXXpayment.py /usr/local/mgr5/paymethods/pmXXXpayment

ln -s /usr/local/mgr5/<ДИРЕКТОРИЯ_ПРОЕКТА>/XXXpayment.py /usr/local/mgr5/cgi/XXXpayment