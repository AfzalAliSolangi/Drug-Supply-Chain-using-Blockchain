from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import multichain
import json
import configparser
import datetime
from collections import defaultdict
import random
import string
import hashlib
from cryptography.fernet import Fernet
from django.contrib.auth.hashers import make_password,check_password
import base64
import qrcode
import json
import os

config = configparser.ConfigParser()

# Load the .conf file
print(config.read('./drugs/config.conf'))

# Access configuration values from the default section
users_manufacturer_items_stream = config.get('Section1','users_manufacturer_items_stream')
users_distributor_items_stream = config.get('Section1','users_distributor_items_stream')
users_pharmacy_items_stream = config.get('Section1','users_pharmacy_items_stream')
users_master_stream = config.get('Section1','users_master_stream') #Need to add different user stream for all users
users_manufacturer_stream = config.get('Section1','users_manufacturer_stream') #Need to add different user stream for all users
manufacturer_orders_stream = config.get('Section1','manufacturer_orders_stream') #Set a default for Manufacturer, add another for distributors
distributor_orders_stream = config.get('Section1','distributor_orders_stream') #Set a default for Manufacturer, add another for distributors
users_distributor_stream = config.get('Section1','users_distributor_stream') #Need to add different user stream for all users
users_pharmacy_stream = config.get('Section1','users_pharmacy_stream') #Need to add different user stream for all users
manufacturer_SLA_stream = config.get('Section1','manufacturer_SLA_stream')
distributor_SLA_stream = config.get('Section1','distributor_SLA_stream')
pharmacy_SLA_stream = config.get('Section1','pharmacy_SLA_stream')
key = config.get('Section1','key') #Key - for manufacturer
publisher = config.get('Section1','publisher') #Set a default for Manufacturer, add another for distributors
qr_codes_path = config.get('Section1','qr_codes_path') #Set a default for Manufacturer, add another for distributors

# Configure your MultiChain connection here
rpcuser = config.get('Section1','rpcuser')
rpcpassword= config.get('Section1','rpcpassword')
rpchost = config.get('Section1','rpchost')
rpcport = config.get('Section1','rpcport')
chainname = config.get('Section1','chainname')
rpc_connection = multichain.MultiChainClient(rpchost, rpcport, rpcuser, rpcpassword)

# Generate a secret key for encryption and decryption of the data
SECRET_KEY = b'pGVMH7s1zlQMtcugRETEOx572lhVYcEjfSIn1X0OBCo='  # Generated using fernet.py
cipher_suite = Fernet(SECRET_KEY)

def send_otp_via_email(email, otp):
    subject = 'Your MedConnect OTP Verification Code'
    plain_message = f'''Dear User,

Thank you for choosing MedConnect for your medical supply needs. To ensure the security of your account, we require you to verify your email address.

Your One-Time Password (OTP) for verification is:

{otp}

Thank you for using MedConnect!

Best regards,
The MedConnect Team'''

    html_message = f'''<p>Dear User,</p>
<p>Thank you for choosing MedConnect for your medical supply needs. To ensure the security of your account, we require you to verify your email address.</p>
<p>Your One-Time Password (OTP) for verification is:</p>
<p><strong>{otp}</strong></p>
<p>Thank you for using MedConnect!</p>
<p>Best regards,<br>The MedConnect Team</p>'''
    
    email_from = settings.EMAIL_HOST
    send_mail(
        subject,
        plain_message,
        email_from,
        [email],
        html_message=html_message
    )

def send_welcome_email(email,user):
    subject = 'Welcome to MedConnect!'
    
    plain_message = f'''Dear {user},

Welcome to MedConnect!

We are thrilled to have you on board. At MedConnect, we are committed to providing you with a seamless and secure medical supply experience. Whether you are a manufacturer, distributor, or pharmacy, our platform is designed to meet your specific needs and streamline your operations.

Here are a few tips to get you started:
- Explore Your Dashboard: Access your dashboard to manage your orders, inventory, and more.

Thank you for choosing MedConnect. We look forward to serving you!

Best regards,
The MedConnect Team'''

    html_message = f'''<p>Dear {user},</p>
<p>Welcome to MedConnect!</p>
<p>We are thrilled to have you on board. At MedConnect, we are committed to providing you with a seamless and secure medical supply experience. Whether you are a manufacturer, distributor, or pharmacy, our platform is designed to meet your specific needs and streamline your operations.</p>
<p>Here are a few tips to get you started:</p>
<ul>
<li><strong>Explore Your Dashboard:</strong> Access your dashboard to manage your orders, inventory, and more.</li>
</ul>
<p>Thank you for choosing MedConnect. We look forward to serving you!</p>
<p>Best regards,<br>The MedConnect Team</p>'''
    
    email_from = settings.EMAIL_HOST
    send_mail(
        subject,
        plain_message,
        email_from,
        [email],
        html_message=html_message
    )

def capitalize_alphabets(s):
    result = ""
    for char in s:
        if char.isalpha():
            result += char.upper()
        else:
            result += char
    return result

def otp_generator(email):
    base_string = f"{email}"
    hashed = hashlib.sha256(base_string.encode()).hexdigest()
    otp = ''.join(random.choices(hashed, k=6))
    return otp

def generate_qr_code(email,product_code,batchid,product_name):
    data = {
    "manufacturer_email": email,
    "Product_code": product_code,
    "Batch_id": batchid,
    "product_name": product_name
    }

    # Convert the data dictionary to a JSON string
    json_data = json.dumps(data)
    
    # Generate the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json_data)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")
    save_path = f"{qr_codes_path}+{product_name}_{batchid}.png"
    save_path = "{}{}_{}.png".format(qr_codes_path,product_name,batchid)
    # Save the image to the specified path
    img.save(save_path)

def encrypt_data(data):
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data

def decrypt_data(encrypted_data):
    decrypted_data = cipher_suite.decrypt(encrypted_data).decode()
    return decrypted_data

# Function to convert bytes data to base64 encoded string
def bytes_to_base64(data):
    return base64.b64encode(data).decode()

# Function to decode base64 encoded string to bytes
def base64_to_bytes(encoded_data):
    return base64.b64decode(encoded_data)

def index(request):
    return render(request, "index.html")

def blog(request):
    return render(request, "blog.html")

def blogsingle(request):
    return render(request, "blog-single.html")

def features(request):
    return render(request, "features.html")

def pricing(request):
    return render(request, "pricing.html")

def contact(request):
    return render(request, "contact.html")






#### MASTER ####
def signup_master(request):
    print("signup-master check")
    return render(request, "email_check_master.html")

def email_check_master(request):
    print("email_check_master")
    x = rpc_connection.subscribe('{}'.format(users_master_stream))
    if request.method == 'POST':
        # print("method check")
        email = request.POST['email']
        response = rpc_connection.liststreamkeys(users_master_stream)
        json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
        json_string = json.loads(json_string) #Converts OrderedDict to JSON String
        # print(json_string)
        email_keys = [entry["key"] for entry in json_string]
        print(email_keys)
        otp = capitalize_alphabets(otp_generator(email))
        print(otp)
        for each_email in email_keys:
            if each_email==email:
                print("present")
                return render(request, "login_master.html",{'message':'User already registered, Please Log In!'}) #if the email is present prompt to login master page
        send_otp_via_email(email,otp)
        return render(request, "tokin_master.html",{'email': email, 'otp': otp}) #if the email is not present then render this page

def process_registration_master(request):
    print("process_registration_master")
    if request.method == 'POST':
        # print("method check")
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(password)
        timestamp_utc = datetime.datetime.utcnow().isoformat()
        # Hash the password
        hashed_password = make_password(password)
        # Encrypt other user details
        encrypted_company_info = encrypt_data(request.POST.get('company_info'))
        encrypted_street_address = encrypt_data(request.POST.get('street_address'))
        encrypted_business_details = encrypt_data(request.POST.get('business_details'))
        encrypted_state = encrypt_data(request.POST.get('state'))
        encrypted_city = encrypt_data(request.POST.get('city'))
        encrypted_zip_code = encrypt_data(request.POST.get('zip_code'))
        request_data = {
            "email": request.POST.get('email'),
            "company_info": bytes_to_base64(encrypted_company_info),
            "street_address": bytes_to_base64(encrypted_street_address),
            "business_details": bytes_to_base64(encrypted_business_details),
            "state": bytes_to_base64(encrypted_state),
            "city": bytes_to_base64(encrypted_city),
            "zip_code": bytes_to_base64(encrypted_zip_code),
            "password": hashed_password,
            "license_certification": request.POST.get('hash_sla') #Hash calculated from the front end don't need to encrypt it
        }
        data = json.dumps(request_data)
        data = json.loads(data)
        txid = rpc_connection.publish(users_master_stream, [email,'True',timestamp_utc], {'json' : data})
        if txid:
            send_welcome_email(email,request.POST.get('company_info'))
            return render(request, "login_master.html")
        
def login_master(request):
        return render(request, "login_master.html")

def login_check_master(request): #Implement Password authentication
    print('login_check_master')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        password_rcvd = request.POST.get('passw')
        result = rpc_connection.liststreamkeyitems(users_master_stream, email_rcvd)
        data = json.dumps(result)
        json_load = json.loads(data)
        #apply length check for json_load
        if(len(json_load)>0):
            email_frm_chain = json_load[0]['keys'][0]
            passw_frm_chain = json_load[0]['data']['json']['password']
            manufacturer_name = decrypt_data(base64_to_bytes(json_load[0]['data']['json']['company_info']))
            comp_info = json_load[0]['data']['json']['company_info']
            print(data)
            print(comp_info)
            print("Email from front end: ",email_rcvd)
            print("Email from stream: ",email_frm_chain)
            print(password_rcvd)
            print(passw_frm_chain)
            if email_rcvd==email_frm_chain and check_password(password_rcvd, passw_frm_chain):
                print(email_rcvd)
                return render(request, "select_usertype.html",{'comp_info': comp_info,'email':email_rcvd, 'company_info': manufacturer_name,'message': f'Welcome, {manufacturer_name}!'})
            else:
                return render(request, "login_master.html", {'error_message': "Incorrect email or password."})
        else:
            return render(request, "login_master.html", {'error_message': "Incorrect email or password."})

def select_user_type(request): #Implement Password authentication
    print('login_check_master')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email',None)
        company_info = request.POST.get('company_info',None)
        print(email_rcvd)
        print(company_info)
        result = rpc_connection.liststreamkeyitems(users_master_stream, email_rcvd)
        data = json.dumps(result)
        json_load = json.loads(data)
        if(len(json_load)>0):
            comp_info = json_load[0]['data']['json']['company_info']
            manufacturer_name = decrypt_data(base64_to_bytes(json_load[0]['data']['json']['company_info']))
            return render(request, "select_usertype.html",{'comp_info': comp_info,'email':email_rcvd, 'company_info': manufacturer_name})
        
def user_type(request):
    print('Selected UserType master')
    if request.method == 'GET':
        email_rcvd = request.GET.get('email',None)
        company_info = request.GET.get('comp_info',None)
        userType = request.GET.get('userType', None)
        print('\nDistributor Email: ',email_rcvd)
        print('Company Info: ',company_info)
        
        if userType=='Manufacturer':
            print('1')
            response = rpc_connection.liststreamitems(users_manufacturer_stream)
            
            

            user_map = {}  # Initialize a dictionary to store user data based on the latest timestamp

            # Sort the response list based on timestamp
            response.sort(key=lambda x: x['keys'][-1], reverse=True)

            for item in response:
                data = item['data']['json']
                email = data['email']
                timestamp = item['keys'][-1]  # Get the timestamp from the last element of keys
                status = item['keys'][1]
                if email not in user_map or timestamp > user_map[email]['timestamp']:
                    user_map[email] = {
                        'timestamp': timestamp,
                        'user_data': data,
                        'status': status
                    }

            users_with_latest_info = [{
                'email': key,
                'timestamp': value['timestamp'],
                'user_data': value['user_data'],
                'status': value['status']
            } for key, value in user_map.items()]

            # print(users_with_latest_info)
            json_string = json.dumps(users_with_latest_info)
            json_string = json.loads(json_string)
            print(json_string)
            combined_list = []

            for item in json_string:
                confirmed_status = item['user_data']
                status = item['status']
                # Decrypting the data fields after converting from base64
                user_email = confirmed_status.get('email', '')
                decrypted_company_info = decrypt_data(base64_to_bytes(confirmed_status.get('company_info', '')))
                decrypted_street_address = decrypt_data(base64_to_bytes(confirmed_status.get('street_address', '')))
                decrypted_business_details = decrypt_data(base64_to_bytes(confirmed_status.get('business_details', '')))
                decrypted_state = decrypt_data(base64_to_bytes(confirmed_status.get('state', '')))
                decrypted_city = decrypt_data(base64_to_bytes(confirmed_status.get('city', '')))
                decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                license_certification = confirmed_status.get('license_certification', '')
                # Add decrypted data to the combined list
                combined_list.append({
                    'email': user_email,
                    'company_info': decrypted_company_info,
                    'street_address': decrypted_street_address,
                    'business_details': decrypted_business_details,
                    'state': decrypted_state,
                    'city': decrypted_city,
                    'zip_code': decrypted_zip_code,
                    'license_certification' : license_certification,
                    'status': status
                })
            
            #Assuming you want to print the combined list to see the output
            print("\n",combined_list)

            
                    
            return render(request, "Master1.html",{'company_info': company_info,'email':email_rcvd,'orders': combined_list,'user_type':userType})
        elif userType =='Distributor':
            print('1')
            response = rpc_connection.liststreamitems(users_distributor_stream)
            
            

            user_map = {}  # Initialize a dictionary to store user data based on the latest timestamp

            # Sort the response list based on timestamp
            response.sort(key=lambda x: x['keys'][-1], reverse=True)

            for item in response:
                data = item['data']['json']
                email = data['email']
                timestamp = item['keys'][-1]  # Get the timestamp from the last element of keys
                status = item['keys'][1]
                if email not in user_map or timestamp > user_map[email]['timestamp']:
                    user_map[email] = {
                        'timestamp': timestamp,
                        'user_data': data,
                        'status': status
                    }

            users_with_latest_info = [{
                'email': key,
                'timestamp': value['timestamp'],
                'user_data': value['user_data'],
                'status': value['status']
            } for key, value in user_map.items()]

            # print(users_with_latest_info)
            json_string = json.dumps(users_with_latest_info)
            json_string = json.loads(json_string)
            print(json_string)
            combined_list = []

            for item in json_string:
                confirmed_status = item['user_data']
                status = item['status']
                # Decrypting the data fields after converting from base64
                user_email = confirmed_status.get('email', '')
                decrypted_company_info = decrypt_data(base64_to_bytes(confirmed_status.get('company_info', '')))
                decrypted_street_address = decrypt_data(base64_to_bytes(confirmed_status.get('street_address', '')))
                decrypted_business_details = decrypt_data(base64_to_bytes(confirmed_status.get('business_details', '')))
                decrypted_state = decrypt_data(base64_to_bytes(confirmed_status.get('state', '')))
                decrypted_city = decrypt_data(base64_to_bytes(confirmed_status.get('city', '')))
                decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                license_certification = confirmed_status.get('license_certification', '')
                # Add decrypted data to the combined list
                combined_list.append({
                    'email': user_email,
                    'company_info': decrypted_company_info,
                    'street_address': decrypted_street_address,
                    'business_details': decrypted_business_details,
                    'state': decrypted_state,
                    'city': decrypted_city,
                    'zip_code': decrypted_zip_code,
                    'license_certification' : license_certification,
                    'status': status
                })
            
            #Assuming you want to print the combined list to see the output
            print("\n",combined_list)

            
                    
            return render(request, "Master1.html",{'company_info': company_info,'email':email_rcvd,'orders': combined_list,'user_type':userType})
        elif userType == 'Pharmacy':
            print('3')
            print('1')
            response = rpc_connection.liststreamitems(users_pharmacy_stream)
            
            

            user_map = {}  # Initialize a dictionary to store user data based on the latest timestamp

            # Sort the response list based on timestamp
            response.sort(key=lambda x: x['keys'][-1], reverse=True)

            for item in response:
                data = item['data']['json']
                email = data['email']
                timestamp = item['keys'][-1]  # Get the timestamp from the last element of keys
                status = item['keys'][1]
                if email not in user_map or timestamp > user_map[email]['timestamp']:
                    user_map[email] = {
                        'timestamp': timestamp,
                        'user_data': data,
                        'status': status
                    }

            users_with_latest_info = [{
                'email': key,
                'timestamp': value['timestamp'],
                'user_data': value['user_data'],
                'status': value['status']
            } for key, value in user_map.items()]

            # print(users_with_latest_info)
            json_string = json.dumps(users_with_latest_info)
            json_string = json.loads(json_string)
            print(json_string)
            combined_list = []

            for item in json_string:
                confirmed_status = item['user_data']
                status = item['status']
                # Decrypting the data fields after converting from base64
                user_email = confirmed_status.get('email', '')
                decrypted_company_info = decrypt_data(base64_to_bytes(confirmed_status.get('company_info', '')))
                decrypted_street_address = decrypt_data(base64_to_bytes(confirmed_status.get('street_address', '')))
                decrypted_business_details = decrypt_data(base64_to_bytes(confirmed_status.get('business_details', '')))
                decrypted_state = decrypt_data(base64_to_bytes(confirmed_status.get('state', '')))
                decrypted_city = decrypt_data(base64_to_bytes(confirmed_status.get('city', '')))
                decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                license_certification = confirmed_status.get('license_certification', '')
                # Add decrypted data to the combined list
                combined_list.append({
                    'email': user_email,
                    'company_info': decrypted_company_info,
                    'street_address': decrypted_street_address,
                    'business_details': decrypted_business_details,
                    'state': decrypted_state,
                    'city': decrypted_city,
                    'zip_code': decrypted_zip_code,
                    'license_certification' : license_certification,
                    'status': status
                })
            
            #Assuming you want to print the combined list to see the output
            print("\n",combined_list)

            
                    
            return render(request, "Master1.html",{'company_info': company_info,'email':email_rcvd,'orders': combined_list,'user_type':userType})
        return HttpResponse("Working!")
    
