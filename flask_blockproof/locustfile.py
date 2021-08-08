from locust import HttpUser, TaskSet, task,User, between
import random

class SessionTasks(HttpUser): 
   
   

    @task()
    def login(self):
     self.client.get('/login')

    @task()
    def consult(self):
      self.client.post('/consultar',{'title':'Locust_Estatico_Consulta', 'url':'https://docs.python.org/pt-br/3/tutorial/'})

 
