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
key = config.get('Section1','key') #Key - for manufacturer
publisher = config.get('Section1','publisher') #Set a default for Manufacturer, add another for distributors
# print(manufacturer_stream)
# print(key)
# print(publisher)

#Only password required to login users
#Fix it before production
password = {'prd': ['monk', "monk123"], 'mas': ['abi', 'abi123'], 'hos': [
    'hari', 'hari123'], 'buyd': ['dhan', 'dhan123'], 'owner': ['power', 'power123']}
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


def login(request):
    print("login check")
    if request.method == 'POST':
        print("method check")
        uname = request.POST['name']
        passw = request.POST['passw']
        # print('uname : ' + uname)
        # print('passw : ' + passw)
        if passw in password['prd']:
            return render(request, "dealerinput.html")
        elif passw in password["mas"]:
            return render(request, "manufacturer.html")
        elif passw in password["hos"]:
            return render(request, "hospitalinput.html")
        elif passw in password["buyd"]:
            return render(request, "Distributor.html",{'json_string' : lst_of_mfg()})
        elif passw in password["owner"]:
            return render(request, "seedetails.html")
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
        print(data)
        x = rpc_connection.subscribe('{}'.format(manufacturer_stream))
        #publish data on the chain
        txid = rpc_connection.publish('{}'.format(manufacturer_stream), '{}'.format(key), {'json': data})
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
        # print(manufacturer)
        if cart_items_json:
            # Parse the JSON data
            print("--------")
            cart_items = json.loads(cart_items_json)
            print(cart_items)
            print("--------")

            prev_products = rpc_connection.liststreamkeyitems('{}'.format(manufacturer_stream), '{}'.format(manufacturer))#Based on the manufacturer KEY the data is being fetched
            prev_products = prev_products[-1]
            prev_products_str = json.dumps(prev_products, indent=4) #Converts OrderedDict to JSON String
            prev_products_str = json.dumps(prev_products, indent=4) #Converts OrderedDict to JSON String
            prev_products = {} 
            json_load = json.loads(prev_products_str)
            prev_products = json_load['data']['json']
            
            print(prev_products)
            print("--------\n")
            for item_a in cart_items:
                for item_b in prev_products['products']:
                    if item_a['productCode'] == item_b['product_code']:
                        item_b['quantity_in_stock'] -= item_a['quantity']
            #need to add logic for subtracting quantity
            updated_items = json.dumps(prev_products, indent=4)
            updated_items = json.loads(updated_items)
            print(updated_items)
            txid = rpc_connection.publish('{}'.format(manufacturer_stream), '{}'.format(manufacturer), {'json': updated_items})
            txid = rpc_connection.publish('{}'.format(order_stream), '{}'.format('contract'), {'json': {'order' : cart_items}})
            # Do something with the cart_items data
            # For example, you can print it for demonstration purposes
            print("xyz")
            # print(cart_items)

            # You can also render a template or return an appropriate HTTP response
            return HttpResponse("Purchase completed. Thank you!")