def deactive_user(request):
    print('deActivating a user')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email',None)
        company_info = request.POST.get('company_info',None)
        useremail = request.POST.get('useremail',None)
        userType = request.POST.get('user_type', None)
        timestamp_utc = datetime.datetime.utcnow().isoformat()
        print(email_rcvd)
        print(company_info)
        print(useremail)
        if userType == 'Manufacturer':
            response = rpc_connection.liststreamkeyitems(users_manufacturer_stream, useremail)
            json_string = json.dumps(response)
            json_string = json.loads(json_string)
            data = json_string[-1]['data']['json']
            txid = rpc_connection.publish(users_manufacturer_stream, [useremail,'False',timestamp_utc], {'json' : data})
            if txid:
                print("Done")
                print('1')
                response = rpc_connection.liststreamitems(users_manufacturer_stream)
                
                
    
                user_map = {}  # Initialize a dictionary to store user data based on the latest timestamp
    
                # Sort the response list based on timestamp
                response.sort(key=lambda x: x['keys'][-1], reverse=True)
    
                for item in response:
                    data = item['data']['json']
                    email = data['email']
                    timestamp = item['keys'][-1]  # Get the timestamp from the last element of keys
                    status = item['keys'][1]
                    if email not in user_map or timestamp > user_map[email]['timestamp']:
                        user_map[email] = {
                            'timestamp': timestamp,
                            'user_data': data,
                            'status': status
                        }
    
                users_with_latest_info = [{
                    'email': key,
                    'timestamp': value['timestamp'],
                    'user_data': value['user_data'],
                    'status': value['status']
                } for key, value in user_map.items()]
    
                # print(users_with_latest_info)
                json_string = json.dumps(users_with_latest_info)
                json_string = json.loads(json_string)
                print(json_string)
                combined_list = []
    
                for item in json_string:
                    confirmed_status = item['user_data']
                    status = item['status']
                    # Decrypting the data fields after converting from base64
                    user_email = confirmed_status.get('email', '')
                    decrypted_company_info = decrypt_data(base64_to_bytes(confirmed_status.get('company_info', '')))
                    decrypted_street_address = decrypt_data(base64_to_bytes(confirmed_status.get('street_address', '')))
                    decrypted_business_details = decrypt_data(base64_to_bytes(confirmed_status.get('business_details', '')))
                    decrypted_state = decrypt_data(base64_to_bytes(confirmed_status.get('state', '')))
                    decrypted_city = decrypt_data(base64_to_bytes(confirmed_status.get('city', '')))
                    decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                    decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                    license_certification = confirmed_status.get('license_certification', '')
                    # Add decrypted data to the combined list
                    combined_list.append({
                        'email': user_email,
                        'company_info': decrypted_company_info,
                        'street_address': decrypted_street_address,
                        'business_details': decrypted_business_details,
                        'state': decrypted_state,
                        'city': decrypted_city,
                        'zip_code': decrypted_zip_code,
                        'license_certification' : license_certification,
                        'status': status
                    })
                
                #Assuming you want to print the combined list to see the output
                print("\n",combined_list)
    
                
                        
                return render(request, "Master1.html",{'company_info': company_info,'email':email_rcvd,'orders': combined_list,'user_type':userType})                
            else:
                print("error")
        elif userType =='Distributor':
            print('Decativating 2')
            response = rpc_connection.liststreamkeyitems(users_distributor_stream, useremail)
            json_string = json.dumps(response)
            json_string = json.loads(json_string)
            data = json_string[-1]['data']['json']
            txid = rpc_connection.publish(users_distributor_stream, [useremail,'False',timestamp_utc], {'json' : data})
            if userType =='Distributor':
                print('1')
                response = rpc_connection.liststreamitems(users_distributor_stream)



                user_map = {}  # Initialize a dictionary to store user data based on the latest timestamp

                # Sort the response list based on timestamp
                response.sort(key=lambda x: x['keys'][-1], reverse=True)

                for item in response:
                    data = item['data']['json']
                    email = data['email']
                    timestamp = item['keys'][-1]  # Get the timestamp from the last element of keys
                    status = item['keys'][1]
                    if email not in user_map or timestamp > user_map[email]['timestamp']:
                        user_map[email] = {
                            'timestamp': timestamp,
                            'user_data': data,
                            'status': status
                        }

                users_with_latest_info = [{
                    'email': key,
                    'timestamp': value['timestamp'],
                    'user_data': value['user_data'],
                    'status': value['status']
                } for key, value in user_map.items()]

                # print(users_with_latest_info)
                json_string = json.dumps(users_with_latest_info)
                json_string = json.loads(json_string)
                print(json_string)
                combined_list = []

                for item in json_string:
                    confirmed_status = item['user_data']
                    status = item['status']
                    # Decrypting the data fields after converting from base64
                    user_email = confirmed_status.get('email', '')
                    decrypted_company_info = decrypt_data(base64_to_bytes(confirmed_status.get('company_info', '')))
                    decrypted_street_address = decrypt_data(base64_to_bytes(confirmed_status.get('street_address', '')))
                    decrypted_business_details = decrypt_data(base64_to_bytes(confirmed_status.get('business_details', '')))
                    decrypted_state = decrypt_data(base64_to_bytes(confirmed_status.get('state', '')))
                    decrypted_city = decrypt_data(base64_to_bytes(confirmed_status.get('city', '')))
                    decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                    decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                    license_certification = confirmed_status.get('license_certification', '')
                    # Add decrypted data to the combined list
                    combined_list.append({
                        'email': user_email,
                        'company_info': decrypted_company_info,
                        'street_address': decrypted_street_address,
                        'business_details': decrypted_business_details,
                        'state': decrypted_state,
                        'city': decrypted_city,
                        'zip_code': decrypted_zip_code,
                        'license_certification' : license_certification,
                        'status': status
                    })

                #Assuming you want to print the combined list to see the output
                print("\n",combined_list)



                return render(request, "Master1.html",{'company_info': company_info,'email':email_rcvd,'orders': combined_list,'user_type':userType})
            else:
                print("error")
        elif userType == 'Pharmacy':
            print('Deactivating 3')
            response = rpc_connection.liststreamkeyitems(users_pharmacy_stream, useremail)
            json_string = json.dumps(response)
            json_string = json.loads(json_string)
            data = json_string[-1]['data']['json']
            txid = rpc_connection.publish(users_pharmacy_stream, [useremail,'False',timestamp_utc], {'json' : data})
            if txid:
                print('3')
                response = rpc_connection.liststreamitems(users_pharmacy_stream)



                user_map = {}  # Initialize a dictionary to store user data based on the latest timestamp

                # Sort the response list based on timestamp
                response.sort(key=lambda x: x['keys'][-1], reverse=True)

                for item in response:
                    data = item['data']['json']
                    email = data['email']
                    timestamp = item['keys'][-1]  # Get the timestamp from the last element of keys
                    status = item['keys'][1]
                    if email not in user_map or timestamp > user_map[email]['timestamp']:
                        user_map[email] = {
                            'timestamp': timestamp,
                            'user_data': data,
                            'status': status
                        }

                users_with_latest_info = [{
                    'email': key,
                    'timestamp': value['timestamp'],
                    'user_data': value['user_data'],
                    'status': value['status']
                } for key, value in user_map.items()]

                # print(users_with_latest_info)
                json_string = json.dumps(users_with_latest_info)
                json_string = json.loads(json_string)
                print(json_string)
                combined_list = []

                for item in json_string:
                    confirmed_status = item['user_data']
                    status = item['status']
                    # Decrypting the data fields after converting from base64
                    user_email = confirmed_status.get('email', '')
                    decrypted_company_info = decrypt_data(base64_to_bytes(confirmed_status.get('company_info', '')))
                    decrypted_street_address = decrypt_data(base64_to_bytes(confirmed_status.get('street_address', '')))
                    decrypted_business_details = decrypt_data(base64_to_bytes(confirmed_status.get('business_details', '')))
                    decrypted_state = decrypt_data(base64_to_bytes(confirmed_status.get('state', '')))
                    decrypted_city = decrypt_data(base64_to_bytes(confirmed_status.get('city', '')))
                    decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                    decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                    license_certification = confirmed_status.get('license_certification', '')
                    # Add decrypted data to the combined list
                    combined_list.append({
                        'email': user_email,
                        'company_info': decrypted_company_info,
                        'street_address': decrypted_street_address,
                        'business_details': decrypted_business_details,
                        'state': decrypted_state,
                        'city': decrypted_city,
                        'zip_code': decrypted_zip_code,
                        'license_certification' : license_certification,
                        'status': status
                    })

                #Assuming you want to print the combined list to see the output
                print("\n",combined_list)



                return render(request, "Master1.html",{'company_info': company_info,'email':email_rcvd,'orders': combined_list,'user_type':userType})
            else:
                print("error")    
    return HttpResponse("Working!")

def active_user(request):
    print('deActivating a user')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email',None)
        company_info = request.POST.get('company_info',None)
        useremail = request.POST.get('useremail',None)
        userType = request.POST.get('user_type', None)
        timestamp_utc = datetime.datetime.utcnow().isoformat()
        print(email_rcvd)
        print(company_info)
        print(useremail)
        if userType == 'Manufacturer':
            response = rpc_connection.liststreamkeyitems(users_manufacturer_stream, useremail)
            json_string = json.dumps(response)
            json_string = json.loads(json_string)
            data = json_string[-1]['data']['json']
            txid = rpc_connection.publish(users_manufacturer_stream, [useremail,'True',timestamp_utc], {'json' : data})
            if txid:
                print("Done")
                print('1')
                response = rpc_connection.liststreamitems(users_manufacturer_stream)
                
                
    
                user_map = {}  # Initialize a dictionary to store user data based on the latest timestamp
    
                # Sort the response list based on timestamp
                response.sort(key=lambda x: x['keys'][-1], reverse=True)
    
                for item in response:
                    data = item['data']['json']
                    email = data['email']
                    timestamp = item['keys'][-1]  # Get the timestamp from the last element of keys
                    status = item['keys'][1]
                    if email not in user_map or timestamp > user_map[email]['timestamp']:
                        user_map[email] = {
                            'timestamp': timestamp,
                            'user_data': data,
                            'status': status
                        }
    
                users_with_latest_info = [{
                    'email': key,
                    'timestamp': value['timestamp'],
                    'user_data': value['user_data'],
                    'status': value['status']
                } for key, value in user_map.items()]
    
                # print(users_with_latest_info)
                json_string = json.dumps(users_with_latest_info)
                json_string = json.loads(json_string)
                print(json_string)
                combined_list = []
    
                for item in json_string:
                    confirmed_status = item['user_data']
                    status = item['status']
                    # Decrypting the data fields after converting from base64
                    user_email = confirmed_status.get('email', '')
                    decrypted_company_info = decrypt_data(base64_to_bytes(confirmed_status.get('company_info', '')))
                    decrypted_street_address = decrypt_data(base64_to_bytes(confirmed_status.get('street_address', '')))
                    decrypted_business_details = decrypt_data(base64_to_bytes(confirmed_status.get('business_details', '')))
                    decrypted_state = decrypt_data(base64_to_bytes(confirmed_status.get('state', '')))
                    decrypted_city = decrypt_data(base64_to_bytes(confirmed_status.get('city', '')))
                    decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                    decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                    license_certification = confirmed_status.get('license_certification', '')
                    # Add decrypted data to the combined list
                    combined_list.append({
                        'email': user_email,
                        'company_info': decrypted_company_info,
                        'street_address': decrypted_street_address,
                        'business_details': decrypted_business_details,
                        'state': decrypted_state,
                        'city': decrypted_city,
                        'zip_code': decrypted_zip_code,
                        'license_certification' : license_certification,
                        'status': status
                    })
                
                #Assuming you want to print the combined list to see the output
                print("\n",combined_list)
    
                
                        
                return render(request, "Master1.html",{'company_info': company_info,'email':email_rcvd,'orders': combined_list,'user_type':userType})
            else:
                print("error")
        elif userType =='Distributor':
            print('Activating 2')
            response = rpc_connection.liststreamkeyitems(users_distributor_stream, useremail)
            json_string = json.dumps(response)
            json_string = json.loads(json_string)
            data = json_string[-1]['data']['json']
            txid = rpc_connection.publish(users_distributor_stream, [useremail,'True',timestamp_utc], {'json' : data})
            if txid:
                print('1')
                response = rpc_connection.liststreamitems(users_distributor_stream)



                user_map = {}  # Initialize a dictionary to store user data based on the latest timestamp

                # Sort the response list based on timestamp
                response.sort(key=lambda x: x['keys'][-1], reverse=True)

                for item in response:
                    data = item['data']['json']
                    email = data['email']
                    timestamp = item['keys'][-1]  # Get the timestamp from the last element of keys
                    status = item['keys'][1]
                    if email not in user_map or timestamp > user_map[email]['timestamp']:
                        user_map[email] = {
                            'timestamp': timestamp,
                            'user_data': data,
                            'status': status
                        }

                users_with_latest_info = [{
                    'email': key,
                    'timestamp': value['timestamp'],
                    'user_data': value['user_data'],
                    'status': value['status']
                } for key, value in user_map.items()]

                # print(users_with_latest_info)
                json_string = json.dumps(users_with_latest_info)
                json_string = json.loads(json_string)
                print(json_string)
                combined_list = []

                for item in json_string:
                    confirmed_status = item['user_data']
                    status = item['status']
                    # Decrypting the data fields after converting from base64
                    user_email = confirmed_status.get('email', '')
                    decrypted_company_info = decrypt_data(base64_to_bytes(confirmed_status.get('company_info', '')))
                    decrypted_street_address = decrypt_data(base64_to_bytes(confirmed_status.get('street_address', '')))
                    decrypted_business_details = decrypt_data(base64_to_bytes(confirmed_status.get('business_details', '')))
                    decrypted_state = decrypt_data(base64_to_bytes(confirmed_status.get('state', '')))
                    decrypted_city = decrypt_data(base64_to_bytes(confirmed_status.get('city', '')))
                    decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                    decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                    license_certification = confirmed_status.get('license_certification', '')
                    # Add decrypted data to the combined list
                    combined_list.append({
                        'email': user_email,
                        'company_info': decrypted_company_info,
                        'street_address': decrypted_street_address,
                        'business_details': decrypted_business_details,
                        'state': decrypted_state,
                        'city': decrypted_city,
                        'zip_code': decrypted_zip_code,
                        'license_certification' : license_certification,
                        'status': status
                    })

                #Assuming you want to print the combined list to see the output
                print("\n",combined_list)



                return render(request, "Master1.html",{'company_info': company_info,'email':email_rcvd,'orders': combined_list,'user_type':userType})
            else:
                print("error")
        elif userType == 'Pharmacy':
            print('Activating 3')
            response = rpc_connection.liststreamkeyitems(users_pharmacy_stream, useremail)
            json_string = json.dumps(response)
            json_string = json.loads(json_string)
            data = json_string[-1]['data']['json']
            txid = rpc_connection.publish(users_pharmacy_stream, [useremail,'True',timestamp_utc], {'json' : data})
            if txid:
                print('3')
                response = rpc_connection.liststreamitems(users_pharmacy_stream)



                user_map = {}  # Initialize a dictionary to store user data based on the latest timestamp

                # Sort the response list based on timestamp
                response.sort(key=lambda x: x['keys'][-1], reverse=True)

                for item in response:
                    data = item['data']['json']
                    email = data['email']
                    timestamp = item['keys'][-1]  # Get the timestamp from the last element of keys
                    status = item['keys'][1]
                    if email not in user_map or timestamp > user_map[email]['timestamp']:
                        user_map[email] = {
                            'timestamp': timestamp,
                            'user_data': data,
                            'status': status
                        }

                users_with_latest_info = [{
                    'email': key,
                    'timestamp': value['timestamp'],
                    'user_data': value['user_data'],
                    'status': value['status']
                } for key, value in user_map.items()]

                # print(users_with_latest_info)
                json_string = json.dumps(users_with_latest_info)
                json_string = json.loads(json_string)
                print(json_string)
                combined_list = []

                for item in json_string:
                    confirmed_status = item['user_data']
                    status = item['status']
                    # Decrypting the data fields after converting from base64
                    user_email = confirmed_status.get('email', '')
                    decrypted_company_info = decrypt_data(base64_to_bytes(confirmed_status.get('company_info', '')))
                    decrypted_street_address = decrypt_data(base64_to_bytes(confirmed_status.get('street_address', '')))
                    decrypted_business_details = decrypt_data(base64_to_bytes(confirmed_status.get('business_details', '')))
                    decrypted_state = decrypt_data(base64_to_bytes(confirmed_status.get('state', '')))
                    decrypted_city = decrypt_data(base64_to_bytes(confirmed_status.get('city', '')))
                    decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                    decrypted_zip_code = decrypt_data(base64_to_bytes(confirmed_status.get('zip_code', '')))
                    license_certification = confirmed_status.get('license_certification', '')
                    # Add decrypted data to the combined list
                    combined_list.append({
                        'email': user_email,
                        'company_info': decrypted_company_info,
                        'street_address': decrypted_street_address,
                        'business_details': decrypted_business_details,
                        'state': decrypted_state,
                        'city': decrypted_city,
                        'zip_code': decrypted_zip_code,
                        'license_certification' : license_certification,
                        'status': status
                    })

                #Assuming you want to print the combined list to see the output
                print("\n",combined_list)



                return render(request, "Master1.html",{'company_info': company_info,'email':email_rcvd,'orders': combined_list,'user_type':userType})
            else:
                print("error")  
    return HttpResponse("Working!")

def manage_sla(request):
    print('manage_sla user')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email',None)
        company_info = request.POST.get('company_info',None)

        #Manufacturer SLA
        response = rpc_connection.liststreamitems(manufacturer_SLA_stream)
        json_string_manufacturer = json.dumps(response)
        json_string_manufacturer = json.loads(json_string_manufacturer)
        if len(json_string_manufacturer)>0:
            Manufacturer_hash_sla = json_string_manufacturer[-1]['data']['json']["hash_sla"]
            print(Manufacturer_hash_sla)
        else:
            Manufacturer_hash_sla = 'None'
            print(Manufacturer_hash_sla)

        #Distributor SLA
        response = rpc_connection.liststreamitems(distributor_SLA_stream)
        json_string_distributor = json.dumps(response)
        json_string_distributor = json.loads(json_string_distributor)
        if len(json_string_distributor)>0:
            distributor_hash_sla = json_string_distributor[-1]['data']['json']["hash_sla"]
            print(distributor_hash_sla)
        else:
            distributor_hash_sla = 'None'
            print(distributor_hash_sla)

        #Pharmacy SLA
        response = rpc_connection.liststreamitems(pharmacy_SLA_stream)
        json_string_pharmacy = json.dumps(response)
        json_string_pharmacy = json.loads(json_string_pharmacy)
        if len(json_string_pharmacy)>0:
            pharmacy_hash_sla = json_string_pharmacy[-1]['data']['json']["hash_sla"]
            print(pharmacy_hash_sla)
        else:
            pharmacy_hash_sla = 'None'
            print(pharmacy_hash_sla)
    return render(request, "Manage_SLA.html",{'company_info': company_info,'email':email_rcvd,'Manufacturer_hash_sla':Manufacturer_hash_sla,'distributor_hash_sla':distributor_hash_sla,'pharmacy_hash_sla':pharmacy_hash_sla})

def manu_sla_submit(request):
    print('submiting Manufacturer user SLA')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email',None)
        company_info = request.POST.get('company_info',None)
        hash_sla = request.POST.get('hash_sla',None)
        timestamp_utc = datetime.datetime.utcnow().isoformat()
        print(email_rcvd)
        print(company_info)
        print(hash_sla)
        txid = rpc_connection.publish('{}'.format(manufacturer_SLA_stream), ['Manufacturer',
                                                                                   timestamp_utc  
                                                                             ],
                                                                             {'json': {
                                                                                 "hash_sla": hash_sla}})
         #Manufacturer SLA
        response = rpc_connection.liststreamitems(manufacturer_SLA_stream)
        json_string_manufacturer = json.dumps(response)
        json_string_manufacturer = json.loads(json_string_manufacturer)
        if len(json_string_manufacturer)>0:
            Manufacturer_hash_sla = json_string_manufacturer[-1]['data']['json']["hash_sla"]
            print(Manufacturer_hash_sla)
        else:
            Manufacturer_hash_sla = 'None'
            print(Manufacturer_hash_sla)

        #Distributor SLA
        response = rpc_connection.liststreamitems(distributor_SLA_stream)
        json_string_distributor = json.dumps(response)
        json_string_distributor = json.loads(json_string_distributor)
        if len(json_string_distributor)>0:
            distributor_hash_sla = json_string_distributor[-1]['data']['json']["hash_sla"]
            print(distributor_hash_sla)
        else:
            distributor_hash_sla = 'None'
            print(distributor_hash_sla)

        #Pharmacy SLA
        response = rpc_connection.liststreamitems(pharmacy_SLA_stream)
        json_string_pharmacy = json.dumps(response)
        json_string_pharmacy = json.loads(json_string_pharmacy)
        if len(json_string_pharmacy)>0:
            pharmacy_hash_sla = json_string_pharmacy[-1]['data']['json']["hash_sla"]
            print(pharmacy_hash_sla)
        else:
            pharmacy_hash_sla = 'None'
            print(pharmacy_hash_sla)
    return render(request, "Manage_SLA.html",{'company_info': company_info,'email':email_rcvd,'Manufacturer_hash_sla':Manufacturer_hash_sla,'distributor_hash_sla':distributor_hash_sla,'pharmacy_hash_sla':pharmacy_hash_sla})


