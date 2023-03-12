#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 12:17:38 2023

@author: prpa
"""

from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Array
import time
import random

""" Para esta solución hemos supuesto que todos los prooductores tiene el 
mismo número de producciones N, por tanto todos acaban simultáneamente.
NMAX lo utilizamos para establecer límites en la producción de números. """

NPROD=8
N=4
NMAX=200

    
def productor(lista_compartida, empty, noempty, mutex,i):
    minimo=0 
    for j in range(N):
        num= random.randint(minimo,max(minimo,NMAX))
        minimo = num + 1
        empty.acquire() 
        time.sleep(0.01*i)
        print (f"producer {current_process().name} produciendo")
        add_data(num,i,lista_compartida, mutex)
        noempty.release() #indico que el hueco ya esta lleno y se puede consumir
        print (f"producer {current_process().name} almacenado {num}")
    empty.acquire()
    time.sleep(0.01*i)
    print(f"producer {current_process().name} has finished")
    add_data(-1,i,lista_compartida, mutex)
    noempty.release()


def add_data(num,i,lista_compartida, mutex):
    mutex.acquire()
    lista_compartida[i]= num
    time.sleep(0.5)
    mutex.release()
    
        
def consumidor(lista_compartida, empty_list, noempty_list,mutex):
     ordenada=[]
     for i in range(N):
        for noempty in noempty_list:
             noempty.acquire() #espero a que todos los productores produzcan (No haya huecos vacios)
        
        print (f"{current_process().name} desalmacenando")
        ordenada=get_data(ordenada, lista_compartida, mutex)
        for empty in empty_list:
                empty.release()
        print (f"consumer {current_process().name} consumiendo {ordenada}")
        time.sleep(1.5)
     print(f"La lista final es {ordenada}")
        
def get_data(ordenada, lista_compartida, mutex):
    mutex.acquire()
    if -1 in lista_compartida:
        return ordenada
    else:
        minimo = min(lista_compartida)
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