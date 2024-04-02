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
manufacturer_stream = config.get('Section1','manufacturer_stream')
order_stream = config.get('Section1','order_stream')
users_stream = config.get('Section1','users_stream') #Need to add different user stream for all users
key = config.get('Section1','key') #Key - for manufacturer
publisher = config.get('Section1','publisher') #Set a default for Manufacturer, add another for distributors
# print(manufacturer_stream)
# print(key)
# print(publisher)  

#Only password required to login users
#Fix it before production
password = {'prd': ['monk', "monk123"],
            'mas': ['manufacturer', 'manufacturer'], 
            'buyd': ['distributor', 'distributor'], 
            }










temp = ['patientid', 'doctorId', 'Time', 'Drug Id', 'Amount Paid']



# Configure your MultiChain connection here
rpcuser = config.get('Section1','rpcuser')
rpcpassword= config.get('Section1','rpcpassword')
rpchost = config.get('Section1','rpchost')
rpcport = config.get('Section1','rpcport')
chainname = config.get('Section1','chainname')
rpc_connection = multichain.MultiChainClient(rpchost, rpcport, rpcuser, rpcpassword)

def lst_of_mfg():#Distributor Fetch screen, fetches the data from the chain and displays
    x = rpc_connection.subscribe('{}'.format(manufacturer_stream)) #subscribing
    response = rpc_connection.liststreamkeys(manufacturer_stream)
    json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
    print(json_string)
    json_load = json.loads(json_string)
    numOfMfg = len(json_load)
    lstMfg = [] # list to save the name of the manufactuers
    for i in range(numOfMfg):
        lstMfg.append(json_load[i]['key'])

    print(lstMfg)
    return lstMfg

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

def signup_master(request):
    print("signup-master check")
    return render(request, "email_check_master.html")

def email_check_master(request):
    print("email_check_master")
    x = rpc_connection.subscribe('{}'.format(users_stream))
    if request.method == 'POST':
        # print("method check")
        email = request.POST['email']
        response = rpc_connection.liststreamkeys(users_stream)
        json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
        json_string = json.loads(json_string) #Converts OrderedDict to JSON String
        # print(json_string)
        email_keys = [entry["key"] for entry in json_string]
        print(email_keys)
        for each_email in email_keys:
            if each_email==email:
                print("present")
                return render(request, "login.html") #if the email is present prompt to login master page
        return render(request, "signup-master.html") #if the email is not present then render this page


def signup_manufacturer(request):
    print("signup-manufacturer check")
    return render(request, "email_check_manufacturer.html")


def email_check_manufacturer(request):
    print("email_check_manufacturer")
    x = rpc_connection.subscribe('{}'.format(users_stream))
    if request.method == 'POST':
        # print("method check")
        email = request.POST['email']
        response = rpc_connection.liststreamkeys(users_stream)
        json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
        json_string = json.loads(json_string) #Converts OrderedDict to JSON String
        # print(json_string)
        email_keys = [entry["key"] for entry in json_string]
        print(email_keys)
        for each_email in email_keys:
            if each_email==email:
                print("present")
                return render(request, "login.html") #if the email is present prompt to login master page
        return render(request, "signup-manufacturer.html",{'email': email}) #if the email is not present then render this page
    

def process_registration_manufacturer(request):
    print("process_registration_manufacturer")
    if request.method == 'POST':
        # print("method check")
        email = request.POST.get('email')
        company_info = request.POST['company_info']
        street_address = request.POST['street_address']
        business_details = request.POST['business_details']
        state = request.POST['state']
        city = request.POST['city']
        zip_code = request.POST['zip_code']
        password = request.POST['password']
        license_certification = request.POST['license_certification']
        print(company_info)
        print(street_address)
        print(business_details)
        print(state)
        print(city)
        print(zip_code)
        print(password)
        print(license_certification)
        print(email)
        return HttpResponse("process_registration_manufacturer")

def signup_distributor(request):
    print("signup-distributor check")
    return render(request, "email_check_distributor.html")


def email_check_distributor(request):
    print("email_check_distributor")
    x = rpc_connection.subscribe('{}'.format(users_stream))
    if request.method == 'POST':
        # print("method check")
        email = request.POST['email']
        response = rpc_connection.liststreamkeys(users_stream)
        json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
        json_string = json.loads(json_string) #Converts OrderedDict to JSON String
        # print(json_string)
        email_keys = [entry["key"] for entry in json_string]
        print(email_keys)
        for each_email in email_keys:
            if each_email==email:
                print("present")
                return render(request, "login.html") #if the email is present prompt to login master page
        return render(request, "signup-distributor.html") #if the email is not present then render this page