def dist_sla_submit(request):
    print('submiting Distributor user SLA')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email',None)
        company_info = request.POST.get('company_info',None)
        hash_sla = request.POST.get('hash_sla',None)
        print(email_rcvd)
        print(company_info)
        print(hash_sla)
        timestamp_utc = datetime.datetime.utcnow().isoformat()
        txid = rpc_connection.publish('{}'.format(distributor_SLA_stream), ['Distributor',
                                                                                   timestamp_utc  
                                                                             ],
                                                                             {'json': {
                                                                                 "hash_sla": hash_sla}})
        
                 #Manufacturer SLA
        response = rpc_connection.liststreamitems(manufacturer_SLA_stream)
        json_string_manufacturer = json.dumps(response)
        json_string_manufacturer = json.loads(json_string_manufacturer)
        if len(json_string_manufacturer)>0:
            Manufacturer_hash_sla = json_string_manufacturer[-1]['data']['json']["hash_sla"]
            print(Manufacturer_hash_sla)
        else:
            Manufacturer_hash_sla = 'None'
            print(Manufacturer_hash_sla)

        #Distributor SLA
        response = rpc_connection.liststreamitems(distributor_SLA_stream)
        json_string_distributor = json.dumps(response)
        json_string_distributor = json.loads(json_string_distributor)
        if len(json_string_distributor)>0:
            distributor_hash_sla = json_string_distributor[-1]['data']['json']["hash_sla"]
            print(distributor_hash_sla)
        else:
            distributor_hash_sla = 'None'
            print(distributor_hash_sla)

        #Pharmacy SLA
        response = rpc_connection.liststreamitems(pharmacy_SLA_stream)
        json_string_pharmacy = json.dumps(response)
        json_string_pharmacy = json.loads(json_string_pharmacy)
        if len(json_string_pharmacy)>0:
            pharmacy_hash_sla = json_string_pharmacy[-1]['data']['json']["hash_sla"]
            print(pharmacy_hash_sla)
        else:
            pharmacy_hash_sla = 'None'
            print(pharmacy_hash_sla)
    return render(request, "Manage_SLA.html",{'company_info': company_info,'email':email_rcvd,'Manufacturer_hash_sla':Manufacturer_hash_sla,'distributor_hash_sla':distributor_hash_sla,'pharmacy_hash_sla':pharmacy_hash_sla})

def pharm_sla_submit(request):
    print('submiting Pharmacy user SLA')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email',None)
        company_info = request.POST.get('company_info',None)
        hash_sla = request.POST.get('hash_sla',None)
        print(email_rcvd)
        print(company_info)
        print(hash_sla)
        timestamp_utc = datetime.datetime.utcnow().isoformat()
        txid = rpc_connection.publish('{}'.format(pharmacy_SLA_stream), ['Pharmacy',
                                                                                   timestamp_utc  
                                                                             ],
                                                                             {'json': {
                                                                                 "hash_sla": hash_sla}})
 
                  #Manufacturer SLA
        response = rpc_connection.liststreamitems(manufacturer_SLA_stream)
        json_string_manufacturer = json.dumps(response)
        json_string_manufacturer = json.loads(json_string_manufacturer)
        if len(json_string_manufacturer)>0:
            Manufacturer_hash_sla = json_string_manufacturer[-1]['data']['json']["hash_sla"]
            print(Manufacturer_hash_sla)
        else:
            Manufacturer_hash_sla = 'None'
            print(Manufacturer_hash_sla)

        #Distributor SLA
        response = rpc_connection.liststreamitems(distributor_SLA_stream)
        json_string_distributor = json.dumps(response)
        json_string_distributor = json.loads(json_string_distributor)
        if len(json_string_distributor)>0:
            distributor_hash_sla = json_string_distributor[-1]['data']['json']["hash_sla"]
            print(distributor_hash_sla)
        else:
            distributor_hash_sla = 'None'
            print(distributor_hash_sla)

        #Pharmacy SLA
        response = rpc_connection.liststreamitems(pharmacy_SLA_stream)
        json_string_pharmacy = json.dumps(response)
        json_string_pharmacy = json.loads(json_string_pharmacy)
        if len(json_string_pharmacy)>0:
            pharmacy_hash_sla = json_string_pharmacy[-1]['data']['json']["hash_sla"]
            print(pharmacy_hash_sla)
        else:
            pharmacy_hash_sla = 'None'
            print(pharmacy_hash_sla)
    return render(request, "Manage_SLA.html",{'company_info': company_info,'email':email_rcvd,'Manufacturer_hash_sla':Manufacturer_hash_sla,'distributor_hash_sla':distributor_hash_sla,'pharmacy_hash_sla':pharmacy_hash_sla})

def otp_master(request):
    if request.method == 'POST':
        email = request.POST['email']
        print(email)
        return render(request, "signup-master1.html",{'email': email}) #if the email is not present then render this page
    
#### MANUFACTURER ####
def signup_manufacturer(request):
    print("signup-manufacturer check")
    return render(request, "email_check_manufacturer.html")

def email_check_manufacturer(request):
    print("email_check_manufacturer")
    x = rpc_connection.subscribe('{}'.format(users_manufacturer_stream))
    if request.method == 'POST':
        # print("method check")
        email = request.POST['email']
        response = rpc_connection.liststreamkeys(users_manufacturer_stream)
        json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
        json_string = json.loads(json_string) #Converts OrderedDict to JSON String
        # print(json_string)
        email_keys = [entry["key"] for entry in json_string]
        print(email_keys)
        otp = capitalize_alphabets(otp_generator(email))
        print(otp)
        for each_email in email_keys:
            if each_email==email:
                print("present")
                return render(request, "login_manufacturer.html",{'message': "User already registered, Please Log In!"}) #if the email is present prompt to login master page
        send_otp_via_email(email,otp)
        return render(request, "tokin_manufacturer.html",{'email': email, 'otp': otp}) #if the email is not present then render this page
    
def process_registration_manufacturer(request):
    print("process_registration_manufacturer")
    if request.method == 'POST':

        #Fetching the SLA published by the MASTER
        response = rpc_connection.liststreamitems(manufacturer_SLA_stream)
        data = json.dumps(response)
        json_load = json.loads(data)
        Manufacturer_hash_sla = json_load[-1]['data']['json']["hash_sla"]
        fetched_SLA = request.POST.get('hash_sla')
        email = request.POST.get('email')

        if fetched_SLA==Manufacturer_hash_sla:
            password = request.POST.get('password')
            timestamp_utc = datetime.datetime.utcnow().isoformat()
            # Hash the password
            hashed_password = make_password(password)
            # Encrypt other user details
            encrypted_company_info = encrypt_data(request.POST.get('company_info'))
            encrypted_street_address = encrypt_data(request.POST.get('street_address'))
            encrypted_business_details = encrypt_data(request.POST.get('business_details'))
            encrypted_state = encrypt_data(request.POST.get('state'))
            encrypted_city = encrypt_data(request.POST.get('city'))
            encrypted_zip_code = encrypt_data(request.POST.get('zip_code'))
            request_data = {
                "email": request.POST.get('email'),
                "company_info": bytes_to_base64(encrypted_company_info),
                "street_address": bytes_to_base64(encrypted_street_address),
                "business_details": bytes_to_base64(encrypted_business_details),
                "state": bytes_to_base64(encrypted_state),
                "city": bytes_to_base64(encrypted_city),
                "zip_code": bytes_to_base64(encrypted_zip_code),
                "password": hashed_password,
                "license_certification": request.POST.get('hash_sla') #Hash calculated from the front end don't need to encrypt it
            }
            data = json.dumps(request_data)
            data = json.loads(data)
            txid = rpc_connection.publish(users_manufacturer_stream, [email,'True',timestamp_utc], {'json' : data})
            if txid:
                send_welcome_email(email,request.POST.get('company_info'))
                return render(request, "login_manufacturer.html",{'message': "Please Log In using you credentials!"})
        else:
            return render(request, "signup-manufacturer1.html",{'email': email, 'message': "Wrong SLA, Please provide correct SLA file!"})
        
def login_manufacturer(request):
        return render(request, "login_manufacturer.html")

def login_check_manufacturer(request): #Implement Password authentication
    print('login_check_manufacturer')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        password_rcvd = request.POST.get('passw')
        result = rpc_connection.liststreamkeyitems(users_manufacturer_stream, email_rcvd)
        data = json.dumps(result)
        json_load = json.loads(data)
        #apply length check for json_load
        if(len(json_load)>0):
            email_frm_chain = json_load[-1]['keys'][0]
            isActive = json_load[-1]['keys'][1]
            passw_frm_chain = json_load[-1]['data']['json']['password']
            manufacturer_name = decrypt_data(base64_to_bytes(json_load[-1]['data']['json']['company_info']))
            comp_info = json_load[-1]['data']['json']['company_info']
            print(data)
            print(comp_info)
            print("Email from front end: ",email_rcvd)
            print("Email from stream: ",email_frm_chain)
            print("isActive: ",isActive)
            print(password_rcvd)
            print(passw_frm_chain)
            if isActive == 'True':
                if email_rcvd==email_frm_chain and check_password(password_rcvd, passw_frm_chain):
                    print(email_rcvd)
                    response = rpc_connection.liststreamqueryitems('{}'.format(manufacturer_orders_stream), {'keys': [email_rcvd]})
                    json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
                    json_string = json.loads(json_string) #Converts OrderedDict to JSON String

                    print(json_string)
                    combined_list = []

                    for item in json_string:
                        keys = item['keys']
                        traxid = item['txid']
                        confirmed_status = item['data']['json']['confirmed']
                        totalprice = item['data']['json']['totalprice']
                        modified_keys = keys[:9] + [traxid] + [totalprice] + keys[9:] + [confirmed_status]
                        combined_list.append(modified_keys)

                    print("\nCombined list\n")
                    print(combined_list)

                    # Sort the list based on the timestamp (second last index)
                    combined_list.sort(key=lambda x: x[-2], reverse=True)


                    #NOTE: This is the logic for finding the latest order based on timestamp
                    # Dictionary to store distinct orders based on combined elements (except the second last index) and timestamp
                    distinct_orders = {}

                    # Iterate through the sorted list and collect the latest orders based on combined elements and timestamp
                    for order in combined_list:
                        key = tuple(order[:9])  # Using elements at indices 0 to 7 as the key (excluding the second last index)
                        if key not in distinct_orders:
                            distinct_orders[key] = order

                    # Convert the dictionary to a list of lists
                    distinct_orders_list = list(distinct_orders.values())



                    # # Print the distinct orders
                    for order in distinct_orders_list:
                        print(order)

                    # Iterate over the combined_list
                    orders = []
                    for index, item in enumerate(distinct_orders_list):
                        # Create a dictionary for each element in the combined_list

                        orderPlaceOn = datetime.datetime.fromisoformat(item[8])
                        # orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d %H:%M:%S')
                        orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d')
                        order = {
                            "orderid":item[0],
                            "trxid": item[9],
                            "Distributor_name": item[1],
                            "Manufacturer_email": item[2],
                            "distributor_email": item[3],
                            "batchId": item[5],
                            "product_name": item[7],
                            "product_code": item[6],
                            "orderPlaceOn": str(orderPlaceOn),
                            "quantity": item[4],
                            "tot_price": item[10],
                            "confirmed": item[12],
                            "timestamp": item[8],
                        }
                        # Append the dictionary to the orders list
                        orders.append(order)

                    # Print the resulting list of dictionaries
                    print(orders)
                    return render(request, "manufacturer1.html",{'comp_info': comp_info,'email':email_rcvd, 'company_info': manufacturer_name,'orders': orders,'message':f'Welcome, {manufacturer_name}!'})
                else:
                    return render(request, "login_manufacturer.html", {'error_message': "Incorrect email or password."})
        
            elif isActive=='False':
                 return render(request, "login_manufacturer.html", {'error_message': "Account Deactivated!"})
        else:
                return render(request, "login_manufacturer.html", {'error_message': "Incorrect email or password."})

def manuorders(request): #If manufacturer is already logged in and move to other tab and back to orders it is for that
    print('manufacturer orders')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        comp_info = request.POST.get('company_info') #Name of the manufacturer
        print(email_rcvd)
        response = rpc_connection.liststreamqueryitems('{}'.format(manufacturer_orders_stream), {'keys': [email_rcvd]})
        json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
        json_string = json.loads(json_string) #Converts OrderedDict to JSON String
        
        print(json_string)
        combined_list = []

        for item in json_string:
            keys = item['keys']
            traxid = item['txid']
            confirmed_status = item['data']['json']['confirmed']
            totalprice = item['data']['json']['totalprice']
            modified_keys = keys[:9] + [traxid] + [totalprice] + keys[9:] + [confirmed_status]
            combined_list.append(modified_keys)

        print("\nCombined list\n")
        print(combined_list)

        # Sort the list based on the timestamp (second last index)
        combined_list.sort(key=lambda x: x[-2], reverse=True)

        
########################################################################################################            
        #NOTE: This is the logic for finding the latest order based on timestamp
        # Dictionary to store distinct orders based on combined elements (except the second last index) and timestamp
        distinct_orders = {}
        
        # Iterate through the sorted list and collect the latest orders based on combined elements and timestamp
        for order in combined_list:
            key = tuple(order[:9])  # Using elements at indices 0 to 7 as the key (excluding the second last index)
            if key not in distinct_orders:
                distinct_orders[key] = order
        
        # Convert the dictionary to a list of lists
        distinct_orders_list = list(distinct_orders.values())

########################################################################################################
        
        
        # # Print the distinct orders
        for order in distinct_orders_list:
            print(order)

        # Iterate over the combined_list
        orders = []
        for index, item in enumerate(distinct_orders_list):
            # Create a dictionary for each element in the combined_list

            orderPlaceOn = datetime.datetime.fromisoformat(item[8])
            # orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d %H:%M:%S')
            orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d')
            order = {
                "orderid":item[0],
                "trxid": item[9],
                "Distributor_name": item[1],
                "Manufacturer_email": item[2],
                "distributor_email": item[3],
                "batchId": item[5],
                "product_name": item[7],
                "product_code": item[6],
                "orderPlaceOn": str(orderPlaceOn),
                "quantity": item[4],
                "tot_price": item[10],
                "confirmed": item[12],
                "timestamp": item[8],
            }
            # Append the dictionary to the orders list
            orders.append(order)

        # Print the resulting list of dictionaries
        print(orders)
        return render(request, "manufacturer1.html",{'comp_info': comp_info,'email':email_rcvd, 'company_info': comp_info,'orders': orders})
    return HttpResponse("Working!")

def manuordercancel(request):
    print('\Cancel Orders From distributors\n')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        print('email',email_rcvd)
        Company_name = request.POST.get('company_info')
        print('Company_name',Company_name)

        selectedOrders = request.POST.get('selectedOrders', None)
        print(selectedOrders)
        selectedOrders = json.loads(selectedOrders)
        
        #Getting hash sla from the user stream
        response = rpc_connection.liststreamkeyitems(users_manufacturer_stream, email_rcvd)
        json_string = json.dumps(response)
        json_string = json.loads(json_string)
        print(json_string)
        fetched_sla = json_string[-1]['data']['json']['license_certification']
        print("Fetched SLA from SLA stream", fetched_sla)
        #Getting hash sla from the SLA stream
        response = rpc_connection.liststreamitems(manufacturer_SLA_stream)
        json_string_manufacturer = json.dumps(response)
        json_string_manufacturer = json.loads(json_string_manufacturer)
        if len(json_string_manufacturer)>0:
            Manufacturer_hash_sla = json_string_manufacturer[-1]['data']['json']["hash_sla"]
            print("Fetched SLA from USER stream",Manufacturer_hash_sla)
        else:
            Manufacturer_hash_sla = 'None'
            print(Manufacturer_hash_sla)
        

        if fetched_sla==Manufacturer_hash_sla:
            for i in range(len(selectedOrders)):
                order = selectedOrders[i]
                print('--------------------------------\n')
                print(order)
                print('--------------------------------\n')
                orderid = order['orderId']
                traxid = order['trxId']
                Distributor_name = order['distributor']
                Manufacturer_email = order['manufacturer_email']
                distributor_email = order['distributor_email']
                batchId = order['batchId']
                product_name = order['product_name']
                product_code = order['productCode']
                order_timestamp = order['timestamp']
                quantity_frm_order = order['quantity'] 
                totalprice = order['status'] 
                timestamp_utc = datetime.datetime.utcnow().isoformat()

                #for debugging
                print('Order_ID :', orderid)
                print('traxid :', traxid)
                print('Distributor_name :', Distributor_name)
                print('Manufacturer_email :',Manufacturer_email)
                print('distributor_email :',distributor_email)
                print('batchId :',batchId)
                print('product_code :', product_code)
                print('timestamp :',order_timestamp)
                print('quantity_frm_order :', quantity_frm_order)
                print('Total Price :', totalprice)
                timestamp_utc = datetime.datetime.utcnow().isoformat()
                txid = rpc_connection.publish('{}'.format(manufacturer_orders_stream), [orderid,Distributor_name,Manufacturer_email,distributor_email,quantity_frm_order, batchId, product_code, product_name,order_timestamp, timestamp_utc],{'json': {
                                                                                                                                                                               'confirmed': 'Cancelled',
                                                                                                                                                                               'totalprice' : totalprice
                                                                                                                                                                           }})
            response = rpc_connection.liststreamqueryitems('{}'.format(manufacturer_orders_stream), {'keys': [email_rcvd]})
            json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
            json_string = json.loads(json_string) #Converts OrderedDict to JSON String

            print(json_string)
            combined_list = []

            for item in json_string:
                keys = item['keys']
                traxid = item['txid']
                confirmed_status = item['data']['json']['confirmed']
                totalprice = item['data']['json']['totalprice']
                modified_keys = keys[:9] + [traxid] + [totalprice] + keys[9:] + [confirmed_status]
                combined_list.append(modified_keys)

            print("\nCombined list\n")
            print(combined_list)

            # Sort the list based on the timestamp (second last index)
            combined_list.sort(key=lambda x: x[-2], reverse=True)


            distinct_orders = {}

            # Iterate through the sorted list and collect the latest orders based on combined elements and timestamp
            for order in combined_list:
                key = tuple(order[:9])  # Using elements at indices 0 to 7 as the key (excluding the second last index)
                if key not in distinct_orders:
                    distinct_orders[key] = order

            # Convert the dictionary to a list of lists
            distinct_orders_list = list(distinct_orders.values())
            # # Print the distinct orders
            for order in distinct_orders_list:
                print(order)

            # Iterate over the combined_list
            orders = []
            for index, item in enumerate(distinct_orders_list):
                # Create a dictionary for each element in the combined_list

                orderPlaceOn = datetime.datetime.fromisoformat(item[8])
                # orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d %H:%M:%S')
                orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d')
                order = {
                    "orderid":item[0],
                    "trxid": item[9],
                    "Distributor_name": item[1],
                    "Manufacturer_email": item[2],
                    "distributor_email": item[3],
                    "batchId": item[5],
                    "product_name": item[7],
                    "product_code": item[6],
                    "orderPlaceOn": str(orderPlaceOn),
                    "quantity": item[4],
                    "tot_price": item[10],
                    "confirmed": item[12],
                    "timestamp": item[8],
                }
                # Append the dictionary to the orders list
                orders.append(order)

            # Print the resulting list of dictionaries
            print(orders)
            return render(request, "manufacturer1.html",{'comp_info': Company_name,'email':email_rcvd, 'company_info': Company_name,'orders': orders,'message': 'Order Request Cancelled!'})
        else:
             return render(request, "manuupdatesla.html",{'company_info': Company_name,'email':email_rcvd,'Manufacturer_hash_sla':fetched_sla,'message': "Wrong SLA, Please provide correct SLA file!"}) 
        
