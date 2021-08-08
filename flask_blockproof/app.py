from flask import Flask,render_template,request,make_response,abort, redirect, url_for,flash
from eth_typing.ethpm import URI
from web3 import HTTPProvider, Web3
import web3
from web3 import Web3 
from web3.middleware import geth_poa_middleware
import sqlite3,json,requests,hashlib,time,socket,subprocess
from datetime import datetime
from difflib import SequenceMatcher
import os
import asyncio



ETH_PROVIDER_ADDRESS = "http://127.0.0.1:8545"
CONTRACT_ABI = "abi"
ADDRESS = "0xaF83f83a42094AfA82C080bd404b4359a6b205e3"


app = Flask(__name__)

class Object:
    def toJASON(self):
        return json.dumps(self,default=lambda o: o.__dict__,
        sort_keys=True, indent=4)

class Dados:


 def __init__(self):
 
  self.autor = ""
 

 def toJASON(self):
     return json.dumps(self,default=lambda o: o.__dict__,sort_keys=True, indent=4)

COOKIE_NAME = "wpc"
SECRET_KEY = 'STkQ9.9*Qs4#:u+S'
regAux = Dados()

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None       
    if request.method == 'POST': 
        regAux.autor = request.form['username']
        validate_result = validate(request.form['username'],request.form['password'])           
        if validate_result == True:
            response = make_response(render_template('opcoes.html', error = ""))         
            response.set_cookie(COOKIE_NAME, request.form['username'])                 
            return response
        else:
            return render_template('login.html', error = "Usuário não cadastrado!")
     
    if request.method == 'GET':       
       return render_template('login.html') 
    


@app.route("/cadastrar")
def cadastrar():
    return render_template("cadastro.html")   

@app.route("/registrar")
def registrar():
   return render_template("registrar.html")   

@app.route("/consultar")
def consultar():  
    return render_template("consultar.html")  

@app.route("/opcoes")
def opcoes():   
    return render_template("opcoes.html")  


@app.route("/cadastro", methods=['POST', 'GET'])
def cadastro():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        tel = request.form['tel']
        password = request.form['password']

        if not name and password:
         flash('Os campos: nome e senha precisam ser preenchidos')
        
        else:
            #conexão com banco de dados
            conn = get_db_connection() 
            conn.execute('INSERT INTO user (nome,email,telefone,senha) VALUES (?, ?, ?, ?)',
                         (name, email, tel, password))            
            conn.commit()
            conn.close() 

    conn = get_db_connection() 
    user = conn.execute('SELECT * FROM user').fetchall()
    conn.close()            
    #return render_template('users.html', user=user)  --> Para ver os users cadastrados
    return render_template('login.html')               


@app.route('/registrar', methods=['POST', 'GET'])
def registro():  
   cookie_value = request.cookies.get(COOKIE_NAME)  
   if validate_cookie(cookie_value):
    if request.method == 'GET':
        return render_template('opcoes.html', error = "")
    else:  
              
        ans = save_to_blockchain(request.form['title'],request.form['url'],regAux.autor)             
         
        #return render_template('resultado.html' , hash = hash , title = regAux.titulo,url = regAux.clearURL ,hash_url=regAux.urlHash,hash_content1=regAux.hashContent,hash_content2=regAux.hashContent_2,user=regAux.autor,timeHour=regAux.timeHour,jaccard = regAux.jaccard ,error = "Registrado com Sucesso")      
        return render_template('resultado.html' ,error = "Registrado com Sucesso", resp = ans)     
            

