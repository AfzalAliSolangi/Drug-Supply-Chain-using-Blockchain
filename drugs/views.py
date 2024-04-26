from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import multichain
import json
import configparser
import datetime
from collections import defaultdict
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
key = config.get('Section1','key') #Key - for manufacturer
publisher = config.get('Section1','publisher') #Set a default for Manufacturer, add another for distributors

# Configure your MultiChain connection here
rpcuser = config.get('Section1','rpcuser')
rpcpassword= config.get('Section1','rpcpassword')
rpchost = config.get('Section1','rpchost')
rpcport = config.get('Section1','rpcport')
chainname = config.get('Section1','chainname')
rpc_connection = multichain.MultiChainClient(rpchost, rpcport, rpcuser, rpcpassword)


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


### MASTER ###
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
        for each_email in email_keys:
            if each_email==email:
                print("present")
                return render(request, "login_master.html") #if the email is present prompt to login master page
        return render(request, "signup-master.html",{'email': email}) #if the email is not present then render this page

def process_registration_master(request):
    print("process_registration_manufacturer")
    if request.method == 'POST':
        # print("method check")
        email = request.POST.get('email')
        request_data = {
            "email": request.POST.get('email'),
            "company_info": request.POST.get('company_info'),
            "street_address": request.POST.get('street_address'),
            "business_details": request.POST.get('business_details'),
            "state": request.POST.get('state'),
            "city": request.POST.get('city'),
            "zip_code": request.POST.get('zip_code'),
            "password": request.POST.get('password'),
            "license_certification": request.POST.get('license_certification')
        }
        data = json.dumps(request_data)
        data = json.loads(data)
        txid = rpc_connection.publish('users_master_stream', '{}'.format(email), {'json' : data})
        if txid:
            return HttpResponse("process_registration_master")
        
def login_master(request):
        return render(request, "login_master.html")

def login_check_master(request): #Implement Password authentication
    print('login_check_master')
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('passw')
        print(name)
        print(password)
        return render(request, "master.html")

## MANUFACTURER ##

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
        for each_email in email_keys:
            if each_email==email:
                print("present")
                return render(request, "login_manufacturer.html") #if the email is present prompt to login master page
        return render(request, "signup-manufacturer.html",{'email': email}) #if the email is not present then render this page
    

def process_registration_manufacturer(request):
    print("process_registration_manufacturer")
    if request.method == 'POST':
        # print("method check")
        email = request.POST.get('email')
        request_data = {
            "email": request.POST.get('email'),
            "company_info": request.POST.get('company_info'),
            "street_address": request.POST.get('street_address'),
            "business_details": request.POST.get('business_details'),
            "state": request.POST.get('state'),
            "city": request.POST.get('city'),
            "zip_code": request.POST.get('zip_code'),
            "password": request.POST.get('password'),
            "license_certification": request.POST.get('license_certification')
        }
        data = json.dumps(request_data)
        data = json.loads(data)
        txid = rpc_connection.publish('users_manufacturer_stream', '{}'.format(email), {'json' : data})
        if txid:
            return HttpResponse("process_registration_manufacturer")
        
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
        email_frm_chain = json_load[0]['keys'][0]
        passw_frm_chain = json_load[0]['data']['json']['password']
        manufacturer_name = json_load[0]['data']['json']['company_info']
        comp_info = json_load[0]['data']['json']['company_info']
        print(data)
        print(comp_info)
        print("Email from front end: ",email_rcvd)
        print("Email from stream: ",email_frm_chain)
        print(password_rcvd)
        print(passw_frm_chain)
        if email_rcvd==email_frm_chain and password_rcvd==passw_frm_chain:
            print(email_rcvd)
            response = rpc_connection.liststreamqueryitems('{}'.format(manufacturer_orders_stream), {'keys': [email_rcvd]})
            json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
            json_string = json.loads(json_string) #Converts OrderedDict to JSON String
            
            # print(json_string)
            combined_list = []

            for item in json_string:
                # Extract keys from the dictionary
                keys = item['keys']
                # Extract data part from the dictionary
                data_part = [item['data']['json'][key] for key in ['confirmed']]
                # Combine keys and data_part into a single list
                combined_list.append(keys + data_part)

            # print("\nCombined list\n")
            # print(combined_list)

            # Sort the list based on the timestamp (second last index)
            combined_list.sort(key=lambda x: x[-2], reverse=True)

            