def manuorderconfirm(request):
    print('\nConfirm Orders From distributors\n')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        print('email',email_rcvd)
        Company_name = request.POST.get('company_info')
        print('Company_name',Company_name)


        selectedOrders = request.POST.get('selectedOrders', None)
        print(selectedOrders)
        selectedOrders = json.loads(selectedOrders)

        #Getting hash sla from the user stream
        response = rpc_connection.liststreamkeyitems(users_manufacturer_stream, email_rcvd)
        json_string = json.dumps(response)
        json_string = json.loads(json_string)
        print(json_string)
        fetched_sla = json_string[-1]['data']['json']['license_certification']
        print("Fetched SLA from SLA stream", fetched_sla)
        #Getting hash sla from the SLA stream
        response = rpc_connection.liststreamitems(manufacturer_SLA_stream)
        json_string_manufacturer = json.dumps(response)
        json_string_manufacturer = json.loads(json_string_manufacturer)
        if len(json_string_manufacturer)>0:
            Manufacturer_hash_sla = json_string_manufacturer[-1]['data']['json']["hash_sla"]
            print("Fetched SLA from USER stream",Manufacturer_hash_sla)
        else:
            Manufacturer_hash_sla = 'None'
            print(Manufacturer_hash_sla)
        

        if fetched_sla==Manufacturer_hash_sla:
            print('length of selected orders: ',len(selectedOrders))
            for i in range(len(selectedOrders)):
                order = selectedOrders[i]
                print('--------------------------------\n')
                print(order)
                print('--------------------------------\n')
                orderid = order['orderId']
                traxid = order['trxId']
                Distributor_name = order['distributor']
                Manufacturer_email = order['manufacturer_email']
                distributor_email = order['distributor_email']
                batchId = order['batchId']
                product_name = order['product_name']
                product_code = order['productCode']
                order_timestamp = order['timestamp']
                quantity_frm_order = order['quantity'] 
                totalprice = order['status'] 
                timestamp_utc = datetime.datetime.utcnow().isoformat()

                #for debugging
                print('Order_ID :', orderid)
                print('traxid :', traxid)
                print('Distributor_name :', Distributor_name)
                print('Manufacturer_email :',Manufacturer_email)
                print('distributor_email :',distributor_email)
                print('batchId :',batchId)
                print('product_code :', product_code)
                print('timestamp :',order_timestamp)
                print('quantity_frm_order :', quantity_frm_order)
                print('Total Price :', totalprice)
                timestamp_utc = datetime.datetime.utcnow().isoformat()

                #gettig data based on keys
                response =  rpc_connection.liststreamqueryitems('{}'.format(users_manufacturer_items_stream), {'keys': [Manufacturer_email, batchId, product_code, product_name]})        # Have a logic which fetches out items based on latest_timestamp
                response = json.dumps(response)
                response = json.loads(response)
                manufacturer_name = response[0]['data']['json']['manufacturer']
                print(len(response))
                #for fetching latest timestamp item
                if len(response) > 0:
                    product_map = {}  # Initialize a dictionary to store product data and timestamp for each unique key

                    # Sort the response list based on timestamp
                    response.sort(key=lambda x: x['keys'][-1], reverse=True)

                    for item in response:
                        data = item['data']['json']
                        key = (data['email'], data['products'][0]['product_code'], data['batchId'], data['products'][0]['product_name'])
                        timestamp = item['keys'][-1]  # Get the timestamp from the last element of keys

                        if key not in product_map or timestamp > product_map[key]['timestamp']:
                            product_map[key] = {
                                'product_data': data['products'][0],
                                'timestamp': timestamp,
                                'email': key[0],
                                'product_code': key[1],
                                'batchId': key[2],
                                'product_name': key[3]
                            }

                    products_with_timestamp = [{
                        'timestamp': value['timestamp'],
                        'email': value['email'],
                        'product_code': value['product_code'],
                        'batchId': value['batchId'],
                        'product_name': value['product_name'],
                        'product_data': value['product_data']
                    } for value in product_map.values()]

                    print(products_with_timestamp)

                    latest_item = products_with_timestamp[0]['product_data']
                    prev_quantity = decrypt_data(base64_to_bytes(products_with_timestamp[0]['product_data']['quantity_in_stock'])) #From the user_manufacturer_items_stream
                    new_quantity = int(prev_quantity)-int(quantity_frm_order)
                    total_amout = int(quantity_frm_order) * int(decrypt_data(base64_to_bytes(products_with_timestamp[0]['product_data']['unit_price'])))

                    print('new quantity :',new_quantity)
                    print('tot_amount :', total_amout)

                    latest_item['quantity_in_stock'] = bytes_to_base64(encrypt_data(str(new_quantity)))
                    print('Item after updating quantity: \n', latest_item)

                    #publishing into users_manufacturer_items_stream
                    txid = rpc_connection.publish('{}'.format(users_manufacturer_items_stream), [
                                                                                                Manufacturer_email,
                                                                                                 product_code,
                                                                                                 batchId,
                                                                                                 product_name,
                                                                                                 timestamp_utc
                                                                                                 ],
                                                                                                 {'json': {
                                                                                                     "manufacturer": manufacturer_name,
                                                                                                     "batchId": bytes_to_base64(encrypt_data(batchId)),
                                                                                                     "email": bytes_to_base64(encrypt_data(Manufacturer_email)),
                                                                                                     "products":[latest_item]
                                                                                                     }
                                                                                                     })#Add a timestamp for sub logic

                    #gettig data based on keys
                    response1 =  rpc_connection.liststreamqueryitems('{}'.format(users_distributor_items_stream), {'keys': [distributor_email,Manufacturer_email, product_code,batchId, product_name]})
                    response1 = json.dumps(response1)
                    response1 = json.loads(response1)
                    print("\nExisting Items in distributor Item stream\n",len(response1))
                    #If already that Item exists in the stream update it
                    if len(response1) > 0:
                        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                        print('\nIf item exist in distributor stream add it back with updated quantity\n')
                        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                        product_map = {}  # Initialize a dictionary to store product data and timestamp for each unique key
                        # Sort the response list based on timestamp
                        response1.sort(key=lambda x: x['keys'][-1], reverse=True)
                        for item in response1:
                            data = item['data']['json']
                            key = (data['email'], data['products'][0]['product_code'], data['batchId'], data['products'][0]['product_name'])
                            timestamp = item['keys'][-1]  # Get the timestamp from the last element of keys
                            if key not in product_map or timestamp > product_map[key]['timestamp']:
                                product_map[key] = {
                                    'product_data': data['products'][0],
                                    'timestamp': timestamp,
                                    'email': key[0],
                                    'product_code': key[1],
                                    'batchId': key[2],
                                    'product_name': key[3]
                                }
                        products_with_timestamp = [{
                            'timestamp': value['timestamp'],
                            'email': value['email'],
                            'product_code': value['product_code'],
                            'batchId': value['batchId'],
                            'product_name': value['product_name'],
                            'product_data': value['product_data']
                        } for value in product_map.values()]
                        print(products_with_timestamp)
                        latest_item = products_with_timestamp[0]['product_data']
                        prev_quantity = products_with_timestamp[0]['product_data']['quantity_in_stock'] #From the user_manufacturer_items_stream
                        new_quantity = int(decrypt_data(base64_to_bytes(prev_quantity)))+int(quantity_frm_order)
                        total_amout = int(quantity_frm_order) * int(decrypt_data(base64_to_bytes(products_with_timestamp[0]['product_data']['unit_price'])))
                        print('new quantity :',new_quantity)
                        print('tot_amount :', total_amout)
                        latest_item['quantity_in_stock'] = bytes_to_base64(encrypt_data(str(new_quantity)))
                        print('Item after updating quantity: \n', latest_item)

                        #publishing into users_distributor_items_stream
                        txid = rpc_connection.publish('{}'.format(users_distributor_items_stream), [distributor_email,
                                                                                                     Manufacturer_email,
                                                                                                     product_code,
                                                                                                     batchId,
                                                                                                     product_name,
                                                                                                     timestamp_utc
                                                                                                     ],
                                                                                                     {'json': {
                                                                                                         "manufacturer":manufacturer_name,
                                                                                                         "email": bytes_to_base64(encrypt_data(Manufacturer_email)),
                                                                                                         "batchId": bytes_to_base64(encrypt_data(batchId)),
                                                                                                         "products":[latest_item]
                                                                                                         }
                                                                                                         })#Add a timestamp for sub logic
                    else:
                        latest_item['quantity_in_stock'] = bytes_to_base64(encrypt_data(str(quantity_frm_order)))
                        # publishing into users_distributor_items_stream
                        txid = rpc_connection.publish('{}'.format(users_distributor_items_stream), [distributor_email,
                                                                                                     Manufacturer_email,
                                                                                                     product_code,
                                                                                                     batchId,
                                                                                                     product_name,
                                                                                                     timestamp_utc
                                                                                                     ],
                                                                                                     {'json': {
                                                                                                         "manufacturer":manufacturer_name,
                                                                                                         "email":bytes_to_base64(encrypt_data(Manufacturer_email)),
                                                                                                         "batchId":bytes_to_base64(encrypt_data(batchId)),
                                                                                                         "products":[latest_item]
                                                                                                         }
                                                                                                         })#Add a timestamp for sub logic
                    #publishing into the manufacturer_orders_stream telling that order is confimed
                    txid = rpc_connection.publish('{}'.format(manufacturer_orders_stream), [orderid,Distributor_name,Manufacturer_email,distributor_email,quantity_frm_order, batchId, product_code, product_name,order_timestamp, timestamp_utc],{'json': {'confirmed': 'Confirmed',
                                                                                                                                                                                   'confirmed': 'Confirmed',
                                                                                                                                                                                   'totalprice' : totalprice
                                                                                                                                                                                   }})

            response = rpc_connection.liststreamqueryitems('{}'.format(manufacturer_orders_stream), {'keys': [email_rcvd]})
            json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
            json_string = json.loads(json_string) #Converts OrderedDict to JSON String

            print(json_string)
            combined_list = []

            for item in json_string:
                keys = item['keys']
                traxid = item['txid']
                confirmed_status = item['data']['json']['confirmed']
                totalprice = item['data']['json']['totalprice']
                modified_keys = keys[:9] + [traxid] + [totalprice] + keys[9:] + [confirmed_status]
                combined_list.append(modified_keys)

            print("\nCombined list\n")
            print(combined_list)

            # Sort the list based on the timestamp (second last index)
            combined_list.sort(key=lambda x: x[-2], reverse=True)


            distinct_orders = {}

            # Iterate through the sorted list and collect the latest orders based on combined elements and timestamp
            for order in combined_list:
                key = tuple(order[:9])  # Using elements at indices 0 to 7 as the key (excluding the second last index)
                if key not in distinct_orders:
                    distinct_orders[key] = order

            # Convert the dictionary to a list of lists
            distinct_orders_list = list(distinct_orders.values())
            # # Print the distinct orders
            for order in distinct_orders_list:
                print(order)

            # Iterate over the combined_list
            orders = []
            for index, item in enumerate(distinct_orders_list):
                # Create a dictionary for each element in the combined_list

                orderPlaceOn = datetime.datetime.fromisoformat(item[8])
                # orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d %H:%M:%S')
                orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d')
                order = {
                    "orderid":item[0],
                    "trxid": item[9],
                    "Distributor_name": item[1],
                    "Manufacturer_email": item[2],
                    "distributor_email": item[3],
                    "batchId": item[5],
                    "product_name": item[7],
                    "product_code": item[6],
                    "orderPlaceOn": str(orderPlaceOn),
                    "quantity": item[4],
                    "tot_price": item[10],
                    "confirmed": item[12],
                    "timestamp": item[8],
                }
                # Append the dictionary to the orders list
                orders.append(order)

            # Print the resulting list of dictionaries
            print(orders)
            return render(request, "manufacturer1.html",{'comp_info': Company_name,'email':email_rcvd, 'company_info': Company_name,'orders': orders,'message': 'Order Request Confirmed!'})
        else:
            return render(request, "manuupdatesla.html",{'company_info': Company_name,'email':email_rcvd,'Manufacturer_hash_sla':fetched_sla,'message': "Wrong SLA, Please provide correct SLA file!"}) 
        
def viewmanuinvent(request):
    print('Viewing Manufacturer Inventory')
    if request.method == 'POST':
        manu_key = request.POST.get('email')
        company_info = request.POST.get('company_info')
        print(manu_key)
        print(company_info)
        response = rpc_connection.liststreamkeyitems('{}'.format(users_manufacturer_items_stream), '{}'.format(manu_key)) # Based on the manufacturer KEY the data is being fetched
        print(response)
        print(len(response))
        if len(response) > 0:
            product_map = {} # Initialize a dictionary to store product data and timestamp for each unique key

            for item in response:
                data = item['data']['json']
                key = (decrypt_data(base64_to_bytes(data['email'])),
                       decrypt_data(base64_to_bytes(data['products'][0]['product_code'])),
                       decrypt_data(base64_to_bytes(data['batchId'])),
                       decrypt_data(base64_to_bytes(data['products'][0]['product_name'])))
                timestamp = item['keys'][-1] # Get the timestamp from the last element of keys

                if key not in product_map or timestamp > product_map[key]['timestamp']:
                    product_map[key] = {
                        'product_data': {
                                        'product_name': decrypt_data(base64_to_bytes(data['products'][0]['product_name'])),
                                        'product_code': decrypt_data(base64_to_bytes(data['products'][0]['product_code'])),
                                        'description': decrypt_data(base64_to_bytes(data['products'][0]['description'])),
                                        'ingredients': decrypt_data(base64_to_bytes(data['products'][0]['ingredients'])),
                                        'dosage': decrypt_data(base64_to_bytes(data['products'][0]['dosage'])),
                                        'quantity_in_stock': decrypt_data(base64_to_bytes(data['products'][0]['quantity_in_stock'])),
                                        'unit_price': decrypt_data(base64_to_bytes(data['products'][0]['unit_price'])),
                                        'manufacturing_date': decrypt_data(base64_to_bytes(data['products'][0]['manufacturing_date'])),
                                        'expiry_date': decrypt_data(base64_to_bytes(data['products'][0]['expiry_date'])),
                                        'drugbank_id': decrypt_data(base64_to_bytes(data['products'][0]['drugbank_id'])),
                                        'form': decrypt_data(base64_to_bytes(data['products'][0]['form'])),
                                        'strength': decrypt_data(base64_to_bytes(data['products'][0]['strength'])),
                                        'route': decrypt_data(base64_to_bytes(data['products'][0]['route'])),
                                        'published_on': decrypt_data(base64_to_bytes(data['products'][0]['published_on']))},
                        'timestamp': timestamp,
                        'email': key[0],
                        'product_code': key[1],
                        'batchId': key[2],
                        'product_name': key[3]
                    }

            products_with_timestamp = [{
                'timestamp': value['timestamp'],
                'email': value['email'],
                'product_code': value['product_code'],
                'batchId': value['batchId'],
                'product_name': value['product_name'],
                'product_data': value['product_data']
            } for value in product_map.values()]

            print(products_with_timestamp)
            return render(request, 'viewmanuinventory1.html', {'products': products_with_timestamp, 'company_info':company_info, 'email':manu_key})
        else:
            return render(request, 'viewmanuinventory1.html', {'message': 'No products available' , 'company_info':company_info, 'email':manu_key})

def adddrugmenu(request):# Adding Drugs In Manufacturer Item Stream
    print('\nAdd Drug Manufacturer\n')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        print('email',email_rcvd)
        Company_name = request.POST.get('company_info')
        print('Company_name',Company_name)
        print("Email of the Manufacturer",email_rcvd)
        print("Name of the Manufacturer",Company_name)
    return render(request, "adddrug1.html",{'company_info': Company_name,'email':email_rcvd})

def adddrug(request): # Manufacturer Input
    print("\n\n")
    if request.method == 'POST':

        data = json.loads(request.POST.get('product_data'))
        print("----PRODCUCTS fetched from MANUFACTURER.html screen----")
        print(data)
        print("--------\n")
        timestamp_utc = datetime.datetime.utcnow().isoformat()
        manufacturer = data["manufacturer"] #key
        email = data["email"] #key
        batchid = data["batchId"] #key
         #product_code key
        print("----MANUFACTURER NAME----")
        print(manufacturer)
        print("----EMAIL----")
        print(email)
        print("--------\n")

        #Logic for verifiying hash sla

        #Getting hash sla from the user stream
        response = rpc_connection.liststreamkeyitems(users_manufacturer_stream, email)
        json_string = json.dumps(response)
        json_string = json.loads(json_string)
        print(json_string)
        fetched_sla = json_string[-1]['data']['json']['license_certification']
        print("Fetched SLA from SLA stream", fetched_sla)
        #Getting hash sla from the SLA stream
        response = rpc_connection.liststreamitems(manufacturer_SLA_stream)
        json_string_manufacturer = json.dumps(response)
        json_string_manufacturer = json.loads(json_string_manufacturer)
        if len(json_string_manufacturer)>0:
            Manufacturer_hash_sla = json_string_manufacturer[-1]['data']['json']["hash_sla"]
            print("Fetched SLA from USER stream",Manufacturer_hash_sla)
        else:
            Manufacturer_hash_sla = 'None'
            print(Manufacturer_hash_sla)

        if fetched_sla==Manufacturer_hash_sla:
            structured_json = {
                "products": []
            }

            for product in data["products"]:

                ingredients_str = ", ".join(product["ingredients"])

                structured_product = {
                    "product_name": bytes_to_base64(encrypt_data(product["product_name"])),
                    "product_code": bytes_to_base64(encrypt_data(product["product_code"])),
                    "description": bytes_to_base64(encrypt_data(product["description"])),
                    "ingredients": bytes_to_base64(encrypt_data(ingredients_str)),
                    "dosage": bytes_to_base64(encrypt_data(product["dosage"])),
                    "quantity_in_stock": bytes_to_base64(encrypt_data(str(product["quantity_in_stock"]))),
                    "unit_price": bytes_to_base64(encrypt_data(str(product["unit_price"]))),
                    "manufacturing_date": bytes_to_base64(encrypt_data(product["manufacturing_date"])),
                    "expiry_date": bytes_to_base64(encrypt_data(product["expiry_date"])),
                    "drugbank_id": bytes_to_base64(encrypt_data(product["drugbank_id"])),
                    "form": bytes_to_base64(encrypt_data(product["form"])),
                    "strength": bytes_to_base64(encrypt_data(product["strength"])),
                    "route": bytes_to_base64(encrypt_data(product["route"])),
                    "published_on": bytes_to_base64(encrypt_data(timestamp_utc))
                }
                structured_json["products"].append(structured_product)

            print(structured_json)
            structured_json = json.dumps(structured_json, indent=4) #Converts OrderedDict to JSON String
            structured_json = json.loads(structured_json) #Converts OrderedDict to JSON String


            response = rpc_connection.liststreamitems(users_manufacturer_items_stream)
            json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
            json_string = json.loads(json_string) #Converts OrderedDict to JSON String
            print('\n\nimp')
            # print(json_string)
            # Initialize an empty list to store keys
            all_keys = []

            #NOTE:
            #Convert the logic to not consider the last index of each key array
            #And adjust the check if for the keys
            # Loop through each dictionary in the list and extract keys

            for item in json_string:
                keys = item['keys'][:-1]  # Remove the last element (timestamp)
                all_keys.append(keys)

            print(all_keys)

            input_key = [email,product["product_code"],batchid,product["product_name"]]
            # Convert the list to a set for comparison
            input_key_set = set(input_key)

            # Check if any inner list in all_keys matches input_key
            for key_list in all_keys:
                if set(key_list) == input_key_set:
                    print("Match found:", key_list)
                    # return render(request, "manufacturer.html", {"error": "Failed to publish data to MultiChain"})
                    return render(request, "adddrug1.html", {'company_info': manufacturer,'email':email, 'message': 'This Item already exists!'})
                    #Output a pop up on the screen saying the item exists
                    #also return a page show the exact details of the existing item
            else:
                print("No match found")
                x = rpc_connection.subscribe('{}'.format(users_manufacturer_items_stream))
                #publish data on the chain
                txid = rpc_connection.publish('{}'.format(users_manufacturer_items_stream), [email,
                                                                                             product["product_code"],
                                                                                             batchid,
                                                                                             product["product_name"],
                                                                                             timestamp_utc
                                                                                             ],
                                                                                             {   'json': {
                                                                                                 'manufacturer': bytes_to_base64(encrypt_data(manufacturer)),
                                                                                                 'batchId': bytes_to_base64(encrypt_data(batchid)),
                                                                                                 'email': bytes_to_base64(encrypt_data(email)),
                                                                                                 'products': list(structured_json['products'])}})#Add a timestamp for sub logic

                qr_data = {
                    "manufacturer_email": email,
                    "Product_code": product["product_code"],
                    "Batch_id": batchid,
                    "product_name": product["product_name"] 
                }

                #Generating QR CODE for the product
                generate_qr_code(email,product["product_code"],batchid,product["product_name"] )

                return render(request, "adddrug1.html", {'company_info': manufacturer,'email':email, 'message': 'Drug Added'})
        else:
            return render(request, "manuupdatesla.html",{'company_info': manufacturer,'email':email,'Manufacturer_hash_sla':fetched_sla,'message': "Wrong SLA, Please provide correct SLA file!"}) 


def manuupdatesla(request):# Adding Drugs In Manufacturer Item Stream
    print('manage_sla user')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email',None)
        company_info = request.POST.get('company_info',None)

        #Manufacturer SLA
        #Getting hash sla from the user stream
        response = rpc_connection.liststreamkeyitems(users_manufacturer_stream, email_rcvd)
        json_string_manufacturer = json.dumps(response)
        json_string_manufacturer = json.loads(json_string_manufacturer)
        print(json_string_manufacturer)
        if len(json_string_manufacturer)>0:
            Manufacturer_hash_sla = json_string_manufacturer[-1]['data']['json']["license_certification"]
            print(Manufacturer_hash_sla)
        else:
            Manufacturer_hash_sla = 'None'
            print(Manufacturer_hash_sla)

    return render(request, "manuupdatesla.html",{'company_info': company_info,'email':email_rcvd,'Manufacturer_hash_sla':Manufacturer_hash_sla}) 