@app.route('/consulta', methods=['POST'])
def consulta():     
  temp =  request.form['urlConsulta'] 

  
  listaSender = [] 
  listaAutors = []
  listaTime = []
  listaTitulo = []
  listaContent = []
  listaContent_2 = []
  minlist_minhash1 = []
  listaJaccard = [] 
  minlist_minhash2 = []
  
  listaSender = get_list_sender(temp)
  listaAutors = get_list_user_blockchain(temp)
  listaTitulo = get_list_title(temp)
  listaContent = get_list_content_blockchain(temp)
  listaContent_2 = get_list_content_blockchain_2(temp)
  minlist_minhash1 = get_list_minHash_1(temp)
  minlist_minhash2 = get_list_minHash_2(temp)
  listaJaccard = get_list_jaccard(temp)
  listaTime = get_list_time(temp)

  return render_template('consulta.html',url = temp,hash_url=consulta_urlHash(temp),
  autor = listaAutors, sender = listaSender,
  titulo = listaTitulo, hash_content1 = listaContent, 
  hash_content2 = listaContent_2,timeHour = listaTime,
  jaccard= listaJaccard,list_min1= minlist_minhash1,
  list_min2=minlist_minhash2,qtdReg= get_qtd_reg(temp)) 


def validate(username, password):                
    conn = get_db_connection() 
    user = conn.execute('SELECT * FROM user WHERE nome = ?',
                       (username,))    
    if user == None:
      return False
   
    for user in user:
        if user[1] == username and user[4]==password:
         regAux.autor = username
         conn.close() 
         return True

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def validate_cookie(cookie_value):
    if cookie_value == regAux.autor:
        return True
    else:
        return False

def hashURL(url):
    resp = hashlib.sha256(url.encode('utf-8')).hexdigest()
    return resp

def consulta_urlHash (urlConsulta):
      
    eth_provider_address: URI = URI(ETH_PROVIDER_ADDRESS)
    w3 = Web3(HTTPProvider(eth_provider_address))   
    w3.eth.defaultAccount = w3.eth.accounts[0]
        
    with open("build/contracts/SaveTransaction.json") as file:
        contract_json = json.load(file) #load contract info as JSON
        contract_abi = contract_json['abi'] #fetch contract's abi - necessary to call its functions
        contract = w3.eth.contract(address=ADDRESS, abi=contract_abi)
        
        hash_block = contract.functions.consulta_urlHash(hashURL(urlConsulta)).call()
         
        return hash_block

def get_list_user_blockchain(urlConsulta):
    i = 0
    listaAutors = []
    eth_provider_address: URI = URI(ETH_PROVIDER_ADDRESS)
    w3 = Web3(HTTPProvider(eth_provider_address))   
    w3.eth.defaultAccount = w3.eth.accounts[0]
        
    with open("build/contracts/SaveTransaction.json") as file:
        contract_json = json.load(file) #load contract info as JSON
        contract_abi = contract_json['abi'] #fetch contract's abi - necessary to call its functions
        contract = w3.eth.contract(address=ADDRESS, abi=contract_abi)

        resumoURL = hashURL(urlConsulta)   
        qtdContent = contract.functions.qtdRegContent(resumoURL).call()

        for i in range(qtdContent):      
         listaAutors.append(contract.functions.consulta_user(resumoURL,0).call())
         #regAux.listaFinal.append(contract.functions.consulta_user(resumoURL,i).call())
         
    return listaAutors

def get_qtd_reg (urlConsulta):
       
    eth_provider_address: URI = URI(ETH_PROVIDER_ADDRESS)
    w3 = Web3(HTTPProvider(eth_provider_address))   
    w3.eth.defaultAccount = w3.eth.accounts[0]
        
    with open("build/contracts/SaveTransaction.json") as file:
        contract_json = json.load(file) #load contract info as JSON
        contract_abi = contract_json['abi'] #fetch contract's abi - necessary to call its functions
        contract = w3.eth.contract(address=ADDRESS, abi=contract_abi)        
        resumoURL = hashURL(urlConsulta)   
        qtdContent = contract.functions.qtdRegContent(resumoURL).call()      
        
        return qtdContent

 
