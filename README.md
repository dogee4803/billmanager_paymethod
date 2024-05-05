[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/dogee4803/billmanager_paymethod/edit/main/README.en.md)
[![ru](https://img.shields.io/badge/lang-ru-blue.svg)](https://github.com/dogee4803/billmanager_paymethod/edit/main/README.md)
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

├── billmgr_mod_mypayment.xml

├── payment.py

├── pmmypayment.py

├── requirements.txt

└── mypayment.py

# Структура проекта
⇨ ./billmgr - общие функции для работы с BILLmanager, библиотека, предоставляющая базовую функциональность (работа с бд, вывод в лог, взаимодействие с панелью через mgrctl)

⇨ ./payment.py - базовая функциональность для реализации cgi и модуля обработки собственного платежного модуля

⇨ ./pmmypayment.py - основной модуль обработчика платежной системы

⇨ ./mypayment.py - cgi для перехода в платежную систему для оплаты

⇨ ./billmgr_mod_mypayment.xml - xml с полями на форме настройки метода оплаты и сообщениями

⇨./requirements.txt - используемые сторонние библиотеки (для pip)

# Установка окружения (установка зависимостей глобально)
apt install python3-pip

cd <ДИРЕКТОРИЯ_ПРОЕКТА>

pip install -r requirements.txt

# Размещение в структуре BILLmanager
cp usr/local/mgr5/<ДИРЕКТОРИЯ_ПРОЕКТА>/billmgr_mod_mypayment.xml /usr/local/mgr5/etc/xml/

ln -s usr/local/mgr5/<ДИРЕКТОРИЯ_ПРОЕКТА>/pmtestpayment.py /usr/local/mgr5/paymethods/pmmypayment

ln -s usr/local/mgr5/<ДИРЕКТОРИЯ_ПРОЕКТА>/testpayment.py /usr/local/mgr5/cgi/mypayment

# Что сделано
1) Формирование платежа на стороне платежной системы, получение ссылки на оплату, переход по ней.
2) Частично реализована валидация введённых данных. Идёт проверка по совпадению имени и паролю терминала для Tinkoff, однако при проверке минимальной суммы выскакивает ошибка во время обработки условия перед исключением.
3) Отредактирован файл xml для success_url_page и fail_url_page
4) Форма payment_form перенесена в отдельный файл с использованием шаблона через Jinja2 

# Что надо сделать
1) Исправить ошибку при обработке условия для минимального размера платы в валидации.
2) Закончить реализацию страниц возврата после оплаты. Заготовки уже написаны, осталось впихнуть получение статуса платежа после заполнения формы.
3) При получении статуса платежа неправильно формируется токен
4) В основном обработчике дополнить функциональность для проверки статуса платежа (следует из предыдущего)
