import json
import time
from celery import Celery
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
ADDRESS = "0xCdf8CE69B35A83f6ED0C167c953bD72ADC22e3D3"

#app = Celery('tasks',broker='redis://localhost//')

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self,*args,**kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery

from flask import Flask

flask_app = Flask(__name__)
flask_app.config.update(
    CELERY_BROKER_URL = 'redis://localhost:6379',
    CELERY_RESULT_BACKEND ='redis://localhost:6379'

)

celery = make_celery(flask_app)

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



#@app.task(serializer='json')
@celery.task()
def add_to_blockchain(hashed_data):
     
     
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
        data_autor = data[5]

        #Cleaning title and url
        
        data_clean_url = data_url.split('"')[1]
        data_clean_title = data_title.split('"')[1] 
        data_clean_autor = data_title.split('"')[1] 
               
        #Preparing the content to be sent to the blockchain       

        #Calculating URL hash
        resumoURL= hashlib.sha256(data_clean_url.encode('utf-8')).hexdigest()              
        
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
            #s={"Recibo Block":tx_receipt,"Title":data_clean_title,"URL":data_clean_url,"Hash da URL":resumoURL,"Hash do Conteúdo 1":hashContent,"Hash do Conteúdo 2":hashContent_2,"Autor":data_clean_autor,"Time":timeHour,"Jaccard":jaccard}
            
            #resp = (str(s)) 
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

            
            #s={"Recibo Block":tx_receipt,"Title":data_clean_title,"URL":data_clean_url,"Hash da URL":resumoURL,"Hash do Conteúdo 1":hashContent,"Hash do Conteúdo 2":hashContent_2,"Autor":data_clean_autor,"Time":timeHour,"Jaccard":jaccard}
            

            #resp = (str(s))
            

    #return resp
            



           
            
        
   






            
       





 
           
    
    