def get_list_sender (urlConsulta):
    i = 0
    
    listaSender =[] 
    eth_provider_address: URI = URI(ETH_PROVIDER_ADDRESS)
    w3 = Web3(HTTPProvider(eth_provider_address))   
    w3.eth.defaultAccount = w3.eth.accounts[0]
        
    with open("build/contracts/SaveTransaction.json") as file:
        contract_json = json.load(file) #load contract info as JSON
        contract_abi = contract_json['abi'] #fetch contract's abi - necessary to call its functions
        contract = w3.eth.contract(address=ADDRESS, abi=contract_abi)
        #Calculating URL hash
        resumoURL = hashURL(urlConsulta)         
        qtdContent = contract.functions.qtdRegContent(resumoURL).call()

        for i in range(qtdContent):              
         listaSender.append(contract.functions.consulta_sender(resumoURL,i).call())
         #regAux.listaFinal.append(contract.functions.consulta_sender(resumoURL,i).call())
    return listaSender

def get_list_time(urlConsulta):
    i = 0
    
    listaTime =[] 
    eth_provider_address: URI = URI(ETH_PROVIDER_ADDRESS)
    w3 = Web3(HTTPProvider(eth_provider_address))   
    w3.eth.defaultAccount = w3.eth.accounts[0]
        
    with open("build/contracts/SaveTransaction.json") as file:
        contract_json = json.load(file) #load contract info as JSON
        contract_abi = contract_json['abi'] #fetch contract's abi - necessary to call its functions
        contract = w3.eth.contract(address=ADDRESS, abi=contract_abi)
        #Calculating URL hash
        resumoURL = hashURL(urlConsulta) 
        qtdContent = contract.functions.qtdRegContent(resumoURL).call()

        for i in range(qtdContent):      
         listaTime.append(contract.functions.consulta_time(resumoURL,i).call())
         #regAux.listaFinal.append(contract.functions.consulta_time(resumoURL,i).call())
    return listaTime

def get_list_title(urlConsulta):
    i = 0
    
    listaTitulo = []
    eth_provider_address: URI = URI(ETH_PROVIDER_ADDRESS)
    w3 = Web3(HTTPProvider(eth_provider_address))   
    w3.eth.defaultAccount = w3.eth.accounts[0]
        
    with open("build/contracts/SaveTransaction.json") as file:
        contract_json = json.load(file) #load contract info as JSON
        contract_abi = contract_json['abi'] #fetch contract's abi - necessary to call its functions
        contract = w3.eth.contract(address=ADDRESS, abi=contract_abi)      

       #Calculating URL hash
        resumoURL = hashURL(urlConsulta) 
        qtdContent = contract.functions.qtdRegContent(resumoURL).call()

        for i in range(qtdContent):      
         listaTitulo.append(contract.functions.consulta_title(resumoURL,i).call())
         #regAux.listaFinal.append(contract.functions.consulta_title(resumoURL,i).call())
    return listaTitulo



def save_to_blockchain(title,url,autor):  
    json_data = json.dumps({"title":title , "url":url, "autor":autor})           
    return add_to_blockchain(json_data) 


def get_list_content_blockchain(urlConsulta):  
    i = 0
    listaContent = []
    eth_provider_address: URI = URI(ETH_PROVIDER_ADDRESS)
    w3 = Web3(HTTPProvider(eth_provider_address))   
    w3.eth.defaultAccount = w3.eth.accounts[0]
      
    with open("build/contracts/SaveTransaction.json") as file:
        contract_json = json.load(file) #load contract info as JSON
        contract_abi = contract_json['abi'] #fetch contract's abi - necessary to call its functions
        contract = w3.eth.contract(address=ADDRESS, abi=contract_abi)

        #Calculating URL hash
        resumoURL= hashURL(urlConsulta)     
        qtdContent = contract.functions.qtdRegContent(resumoURL).call()   
            

        for i in range(qtdContent):      
         listaContent.append(contract.functions.consulta_ContentHash(resumoURL,i).call())         
         #regAux.listaFinal.append(contract.functions.consulta_ContentHash(resumoURL,i).call())
         
    return listaContent 

