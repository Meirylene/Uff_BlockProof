'''
Important docs
https://web3py.readthedocs.io/en/stable/web3.eth.html#web3.eth.Eth.getTransaction
https://web3py.readthedocs.io/en/stable/web3.eth.html#web3.eth.Eth.getTransactionReceipt
import hashlib
import json
import os



from flask import Flask, request, jsonify
from hexbytes import HexBytes
from web3 import Web3, HTTPProvider
from eth_typing.ethpm import URI
from web3.datastructures import AttributeDict

ETH_PROVIDER_ADDRESS: URI = URI('http://127.0.0.1:7545')
contract_json_path = os.environ.get('DEPLOYED_CONTRACT_BUILD')
contract_address = os.environ.get('DEPLOYED_CONTRACT_ADDRESS')
with open(contract_json_path) as f:
    info_json = json.load(f)
    contract_abi = info_json["abi"]

app = Flask(__name__)
w3 = Web3(HTTPProvider(ETH_PROVIDER_ADDRESS))
# TODO: how do we choose the payer?
payer_account = w3.eth.accounts[0]
w3.eth.defaultAccount = w3.eth.accounts[0]
contract = w3.eth.contract(address=contract_address, abi=contract_abi)


def add_to_blockchain(hashed_data):
    # mock_tx_receipt = AttributeDict(  # noqa
    #     {'transactionHash': HexBytes('0x9ab9e543bb9a8ae60aff642760db007a6c8ad659a8f2705cc40eab965b82070b'),
    #      'transactionIndex': 0,
    #      'blockHash': HexBytes('0x917c5d69b52c2f7b9ad02cf25f9e8fb816f5df6b658eb6d746925fdbf57e4131'),
    #      'blockNumber': 17, 'from': '0xd79c1EcD567E59d98E9520B32f8bAfe129A7B3b8',
    #      'to': '0x82cc31Cc6475E9aaf92Aa43C28ec1e6DA6979a89', 'gasUsed': 125660, 'cumulativeGasUsed': 125660,
    #      'contractAddress': None, 'logs': [], 'status': 1, 'logsBloom': HexBytes('0x00000...')}),

    tx_hash = contract.functions.saveTransaction(hashed_data, w3.eth.defaultAccount).transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    #import ipdb;ipdb.set_trace()
    # TODO: retrieve values to the client, cannot use `view` function because of concurrency
    # https://solidity.readthedocs.io/en/develop/contracts.html#events
    # TODO: is mutating the state enough to identify everything?
    return tx_receipt


@app.route('/add-transaction', methods=['POST'])
def add_transaction():
    # Validation
    if not request.data:
        return jsonify({'error': 'Data must be passed in payload'}), 400
    payload = request.json.get('payload', None)
    if not payload:
        return jsonify({'error': 'payload cannot be empty'}), 400

    hashed_data = hashlib.sha256(payload.encode()).hexdigest()
    wpc_response = add_to_blockchain(hashed_data)

    # response_data = jsonify(wpc_response)
    #return response_data
    
    return 'x'


@app.route('/list-transactions', methods=['GET'])
def list_transactions():
    # TODO: not sure we will need it.
    return jsonify([])
'''
from locust import HttpUser, TaskSet, task,User, between
import random

class SessionTasks(HttpUser): 
   
   

    @task()
    def login(self):
     self.client.get('/login')

    @task()
    def consult(self):
      self.client.post('/consultar',{'title':'Locust_Estatico_Consulta', 'url':'https://docs.python.org/pt-br/3/tutorial/'})

   # @task()
   # def registros(self):
   #   vet =[]

   #   vet.append('https://gshow.globo.com/realities/bbb/bbb21/casa-bbb/noticia/no-bbb21-arthur-fala-sobre-carla-diaz-nao-estou-forcando-a-barra.ghtml')
   #   vet.append('https://docs.python.org/pt-br/3.7/library/random.html')
   #   vet.append('http://www.ic.uff.br/index.php/pt/departamento/docentes')
   #   vet.append('http://pythonclub.com.br/testes-de-carga-com-o-locust.html#:~:text=O%20Locust%20%C3%A9%20baseado%20em,conceito%20de%20Master%20e%20Slave.')
   #   vet.append('https://blog.mandic.com.br/artigos/5-passos-simples-para-automatizar-testes-com-selenium-e-jmeter/')
   #   vet.append('https://blog.mandic.com.br/artigos/5-passos-simples-para-automatizar-testes-com-selenium-e-jmeter/')
   #   vet.append('https://globoesporte.globo.com/ginastica-artistica/noticia/arthur-nory-tem-casa-invadida-e-medalhas-roubadas-valor-gigante.ghtml')
   #   vet.append('https://docs.python.org/3/')
   #   vet.append('https://flask.palletsprojects.com/en/1.1.x/')
   #   vet.append('https://osquery.readthedocs.io/en/latest/')
      #var = "https://g1.globo.com/sp/sao-paulo/noticia/2020/12/07/doria-diz-que-vacinacao-contra-covid-19-em-sp-comeca-no-dia-25-de-janeiro-em-profissionais-de-saude-indigenas-e-quilombolas.ghtml"
      #self.client.post('/registrar',{'title':'Locust_Estatico', 'url':'https://docs.python.org/pt-br/3/tutorial/'})
  #    self.client.post('/registrar',{'title':'Locust_Dinamico', 'url':vet[random.randint(0, 9)]})
     
     
    


     


    
   