########################################################################################################            
            #NOTE: This is the logic for finding the latest order based on timestamp
            # Dictionary to store distinct orders based on combined elements (except the second last index) and timestamp
            distinct_orders = {}
            
            # Iterate through the sorted list and collect the latest orders based on combined elements and timestamp
            for order in combined_list:
                key = tuple(order[:8])  # Using elements at indices 0 to 7 as the key (excluding the second last index)
                if key not in distinct_orders:
                    distinct_orders[key] = order
            
            # Convert the dictionary to a list of lists
            distinct_orders_list = list(distinct_orders.values())

########################################################################################################
            
            
            # # Print the distinct orders
            # for order in distinct_orders_list:
            #     print(order)

            # Iterate over the combined_list
            orders = []
            for index, item in enumerate(distinct_orders_list):
                # Create a dictionary for each element in the combined_list

                orderPlaceOn = datetime.datetime.fromisoformat(item[7])
                # orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d %H:%M:%S')
                orderPlaceOn = orderPlaceOn.strftime('%Y-%m-%d')
                order = {
                    "Distributor_name": item[0],
                    "Manufacturer_email": item[1],
                    "distributor_email": item[2],
                    "batchId": item[4],
                    "product_name": item[6],
                    "product_code": item[5],
                    "orderPlaceOn": str(orderPlaceOn),
                    "quantity": item[3],
                    "confirmed": item[9],
                }
                # Append the dictionary to the orders list
                orders.append(order)

            # Print the resulting list of dictionaries
            print(orders)
            return render(request, "manufacturer1.html",{'comp_info': comp_info,'email':email_rcvd, 'company_info': manufacturer_name,'orders': orders})
        else:
            return render(request, "login_manufacturer.html", {'error_message': "Incorrect email or password."})

    

def manuorderconfirm(request):
    print('\nConfirm Orders From distributors\n')
    if request.method == 'POST':
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
            Distributor_name = order['Distributor_name']
            Manufacturer_email = order['Manufacturer_email']
            distributor_email = order['distributor_email']
            batchId = order['batchId']
            product_name = order['product_name']
            product_code = order['product_code']
            timestamp = order['timestamp']
            quantity_frm_order = order['quantity'] 
            timestamp_utc = datetime.datetime.utcnow().isoformat()

            #for debugging
            print('Distributor_name :', Distributor_name)
            print('Manufacturer_email :',Manufacturer_email)
            print('distributor_email :',distributor_email)
            print('batchId :',batchId)
            print('product_code :', product_code)
            print('timestamp :',timestamp)
            print('quantity_frm_order :', quantity_frm_order)
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
                prev_quantity = products_with_timestamp[0]['product_data']['quantity_in_stock'] #From the user_manufacturer_items_stream
                new_quantity = int(prev_quantity)-int(quantity_frm_order)
                total_amout = int(quantity_frm_order) * int(products_with_timestamp[0]['product_data']['unit_price'])

                print('new quantity :',new_quantity)
                print('tot_amount :', total_amout)

                latest_item['quantity_in_stock'] = new_quantity
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
                                                                                                 "manufacturer":manufacturer_name,
                                                                                                 "email":Manufacturer_email,
                                                                                                 "batchId":batchId,
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
                    new_quantity = int(prev_quantity)+int(quantity_frm_order)
                    total_amout = int(quantity_frm_order) * int(products_with_timestamp[0]['product_data']['unit_price'])
                    print('new quantity :',new_quantity)
                    print('tot_amount :', total_amout)
                    latest_item['quantity_in_stock'] = new_quantity
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
                                                                                                     "email":Manufacturer_email,
                                                                                                     "batchId":batchId,
                                                                                                     "products":[latest_item]
                                                                                                     }
                                                                                                     })#Add a timestamp for sub logic
                else:
                    latest_item['quantity_in_stock'] = quantity_frm_order
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
                                                                                                     "email":Manufacturer_email,
                                                                                                     "batchId":batchId,
                                                                                                     "products":[latest_item]
                                                                                                     }
                                                                                                     })#Add a timestamp for sub logic
                #publishing into the manufacturer_orders_stream telling that order is confimed
                txid = rpc_connection.publish('{}'.format(manufacturer_orders_stream), [Distributor_name,Manufacturer_email,distributor_email,Manufacturer_email, batchId, product_code, product_name, timestamp_utc],{'json': {'quantity': quantity_frm_order,
                                                                                                                                                                               'confirmed': 'True',
                                                                                                                                                                               }})

        return render(request, 'manuproducts.html')

