"""
Created on Thu Mar  9 22:51:47 2023

@author: Cristina Pino Bodas
"""


from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Array
import time
import random

"""En esta solución hemos supuesto que no todos los productores acaban a la vez, 
es decir que cada uno tiene un número de producciones. El número máximo de 
producciones es N y el número de procesos es NPROD. 
NMAX lo utilizamos para establecer un intervalo previo de los números que 
se producen."""

NPROD=8
N=7
NMAX=200

    
def productor(lista_compartida, empty, noempty, mutex,i):
    minimo=0 
    iteracciones = random.randint(0,N)
    for j in range(iteracciones):
        num= random.randint(minimo,max(minimo,NMAX))
        minimo = num + 1
        empty.acquire() 
        time.sleep(0.01*i)
        print (f"producer {current_process().name} produciendo")
        add_data(num,i,lista_compartida, mutex)
        noempty.release() #indico que el hueco ya esta lleno y se puede consumir
        print (f"producer {current_process().name} almacenado {num}")
    empty.acquire()
    print(f"producer {current_process().name} has finished")
    add_data(-1,i,lista_compartida, mutex)
    noempty.release()


def add_data(num,i,lista_compartida, mutex):
    mutex.acquire()
    lista_compartida[i]= num
    mutex.release()
    
        
def consumidor(lista_compartida, empty_list, noempty_list,mutex):
     ordenada=[]
     while len([x for x in noempty_list if x is not None]) > 0:
        for noempty in noempty_list:
            if noempty is None:
                continue
            noempty.acquire() #espero a que todos los productores produzcan (No haya huecos vacios)
        
        for i in range(NPROD):
            if lista_compartida[i] == -1:
                noempty_list[i] = None
        
        print (f"{current_process().name} desalmacenando")
        ordenada=get_data(ordenada, lista_compartida, mutex)
        for empty in empty_list:
            try:
                empty.release()
            except:
                pass
        print (f"{current_process().name} consumiendo {ordenada}")
        time.sleep(1.5)
     print(f"lista final {ordenada}")
        
def get_data(ordenada, lista_compartida, mutex):
    mutex.acquire()
    lista =  [x for x in lista_compartida if x >= 0]
    if len(lista) == 0:
        return ordenada
    else:
        minimo = min(lista)
        ordenada.append(minimo)
        for i in range(NPROD):
            lista_compartida[i]= -2
        mutex.release()
        return ordenada
    





def main():
    lista_compartida= Array('i',NPROD)
    for i in range(NPROD):
        lista_compartida[i]= -2
    print ("almacen inicial", lista_compartida[:])
    noempty_list=[ Semaphore(0) for i in range(NPROD)]
    empty_list= [BoundedSemaphore(1) for i in range(NPROD)] 
    mutex= Lock()
    prodlist= [Process(target=productor,name=f'prod_{i}',args=(lista_compartida, empty_list[i], noempty_list[i], mutex,i)) for i in range(NPROD)]
    cons= Process(target=consumidor, name= "Consumidor" , args=(lista_compartida, empty_list, noempty_list,mutex))
    for p in prodlist:
        p.start()
    cons.start()

    for p in prodlist:
        p.join()
    cons.join()
    
if __name__ == '__main__':
    main()  