def get_list_content_blockchain_2(urlConsulta):  
    i = 0
      
    listaContent_2 = []
    eth_provider_address: URI = URI(ETH_PROVIDER_ADDRESS)
    w3 = Web3(HTTPProvider(eth_provider_address))   
    w3.eth.defaultAccount = w3.eth.accounts[0]
        
    with open("build/contracts/SaveTransaction.json") as file:
        contract_json = json.load(file) #load contract info as JSON
        contract_abi = contract_json['abi'] #fetch contract's abi - necessary to call its functions
        contract = w3.eth.contract(address=ADDRESS, abi=contract_abi)

        #Calculating URL hash
        resumoURL= hashURL(urlConsulta)
        qtdContent = contract.functions.qtdRegContent(resumoURL).call()
       
        for i in range(qtdContent):      
         listaContent_2.append(contract.functions.consulta_ContentHash_2(resumoURL,i).call())
         #regAux.listaFinal.append(contract.functions.consulta_ContentHash_2(resumoURL,i).call())
        
    return listaContent_2

def get_list_minHash_1(urlConsulta):  
    i = 0    
     
    minlist_minhash1 = []
    eth_provider_address: URI = URI(ETH_PROVIDER_ADDRESS)
    w3 = Web3(HTTPProvider(eth_provider_address))   
    w3.eth.defaultAccount = w3.eth.accounts[0]
        
    with open("build/contracts/SaveTransaction.json") as file:
        contract_json = json.load(file) #load contract info as JSON
        contract_abi = contract_json['abi'] #fetch contract's abi - necessary to call its functions
        contract = w3.eth.contract(address=ADDRESS, abi=contract_abi)

        #Calculating URL hash
        resumoURL = hashURL(urlConsulta) 
        qtdContent = contract.functions.qtdRegContent(resumoURL).call()        

        for i in range(qtdContent):      
         minlist_minhash1.append(contract.functions.consulta_minList_minHash1(resumoURL,i).call())
         #regAux.listaFinal.append(contract.functions.consulta_minList_minHash1(resumoURL,i).call())
    return minlist_minhash1

def get_list_minHash_2(urlConsulta): 
    i = 0 
     
    minlist_minhash2 = []
    eth_provider_address: URI = URI(ETH_PROVIDER_ADDRESS)
    w3 = Web3(HTTPProvider(eth_provider_address))   
    w3.eth.defaultAccount = w3.eth.accounts[0]
        
    with open("build/contracts/SaveTransaction.json") as file:
        contract_json = json.load(file) #load contract info as JSON
        contract_abi = contract_json['abi'] #fetch contract's abi - necessary to call its functions
        contract = w3.eth.contract(address=ADDRESS, abi=contract_abi)

        #Calculating URL hash
        resumoURL = hashURL(urlConsulta) 
        qtdContent = contract.functions.qtdRegContent(resumoURL).call()

        for i in range(qtdContent):      
         minlist_minhash2.append(contract.functions.consulta_minList_minHash2(resumoURL,i).call())
         #regAux.listaFinal.append(contract.functions.consulta_minList_minHash2(resumoURL,i).call())
    return minlist_minhash2

def get_list_jaccard(urlConsulta):  
    i = 0
   
    listaJaccard = []
    eth_provider_address: URI = URI(ETH_PROVIDER_ADDRESS)
    w3 = Web3(HTTPProvider(eth_provider_address))   
    w3.eth.defaultAccount = w3.eth.accounts[0]
        
    with open("build/contracts/SaveTransaction.json") as file:
        contract_json = json.load(file) #load contract info as JSON
        contract_abi = contract_json['abi'] #fetch contract's abi - necessary to call its functions
        contract = w3.eth.contract(address=ADDRESS, abi=contract_abi)

        #Calculating URL hash
        resumoURL = hashURL(urlConsulta) 
        qtdContent = contract.functions.qtdRegContent(resumoURL).call()        

        for i in range(qtdContent):      
         listaJaccard.append(contract.functions.consulta_jaccard(resumoURL,i).call())
         #regAux.listaFinal.append(contract.functions.consulta_jaccard(resumoURL,i).call())
    return listaJaccard



#Funcao para quebrar a string em partes de tamanho igual a size
def get_features(string,size):
    list_tok =[]
    if size == 0:
        return
    if size > len(string):
        list_tok.append(string)
    else:
      for i in range (0,len(string), size):
          list_tok.append(string[i:i+size:1])
    return list_tok