def viewmanuinvent(request):
    print('Viewing Manufacturer Inventory')
    if request.method == 'POST':
        manu_key = request.POST.get('email')
        print(manu_key)
        response = rpc_connection.liststreamkeyitems('{}'.format(users_manufacturer_items_stream), '{}'.format(manu_key)) # Based on the manufacturer KEY the data is being fetched
        print(len(response))
        if len(response) > 0:
            product_map = {} # Initialize a dictionary to store product data and timestamp for each unique key

            for item in response:
                data = item['data']['json']
                key = (data['email'], data['products'][0]['product_code'], data['batchId'], data['products'][0]['product_name'])
                timestamp = item['keys'][-1] # Get the timestamp from the last element of keys

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
            return render(request, 'viewmanuinventory.html', {'products': products_with_timestamp})
        else:
            return render(request, 'viewmanuinventory.html', {'message': 'No products available'})


def adddrugmenu(request):
    print('\nAdd Drug Manufacturer\n')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        Company_name = request.POST.get('company_info')
        print("Email of the Manufacturer",email_rcvd)
        print("Name of the Manufacturer",Company_name)
    return render(request, "adddrug.html",{'comp_info': Company_name,'email':email_rcvd})

def adddrug(request): # Manufacturer Input
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
        structured_json = {
            "products": []
        }

        for product in data["products"]:
            structured_product = {
                "product_name": product["product_name"],
                "product_code": product["product_code"],
                "description": product["description"],
                "ingredients": product["ingredients"],
                "dosage": product["dosage"],
                "quantity_in_stock": product["quantity_in_stock"],
                "unit_price": product["unit_price"],
                "manufacturing_date": product["manufacturing_date"],
                "expiry_date": product["expiry_date"],
                "published_on": timestamp_utc
            }
            structured_json["products"].append(structured_product)
        
        print(structured_json)
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
                return HttpResponse("This item Already exists!")
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
                                                                                         {'json': data})#Add a timestamp for sub logic
            return render(request, "adddrug.html", {"txid": txid})


####Distributor#####
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
        for each_email in email_keys:
            if each_email==email:
                print("present")
                return render(request, "login_distributor.html") #if the email is present prompt to login master page
        return render(request, "signup-distributor.html",{'email': email}) #if the email is not present then render this page

def process_registration_distributor(request):
    print("process_registration_distributor")
    if request.method == 'POST':
        # print("method check")
        email = request.POST.get('email')
        request_data = {
            "email": request.POST.get('email'),
            "company_info": request.POST.get('company_info'),
            "street_address": request.POST.get('street_address'),
            "business_details": request.POST.get('business_details'),
            "state": request.POST.get('state'),
            "city": request.POST.get('city'),
            "zip_code": request.POST.get('zip_code'),
            "password": request.POST.get('password'),
            "license_certification": request.POST.get('license_certification')
        }
        data = json.dumps(request_data)
        data = json.loads(data)
        txid = rpc_connection.publish('users_distributor_stream', '{}'.format(email), {'json' : data})
        if txid:
            return render(request, "login_distributor.html")

def login_distributor(request):
        return render(request, "login_distributor.html")

