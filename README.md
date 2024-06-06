# Drug Supply Chain using Blockchain

This project is a drug supply chain management system implemented using blockchain technology.

## Prerequisites

Make sure you have Python installed on your Windows machine and Multichain.

## Installation

1. To clone the repo, run the following command in your terminal:

    ```
    git clone -b master https://github.com/AfzalAliSolangi/Drug-Supply-Chain-using-Blockchain.git
    ```

2. Run the following commands to install the required libraries:

    ```
    pip3 install django
    pip3 install cryptography
    pip3 install django-cors-headers
    pip3 install qrcode
    ```
3. Open the `blockchain/settings.py` file and add your email and key to configure email settings:

    ```python
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'your-email@gmail.com'
    EMAIL_HOST_PASSWORD = 'your-email-password-or-app-specific-key'
    ```
    
## Usage

To run the server, execute the following command:

   ```
    python manage.py runserver 0.0.0.0:8000
   ```

## MultiChain Streams
Need to create the streams first before using the application. Replace < chain-name > with your chain name.
### Creating Streams

```bash
multichain-cli <chain-name> create stream users_manufacturer_items_stream true
multichain-cli <chain-name> create stream users_distributor_items_stream true
multichain-cli <chain-name> create stream users_pharmacy_items_stream true
multichain-cli <chain-name> create stream users_pharmacy_sold_items_stream true
multichain-cli <chain-name> create stream manufacturer_orders_stream true
multichain-cli <chain-name> create stream distributor_orders_stream true
multichain-cli <chain-name> create stream users_master_stream true
multichain-cli <chain-name> create stream users_manufacturer_stream true
multichain-cli <chain-name> create stream users_distributor_stream true
multichain-cli <chain-name> create stream users_pharmacy_stream true
multichain-cli <chain-name> create stream manufacturer_sla_stream true
multichain-cli <chain-name> create stream distributor_sla_stream true
multichain-cli <chain-name> create stream pharmacy_sla_stream true
multichain-cli <chain-name> subscribe users_manufacturer_items_stream
multichain-cli <chain-name> subscribe users_distributor_items_stream
multichain-cli <chain-name> subscribe users_pharmacy_items_stream
multichain-cli <chain-name> subscribe users_pharmacy_sold_items_stream
multichain-cli <chain-name> subscribe manufacturer_orders_stream
multichain-cli <chain-name> subscribe distributor_orders_stream
multichain-cli <chain-name> subscribe users_master_stream
multichain-cli <chain-name> subscribe users_manufacturer_stream
multichain-cli <chain-name> subscribe users_distributor_stream
multichain-cli <chain-name> subscribe users_pharmacy_stream
multichain-cli <chain-name> subscribe manufacturer_sla_stream
multichain-cli <chain-name> subscribe distributor_sla_stream
multichain-cli <chain-name> subscribe pharmacy_sla_stream
```

## Special Thanks

Special thanks for the guidance for the project to Assistant Professor Dr. Shehbaz A. Siddiqui (FAST National University of Computer and Emerging Sciences, Karachi).
