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
stream_name = config.get('Section1','stream_name')
key = config.get('Section1','key')
publisher = config.get('Section1','publisher')
print(stream_name)
print(key)
print(publisher)

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
    x = rpc_connection.subscribe('{}'.format(stream_name)) #subscribing
    response = rpc_connection.liststreamkeys(stream_name)
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
        x = rpc_connection.subscribe('{}'.format(stream_name))
        #publish data on the chain
        txid = rpc_connection.publish('{}'.format(stream_name), '{}'.format(key), {'json': data})
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
    x = rpc_connection.subscribe('{}'.format(stream_name)) #subscribing
    response = rpc_connection.liststreamkeys(stream_name)
    json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
    print(json_string)
    json_load = json.loads(json_string)
    numOfMfg = len(json_load)
    lstMfg = [] # list to save the name of the manufactuers

    for i in range(numOfMfg):
        lstMfg.append(json_load[i]['key'])

    return render(request, "Distributor.html", {'json_string': lstMfg})

def products(request):
    selected_manufacturer = request.GET.get('manufacturer', None)
    print(selected_manufacturer)
    x = rpc_connection.subscribe('{}'.format(stream_name)) #subscribing
    response =  rpc_connection.liststreamqueryitems('{}'.format(stream_name), {'key' : '{}'.format(selected_manufacturer), 'publisher' : '{}'.format(publisher)}) 
    json_string = json.dumps(response, indent=4) #Converts OrderedDict to JSON String
    json_load = json.loads(json_string)
    print(json_load)
    # Your logic for the products view goes here
    return render(request, 'products.html', {'selected_manufacturer': selected_manufacturer})