def login_check_distributor(request): #Implement Password authentication
    print('login_check_distributor')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        password_rcvd = request.POST.get('passw')
        result = rpc_connection.liststreamkeyitems(users_distributor_stream, email_rcvd)
        data = json.dumps(result)
        json_load = json.loads(data)
        email_frm_chain = json_load[0]['keys'][0]
        passw_frm_chain = json_load[0]['data']['json']['password']
        comp_info = json_load[0]['data']['json']['company_info']
        print(data)
        print(comp_info)
        print("Email from front end: ",email_rcvd)
        print("Email from stream: ",email_frm_chain)
        print(password_rcvd)
        print(passw_frm_chain)
        if email_rcvd==email_frm_chain and password_rcvd==passw_frm_chain:
            return render(request, "Distributor.html", {'email': email_rcvd, 'comp_info' : comp_info})
        else:
            return render(request, "login_distributor.html", {'error_message': "Incorrect email or password."})


##Started working from here on 2024/04/22##
def viewdistinvent(request):
    print('\nViewing Distributor Inventory')
    if request.method == 'POST':
        dist_key = request.POST.get('email')
        print(dist_key)
        response = rpc_connection.liststreamkeyitems('{}'.format(users_distributor_items_stream), '{}'.format(dist_key)) # Based on the manufacturer KEY the data is being fetched
        print(len(response))
        if len(response) > 0:
            product_map = {} # Initialize a dictionary to store product data and timestamp for each unique key

            for item in response:
                data = item['data']['json']
                key = (data['email'], data['products'][0]['product_code'], data['batchId'], data['products'][0]['product_name'])
                timestamp = item['keys'][-1] # Get the timestamp from the last element of keys

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
            return render(request, 'viewdistinventory.html', {'products': products_with_timestamp})
        else:
            return render(request, 'viewdistinventory.html', {'message': 'No products available'})



def distorderprod(request):
    print("\nOrdering Products from Manufacturer")
    if request.method == 'POST':
        email_dist = request.POST.get('email',None)
        print('\nDistributor Email: ',email_dist)
        
        #for fetching out the name of the Distributor name
        result = rpc_connection.liststreamkeyitems(users_distributor_stream, email_dist)
        data = json.dumps(result)
        json_load = json.loads(data)
        comp_info = json_load[0]['data']['json']['company_info'] 
        
        # Now fetch the distributor names and their emails(keys), only names will be shown in the drop down of the distributor.html screen
        response = rpc_connection.liststreamitems(users_manufacturer_stream)
        json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
        print(json_string)
        json_load = json.loads(json_string)
        keys_company_info = {}
        for item in json_load:
            for key in item['keys']:
                keys_company_info[key] = item['data']['json']['company_info']
        print("\nkeys_company_info:\n",keys_company_info)
        return render(request, "distorderprod.html", {'keys_company_info': keys_company_info,'email_dist': email_dist, 'comp_info' : comp_info})

def manuproducts(request):
    email_dist = request.GET.get('email_dist', None)
    selected_manufacturer = request.GET.get('manufacturer', None) # Manufacturer name being passed from Distributor.html
    comp_info = request.GET.get('comp_info', None) # Manufacturer name being passed from Distributor.html
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
            key = (data['email'], data['products'][0]['product_code'], data['batchId'], data['products'][0]['product_name'])
            timestamp = item['keys'][-1] # Get the timestamp from the last element of keys
            
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
        return render(request, 'manuproducts.html', {'products': products_with_timestamp, 'manufacturer': selected_manufacturer, 'email_dist': email_dist, 'comp_info': comp_info})
    else:
        return render(request, 'manuproducts.html', {'message': 'No products available'})

@csrf_protect
def distcheckout(request):
    print("\n\ncheckout\n\n")
    if request.method == 'POST':
        # Retrieve the cartItems data from the POST request
        cart_items_json = request.POST.get('cartItems', None)
        manufacturer = request.POST.get('manufacturer', None)
        email_dist = request.POST.get('email_dist', None)
        comp_info = request.POST.get('comp_info', None)
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
                print(manu_email)
                print(batchId)
                print(productCode)
                print(productName)
                print(timestamp)
                print(quantity)

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
                # Publishes the ordered products into the manufacturer_orders_stream stream accessed by Manufacturer
                # before publishing have SLA Logic
                txid = rpc_connection.publish('{}'.format(manufacturer_orders_stream), [comp_info,manu_email,email_dist,str(quantity), batchId, productCode, productName, time_of_order, timestamp_utc],{'json': {
                                                                                                                                                                           'confirmed': '',
                                                                                                                                                                      }
                                                                                                                                                                    })
            #render a template or return an appropriate HTTP response, still to be decided
            print(txid) 
            return HttpResponse("Purchase completed. Thank you!")