def manu_sla_upload(request):
    print('submiting Manufacturer user SLA')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email',None)
        company_info = request.POST.get('company_info',None)
        hash_sla = request.POST.get('hash_sla',None)
        timestamp_utc = datetime.datetime.utcnow().isoformat()
        print(email_rcvd)
        print(company_info)
        print(hash_sla)

        #Getting the particular user for which sla will be updated
        response = rpc_connection.liststreamkeyitems(users_manufacturer_stream, email_rcvd)
        json_string_manufacturer = json.dumps(response)
        json_string_manufacturer = json.loads(json_string_manufacturer)
        #Logic for updating the SLA
        if len(json_string_manufacturer)>0:
            json_data = json_string_manufacturer[-1]
            json_data['data']['json']["license_certification"] = hash_sla
            data = json_data['data']['json']
            keys = json_data['keys']
            print("keys: ",keys)
            Manufacturer_hash_sla = json_string_manufacturer[-1]['data']['json']["license_certification"]
            txid = rpc_connection.publish('{}'.format(users_manufacturer_stream), keys,
                                                                             {'json': data })
            print(Manufacturer_hash_sla)
        else:
            Manufacturer_hash_sla = 'None'
            print(Manufacturer_hash_sla)

    return render(request, "manuupdatesla.html",{'company_info': company_info,'email':email_rcvd,'Manufacturer_hash_sla':Manufacturer_hash_sla})

def otp_manufacturer(request):
    if request.method == 'POST':
        email = request.POST['email']
        print(email)
        return render(request, "signup-manufacturer1.html",{'email': email}) #if the email is not present then render this page
    


#### DISTRIBUTOR #####
def signup_distributor(request):
    print("signup-distributor check")
    return render(request, "email_check_distributor.html")

def email_check_distributor(request):
    print("email_check_distributor")
    x = rpc_connection.subscribe('{}'.format(users_distributor_stream))
    if request.method == 'POST':
        # print("method check")
        email = request.POST['email']
        response = rpc_connection.liststreamkeys(users_distributor_stream)
        json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
        json_string = json.loads(json_string) #Converts OrderedDict to JSON String
        # print(json_string)
        email_keys = [entry["key"] for entry in json_string]
        print(email_keys)
        otp = capitalize_alphabets(otp_generator(email))
        print(otp)
        for each_email in email_keys:
            if each_email==email:
                print("present")
                return render(request, "login_distributor.html",{'message': "User already registered, Please Log In!"}) #if the email is present prompt to login master page
        send_otp_via_email(email,otp)
        return render(request, "tokin_distributor.html",{'email': email, 'otp': otp}) #if the email is not present then render this page

def process_registration_distributor(request):
    print("process_registration_distributor")
    if request.method == 'POST':

        #Fetching the SLA published by the MASTER
        response = rpc_connection.liststreamitems(distributor_SLA_stream)
        data = json.dumps(response)
        json_load = json.loads(data)
        distributor_hash_sla = json_load[-1]['data']['json']["hash_sla"]
        fetched_SLA = request.POST.get('hash_sla')
        email = request.POST.get('email')

        if fetched_SLA==distributor_hash_sla:
            email = request.POST.get('email')
            password = request.POST.get('password')
            timestamp_utc = datetime.datetime.utcnow().isoformat()
            # Hash the password
            hashed_password = make_password(password)
            # Encrypt other user details
            encrypted_company_info = encrypt_data(request.POST.get('company_info'))
            encrypted_street_address = encrypt_data(request.POST.get('street_address'))
            encrypted_business_details = encrypt_data(request.POST.get('business_details'))
            encrypted_state = encrypt_data(request.POST.get('state'))
            encrypted_city = encrypt_data(request.POST.get('city'))
            encrypted_zip_code = encrypt_data(request.POST.get('zip_code'))
            request_data = {
                "email": request.POST.get('email'),
                "company_info": bytes_to_base64(encrypted_company_info),
                "street_address": bytes_to_base64(encrypted_street_address),
                "business_details": bytes_to_base64(encrypted_business_details),
                "state": bytes_to_base64(encrypted_state),
                "city": bytes_to_base64(encrypted_city),
                "zip_code": bytes_to_base64(encrypted_zip_code),
                "password": hashed_password,
                "license_certification": request.POST.get('hash_sla') #Hash calculated from the front end don't need to encrypt it
            }
            data = json.dumps(request_data)
            data = json.loads(data)
            txid = rpc_connection.publish(users_distributor_stream, [email,'True',timestamp_utc], {'json' : data})
            if txid:
                send_welcome_email(email,request.POST.get('company_info'))
                return render(request, "login_distributor.html",{'message': "Please Log In using you credentials!"})
        else:
            return render(request, "signup-distributor1.html",{'email': email, 'message': "Wrong SLA, Please provide correct SLA file!"})
        
def login_distributor(request):
        return render(request, "login_distributor.html")

def login_check_distributor(request):
    print('login_check_distributor')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        password_rcvd = request.POST.get('passw')
        result = rpc_connection.liststreamkeyitems(users_distributor_stream, email_rcvd)
        data = json.dumps(result)
        json_load = json.loads(data)
        if(len(json_load)>0):
            email_frm_chain = json_load[-1]['keys'][0]
            isActive = json_load[-1]['keys'][1]
            passw_frm_chain = json_load[-1]['data']['json']['password']
            manufacturer_name = decrypt_data(base64_to_bytes(json_load[0]['data']['json']['company_info']))
            comp_info = json_load[-1]['data']['json']['company_info']
            print(data)
            print(comp_info)
            print("Email from front end: ",email_rcvd)
            print("Email from stream: ",email_frm_chain)
            print(password_rcvd)
            print(passw_frm_chain)
            if isActive == 'True':
                if email_rcvd==email_frm_chain and check_password(password_rcvd, passw_frm_chain):
                    response = rpc_connection.liststreamqueryitems('{}'.format(distributor_orders_stream), {'keys': [email_rcvd]})
                    json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
                    json_string = json.loads(json_string) #Converts OrderedDict to JSON String

                    print(json_string)
                    combined_list = []

                    for item in json_string:
                        keys = item['keys']
                        traxid = item['txid']
                        confirmed_status = item['data']['json']['confirmed']
                        totalprice = item['data']['json']['totalprice']
                        modified_keys = keys[:9] + [traxid] + [totalprice] + keys[9:] + [confirmed_status]
                        combined_list.append(modified_keys)

                    print("\nCombined list\n")
                    print(combined_list)

                    # Sort the list based on the timestamp (second last index)
                    combined_list.sort(key=lambda x: x[-2], reverse=True)


                    #NOTE: This is the logic for finding the latest order based on timestamp
                    # Dictionary to store distinct orders based on combined elements (except the second last index) and timestamp
                    distinct_orders = {}

                    # Iterate through the sorted list and collect the latest orders based on combined elements and timestamp
                    for order in combined_list:
                        key = tuple(order[:9])  # Using elements at indices 0 to 7 as the key (excluding the second last index)
                        if key not in distinct_orders:
                            distinct_orders[key] = order

                    # Convert the dictionary to a list of lists
                    distinct_orders_list = list(distinct_orders.values())



                    # # Print the distinct orders
                    for order in distinct_orders_list:
                        print(order)

                    # Iterate over the combined_list
                    orders = []
                    for index, item in enumerate(distinct_orders_list):
                        # Create a dictionary for each element in the combined_list

                        orderPlaceOn = datetime.datetime.fromisoformat(item[11])
                        # orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d %H:%M:%S')
                        orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d')
                        order = {
                            "orderid":item[0],
                            "trxid": item[9],
                            "Distributor_name": item[1],
                            "Manufacturer_email": item[2],
                            "distributor_email": item[3],
                            "batchId": item[6],
                            "product_name": item[8],
                            "product_code": item[7],
                            "orderPlaceOn": str(orderPlaceOn),
                            "quantity": item[5],
                            "tot_price": item[10],
                            "confirmed": item[13],
                            "timestamp": item[12],
                            "manu_email": item[4],
                        }
                        # Append the dictionary to the orders list
                        orders.append(order)

                    # Print the resulting list of dictionaries
                    print(orders)

                    # return render(request, "distributor_orders.html",{'orders': orders})

                    return render(request, "Distributor1.html", {'comp_info': comp_info,'email':email_rcvd, 'company_info': manufacturer_name,'orders': orders,'message':f'Welcome, {manufacturer_name}!'})
                else:
                    return render(request, "login_distributor.html", {'error_message': "Incorrect email or password."})
            elif isActive=='False':
                 return render(request, "login_distributor.html", {'error_message': "Account Deactivated!"})
        else:
                return render(request, "login_distributor.html", {'error_message': "Incorrect email or password."})    

def viewdistinvent(request):
    print('\nViewing Distributor Inventory')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        company_info = request.POST.get('company_info')
        print('Distributor Email: ',email_rcvd)
        print('company_info: ',company_info)
        response = rpc_connection.liststreamkeyitems('{}'.format(users_distributor_items_stream), '{}'.format(email_rcvd)) # Based on the manufacturer KEY the data is being fetched
        print(len(response))
        if len(response) > 0:
            product_map = {} # Initialize a dictionary to store product data and timestamp for each unique key

            for item in response:
                data = item['data']['json']
                key = (decrypt_data(base64_to_bytes(data['email'])),
                       decrypt_data(base64_to_bytes(data['products'][0]['product_code'])),
                       decrypt_data(base64_to_bytes(data['batchId'])),
                       decrypt_data(base64_to_bytes(data['products'][0]['product_name'])))
                timestamp = item['keys'][-1] # Get the timestamp from the last element of keys

                if key not in product_map or timestamp > product_map[key]['timestamp']:
                    product_map[key] = {
                            'product_data': {
                                        'product_name': decrypt_data(base64_to_bytes(data['products'][0]['product_name'])),
                                        'product_code': decrypt_data(base64_to_bytes(data['products'][0]['product_code'])),
                                        'description': decrypt_data(base64_to_bytes(data['products'][0]['description'])),
                                        'ingredients': decrypt_data(base64_to_bytes(data['products'][0]['ingredients'])),
                                        'dosage': decrypt_data(base64_to_bytes(data['products'][0]['dosage'])),
                                        'quantity_in_stock': decrypt_data(base64_to_bytes(data['products'][0]['quantity_in_stock'])),
                                        'unit_price': decrypt_data(base64_to_bytes(data['products'][0]['unit_price'])),
                                        'manufacturing_date': decrypt_data(base64_to_bytes(data['products'][0]['manufacturing_date'])),
                                        'expiry_date': decrypt_data(base64_to_bytes(data['products'][0]['expiry_date'])),
                                        'drugbank_id': decrypt_data(base64_to_bytes(data['products'][0]['drugbank_id'])),
                                        'form': decrypt_data(base64_to_bytes(data['products'][0]['form'])),
                                        'strength': decrypt_data(base64_to_bytes(data['products'][0]['strength'])),
                                        'route': decrypt_data(base64_to_bytes(data['products'][0]['route'])),
                                        'published_on': decrypt_data(base64_to_bytes(data['products'][0]['published_on']))},
                        'timestamp': timestamp,
                        'email': key[0],
                        'product_code': key[1],
                        'batchId': key[2],
                        'product_name': key[3]
                    }

            products_with_timestamp = [{
                'timestamp': value['timestamp'],
                'email': value['email'],
                'product_code': value['product_code'],
                'batchId': value['batchId'],
                'product_name': value['product_name'],
                'product_data': value['product_data']
            } for value in product_map.values()]

            print(products_with_timestamp)
            return render(request, 'viewdistinventory1.html', {'products': products_with_timestamp , 'email': email_rcvd, 'company_info': company_info})
        else:
            return render(request, 'viewdistinventory1.html', {'message': 'No products available', 'email': email_rcvd, 'company_info': company_info})

def distorderprod(request):
    print("\nOrdering Products from Manufacturer")
    if request.method == 'POST':
        email_dist = request.POST.get('email',None)
        company_info = request.POST.get('company_info',None)
        print('\nDistributor Email: ',email_dist)
        print('\nCompany Info: ',company_info)
        
        #for fetching out the name of the Distributor name
        result = rpc_connection.liststreamkeyitems(users_distributor_stream, email_dist)
        data = json.dumps(result)
        json_load = json.loads(data)
        comp_info = json_load[0]['data']['json']['company_info'] 
        
        # Now fetch the distributor names and their emails(keys), only names will be shown in the drop down of the distributor.html screen        
        response = rpc_connection.liststreamitems(users_manufacturer_stream)
        user_map = {}  # Initialize a dictionary to store user data based on the latest timestamp
        # Sort the response list based on timestamp
        response.sort(key=lambda x: x['keys'][-1], reverse=True)
        for item in response:
            data = item['data']['json']
            email = data['email']
            timestamp = item['keys'][-1]  # Get the timestamp from the last element of keys
            status = item['keys'][1]
            if email not in user_map or timestamp > user_map[email]['timestamp']:
                user_map[email] = {
                    'timestamp': timestamp,
                    'user_data': data,
                    'status': status
                }

        users_with_latest_info = [{
            'email': key,
            'timestamp': value['timestamp'],
            'user_data': value['user_data'],
            'status': value['status']
        } for key, value in user_map.items()]

        # print(users_with_latest_info)
        json_string = json.dumps(users_with_latest_info)
        json_load = json.loads(json_string)
        print(json_string)        

        keys_company_info = {}
        for item in json_load:
            keys_company_info[item["email"]] = decrypt_data(base64_to_bytes(item['user_data']['company_info']))
        print("\nkeys_company_info:\n",keys_company_info)
        return render(request, "distorderprod1.html", {'keys_company_info': keys_company_info,'email': email_dist, 'company_info' : company_info})

def manuproducts(request):
    email_dist = request.GET.get('email', None)
    selected_manufacturer = request.GET.get('manufacturer', None) # Manufacturer name being passed from Distributor.html
    comp_info = request.GET.get('comp_info', None) # Manufacturer name being passed from Distributor.html

    #Getting hash sla from the user stream
    response = rpc_connection.liststreamkeyitems(users_distributor_stream, email_dist)
    json_string = json.dumps(response)
    json_string = json.loads(json_string)
    print(json_string)
    fetched_sla = json_string[-1]['data']['json']['license_certification']
    print("Fetched SLA from SLA stream", fetched_sla)
    #Getting hash sla from the SLA stream
    response = rpc_connection.liststreamitems(distributor_SLA_stream)
    json_string_distributor = json.dumps(response)
    json_string_distributor = json.loads(json_string_distributor)
    if len(json_string_distributor)>0:
        Distributor_hash_sla = json_string_distributor[-1]['data']['json']["hash_sla"]
        print("Fetched SLA from USER stream",Distributor_hash_sla)
    else:
        Distributor_hash_sla = 'None'
        print(Distributor_hash_sla)

    if fetched_sla==Distributor_hash_sla:
        print(selected_manufacturer)
        print("Distributor emails: ",email_dist)
        print("comp_info :" ,comp_info) 
        x = rpc_connection.subscribe('{}'.format(users_manufacturer_items_stream)) # Subscribing
        response = rpc_connection.liststreamkeyitems('{}'.format(users_manufacturer_items_stream), '{}'.format(selected_manufacturer)) # Based on the manufacturer KEY the data is being fetched
        # Have a logic which fetches out items based on latest_timestamp
        print(len(response))
        if len(response) > 0:
            product_map = {} # Initialize a dictionary to store product data and timestamp for each unique key

            for item in response:
                data = item['data']['json']
                key = (decrypt_data(base64_to_bytes(data['email'])),
                       decrypt_data(base64_to_bytes(data['products'][0]['product_code'])),
                       decrypt_data(base64_to_bytes(data['batchId'])),
                       decrypt_data(base64_to_bytes(data['products'][0]['product_name'])))
                timestamp = item['keys'][-1] # Get the timestamp from the last element of keys

                if key not in product_map or timestamp > product_map[key]['timestamp']:
                    product_map[key] = {
                        'product_data': {
                                            'product_name': decrypt_data(base64_to_bytes(data['products'][0]['product_name'])),
                                            'product_code': decrypt_data(base64_to_bytes(data['products'][0]['product_code'])),
                                            'description': decrypt_data(base64_to_bytes(data['products'][0]['description'])),
                                            'ingredients': list(decrypt_data(base64_to_bytes(data['products'][0]['ingredients']))),
                                            'dosage': decrypt_data(base64_to_bytes(data['products'][0]['dosage'])),
                                            'quantity_in_stock': decrypt_data(base64_to_bytes(data['products'][0]['quantity_in_stock'])),
                                            'unit_price': decrypt_data(base64_to_bytes(data['products'][0]['unit_price'])),
                                            'manufacturing_date': decrypt_data(base64_to_bytes(data['products'][0]['manufacturing_date'])),
                                            'expiry_date': decrypt_data(base64_to_bytes(data['products'][0]['expiry_date'])),
                                            'drugbank_id': decrypt_data(base64_to_bytes(data['products'][0]['drugbank_id'])),
                                            'form': decrypt_data(base64_to_bytes(data['products'][0]['form'])),
                                            'strength': decrypt_data(base64_to_bytes(data['products'][0]['strength'])),
                                            'route': decrypt_data(base64_to_bytes(data['products'][0]['route'])),
                                            'published_on': decrypt_data(base64_to_bytes(data['products'][0]['published_on']))},
                        'timestamp': timestamp,
                        'email': key[0],
                        'product_code': key[1],
                        'batchId': key[2],
                        'product_name': key[3]
                    }

            products_with_timestamp = [{
                'timestamp': value['timestamp'],
                'email': value['email'],
                'product_code': value['product_code'],
                'batchId': value['batchId'],
                'product_name': value['product_name'],
                'product_data': value['product_data']
            } for value in product_map.values()]

            print(products_with_timestamp)
            return render(request, 'manuproducts1.html', {'products': products_with_timestamp, 'manufacturer': selected_manufacturer, 'email': email_dist, 'company_info': comp_info})
        else:
            return render(request, 'manuproducts1.html', {'message': 'No products available!', 'manufacturer': selected_manufacturer, 'email': email_dist, 'company_info': comp_info})
    else:
         return render(request, "distupdatesla.html",{'company_info': comp_info,'email':email_dist,'distributor_hash_sla':fetched_sla,'message': "Wrong SLA, Please provide correct SLA file!"}) 
@csrf_protect
def distcheckout(request):
    print("\n\ncheckout\n\n")
    if request.method == 'POST':
        # Retrieve the cartItems data from the POST request
        cart_items_json = request.POST.get('cartItems', None)
        manufacturer = request.POST.get('manufacturer', None)
        email_dist = request.POST.get('email', None)
        comp_info = request.POST.get('company_info', None)
        print(email_dist)
        print(comp_info)
        if cart_items_json and manufacturer:
            # Parse the JSON data
            cart_items = json.loads(cart_items_json)

            # Do something with the cart_items data (e.g., save to the database, process the order, etc.)
            # For example, you can print it for demonstration purposes
            print(cart_items)

            # You can also render a template or return an appropriate HTTP response
            return render(request, 'distcheckout.html', {'cart_items': cart_items, 'manufacturer' : manufacturer, 'email_dist': email_dist, 'comp_info':comp_info})
    