#Funcao para aplicar a funcao hash em todos os itens da lista
def hash_md5(list_tok,tam):
    lista = []
    for j in range (tam):
        lista.append(hashlib.md5(list_tok[j].encode('utf-8')).hexdigest())
    return lista

def verify(req):
    list_md5 = []
    list_tok = []
    list_hash_min = []
    rep = 0
    list_tok = get_features(req,30)
    while rep < 100:
        list_md5 = hash_md5(list_tok,len(list_tok))
        list_hash_min.append(min(list_md5))
        list_tok = list_md5
        rep = rep + 1
    return list_hash_min


def add_to_blockchain(hashed_data):     
    resp = ''
    eth_provider_address: URI = URI(ETH_PROVIDER_ADDRESS)
    w3 = Web3(HTTPProvider(eth_provider_address))   
    w3.eth.defaultAccount = w3.eth.accounts[0]
        
    with open("build/contracts/SaveTransaction.json") as file:
        contract_json = json.load(file) #load contract info as JSON
        contract_abi = contract_json['abi'] #fetch contract's abi - necessary to call its functions
        contract = w3.eth.contract(address=ADDRESS, abi=contract_abi)

        #Cleaning the string data

        data = hashed_data.split()
        #durty title / url
        data_title = data[1]
        data_url = data[3]
        data_autor = regAux.autor

        #Cleaning title and url
        
        data_clean_url = data_url.split('"')[1]
        data_clean_title = data_title.split('"')[1] 
        data_clean_autor = regAux.autor

             
                  
        #Preparing the content to be sent to the blockchain       

        #Calculating URL hash
        resumoURL = hashURL(data_clean_url)
             
        
        #Getting the time
        now = datetime.now()   
        timeHour = now.strftime('%m/%d/%Y | %H-%M-%S')  

        #Calculating content hash-1       
        req = requests.get(data_clean_url)
        res = hashlib.sha256()
        res.update(req.content)
        resumoContent = res.hexdigest()    

        #Calculating content hash-2
        req2 = requests.get(data_clean_url)
        res2 = hashlib.sha256()
        res2.update(req2.content)
        resumoContent2 = res2.hexdigest()  

      
        if (resumoContent == resumoContent2):            
            #Insiro os dados sem calcular o jaccard
            hashContent = resumoContent
            hashContent_2 = ""
            minlist_minhash1 = ""
            minlist_minhash2 = ""
            jaccard = ""
            hashContent = resumoContent
            tx_hash = contract.functions.insertTransaction(resumoURL,hashContent,hashContent_2,data_clean_autor,timeHour,data_clean_title,minlist_minhash1,minlist_minhash2,jaccard).transact()                    
            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash) 
            s={"Recibo Block":tx_receipt,"Title":data_clean_title,"URL":data_clean_url,"Hash da URL":resumoURL,"Hash do Conteúdo 1":hashContent,"Hash do Conteúdo 2":hashContent_2,"Autor":data_clean_autor,"Time":timeHour,"Jaccard":jaccard}
            
            resp = (str(s)) 
        else:      
            
            hashContent = resumoContent
            hashContent_2 = resumoContent2
            list_hash_min_1 = verify(req.text)
            list_hash_min_2 = verify(req2.text)
           
            minlist_minhash1 = str(list_hash_min_1)            
            minlist_minhash2 = str(list_hash_min_2)
            jaccard= str(float(len(set(list_hash_min_1)&set(list_hash_min_2))) / float(len(set(list_hash_min_1)| set(list_hash_min_2) )))

            
            tx_hash = contract.functions.insertTransaction(resumoURL,hashContent,hashContent_2,data_clean_autor,timeHour,data_clean_title,minlist_minhash1,minlist_minhash2,jaccard).transact()                    
            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash) 

            
            s={"Recibo Block":tx_receipt,"Title":data_clean_title,"URL":data_clean_url,"Hash da URL":resumoURL,"Hash do Conteúdo 1":hashContent,"Hash do Conteúdo 2":hashContent_2,"Autor":data_clean_autor,"Time":timeHour,"Jaccard":jaccard}
            

            resp = (str(s))
            

    return resp
            