def pharmorders(request):
    print('\nOrders From Pharmacies\n')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        print(email_rcvd)
        response = rpc_connection.liststreamqueryitems('{}'.format(distributor_orders_stream), {'keys': [email_rcvd]})
        json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
        json_string = json.loads(json_string) #Converts OrderedDict to JSON String
        combined_list = []

        for item in json_string:
            # Extract keys from the dictionary
            keys = item['keys']

            # Extract data part from the dictionary
            data_part = [item['data']['json'][key] for key in ['quantity', 'confirmed']]

            # Combine keys and data_part into a single list
            combined_list.append(keys + data_part)
        print(combined_list)

        
        orders = []

        # Iterate over the combined_list
        for index, item in enumerate(combined_list):
            # Create a dictionary for each element in the combined_list
            order = {
                "Distributor_name": item[0],
                "Manufacturer_email": item[1],
                "distributor_email": item[2],
                "batchId": item[4],
                "product_name": item[6],
                "product_code": item[5],
                "timestamp": item[7],
                "quantity": item[8],
                "confirmed": item[9],
            }
            # Append the dictionary to the orders list
            orders.append(order)

        # Print the resulting list of dictionaries
        print(orders)

        return render(request, "distributor_orders.html",{'orders': orders})
    
def distorderconfirm(request):
    print('\nConfirm Orders From distributors\n')
    if request.method == 'POST':
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
            Pharmacy_name = order['Distributor_name']
            distributor_email = order['Manufacturer_email']
            pharmacy_email = order['distributor_email']
            batchId = order['batchId']
            product_name = order['product_name']
            product_code = order['product_code']
            timestamp = order['timestamp']
            quantity_frm_order = order['quantity'] 
            timestamp_utc = datetime.datetime.utcnow().isoformat()

            #for debugging
            print('Pharmacy_name :', Pharmacy_name)
            print('distributor_email :',distributor_email)
            print('pharmacy_email :',pharmacy_email)
            print('batchId :',batchId)
            print('product_code :', product_code)
            print('timestamp :',timestamp)
            print('quantity_frm_order :', quantity_frm_order)
            timestamp_utc = datetime.datetime.utcnow().isoformat()

            Manufacturer_email =  rpc_connection.liststreamqueryitems('{}'.format(distributor_orders_stream), {'keys': [Pharmacy_name, distributor_email, pharmacy_email, batchId, product_code, product_name,timestamp]})        # Have a logic which fetches out items based on latest_timestamp
            Manufacturer_email = json.dumps(Manufacturer_email)
            Manufacturer_email = json.loads(Manufacturer_email)
            Manufacturer_email = Manufacturer_email[0]['keys'][3]
            print("Manufacturer_email : ",Manufacturer_email)
            #gettig data based on keys
            response =  rpc_connection.liststreamqueryitems('{}'.format(users_distributor_items_stream), {'keys': [distributor_email,Manufacturer_email, batchId, product_code, product_name]})        # Have a logic which fetches out items based on latest_timestamp
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
                prev_quantity = products_with_timestamp[0]['product_data']['quantity_in_stock'] #From the user_manufacturer_items_stream
                new_quantity = int(prev_quantity)-int(quantity_frm_order)
                total_amout = int(quantity_frm_order) * int(products_with_timestamp[0]['product_data']['unit_price'])

                print('new quantity :',new_quantity)
                print('tot_amount :', total_amout)

                latest_item['quantity_in_stock'] = new_quantity
                print('Item after updating quantity: \n', latest_item)

                #publishing into users_manufacturer_items_stream
                txid = rpc_connection.publish('{}'.format(users_distributor_items_stream), [distributor_email,
                                                                                            Manufacturer_email,
                                                                                             product_code,
                                                                                             batchId,
                                                                                             product_name,
                                                                                             timestamp_utc
                                                                                             ],
                                                                                             {'json': {
                                                                                                 "manufacturer":manufacturer_name,
                                                                                                 "email":Manufacturer_email,
                                                                                                 "batchId":batchId,
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
                    new_quantity = int(prev_quantity)+int(quantity_frm_order)
                    total_amout = int(quantity_frm_order) * int(products_with_timestamp[0]['product_data']['unit_price'])
                    print('new quantity :',new_quantity)
                    print('tot_amount :', total_amout)
                    latest_item['quantity_in_stock'] = new_quantity
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
                                                                                                     "email":Manufacturer_email,
                                                                                                     "batchId":batchId,
                                                                                                     "products":[latest_item]
                                                                                                     }
                                                                                                     })#Add a timestamp for sub logic
                else:
                    latest_item['quantity_in_stock'] = quantity_frm_order
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
                                                                                                     "email":Manufacturer_email,
                                                                                                     "batchId":batchId,
                                                                                                     "products":[latest_item]
                                                                                                     }
                                                                                                     })#Add a timestamp for sub logic
                #publishing into the manufacturer_orders_stream telling that order is confimed
                txid = rpc_connection.publish('{}'.format(distributor_orders_stream), [Pharmacy_name,distributor_email,pharmacy_email,Manufacturer_email, batchId, product_code, product_name, timestamp_utc],{'json': {'quantity': quantity_frm_order,
                                                                                                                                                                               'confirmed': 'True',
                                                                                                                                                                               }})

        return render(request, 'manuproducts.html')