@csrf_protect
def distreqorder(request):
    print('\npublish')
    if request.method == 'POST':
        # Retrieve the cartItems data from the POST request
        cart_items_json = request.POST.get('cartItems', None)
        email_dist = request.POST.get('email_dist', None)
        comp_info = request.POST.get('comp_info', None)
        print(email_dist)
        print(comp_info)
        #NOTE:
        # Please implement the flow in which whenever the distributor places an order,
        # it first goes to the order confirmation page of the MANUFACTURER.
        # Once manufacturer confirms the order, the quantity of the medicine is minused from the MANUFACTURER stream
        # and new Item is published in the MANUFACTURER stream.

        # Retrieve the manufacturer name from checkout.html from the POST request
        manufacturer = request.POST.get('manufacturer', None)
        print("\n\n----MANUFACTURER NAME----")
        print(manufacturer)
        print("--------\n")
        
        #Also getting the manufacturer name becuase it's a key in the MANUFACTURER 
        if cart_items_json:
            print("----CART ITEMS from frontEND----")
            cart_items = json.loads(cart_items_json)
            print(len(cart_items))
            print("--------\n")
            for cart_item in cart_items:
                manu_email = cart_item['manu_email']
                batchId = cart_item['batchId']
                productCode = cart_item['productCode']
                productName = cart_item['productName']
                timestamp = cart_item['timestamp']
                quantity = cart_item['quantity']
                totalprice = cart_item['totalprice']
                print(manu_email)
                print(batchId)
                print(productCode)
                print(productName)
                print(timestamp)
                print(quantity)
                print(totalprice)

                timestamp_utc = datetime.datetime.utcnow().isoformat()

                # Fetching the products from the MANUFACTURER STREAM to update their quantity
                prev_products = rpc_connection.liststreamqueryitems('{}'.format(users_manufacturer_items_stream), {'keys': [manu_email, batchId, productCode, productName, timestamp]})
                prev_products_str = json.dumps(prev_products, indent=4)  # Converts OrderedDict to JSON String
                json_load = json.loads(prev_products_str)
                prev_products = json_load[0]['data']['json']
                print("----PRODUCTS fetched from MANUFACTURER stream----")
                print(prev_products_str)

                # Logic for subtracting the quantity of the products from the order stream
                for item_b in prev_products['products']:
                    if cart_item['productCode'] == item_b['product_code']:
                        item_b['quantity_in_stock'] -= cart_item['quantity']

                updated_items_str = json.dumps(prev_products, indent=4)  # Converts OrderedDict to JSON String
                updated_items = json.loads(updated_items_str)
                print("----Updated PRODUCTS quantity published to MANUFACTURER STREAM----")
                print(updated_items_str)

                time_of_order=timestamp_utc

                # Generate OrderId based on various attributes
                base_string = f"{email_dist}{manu_email}{quantity}{batchId}{productCode}{productName}{timestamp_utc}"
                hashed = hashlib.sha256(base_string.encode()).hexdigest()
                orderid = ''.join(random.choices(hashed, k=6))
                
                # Publishes the ordered products into the manufacturer_orders_stream stream accessed by Manufacturer
                # before publishing have SLA Logic
                txid = rpc_connection.publish('{}'.format(manufacturer_orders_stream), [orderid,comp_info,manu_email,email_dist,str(quantity), batchId, productCode, productName, time_of_order, timestamp_utc],{'json': {
                                                                                                                                                                           'confirmed': '',
                                                                                                                                                                           'totalprice': str(totalprice)
                                                                                                                                                                      }
                                                                                                                                                                    })
            #render a template or return an appropriate HTTP response, still to be decided
            print(txid) 
            response = rpc_connection.liststreamqueryitems('{}'.format(manufacturer_orders_stream), {'keys': [email_dist]})
            json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
            json_string = json.loads(json_string) #Converts OrderedDict to JSON String

            print(json_string)
            combined_list = []
            for item in json_string:
                keys = item['keys']
                traxid = item['txid']
                confirmed_status = item['data']['json']['confirmed']
                totalprice = item['data']['json']['totalprice']
                modified_keys = keys[:9] + [traxid] + [totalprice] + keys[9:] + [confirmed_status]
                combined_list.append(modified_keys)
            print("\nCombined list\n")
            print(combined_list)
            # Sort the list based on the timestamp (second last index)
            combined_list.sort(key=lambda x: x[-2], reverse=True)

            #######################################################################################################            
            #NOTE: This is the logic for finding the latest order based on timestamp
            # Dictionary to store distinct orders based on combined elements (except the second last index) and timestamp
            distinct_orders = {}

            # Iterate through the sorted list and collect the latest orders based on combined elements and timestamp
            for order in combined_list:
                key = tuple(order[:9])  # Using elements at indices 0 to 7 as the key (excluding the second last index)
                if key not in distinct_orders:
                    distinct_orders[key] = order

            # Convert the dictionary to a list of lists
            distinct_orders_list = list(distinct_orders.values())
            #######################################################################################################


            # # Print the distinct orders
            for order in distinct_orders_list:
                print(order)
            # Iterate over the combined_list
            orders = []
            for index, item in enumerate(distinct_orders_list):
                # Create a dictionary for each element in the combined_list
                orderPlaceOn = datetime.datetime.fromisoformat(item[8])
                # orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d %H:%M:%S')
                orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d')
                order = {
                    "orderid":item[0],
                    "trxid": item[9],
                    "Distributor_name": item[1],
                    "Manufacturer_email": item[2],
                    "distributor_email": item[3],
                    "batchId": item[5],
                    "product_name": item[7],
                    "product_code": item[6],
                    "orderPlaceOn": str(orderPlaceOn),
                    "quantity": item[4],
                    "tot_price": item[10],
                    "confirmed": item[12],
                    "timestamp": item[8],
                }
                # Append the dictionary to the orders list
                orders.append(order)
            # Print the resulting list of dictionaries
            print(orders)
            # return render(request, "distributor_orders.html",{'orders': orders})

            return render(request, "distorderstatus1.html", {'comp_info': comp_info,'email':email_dist, 'company_info': comp_info,'orders': orders})
            

def pharmorders(request):
    print('\nOrders From Pharmacies\n')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        print("Email :",email_rcvd)
        comp_info = request.POST.get('company_info') #Name of the Distributor
        print("comany_info:",comp_info)
        response = rpc_connection.liststreamqueryitems('{}'.format(distributor_orders_stream), {'keys': [email_rcvd]})
        json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
        json_string = json.loads(json_string) #Converts OrderedDict to JSON String
        
        print(json_string)
        combined_list = []
        for item in json_string:
            keys = item['keys']
            traxid = item['txid']
            confirmed_status = item['data']['json']['confirmed']
            totalprice = item['data']['json']['totalprice']
            modified_keys = keys[:9] + [traxid] + [totalprice] + keys[9:] + [confirmed_status]
            combined_list.append(modified_keys)
        print("\nCombined list\n")
        print(combined_list)
        # Sort the list based on the timestamp (second last index)
        combined_list.sort(key=lambda x: x[-2], reverse=True)
        
        #######################################################################################################            
        #NOTE: This is the logic for finding the latest order based on timestamp
        # Dictionary to store distinct orders based on combined elements (except the second last index) and timestamp
        distinct_orders = {}
        
        # Iterate through the sorted list and collect the latest orders based on combined elements and timestamp
        for order in combined_list:
            key = tuple(order[:9])  # Using elements at indices 0 to 7 as the key (excluding the second last index)
            if key not in distinct_orders:
                distinct_orders[key] = order
        
        # Convert the dictionary to a list of lists
        distinct_orders_list = list(distinct_orders.values())
        #######################################################################################################
        
        
        # # Print the distinct orders
        for order in distinct_orders_list:
            print(order)
        # Iterate over the combined_list
        orders = []
        for index, item in enumerate(distinct_orders_list):
            # Create a dictionary for each element in the combined_list
            orderPlaceOn = datetime.datetime.fromisoformat(item[11])
            # orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d %H:%M:%S')
            orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d')
            order = {
                "orderid":item[0],
                "trxid": item[9],
                "Distributor_name": item[1],
                "Manufacturer_email": item[2],
                "distributor_email": item[3],
                "batchId": item[6],
                "product_name": item[8],
                "product_code": item[7],
                "orderPlaceOn": str(orderPlaceOn),
                "quantity": item[5],
                "tot_price": item[10],
                "confirmed": item[13],
                "timestamp": item[12],
                "manu_email": item[4],
            }
            # Append the dictionary to the orders list
            orders.append(order)
        # Print the resulting list of dictionaries
        print(orders)
        # return render(request, "distributor_orders.html",{'orders': orders})

        return render(request, "Distributor1.html", {'comp_info': comp_info,'email':email_rcvd, 'company_info': comp_info,'orders': orders})

def distordercancel(request):
    print('\Cancel Orders From Pharmacies\n')
    if request.method == 'POST':
        email_dist = request.POST.get('email', None)
        comp_info = request.POST.get('company_info', None) # Manufacturer name being passed from Distributor.html
        print("1 ",email_dist)
        print("2 ",comp_info)

        #Getting hash sla from the user stream
        response = rpc_connection.liststreamkeyitems(users_distributor_stream, email_dist)
        json_string = json.dumps(response)
        json_string = json.loads(json_string)
        print(json_string)
        fetched_sla = json_string[-1]['data']['json']['license_certification']
        print("Fetched SLA from SLA stream", fetched_sla)
        #Getting hash sla from the SLA stream
        response = rpc_connection.liststreamitems(distributor_SLA_stream)
        json_string_distributor = json.dumps(response)
        json_string_distributor = json.loads(json_string_distributor)
        if len(json_string_distributor)>0:
            Distributor_hash_sla = json_string_distributor[-1]['data']['json']["hash_sla"]
            print("Fetched SLA from USER stream",Distributor_hash_sla)
        else:
            Distributor_hash_sla = 'None'
            print(Distributor_hash_sla)

        if fetched_sla==Distributor_hash_sla:
            selectedOrders = request.POST.get('selectedOrders', None)
            print(selectedOrders)
            selectedOrders = json.loads(selectedOrders)
            for i in range(len(selectedOrders)):
                order = selectedOrders[i]
                print('--------------------------------\n')
                print(order)
                print('--------------------------------\n')
                orderid = order['orderId']
                traxid = order['trxId']
                Pharmacy_name = order['distributor']
                distributor_email = order['manufacturer_email']
                pharmacy_email = order['distributor_email']
                batchId = order['batchId']
                product_name = order['product_name']
                product_code = order['productCode']
                order_timestamp = order['timestamp']
                quantity_frm_order = order['quantity'] 
                totalprice = order['status']  
                timestamp_utc = datetime.datetime.utcnow().isoformat()

                #for debugging
                print('Order_ID :', orderid)
                print('traxid :', traxid)
                print('Pharmacy_name :', Pharmacy_name)
                print('distributor_email :',distributor_email)
                print('pharmacy_email :',pharmacy_email)
                print('batchId :',batchId)
                print('product_code :', product_code)
                print('timestamp :',order_timestamp)
                print('quantity_frm_order :', quantity_frm_order)
                print('Total Price :', totalprice)
                timestamp_utc = datetime.datetime.utcnow().isoformat()

                Manufacturer_email =  rpc_connection.liststreamqueryitems('{}'.format(distributor_orders_stream), {'keys': [orderid, Pharmacy_name, distributor_email, pharmacy_email, batchId, product_code, product_name,order_timestamp]})        # Have a logic which fetches out items based on latest_timestamp
                Manufacturer_email = json.dumps(Manufacturer_email)
                Manufacturer_email = json.loads(Manufacturer_email)
                print(Manufacturer_email)
                Manufacturer_email = Manufacturer_email[0]['keys'][4]

                txid = rpc_connection.publish('{}'.format(distributor_orders_stream), [orderid, Pharmacy_name,distributor_email,pharmacy_email,Manufacturer_email,quantity_frm_order, batchId, product_code, product_name, order_timestamp, timestamp_utc],{'json': {
                                                                                                                                                                                   'confirmed': 'Cancelled',
                                                                                                                                                                                   'totalprice' : totalprice
                                                                                                                                                                                   }})
            response = rpc_connection.liststreamqueryitems('{}'.format(distributor_orders_stream), {'keys': [email_dist]})
            json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
            json_string = json.loads(json_string) #Converts OrderedDict to JSON String

            print(json_string)
            combined_list = []
            for item in json_string:
                keys = item['keys']
                traxid = item['txid']
                confirmed_status = item['data']['json']['confirmed']
                totalprice = item['data']['json']['totalprice']
                modified_keys = keys[:9] + [traxid] + [totalprice] + keys[9:] + [confirmed_status]
                combined_list.append(modified_keys)
            print("\nCombined list\n")
            print(combined_list)
            # Sort the list based on the timestamp (second last index)
            combined_list.sort(key=lambda x: x[-2], reverse=True)

            #######################################################################################################            
            #NOTE: This is the logic for finding the latest order based on timestamp
            # Dictionary to store distinct orders based on combined elements (except the second last index) and timestamp
            distinct_orders = {}

            # Iterate through the sorted list and collect the latest orders based on combined elements and timestamp
            for order in combined_list:
                key = tuple(order[:9])  # Using elements at indices 0 to 7 as the key (excluding the second last index)
                if key not in distinct_orders:
                    distinct_orders[key] = order

            # Convert the dictionary to a list of lists
            distinct_orders_list = list(distinct_orders.values())
            #######################################################################################################


            # # Print the distinct orders
            for order in distinct_orders_list:
                print(order)
            # Iterate over the combined_list
            orders = []
            for index, item in enumerate(distinct_orders_list):
                # Create a dictionary for each element in the combined_list
                orderPlaceOn = datetime.datetime.fromisoformat(item[11])
                # orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d %H:%M:%S')
                orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d')
                order = {
                    "orderid":item[0],
                    "trxid": item[9],
                    "Distributor_name": item[1],
                    "Manufacturer_email": item[2],
                    "distributor_email": item[3],
                    "batchId": item[6],
                    "product_name": item[8],
                    "product_code": item[7],
                    "orderPlaceOn": str(orderPlaceOn),
                    "quantity": item[5],
                    "tot_price": item[10],
                    "confirmed": item[13],
                    "timestamp": item[12],
                    "manu_email": item[4],
                }
                # Append the dictionary to the orders list
                orders.append(order)
            # Print the resulting list of dictionaries
            print(orders)
            # return render(request, "distributor_orders.html",{'orders': orders})

            return render(request, "Distributor1.html", {'comp_info': comp_info,'email':email_dist, 'company_info': comp_info,'orders': orders,'message': 'Order Request Cancelled!'})
        else:
            return render(request, "distupdatesla.html",{'company_info': comp_info,'email':email_dist,'distributor_hash_sla':fetched_sla,'message': "Wrong SLA, Please provide correct SLA file!"}) 
    
def distorderconfirm(request):
    print('\nConfirm Orders From Pharmacies\n')
    if request.method == 'POST':
        email_dist = request.POST.get('email', None)
        comp_info = request.POST.get('company_info', None) # Manufacturer name being passed from Distributor.html

        #Getting hash sla from the user stream
        response = rpc_connection.liststreamkeyitems(users_distributor_stream, email_dist)
        json_string = json.dumps(response)
        json_string = json.loads(json_string)
        print(json_string)
        fetched_sla = json_string[-1]['data']['json']['license_certification']
        print("Fetched SLA from SLA stream", fetched_sla)
        #Getting hash sla from the SLA stream
        response = rpc_connection.liststreamitems(distributor_SLA_stream)
        json_string_distributor = json.dumps(response)
        json_string_distributor = json.loads(json_string_distributor)
        if len(json_string_distributor)>0:
            Distributor_hash_sla = json_string_distributor[-1]['data']['json']["hash_sla"]
            print("Fetched SLA from USER stream",Distributor_hash_sla)
        else:
            Distributor_hash_sla = 'None'
            print(Distributor_hash_sla)

        if fetched_sla==Distributor_hash_sla:
            selectedOrders = request.POST.get('selectedOrders', None)
            print(selectedOrders)

            #Getting item from selectedOrders
            selectedOrders = json.loads(selectedOrders)
            print('length of selected orders: ',len(selectedOrders))
            for i in range(len(selectedOrders)):
                order = selectedOrders[i]
                print('--------------------------------\n')
                print(order)
                print('--------------------------------\n')
                orderid = order['orderId']
                traxid = order['trxId']
                Pharmacy_name = order['distributor']
                distributor_email = order['manufacturer_email']
                pharmacy_email = order['distributor_email']
                batchId = order['batchId']
                product_name = order['product_name']
                product_code = order['productCode']
                order_timestamp = order['timestamp']
                quantity_frm_order = order['quantity'] 
                totalprice = order['status']  
                timestamp_utc = datetime.datetime.utcnow().isoformat()

                #for debugging
                print('Order_ID :', orderid)
                print('traxid :', traxid)
                print('Pharmacy_name :', Pharmacy_name)
                print('distributor_email :',distributor_email)
                print('pharmacy_email :',pharmacy_email)
                print('batchId :',batchId)
                print('product_code :', product_code)
                print('timestamp :',order_timestamp)
                print('quantity_frm_order :', quantity_frm_order)
                print('Total Price :', totalprice)
                timestamp_utc = datetime.datetime.utcnow().isoformat()

                Manufacturer_email =  rpc_connection.liststreamqueryitems('{}'.format(distributor_orders_stream), {'keys': [orderid, Pharmacy_name, distributor_email, pharmacy_email, batchId, product_code, product_name,order_timestamp]})        # Have a logic which fetches out items based on latest_timestamp
                Manufacturer_email = json.dumps(Manufacturer_email)
                Manufacturer_email = json.loads(Manufacturer_email)
                print(Manufacturer_email)
                Manufacturer_email = Manufacturer_email[0]['keys'][4]
                print("Manufacturer_email : ",Manufacturer_email)
                #gettig data based on keys
                response =  rpc_connection.liststreamqueryitems('{}'.format(users_distributor_items_stream), {'keys': [distributor_email,Manufacturer_email, batchId, product_code, product_name]})        # Have a logic which fetches out items based on latest_timestamp
                response = json.dumps(response)
                response = json.loads(response)
                manufacturer_name = response[0]['data']['json']['manufacturer']
                print(manufacturer_name)
                print(len(response))

                #for fetching latest timestamp item
                if len(response) > 0:
                    product_map = {}  # Initialize a dictionary to store product data and timestamp for each unique key

                    # Sort the response list based on timestamp
                    response.sort(key=lambda x: x['keys'][-1], reverse=True)

                    for item in response:
                        data = item['data']['json']
                        key = (data['email'], data['products'][0]['product_code'], data['batchId'], data['products'][0]['product_name'])
                        timestamp = item['keys'][-1]  # Get the timestamp from the last element of keys

                        if key not in product_map or timestamp > product_map[key]['timestamp']:
                            product_map[key] = {
                                'product_data': data['products'][0],
                                'timestamp': timestamp,
                                'email': key[0],
                                'product_code': key[1],
                                'batchId': key[2],
                                'product_name': key[3]
                            }

                    products_with_timestamp = [{
                        'timestamp': value['timestamp'],
                        'email': value['email'],
                        'product_code': value['product_code'],
                        'batchId': value['batchId'],
                        'product_name': value['product_name'],
                        'product_data': value['product_data']
                    } for value in product_map.values()]

                    print(products_with_timestamp)

                    latest_item = products_with_timestamp[0]['product_data']
                    prev_quantity = decrypt_data(base64_to_bytes(products_with_timestamp[0]['product_data']['quantity_in_stock'])) #From the user_manufacturer_items_stream
                    new_quantity = int(prev_quantity)-int(quantity_frm_order)
                    total_amout = int(quantity_frm_order) * int(decrypt_data(base64_to_bytes(products_with_timestamp[0]['product_data']['unit_price'])))

                    print('new quantity :',new_quantity)
                    print('tot_amount :', total_amout)

                    latest_item['quantity_in_stock'] = bytes_to_base64(encrypt_data(str(new_quantity)))
                    print('Item after updating quantity: \n', latest_item)

                    # #publishing into users_manufacturer_items_stream
                    txid = rpc_connection.publish('{}'.format(users_distributor_items_stream), [distributor_email,
                                                                                                Manufacturer_email,
                                                                                                 product_code,
                                                                                                 batchId,
                                                                                                 product_name,
                                                                                                 timestamp_utc
                                                                                                 ],
                                                                                                 {'json': {
                                                                                                     "manufacturer":manufacturer_name,
                                                                                                     "batchId": bytes_to_base64(encrypt_data(batchId)),
                                                                                                     "email": bytes_to_base64(encrypt_data(Manufacturer_email)),
                                                                                                     "products":[latest_item]
                                                                                                     }
                                                                                                     })#Add a timestamp for sub logic
                    #gettig data based on keys
                    response1 =  rpc_connection.liststreamqueryitems('{}'.format(users_pharmacy_items_stream), {'keys': [pharmacy_email,distributor_email,Manufacturer_email, product_code,batchId, product_name]})
                    response1 = json.dumps(response1)
                    response1 = json.loads(response1)
                    print("\nExisting Items in distributor Item stream\n",len(response1))
                    #If already that Item exists in the stream update it
                    if len(response1) > 0:
                        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                        print('\nIf item exist in distributor stream add it back with updated quantity\n')
                        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                        product_map = {}  # Initialize a dictionary to store product data and timestamp for each unique key
                        # Sort the response list based on timestamp
                        response1.sort(key=lambda x: x['keys'][-1], reverse=True)
                        for item in response1:
                            data = item['data']['json']
                            key = (data['email'], data['products'][0]['product_code'], data['batchId'], data['products'][0]['product_name'])
                            timestamp = item['keys'][-1]  # Get the timestamp from the last element of keys
                            if key not in product_map or timestamp > product_map[key]['timestamp']:
                                product_map[key] = {
                                    'product_data': data['products'][0],
                                    'timestamp': timestamp,
                                    'email': key[0],
                                    'product_code': key[1],
                                    'batchId': key[2],
                                    'product_name': key[3]
                                }
                        products_with_timestamp = [{
                            'timestamp': value['timestamp'],
                            'email': value['email'],
                            'product_code': value['product_code'],
                            'batchId': value['batchId'],
                            'product_name': value['product_name'],
                            'product_data': value['product_data']
                        } for value in product_map.values()]
                        print(products_with_timestamp)
                        latest_item = products_with_timestamp[0]['product_data']
                        prev_quantity = products_with_timestamp[0]['product_data']['quantity_in_stock'] #From the user_manufacturer_items_stream
                        new_quantity = int(decrypt_data(base64_to_bytes(prev_quantity)))+int(quantity_frm_order)
                        total_amout = int(quantity_frm_order) * int(decrypt_data(base64_to_bytes(products_with_timestamp[0]['product_data']['unit_price'])))
                        print('new quantity :',new_quantity)
                        print('tot_amount :', total_amout)
                        latest_item['quantity_in_stock'] = bytes_to_base64(encrypt_data(str(new_quantity)))
                        print('Item after updating quantity: \n', latest_item)

                        #publishing into users_distributor_items_stream
                        txid = rpc_connection.publish('{}'.format(users_pharmacy_items_stream), [    pharmacy_email,
                                                                                                     distributor_email,
                                                                                                     Manufacturer_email,
                                                                                                     product_code,
                                                                                                     batchId,
                                                                                                     product_name,
                                                                                                     timestamp_utc
                                                                                                     ],
                                                                                                     {'json': {
                                                                                                         "manufacturer":manufacturer_name,
                                                                                                         "email": bytes_to_base64(encrypt_data(Manufacturer_email)),
                                                                                                         "batchId": bytes_to_base64(encrypt_data(batchId)),
                                                                                                         "products":[latest_item]
                                                                                                         }
                                                                                                         })#Add a timestamp for sub logic
                    else:
                        latest_item['quantity_in_stock'] = bytes_to_base64(encrypt_data(str(quantity_frm_order)))
                        #publishing into users_distributor_items_stream
                        txid = rpc_connection.publish('{}'.format(users_pharmacy_items_stream), [   pharmacy_email,
                                                                                                     distributor_email,
                                                                                                     Manufacturer_email,
                                                                                                     product_code,
                                                                                                     batchId,
                                                                                                     product_name,
                                                                                                     timestamp_utc
                                                                                                     ],
                                                                                                     {'json': {
                                                                                                         "manufacturer":manufacturer_name,
                                                                                                         "email": bytes_to_base64(encrypt_data(Manufacturer_email)),
                                                                                                         "batchId": bytes_to_base64(encrypt_data(batchId)),
                                                                                                         "products":[latest_item]
                                                                                                         }
                                                                                                         })#Add a timestamp for sub logic
                    #publishing into the manufacturer_orders_stream telling that order is confimed
                    txid = rpc_connection.publish('{}'.format(distributor_orders_stream), [orderid, Pharmacy_name,distributor_email,pharmacy_email,Manufacturer_email,quantity_frm_order, batchId, product_code, product_name, order_timestamp, timestamp_utc],{'json': {
                                                                                                                                                                                   'confirmed': 'Confirmed',
                                                                                                                                                                                   'totalprice' : totalprice
                                                                                                                                                                                   }})
            response = rpc_connection.liststreamqueryitems('{}'.format(distributor_orders_stream), {'keys': [email_dist]})
            json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
            json_string = json.loads(json_string) #Converts OrderedDict to JSON String

            print(json_string)
            combined_list = []
            for item in json_string:
                keys = item['keys']
                traxid = item['txid']
                confirmed_status = item['data']['json']['confirmed']
                totalprice = item['data']['json']['totalprice']
                modified_keys = keys[:9] + [traxid] + [totalprice] + keys[9:] + [confirmed_status]
                combined_list.append(modified_keys)
            print("\nCombined list\n")
            print(combined_list)
            # Sort the list based on the timestamp (second last index)
            combined_list.sort(key=lambda x: x[-2], reverse=True)

            #######################################################################################################            
            #NOTE: This is the logic for finding the latest order based on timestamp
            # Dictionary to store distinct orders based on combined elements (except the second last index) and timestamp
            distinct_orders = {}

            # Iterate through the sorted list and collect the latest orders based on combined elements and timestamp
            for order in combined_list:
                key = tuple(order[:9])  # Using elements at indices 0 to 7 as the key (excluding the second last index)
                if key not in distinct_orders:
                    distinct_orders[key] = order

            # Convert the dictionary to a list of lists
            distinct_orders_list = list(distinct_orders.values())
            #######################################################################################################


            # # Print the distinct orders
            for order in distinct_orders_list:
                print(order)
            # Iterate over the combined_list
            orders = []
            for index, item in enumerate(distinct_orders_list):
                # Create a dictionary for each element in the combined_list
                orderPlaceOn = datetime.datetime.fromisoformat(item[11])
                # orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d %H:%M:%S')
                orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d')
                order = {
                    "orderid":item[0],
                    "trxid": item[9],
                    "Distributor_name": item[1],
                    "Manufacturer_email": item[2],
                    "distributor_email": item[3],
                    "batchId": item[6],
                    "product_name": item[8],
                    "product_code": item[7],
                    "orderPlaceOn": str(orderPlaceOn),
                    "quantity": item[5],
                    "tot_price": item[10],
                    "confirmed": item[13],
                    "timestamp": item[12],
                    "manu_email": item[4],
                }
                # Append the dictionary to the orders list
                orders.append(order)
            # Print the resulting list of dictionaries
            print(orders)
            # return render(request, "distributor_orders.html",{'orders': orders})

            return render(request, "Distributor1.html", {'comp_info': comp_info,'email':email_dist, 'company_info': comp_info,'orders': orders,'message': 'Order Request Confirmed!'})
        else:
            return render(request, "distupdatesla.html",{'company_info': comp_info,'email':email_dist,'distributor_hash_sla':fetched_sla,'message': "Wrong SLA, Please provide correct SLA file!"}) 
        