def signup_pharmacy(request):
    print("Signup-pharmacy check")
    return render(request, "email_check_pharmacy.html")

def email_check_pharmacy(request):
    print("email_check_pharmacy")
    x = rpc_connection.subscribe('{}'.format(users_stream))
    if request.method == 'POST':
        # print("method check")
        email = request.POST['email']
        response = rpc_connection.liststreamkeys(users_stream)
        json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
        json_string = json.loads(json_string) #Converts OrderedDict to JSON String
        # print(json_string)
        email_keys = [entry["key"] for entry in json_string]
        print(email_keys)
        for each_email in email_keys:
            if each_email==email:
                print("present")
                return render(request, "login.html") #if the email is present prompt to login master page
        return render(request, "Signup-pharmacy.html") #if the email is not present then render this page




def login(request):
    print("login check")
    if request.method == 'POST':
        print("method check")
        uname = request.POST['name']
        passw = request.POST['passw']
        # print('uname : ' + uname)
        # print('passw : ' + passw)
        # if passw in password['prd']:
        #     return render(request, "dealerinput.html")
        # elif passw in password["mas"]:
        #     return render(request, "manufacturer.html")
        # elif passw in password["hos"]:
        #     return render(request, "hospitalinput.html")
        # elif passw in password["buyd"]:
        #     return render(request, "Distributor.html",{'json_string' : lst_of_mfg()})
        # elif passw in password["owner"]:
        #     return render(request, "seedetails.html")
        # else:
        #     return render(request, "login.html")
        if passw in password["mas"]:
            return render(request, "manufacturer.html")
        elif passw in password["buyd"]:
            return render(request, "Distributor.html",{'json_string' : lst_of_mfg()})
        else:
            return render(request, "login.html")
    else:
        return render(request, "login.html")


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
        print("----MANUFACTURER NAME----")
        print(manufacturer)
        print("--------\n")
        #Manufacturer name will be a key when publishing in the MANUFACTURER stream

        structured_json = {
            "address": data["address"],
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
        x = rpc_connection.subscribe('{}'.format(manufacturer_stream))
        #publish data on the chain
        txid = rpc_connection.publish('{}'.format(manufacturer_stream), '{}'.format(manufacturer), {'json': data})
    if txid:
        return render(request, "manufacturer.html", {"txid": txid})
    else:
        return render(request, "manufacturer.html", {"error": "Failed to publish data to MultiChain"})               
        

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


def distributor(request):#Distributor Fetch screen, fetches the data from the chain and displays
    x = rpc_connection.subscribe('{}'.format(manufacturer_stream)) #subscribing
    response = rpc_connection.liststreamkeys(manufacturer_stream)
    json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
    print(json_string)
    json_load = json.loads(json_string)
    numOfMfg = len(json_load)
    lstMfg = [] # list to save the name of the manufactuers

    for i in range(numOfMfg):
        lstMfg.append(json_load[i]['key'])

    return render(request, "Distributor.html", {'json_string': lstMfg})

def products(request):
    selected_manufacturer = request.GET.get('manufacturer', None) #Manufacturer name being passed from Distributor.html
    print(selected_manufacturer)
    x = rpc_connection.subscribe('{}'.format(manufacturer_stream)) #subscribing
    response = rpc_connection.liststreamkeyitems('{}'.format(manufacturer_stream), '{}'.format(selected_manufacturer))#Based on the manufacturer KEY the data is being fetched
    response = response[-1]# always fetches the latest record of medicines from the manufacturer stream
    json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
    response = {} #Cleaning the unused response
    print(json_string)
    json_load = json.loads(json_string)
    products = json_load['data']['json']['products']
    return render(request, 'products.html', {'products': products,'manufacturer' : selected_manufacturer})

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
            prev_products = rpc_connection.liststreamkeyitems('{}'.format(manufacturer_stream), '{}'.format(manufacturer))#Based on the manufacturer KEY the data is being fetched
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
            txid = rpc_connection.publish('{}'.format(manufacturer_stream), '{}'.format(manufacturer), {'json': updated_items})
           
            #Publises the ordered products into the PRODUCT stream
            txid = rpc_connection.publish('{}'.format(order_stream), '{}'.format('contract'), {'json': {'order' : cart_items}})

            print("ITEMS UPDATED!!")

            #render a template or return an appropriate HTTP response, still to be decided
            return HttpResponse("Purchase completed. Thank you!")