####Pharmacy#####
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
        for each_email in email_keys:
            if each_email==email:
                print("present")
                return render(request, "login_pharmacy.html") #if the email is present prompt to login master page
        return render(request, "Signup-pharmacy.html",{'email': email}) #if the email is not present then render this page

def process_registration_pharmacy(request):
    print("process_registration_pharmacy")
    if request.method == 'POST':
        # print("method check")
        email = request.POST.get('email')
        request_data = {
            "email": request.POST.get('email'),
            "company_info": request.POST.get('company_info'),
            "street_address": request.POST.get('street_address'),
            "business_details": request.POST.get('business_details'),
            "state": request.POST.get('state'),
            "city": request.POST.get('city'),
            "zip_code": request.POST.get('zip_code'),
            "password": request.POST.get('password'),
            "license_certification": request.POST.get('license_certification')
        }
        data = json.dumps(request_data)
        data = json.loads(data)
        txid = rpc_connection.publish('users_pharmacy_stream', '{}'.format(email), {'json' : data})
        if txid:
            return HttpResponse("process_registration_pharmacy")

def login_pharmacy(request):
        return render(request, "login_pharmacy.html")

#####Started working from here on 2024/04/23##
def login_check_pharmacy(request): #Implement Password authentication
    print('login_check_pharmacy')
    if request.method == 'POST':
        email_rcvd = request.POST.get('email')
        password_rcvd = request.POST.get('passw')
        result = rpc_connection.liststreamkeyitems(users_pharmacy_stream, email_rcvd)
        data = json.dumps(result)
        json_load = json.loads(data)
        #apply length check for json_load
        email_frm_chain = json_load[0]['keys'][0]
        passw_frm_chain = json_load[0]['data']['json']['password']
        pharmacy_name = json_load[0]['data']['json']['company_info']
        comp_info = json_load[0]['data']['json']['company_info']
        print(data)
        print(comp_info)
        print(pharmacy_name)
        print("Email from front end: ",email_rcvd)
        print("Email from stream: ",email_frm_chain)
        print(password_rcvd)
        print(passw_frm_chain)
        if email_rcvd==email_frm_chain and password_rcvd==passw_frm_chain:
            return render(request, "pharmacy.html",{'comp_info': comp_info,'email':email_rcvd, 'company_info': pharmacy_name})
        else:
            return render(request, "login_pharmacy.html", {'error_message': "Incorrect email or password."})