def distorderstatus(request):
    print('\nOrders Statuses for distributor\n')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        print("Email :",email_rcvd)
        comp_info = request.POST.get('company_info') #Name of the Distributor
        print("comany_info:",comp_info)
        response = rpc_connection.liststreamqueryitems('{}'.format(manufacturer_orders_stream), {'keys': [email_rcvd]})
        json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
        json_string = json.loads(json_string) #Converts OrderedDict to JSON String
        
        print(json_string)
        combined_list = []
        for item in json_string:
            keys = item['keys']
            traxid = item['txid']
            confirmed_status = item['data']['json']['confirmed']
            totalprice = item['data']['json']['totalprice']
            modified_keys = keys[:9] + [traxid] + [totalprice] + keys[9:] + [confirmed_status]
            combined_list.append(modified_keys)
        print("\nCombined list\n")
        print(combined_list)
        # Sort the list based on the timestamp (second last index)
        combined_list.sort(key=lambda x: x[-2], reverse=True)
        
        #######################################################################################################            
        #NOTE: This is the logic for finding the latest order based on timestamp
        # Dictionary to store distinct orders based on combined elements (except the second last index) and timestamp
        distinct_orders = {}
        
        # Iterate through the sorted list and collect the latest orders based on combined elements and timestamp
        for order in combined_list:
            key = tuple(order[:9])  # Using elements at indices 0 to 7 as the key (excluding the second last index)
            if key not in distinct_orders:
                distinct_orders[key] = order
        
        # Convert the dictionary to a list of lists
        distinct_orders_list = list(distinct_orders.values())
        #######################################################################################################
        
        
        # # Print the distinct orders
        for order in distinct_orders_list:
            print(order)
        # Iterate over the combined_list
        orders = []
        for index, item in enumerate(distinct_orders_list):
            # Create a dictionary for each element in the combined_list
            orderPlaceOn = datetime.datetime.fromisoformat(item[8])
            # orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d %H:%M:%S')
            orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d')
            order = {
                "orderid":item[0],
                "trxid": item[9],
                "Distributor_name": item[1],
                "Manufacturer_email": item[2],
                "distributor_email": item[3],
                "batchId": item[5],
                "product_name": item[7],
                "product_code": item[6],
                "orderPlaceOn": str(orderPlaceOn),
                "quantity": item[4],
                "tot_price": item[10],
                "confirmed": item[12],
                "timestamp": item[8],
            }
            # Append the dictionary to the orders list
            orders.append(order)
        # Print the resulting list of dictionaries
        print(orders)
        # return render(request, "distributor_orders.html",{'orders': orders})

        return render(request, "distorderstatus1.html", {'comp_info': comp_info,'email':email_rcvd, 'company_info': comp_info,'orders': orders})

def distupdatesla(request):# Adding Drugs In Manufacturer Item Stream
    print('manage_sla user')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email',None)
        company_info = request.POST.get('company_info',None)

        #Distributor SLA
        #Getting hash sla from the user stream
        response = rpc_connection.liststreamkeyitems(users_distributor_stream,email_rcvd)
        json_string_distributor = json.dumps(response)
        json_string_distributor = json.loads(json_string_distributor)
        print(json_string_distributor)
        if len(json_string_distributor)>0:
            distributor_hash_sla = json_string_distributor[-1]['data']['json']["license_certification"]
            print(distributor_hash_sla)
        else:
            distributor_hash_sla = 'None'
            print(distributor_hash_sla)

    return render(request, "distupdatesla.html",{'company_info': company_info,'email':email_rcvd,'distributor_hash_sla':distributor_hash_sla}) 

def dist_sla_upload(request):
    print('submiting Manufacturer user SLA')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email',None)
        company_info = request.POST.get('company_info',None)
        hash_sla = request.POST.get('hash_sla',None)
        timestamp_utc = datetime.datetime.utcnow().isoformat()
        print(email_rcvd)
        print(company_info)
        print(hash_sla)

        #Getting the particular user for which sla will be updated
        response = rpc_connection.liststreamkeyitems(users_distributor_stream, email_rcvd)
        json_string_distributor = json.dumps(response)
        json_string_distributor = json.loads(json_string_distributor)
        #Logic for updating the SLA
        if len(json_string_distributor)>0:
            json_data = json_string_distributor[-1]
            json_data['data']['json']["license_certification"] = hash_sla
            data = json_data['data']['json']
            keys = json_data['keys']
            print("keys: ",keys)
            Distributor_hash_sla = json_string_distributor[-1]['data']['json']["license_certification"]
            txid = rpc_connection.publish('{}'.format(users_distributor_stream), keys,
                                                                             {'json': data })
            print(Distributor_hash_sla)
        else:
            Distributor_hash_sla = 'None'
            print(Distributor_hash_sla)

    return render(request, "distupdatesla.html",{'company_info': company_info,'email':email_rcvd,'distributor_hash_sla':Distributor_hash_sla})

def otp_distributor(request):
    if request.method == 'POST':
        email = request.POST['email']
        print(email)
        return render(request, "signup-distributor1.html",{'email': email}) #if the email is not present then render this page
    

#### PHARMACY #####
def signup_pharmacy(request):
    print("Signup-pharmacy check")
    return render(request, "email_check_pharmacy.html")

def email_check_pharmacy(request):
    print("email_check_pharmacy")
    x = rpc_connection.subscribe('{}'.format(users_pharmacy_stream))
    if request.method == 'POST':
        # print("method check")
        email = request.POST['email']
        response = rpc_connection.liststreamkeys(users_pharmacy_stream)
        json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
        json_string = json.loads(json_string) #Converts OrderedDict to JSON String
        # print(json_string)
        email_keys = [entry["key"] for entry in json_string]
        print(email_keys)
        otp = capitalize_alphabets(otp_generator(email))
        print(otp)
        for each_email in email_keys:
            if each_email==email:
                print("present")
                return render(request, "login_pharmacy.html",{'message': "User already registered, Please Log In!"}) #if the email is present prompt to login master page
        send_otp_via_email(email,otp)
        return render(request, "tokin_pharmacy.html",{'email': email, 'otp': otp}) #if the email is not present then render this page

def process_registration_pharmacy(request):
    print("process_registration_pharmacy")
    if request.method == 'POST':

        #Fetching the SLA published by the MASTER
        response = rpc_connection.liststreamitems(pharmacy_SLA_stream)
        data = json.dumps(response)
        json_load = json.loads(data)
        pharmacy_hash_sla = json_load[-1]['data']['json']["hash_sla"]
        fetched_SLA = request.POST.get('hash_sla')
        email = request.POST.get('email')

        if fetched_SLA==pharmacy_hash_sla:
            email = request.POST.get('email')
            password = request.POST.get('password')
            timestamp_utc = datetime.datetime.utcnow().isoformat()
            # Hash the password
            hashed_password = make_password(password)
            # Encrypt other user details
            encrypted_company_info = encrypt_data(request.POST.get('company_info'))
            encrypted_street_address = encrypt_data(request.POST.get('street_address'))
            encrypted_business_details = encrypt_data(request.POST.get('business_details'))
            encrypted_state = encrypt_data(request.POST.get('state'))
            encrypted_city = encrypt_data(request.POST.get('city'))
            encrypted_zip_code = encrypt_data(request.POST.get('zip_code'))
            request_data = {
                "email": request.POST.get('email'),
                "company_info": bytes_to_base64(encrypted_company_info),
                "street_address": bytes_to_base64(encrypted_street_address),
                "business_details": bytes_to_base64(encrypted_business_details),
                "state": bytes_to_base64(encrypted_state),
                "city": bytes_to_base64(encrypted_city),
                "zip_code": bytes_to_base64(encrypted_zip_code),
                "password": hashed_password,
                "license_certification": request.POST.get('hash_sla') #Hash calculated from the front end don't need to encrypt it
            }
            data = json.dumps(request_data)
            data = json.loads(data)
            txid = rpc_connection.publish(users_pharmacy_stream, [email,'True',timestamp_utc], {'json' : data})
            if txid:
                send_welcome_email(email,request.POST.get('company_info'))
                return render(request, "login_pharmacy.html",{'message': "Please Log In using you credentials!"})
        else:
            return render(request, "Signup-pharmacy1.html",{'email': email, 'message': "Wrong SLA, Please provide correct SLA file!"})

def login_pharmacy(request):
        return render(request, "login_pharmacy.html")

def login_check_pharmacy(request): #Implement Password authentication
    print('login_check_pharmacy')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        password_rcvd = request.POST.get('passw')
        result = rpc_connection.liststreamkeyitems(users_pharmacy_stream, email_rcvd)
        data = json.dumps(result)
        json_load = json.loads(data)
        #apply length check for json_load
        if(len(json_load)>0):
            email_frm_chain = json_load[-1]['keys'][0]
            isActive = json_load[-1]['keys'][1]
            passw_frm_chain = json_load[-1]['data']['json']['password']
            pharmacy_name = decrypt_data(base64_to_bytes(json_load[0]['data']['json']['company_info']))
            comp_info = json_load[0]['data']['json']['company_info']
            print(data)
            print(comp_info)
            print(pharmacy_name)
            print("Email from front end: ",email_rcvd)
            print("Email from stream: ",email_frm_chain)
            print(password_rcvd)
            print(passw_frm_chain)
            if isActive == 'True':
                if email_rcvd==email_frm_chain and check_password(password_rcvd, passw_frm_chain):
                    #####
                    response = rpc_connection.liststreamqueryitems('{}'.format(distributor_orders_stream), {'keys': [email_rcvd]})
                    json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
                    json_string = json.loads(json_string) #Converts OrderedDict to JSON String
                    print(json_string)
                    combined_list = []
                    for item in json_string:
                        keys = item['keys']
                        traxid = item['txid']
                        confirmed_status = item['data']['json']['confirmed']
                        totalprice = item['data']['json']['totalprice']
                        modified_keys = keys[:9] + [traxid] + [totalprice] + keys[9:] + [confirmed_status]
                        combined_list.append(modified_keys)
                    print("\nCombined list\n")
                    print(combined_list)
                    # Sort the list based on the timestamp (second last index)
                    combined_list.sort(key=lambda x: x[-2], reverse=True)
                    #NOTE: This is the logic for finding the latest order based on timestamp
                    # Dictionary to store distinct orders based on combined elements (except the second last index) and timestamp
                    distinct_orders = {}
                    # Iterate through the sorted list and collect the latest orders based on combined elements and timestamp
                    for order in combined_list:
                        key = tuple(order[:9])  # Using elements at indices 0 to 7 as the key (excluding the second last index)
                        if key not in distinct_orders:
                            distinct_orders[key] = order
                    # Convert the dictionary to a list of lists
                    distinct_orders_list = list(distinct_orders.values())
                    # # Print the distinct orders
                    for order in distinct_orders_list:
                        print(order)
                    # Iterate over the combined_list
                    orders = []
                    for index, item in enumerate(distinct_orders_list):
                        # Create a dictionary for each element in the combined_list
                        orderPlaceOn = datetime.datetime.fromisoformat(item[11])
                        # orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d %H:%M:%S')
                        orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d')
                        order = {
                            "orderid":item[0],
                            "trxid": item[9],
                            "Distributor_name": item[1],
                            "Manufacturer_email": item[2],
                            "distributor_email": item[3],
                            "batchId": item[6],
                            "product_name": item[8],
                            "product_code": item[7],
                            "orderPlaceOn": str(orderPlaceOn),
                            "quantity": item[5],
                            "tot_price": item[10],
                            "confirmed": item[13],
                            "timestamp": item[12],
                            "manu_email": item[4],
                        }
                        # Append the dictionary to the orders list
                        orders.append(order)
                    # Print the resulting list of dictionaries
                    print(orders)
                #####
                    return render(request, "pharmacy1.html",{'comp_info': comp_info,'email':email_rcvd, 'company_info': pharmacy_name, 'orders':orders, 'message':f'Welcome, {pharmacy_name}!'})
                else:
                    return render(request, "login_pharmacy.html", {'error_message': "Incorrect email or password."})
            elif isActive=='False':
                 return render(request, "login_pharmacy.html", {'error_message': "Account Deactivated!"})         
        else:
                return render(request, "login_pharmacy.html", {'error_message': "Incorrect email or password."})

def pharmorderprod(request):
    print("\nOrdering Products from Distributor")
    if request.method == 'POST':
        email_pharm = request.POST.get('email',None)
        company_info = request.POST.get('company_info',None)
        print('\nDistributor Email: ',email_pharm)
        print('\nCompany Info: ',company_info)

        #for fetching out the name of the Distributor name
        result = rpc_connection.liststreamkeyitems(users_pharmacy_stream, email_pharm)
        data = json.dumps(result)
        json_load = json.loads(data)
        comp_info = json_load[0]['data']['json']['company_info'] 
        
        # Now fetch the distributor names and their emails(keys), only names will be shown in the drop down of the distributor.html screen
        response = rpc_connection.liststreamitems(users_distributor_stream)
        user_map = {}  # Initialize a dictionary to store user data based on the latest timestamp
        # Sort the response list based on timestamp
        response.sort(key=lambda x: x['keys'][-1], reverse=True)
        for item in response:
            data = item['data']['json']
            email = data['email']
            timestamp = item['keys'][-1]  # Get the timestamp from the last element of keys
            status = item['keys'][1]
            if email not in user_map or timestamp > user_map[email]['timestamp']:
                user_map[email] = {
                    'timestamp': timestamp,
                    'user_data': data,
                    'status': status
                }

        users_with_latest_info = [{
            'email': key,
            'timestamp': value['timestamp'],
            'user_data': value['user_data'],
            'status': value['status']
        } for key, value in user_map.items()]

        # print(users_with_latest_info)
        json_string = json.dumps(users_with_latest_info)
        json_load = json.loads(json_string)
        print(json_string)        

        keys_company_info = {}
        i=1
        for item in json_load:
            keys_company_info[item["email"]] = decrypt_data(base64_to_bytes(item['user_data']['company_info']))
        print("\nkeys_company_info:\n",keys_company_info)
        return render(request, "pharmorderprod1.html", {'keys_company_info': keys_company_info,'email': email_pharm, 'company_info' : company_info})

