from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import multichain
import json
import configparser

config = configparser.ConfigParser()

# Load the .conf file
print(config.read('./drugs/config.conf'))

# Access configuration values from the default section
users_manufacturer_items_stream = config.get('Section1','users_manufacturer_items_stream')
order_stream = config.get('Section1','order_stream')
users_master_stream = config.get('Section1','users_master_stream') #Need to add different user stream for all users
users_manufacturer_stream = config.get('Section1','users_manufacturer_stream') #Need to add different user stream for all users
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
        comp_info = json_load[0]['data']['json']['company_info']
        print(data)
        print(comp_info)
        print("Email from front end: ",email_rcvd)
        print("Email from stream: ",email_frm_chain)
        print(password_rcvd)
        print(passw_frm_chain)
        if email_rcvd==email_frm_chain and password_rcvd==passw_frm_chain:
            return render(request, "manufacturer.html",{'comp_info': comp_info,'email':email_rcvd})
        else:
            return render(request, "login_manufacturer.html", {'error_message': "Incorrect email or password."})

def manufacturer(request): # Manufacturer Input
    if request.method == 'POST':
        data = json.loads(request.POST.get('product_data'))
        print("----PRODCUCTS fetched from MANUFACTURER.html screen----")
        print(data)
        print("--------\n")

        #NOTE:
        # Currently we a re getting it from the Manufacturer screen as an input
        # Implement the logic where the USERS are present in a stream, while logging in
        # the password and user is verified using the stream, and from the stream the Manufacturer name
        # is fetched.

        manufacturer = data["manufacturer"]
        email = data["email"]
        batchid = data["batchId"]
        print("----MANUFACTURER NAME----")
        print(manufacturer)
        print("----EMAIL----")
        print(email)
        print("--------\n")
        #Manufacturer name will be a key when publishing in the MANUFACTURER stream

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
                "expiry_date": product["expiry_date"]
            }
            structured_json["products"].append(structured_product)
        
        print(structured_json)

        x = rpc_connection.subscribe('{}'.format(users_manufacturer_items_stream))
        #publish data on the chain
        txid = rpc_connection.publish('{}'.format(users_manufacturer_items_stream), [email,batchid], {'json': data})
    if txid:
        return render(request, "manufacturer.html", {"txid": txid})
    else:
        return render(request, "manufacturer.html", {"error": "Failed to publish data to MultiChain"})    

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
            # Now fetch the distributor names and their emails(keys), only names will be shown in the drop down of the distributor.html screen
            response = rpc_connection.liststreamitems(users_manufacturer_stream)
            json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
            print(json_string)
            json_load = json.loads(json_string)
            keys_company_info = {}

            for item in json_load:
                for key in item['keys']:
                    keys_company_info[key] = item['data']['json']['company_info']

            print(keys_company_info)

            return render(request, "Distributor.html", {'keys_company_info': keys_company_info})
        else:
            return render(request, "login_distributor.html", {'error_message': "Incorrect email or password."})




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

def login_check_pharmacy(request): #Implement Password authentication
    print('login_check_manufacturer')
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('passw')
        print(name)
        print(password)
        return HttpResponse("log in pharmacy success!")

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


def products(request):
    selected_manufacturer = request.GET.get('manufacturer', None) #Manufacturer name being passed from Distributor.html
    print(selected_manufacturer)
    x = rpc_connection.subscribe('{}'.format(users_manufacturer_items_stream)) #subscribing
    response = rpc_connection.liststreamkeyitems('{}'.format(users_manufacturer_items_stream), '{}'.format(selected_manufacturer))#Based on the manufacturer KEY the data is being fetched
    print(len(response))
    if len(response)>0:
        response = response[-1]# always fetches the latest record of medicines from the manufacturer stream
        json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
        response = {} #Cleaning the unused response
        print(json_string)
        json_load = json.loads(json_string)
        products = json_load['data']['json']['products']
        return render(request, 'products.html', {'products': products,'manufacturer' : selected_manufacturer})
    else:
        return render(request, 'products.html', {'message': 'No products available'})

@csrf_protect
def checkout(request):
    if request.method == 'POST':
        # Retrieve the cartItems data from the POST request
        cart_items_json = request.POST.get('cartItems', None)
        manufacturer = request.POST.get('manufacturer', None)
        # print(manufacturer)

        if cart_items_json and manufacturer:
            # Parse the JSON data
            cart_items = json.loads(cart_items_json)

            # Do something with the cart_items data (e.g., save to the database, process the order, etc.)
            # For example, you can print it for demonstration purposes
            print(cart_items)

            # You can also render a template or return an appropriate HTTP response
            return render(request, 'checkout.html', {'cart_items': cart_items,'manufacturer' : manufacturer})
    
@csrf_protect
def publish(request):
    if request.method == 'POST':
        # Retrieve the cartItems data from the POST request
        cart_items_json = request.POST.get('cartItems', None)
        #NOTE:
        # Please implement the flow in which whenever the distributor places an order,
        # it first goes to the order confirmation page of the MANUFACTURER.
        # Once manufacturer confirms the order, the quantity of the medicine is minused from the MANUFACTURER stream
        # and new Item is published in the MANUFACTURER stream.

        # Retrieve the manufacturer name from checkout.html from the POST request
        manufacturer = request.POST.get('manufacturer', None)
        print("----MANUFACTURER NAME----")
        print(manufacturer)
        print("--------\n")

        #Also getting the manufacturer name becuase it's a key in the MANUFACTURER 
        if cart_items_json:
            print("----CART ITEMS from frontEND----")
            cart_items = json.loads(cart_items_json)
            print(cart_items)
            print("--------\n")

            #Fetching the products from the MANUFACTURER STREAM to update their quantity
            prev_products = rpc_connection.liststreamkeyitems('{}'.format(users_manufacturer_items_stream), '{}'.format(manufacturer))#Based on the manufacturer KEY the data is being fetched
            prev_products = prev_products[-1]
            prev_products_str = json.dumps(prev_products, indent=4) #Converts OrderedDict to JSON String
            prev_products = {} 
            json_load = json.loads(prev_products_str)
            prev_products = json_load['data']['json']
            print("----PRODCUCTS fetched from MANUFACTURER stream----")
            print(prev_products_str)
            print("--------\n")

            #Logic for subtracting the quantity of the products from the order stream 
            for item_a in cart_items:
                for item_b in prev_products['products']:
                    if item_a['productCode'] == item_b['product_code']:
                        item_b['quantity_in_stock'] -= item_a['quantity']
            updated_items_str = json.dumps(prev_products, indent=4) #Converts OrderedDict to JSON String
            updated_items = json.loads(updated_items_str)
            print("----Updated PRODCUCTS quantity publised to MANUFACTURER STEAM----")
            print(updated_items_str)
            print("--------\n")

            #Publishes the updated quantity of the products into the MANUFACTURER stream
            txid = rpc_connection.publish('{}'.format(users_manufacturer_items_stream), '{}'.format(manufacturer), {'json': updated_items})
           
            #Publises the ordered products into the PRODUCT stream
            txid = rpc_connection.publish('{}'.format(order_stream), '{}'.format('contract'), {'json': {'order' : cart_items}})

            print("ITEMS UPDATED!!")

            #render a template or return an appropriate HTTP response, still to be decided
            return HttpResponse("Purchase completed. Thank you!")