def pharmorderprod(request):
    print("\nOrdering Products from Distributor")
    if request.method == 'POST':
        email_pharm = request.POST.get('email',None)
        print('\Pharmacy Email: ',email_pharm)
        
        #for fetching out the name of the Distributor name
        result = rpc_connection.liststreamkeyitems(users_pharmacy_stream, email_pharm)
        data = json.dumps(result)
        json_load = json.loads(data)
        comp_info = json_load[0]['data']['json']['company_info'] 
        
        # Now fetch the distributor names and their emails(keys), only names will be shown in the drop down of the distributor.html screen
        response = rpc_connection.liststreamitems(users_distributor_stream)
        json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
        print(json_string)
        json_load = json.loads(json_string)
        keys_company_info = {}
        for item in json_load:
            for key in item['keys']:
                keys_company_info[key] = item['data']['json']['company_info']
        print("\nkeys_company_info:\n",keys_company_info)
        return render(request, "pharmorderprod.html", {'keys_company_info': keys_company_info,'email_dist': email_pharm, 'comp_info' : comp_info})

def distproducts(request):
    email_pharm = request.GET.get('email_pharm', None)
    selected_distributor = request.GET.get('distributor', None) # Manufacturer name being passed from Distributor.html
    comp_info = request.GET.get('comp_info', None) # Manufacturer name being passed from Distributor.html
    print(selected_distributor)
    print("Distributor emails: ",email_pharm)
    print("comp_info :" ,comp_info) 
    x = rpc_connection.subscribe('{}'.format(users_distributor_items_stream)) # Subscribing
    response = rpc_connection.liststreamkeyitems('{}'.format(users_distributor_items_stream), '{}'.format(selected_distributor)) # Based on the manufacturer KEY the data is being fetched
    # Have a logic which fetches out items based on latest_timestamp
    print(len(response))
    if len(response) > 0:
        product_map = {} # Initialize a dictionary to store product data and timestamp for each unique key
        
        for item in response:
            data = item['data']['json']
            key = (data['email'], data['products'][0]['product_code'], data['batchId'], data['products'][0]['product_name'])
            timestamp = item['keys'][-1] # Get the timestamp from the last element of keys
            
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
        return render(request, 'distproducts.html', {'products': products_with_timestamp, 'manufacturer': selected_distributor, 'email_dist': email_pharm, 'comp_info': comp_info})
    else:
        return render(request, 'distproducts.html', {'message': 'No products available'})

@csrf_protect
def pharmcheckout(request):
    print("\n\npharmacy checkout\n\n")
    if request.method == 'POST':
        # Retrieve the cartItems data from the POST request
        cart_items_json = request.POST.get('cartItems', None)
        manufacturer = request.POST.get('manufacturer', None)
        email_dist = request.POST.get('email_dist', None)
        comp_info = request.POST.get('comp_info', None)
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
        dist_key = request.POST.get('email')
        print(dist_key)
        response = rpc_connection.liststreamkeyitems('{}'.format(users_pharmacy_items_stream), '{}'.format(dist_key)) # Based on the manufacturer KEY the data is being fetched
        print(len(response))
        if len(response) > 0:
            product_map = {} # Initialize a dictionary to store product data and timestamp for each unique key

            for item in response:
                data = item['data']['json']
                key = (data['email'], data['products'][0]['product_code'], data['batchId'], data['products'][0]['product_name'])
                timestamp = item['keys'][-1] # Get the timestamp from the last element of keys

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
            return render(request, 'viewdistinventory.html', {'products': products_with_timestamp})
        else:
            return render(request, 'viewdistinventory.html', {'message': 'No products available'})


def pharmreqorder(request):
    print('\nPharmacy publish order request to Distributor')
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
                print(manu_email)
                print(batchId)
                print(productCode)
                print(productName)
                print(timestamp)
                print(quantity)

                timestamp_utc = datetime.datetime.utcnow().isoformat()


                # Publishes the ordered products into the distributor_orders_stream stream accessed by Pharmacy
                txid = rpc_connection.publish('{}'.format(distributor_orders_stream), [comp_info,manufacturer,email_dist,manu_email, batchId, productCode, productName, timestamp_utc],{'json': {'quantity': quantity,
                                                                                                                                                                           'confirmed': 'False',
                                                                                                                                                                           }})
            #render a template or return an appropriate HTTP response, still to be decided
            return HttpResponse("Purchase completed. Thank you!")

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

#Code developed need to replace it. After replacing pass the keys from distributor.html to this func
#Use user_manufacturer_item_stream2(with timestamp included)