def distproducts(request):
    email_pharm = request.GET.get('email', None)
    selected_distributor = request.GET.get('manufacturer', None) # Manufacturer name being passed from Distributor.html
    comp_info = request.GET.get('comp_info', None) # Manufacturer name being passed from Distributor.html
    
    #Getting hash sla from the user stream
    response = rpc_connection.liststreamkeyitems(users_pharmacy_stream, email_pharm)
    json_string = json.dumps(response)
    json_string = json.loads(json_string)
    print(json_string)
    fetched_sla = json_string[-1]['data']['json']['license_certification']
    print("Fetched SLA from SLA stream", fetched_sla)
    #Getting hash sla from the SLA stream
    response = rpc_connection.liststreamitems(pharmacy_SLA_stream)
    json_string_pharmacy = json.dumps(response)
    json_string_pharmacy = json.loads(json_string_pharmacy)
    if len(json_string_pharmacy)>0:
        Pharmacy_hash_sla = json_string_pharmacy[-1]['data']['json']["hash_sla"]
        print("Fetched SLA from USER stream",Pharmacy_hash_sla)
    else:
        Pharmacy_hash_sla = 'None'
        print(Pharmacy_hash_sla)    
    
    if fetched_sla==Pharmacy_hash_sla:    
        print(selected_distributor)
        print("Distributor emails: ",email_pharm)
        print("selected_distributor:",selected_distributor)
        print("comp_info :" ,comp_info) 
        x = rpc_connection.subscribe('{}'.format(users_distributor_items_stream)) # Subscribing
        response = rpc_connection.liststreamkeyitems('{}'.format(users_distributor_items_stream), '{}'.format(selected_distributor)) # Based on the manufacturer KEY the data is being fetched
        # Have a logic which fetches out items based on latest_timestamp
        print(len(response))
        if len(response) > 0:
            product_map = {} # Initialize a dictionary to store product data and timestamp for each unique key

            for item in response:
                data = item['data']['json']
                key = (decrypt_data(base64_to_bytes(data['email'])),
                       decrypt_data(base64_to_bytes(data['products'][0]['product_code'])),
                       decrypt_data(base64_to_bytes(data['batchId'])),
                       decrypt_data(base64_to_bytes(data['products'][0]['product_name'])))
                timestamp = item['keys'][-1] # Get the timestamp from the last element of keys

                if key not in product_map or timestamp > product_map[key]['timestamp']:
                    product_map[key] = {
                        'product_data': {
                                            'product_name': decrypt_data(base64_to_bytes(data['products'][0]['product_name'])),
                                            'product_code': decrypt_data(base64_to_bytes(data['products'][0]['product_code'])),
                                            'description': decrypt_data(base64_to_bytes(data['products'][0]['description'])),
                                            'ingredients': list(decrypt_data(base64_to_bytes(data['products'][0]['ingredients']))),
                                            'dosage': decrypt_data(base64_to_bytes(data['products'][0]['dosage'])),
                                            'quantity_in_stock': decrypt_data(base64_to_bytes(data['products'][0]['quantity_in_stock'])),
                                            'unit_price': decrypt_data(base64_to_bytes(data['products'][0]['unit_price'])),
                                            'manufacturing_date': decrypt_data(base64_to_bytes(data['products'][0]['manufacturing_date'])),
                                            'expiry_date': decrypt_data(base64_to_bytes(data['products'][0]['expiry_date'])),
                                            'drugbank_id': decrypt_data(base64_to_bytes(data['products'][0]['drugbank_id'])),
                                            'form': decrypt_data(base64_to_bytes(data['products'][0]['form'])),
                                            'strength': decrypt_data(base64_to_bytes(data['products'][0]['strength'])),
                                            'route': decrypt_data(base64_to_bytes(data['products'][0]['route'])),
                                            'published_on': decrypt_data(base64_to_bytes(data['products'][0]['published_on']))},
                        'timestamp': timestamp,
                        'email': key[0],
                        'product_code': key[1],
                        'batchId': key[2],
                        'product_name': key[3]
                    }

            products_with_timestamp = [{
                'timestamp': value['timestamp'],
                'email': value['email'],
                'product_code': value['product_code'],
                'batchId': value['batchId'],
                'product_name': value['product_name'],
                'product_data': value['product_data']
            } for value in product_map.values()]

            print(products_with_timestamp)
            return render(request, 'distproducts1.html', {'products': products_with_timestamp, 'manufacturer': selected_distributor, 'email': email_pharm, 'company_info': comp_info})
        else:
            return render(request, 'distproducts1.html', {'message': 'No products available!','manufacturer': selected_distributor, 'email': email_pharm, 'company_info': comp_info})
    else:
         return render(request, "pharmupdatesla.html",{'company_info': comp_info,'email':email_pharm,'pharmacy_hash_sla':fetched_sla,'message': "Wrong SLA, Please provide correct SLA file!"}) 
@csrf_protect
def pharmcheckout(request):
    print("\n\npharmacy checkout\n\n")
    if request.method == 'POST':
        # Retrieve the cartItems data from the POST request
        cart_items_json = request.POST.get('cartItems', None)
        manufacturer = request.POST.get('manufacturer', None)
        email_dist = request.POST.get('email', None)
        comp_info = request.POST.get('company_info', None)
        print(manufacturer)
        print(email_dist)
        print(comp_info)
        print(cart_items_json)
        if cart_items_json and manufacturer:
            # Parse the JSON data
            cart_items = json.loads(cart_items_json)

            # Do something with the cart_items data (e.g., save to the database, process the order, etc.)
            # For example, you can print it for demonstration purposes
            print(cart_items)

            # You can also render a template or return an appropriate HTTP response
            return render(request, 'pharmcheckout.html', {'cart_items': cart_items, 'manufacturer' : manufacturer, 'email_dist': email_dist, 'comp_info':comp_info})

def viewpharminvent(request):
    print('\nViewing Pharmacy Inventory')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        company_info = request.POST.get('company_info')
        print("email_rcvd: ",email_rcvd)
        print("company_info :",company_info)
        response = rpc_connection.liststreamkeyitems('{}'.format(users_pharmacy_items_stream), '{}'.format(email_rcvd)) # Based on the manufacturer KEY the data is being fetched
        print(len(response))
        if len(response) > 0:
            product_map = {} # Initialize a dictionary to store product data and timestamp for each unique key

            for item in response:
                data = item['data']['json']
                key = (decrypt_data(base64_to_bytes(data['email'])),
                       decrypt_data(base64_to_bytes(data['products'][0]['product_code'])),
                       decrypt_data(base64_to_bytes(data['batchId'])),
                       decrypt_data(base64_to_bytes(data['products'][0]['product_name'])))
                timestamp = item['keys'][-1] # Get the timestamp from the last element of keys

                if key not in product_map or timestamp > product_map[key]['timestamp']:
                    product_map[key] = {
                        'product_data': {
                                        'product_name': decrypt_data(base64_to_bytes(data['products'][0]['product_name'])),
                                        'product_code': decrypt_data(base64_to_bytes(data['products'][0]['product_code'])),
                                        'description': decrypt_data(base64_to_bytes(data['products'][0]['description'])),
                                        'ingredients': decrypt_data(base64_to_bytes(data['products'][0]['ingredients'])),
                                        'dosage': decrypt_data(base64_to_bytes(data['products'][0]['dosage'])),
                                        'quantity_in_stock': decrypt_data(base64_to_bytes(data['products'][0]['quantity_in_stock'])),
                                        'unit_price': decrypt_data(base64_to_bytes(data['products'][0]['unit_price'])),
                                        'manufacturing_date': decrypt_data(base64_to_bytes(data['products'][0]['manufacturing_date'])),
                                        'expiry_date': decrypt_data(base64_to_bytes(data['products'][0]['expiry_date'])),
                                        'drugbank_id': decrypt_data(base64_to_bytes(data['products'][0]['drugbank_id'])),
                                        'form': decrypt_data(base64_to_bytes(data['products'][0]['form'])),
                                        'strength': decrypt_data(base64_to_bytes(data['products'][0]['strength'])),
                                        'route': decrypt_data(base64_to_bytes(data['products'][0]['route'])),
                                        'published_on': decrypt_data(base64_to_bytes(data['products'][0]['published_on']))},
                        'timestamp': timestamp,
                        'email': key[0],
                        'product_code': key[1],
                        'batchId': key[2],
                        'product_name': key[3]
                    }

            products_with_timestamp = [{
                'timestamp': value['timestamp'],
                'email': value['email'],
                'product_code': value['product_code'],
                'batchId': value['batchId'],
                'product_name': value['product_name'],
                'product_data': value['product_data']
            } for value in product_map.values()]

            print(products_with_timestamp)
            return render(request, 'viewpharminventory1.html', {'products': products_with_timestamp, 'email': email_rcvd, 'company_info': company_info})
        else:
            print('oh yes')
            return render(request, 'viewpharminventory1.html', {'message': 'No products available', 'email': email_rcvd, 'company_info': company_info})

def pharmreqorder(request):
    print('\nPharmacy publish order request to Distributor')
    if request.method == 'POST':
        # Retrieve the cartItems data from the POST request
        cart_items_json = request.POST.get('cartItems', None)
        email_pharm = request.POST.get('email_dist', None)
        email_dist = request.POST.get('manufacturer', None)
        comp_info = request.POST.get('comp_info', None)
        print(email_pharm)
        print(email_dist)
        print(comp_info)
        #NOTE:
        # Please implement the flow in which whenever the distributor places an order,
        # it first goes to the order confirmation page of the MANUFACTURER.
        # Once manufacturer confirms the order, the quantity of the medicine is minused from the MANUFACTURER stream
        # and new Item is published in the MANUFACTURER stream.

        #Also getting the manufacturer name becuase it's a key in the MANUFACTURER 
        if cart_items_json:
            print("----CART ITEMS from frontEND----")
            cart_items = json.loads(cart_items_json)
            print(len(cart_items))
            print("--------\n")
            for cart_item in cart_items:
                manu_email = cart_item['manu_email']
                batchId = cart_item['batchId']
                productCode = cart_item['productCode']
                productName = cart_item['productName']
                timestamp = cart_item['timestamp']
                quantity = cart_item['quantity']
                totalprice = cart_item['totalprice']
                print(manu_email)
                print(batchId)
                print(productCode)
                print(productName)
                print(timestamp)
                print(quantity)
                print(totalprice)

                timestamp_utc = datetime.datetime.utcnow().isoformat()

                time_of_order=timestamp_utc

                # Generate OrderId based on various attributes
                base_string = f"{email_dist}{email_pharm}{manu_email}{quantity}{batchId}{productCode}{productName}{timestamp_utc}"
                hashed = hashlib.sha256(base_string.encode()).hexdigest()
                orderid = ''.join(random.choices(hashed, k=6))
                
                # Publishes the ordered products into the distributor_orders_stream stream accessed by Pharmacy
                txid = rpc_connection.publish('{}'.format(distributor_orders_stream), [orderid,comp_info,email_dist,email_pharm,manu_email,str(quantity), batchId, productCode, productName, time_of_order, timestamp_utc],{'json': {
                                                                                                                                                                           'confirmed': '',
                                                                                                                                                                           'totalprice': str(totalprice)
                                                                                                                                                                           }})
            #render a template or return an appropriate HTTP response, still to be decided
            return HttpResponse("Purchase completed. Thank you!")

def pharmorderstatus(request):
    print('\nOrders From Pharmacies\n')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        print("Email :",email_rcvd)
        comp_info = request.POST.get('company_info') #Name of the Distributor
        print("comany_info:",comp_info)
        response = rpc_connection.liststreamqueryitems('{}'.format(distributor_orders_stream), {'keys': [email_rcvd]})
        json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
        json_string = json.loads(json_string) #Converts OrderedDict to JSON String
        
        print(json_string)
        combined_list = []
        for item in json_string:
            keys = item['keys']
            traxid = item['txid']
            confirmed_status = item['data']['json']['confirmed']
            totalprice = item['data']['json']['totalprice']
            modified_keys = keys[:9] + [traxid] + [totalprice] + keys[9:] + [confirmed_status]
            combined_list.append(modified_keys)
        print("\nCombined list\n")
        print(combined_list)
        # Sort the list based on the timestamp (second last index)
        combined_list.sort(key=lambda x: x[-2], reverse=True)
        
        #######################################################################################################            
        #NOTE: This is the logic for finding the latest order based on timestamp
        # Dictionary to store distinct orders based on combined elements (except the second last index) and timestamp
        distinct_orders = {}
        
        # Iterate through the sorted list and collect the latest orders based on combined elements and timestamp
        for order in combined_list:
            key = tuple(order[:9])  # Using elements at indices 0 to 7 as the key (excluding the second last index)
            if key not in distinct_orders:
                distinct_orders[key] = order
        
        # Convert the dictionary to a list of lists
        distinct_orders_list = list(distinct_orders.values())
        #######################################################################################################
        
        
        # # Print the distinct orders
        for order in distinct_orders_list:
            print(order)
        # Iterate over the combined_list
        orders = []
        for index, item in enumerate(distinct_orders_list):
            # Create a dictionary for each element in the combined_list
            orderPlaceOn = datetime.datetime.fromisoformat(item[11])
            # orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d %H:%M:%S')
            orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d')
            order = {
                "orderid":item[0],
                "trxid": item[9],
                "Distributor_name": item[1],
                "Manufacturer_email": item[2],
                "distributor_email": item[3],
                "batchId": item[6],
                "product_name": item[8],
                "product_code": item[7],
                "orderPlaceOn": str(orderPlaceOn),
                "quantity": item[5],
                "tot_price": item[10],
                "confirmed": item[13],
                "timestamp": item[12],
                "manu_email": item[4],
            }
            # Append the dictionary to the orders list
            orders.append(order)
        # Print the resulting list of dictionaries
        print(orders)
        # return render(request, "distributor_orders.html",{'orders': orders})

        return render(request, "pharmacy1.html",{'company_info': comp_info,'email':email_rcvd, 'orders':orders })


def pharmupdatesla(request):# Adding Drugs In Manufacturer Item Stream
    print('manage_sla user')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email',None)
        company_info = request.POST.get('company_info',None)

        #Pharmacy SLA
        response = rpc_connection.liststreamkeyitems(users_pharmacy_stream,email_rcvd)
        json_string_pharmacy = json.dumps(response)
        json_string_pharmacy = json.loads(json_string_pharmacy)
        print(json_string_pharmacy)
        if len(json_string_pharmacy)>0:
            pharmacy_hash_sla = json_string_pharmacy[-1]['data']['json']["license_certification"]
            print(pharmacy_hash_sla)
        else:
            pharmacy_hash_sla = 'None'
            print(pharmacy_hash_sla)

    return render(request, "pharmupdatesla.html",{'company_info': company_info,'email':email_rcvd, 'pharmacy_hash_sla':pharmacy_hash_sla})


def pharm_sla_upload(request):
    print('submiting Manufacturer user SLA')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email',None)
        company_info = request.POST.get('company_info',None)
        hash_sla = request.POST.get('hash_sla',None)
        timestamp_utc = datetime.datetime.utcnow().isoformat()
        print(email_rcvd)
        print(company_info)
        print(hash_sla)

        #Getting the particular user for which sla will be updated
        response = rpc_connection.liststreamkeyitems(users_pharmacy_stream, email_rcvd)
        json_string_pharmacy = json.dumps(response)
        json_string_pharmacy = json.loads(json_string_pharmacy)
        #Logic for updating the SLA
        if len(json_string_pharmacy)>0:
            json_data = json_string_pharmacy[-1]
            json_data['data']['json']["license_certification"] = hash_sla
            data = json_data['data']['json']
            keys = json_data['keys']
            print("keys: ",keys)
            Pharmacy_hash_sla = json_string_pharmacy[-1]['data']['json']["license_certification"]
            txid = rpc_connection.publish('{}'.format(users_pharmacy_stream), keys,
                                                                             {'json': data })
            print(Pharmacy_hash_sla)
        else:
            Pharmacy_hash_sla = 'None'
            print(Pharmacy_hash_sla)

    return render(request, "pharmupdatesla.html",{'company_info': company_info,'email':email_rcvd,'pharmacy_hash_sla':Pharmacy_hash_sla})

def getdetails(request):
    patid = int(request.GET['patid'])
    # k=webs3.retrive_data(patid)
    context = {
        'left': temp,
        # 'value': k
    }
    print(context)
    return render(request, "logval.html", context)

    # return render(request,"seedetails.html")

def base(request):
    return render(request, "base.html")

def prddata(request):
    if request.method == 'POST':
        drg_id = int(request.POST['drgid'])
        no_of_drg = int(request.POST['totdrg'])
        # webs3.produced_data(drg_id, no_of_drg)
        # print("drg id  :" + drg_id )
        # print("no of drugs : " + no_of_drg)
        context = {
            "drgid":  drg_id,
            "totdrg": no_of_drg
        }
        return render(request, "dealerinput.html", context)
    else:
        return render(request, "dealerinput.html")

def hostpitalinput(request):
    if request.method == 'POST':
        hospid = int(request.POST['hospid'])
        patid = int(request.POST['patid'])
        docid = int(request.POST['docid'])
        txid = rpc_connection.publish('testchain', 'contract', {'json' :{
        'manufacturer': hospid,
        'distributor': patid,
        'signature': docid,
        }})
    if txid:
        return render(request, "hospitaltrxid.html", {"txid": txid})
    else:
        return render(request, "hospitalinput.html", {"error": "Failed to publish data to MultiChain"})

def qrscanned(request):
    if request.method == 'POST':
        required_keys = ['manufacturer_email', 'Product_code', 'Batch_id', 'product_name']
        scanned_data = {}

        try:
            # Attempt to load the JSON data from request.body
            data = json.loads(request.body)
            scanned_data_str = data.get('scannedData')

            if scanned_data_str:
                try:
                    # Attempt to load the scanned data JSON string
                    scanned_data = json.loads(scanned_data_str)
                except json.JSONDecodeError:
                    pass  # Continue to set keys to empty string
        except json.JSONDecodeError:
            pass  # Continue to set keys to empty string

        # Set missing keys to empty string
        for key in required_keys:
            if key not in scanned_data:
                scanned_data[key] = ''

        Manufacturer_email = scanned_data['manufacturer_email']
        Product_code = scanned_data['Product_code']
        Batch_id = scanned_data['Batch_id']
        product_name = scanned_data['product_name']

        print(Manufacturer_email)
        print(Product_code)
        print(Batch_id)
        print(product_name)

        # Manufacturer
        result = rpc_connection.liststreamqueryitems('{}'.format(users_manufacturer_items_stream), {'keys': [Manufacturer_email, Product_code, Batch_id, product_name]})
        data = json.dumps(result)
        json_load = json.loads(data)
        if len(json_load) > 0:
            rep1 = 'Item exists in Manufacturer items Stream.'
        else:
            rep1 = 'Item does not exist in Manufacturer items Stream.'

        # Distributor
        result = rpc_connection.liststreamqueryitems('{}'.format(users_distributor_items_stream), {'keys': [Manufacturer_email, Product_code, Batch_id, product_name]})
        data = json.dumps(result)
        json_load = json.loads(data)
        if len(json_load) > 0:
            rep2 = 'Item exists in Distributor items Stream.'
        else:
            rep2 = 'Item does not exist in Distributor items Stream.'

        # Pharmacy
        result = rpc_connection.liststreamqueryitems('{}'.format(users_pharmacy_items_stream), {'keys': [Manufacturer_email, Product_code, Batch_id, product_name]})
        data = json.dumps(result)
        json_load = json.loads(data)
        if len(json_load) > 0:
            rep3 = 'Item exists in Pharmacy items Stream.'
        else:
            rep3 = 'Item does not exist in Pharmacy items Stream.'


        print(rep1)
        print(rep2)
        print(rep3)

        # Return the results as a JSON response
        response_data = {
            'rep1': rep1,
            'rep2': rep2,
            'rep3': rep3
        }

        return JsonResponse(response_data)
    
    else:
        return HttpResponse('Invalid method', status=405)
    
def otp_pharmacy(request):
    if request.method == 'POST':
        email = request.POST['email']
        print(email)
        return render(request, "Signup-pharmacy1.html",{'email': email}) #if the email is not present then render this page
    