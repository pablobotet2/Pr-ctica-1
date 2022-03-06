#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 17:29:45 2022

@author: pablo
"""

from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array, Queue
from time import sleep
from random import random, randint

"N es cuanto produce cada uno"
N = 20
cap=5
K = 3
NPROD = 3
NCONS = 1


def delay(factor = 3):
    sleep(random()/factor)

def add_data(storage,pid,indices,mutex,last):
    mutex.acquire()
    try:
        indices[pid]=indices[pid]+1        
        for i in range (cap-1,0,-1):
            storage[pid*cap+i]=storage[pid*cap+i-1]
        storage[cap*pid]=randint(0,5)+last[pid]
        last[pid]=storage[cap*pid]
    finally:
        mutex.release()

"Cogemos el dato y lo cambiamos por 0, la idea del bucle es que te devuleve el min y la pos"
"El primer bucle nos devuelve el min y el productor"
"la segunda parte es reorganizar el storage"

def get_data(storage,mutex,indices,last):
    mutex.acquire()          
    try:
        l=[storage[cap*i+indices[i]-1] for i in range(NPROD)]
        minimo=l[0]
        i=0
        while minimo==-1:
           i=i+1
           minimo=l[i]
        productor=l.index(minimo)
        storage[cap*productor+indices[productor]-1]=0
        indices[productor]=indices[productor]-1
    finally:
        mutex.release()
        print("Storage tras escoger el elemento: ")
        for i in range(NPROD*cap):
            print(storage[i])
    return minimo,productor
""
def producer(storage, empty, non_empty, mutex,indices,last):
    for v in range(N):
        print (f"producer {current_process().name} produciendo")
        pid=int(current_process().name.split('_')[1])
        delay(6)
        empty[pid].acquire()
        try:
            add_data(storage, pid,indices,
                     mutex,last)
        finally:    
            non_empty[pid].release()
        print (f"producer {current_process().name} almacenado {v}")
    empty[pid].acquire()
    try:
        storage[pid*cap]=-1
        last[pid]=-1
    finally:    
        non_empty[pid].release()
    
def fin(last):
    return  max(last)==-1

def consumer(storage, empty, non_empty, mutex,queue,indices,last):
    l=[]
    k=[]
    for i in non_empty:
        i.acquire()
    while not(fin(last)):
        
        delay(6)
        valor,pos=get_data(storage,mutex,indices,last)
        print (f"consumer {pos} desalmacenando")
        l.append(valor)
        queue.put(valor)
        print (f"consumer {pos} consumiendo {valor}")
        non_empty[pos].acquire()
        empty[pos].release()
        
    print("Han acabado los productores")
    for i in range (NPROD):#HE INTENTADO HACER EL FINAL DE OTRA MANERA 
        #SÉ QUE N ES LO QUE SE BUSCA. ÚNICAMENTE ORDENA LOS ELEMENTOS SOBRANTES UNA VEZ 
        #HA ACABADO EL MULTIPROCESSING
        for j in range (indices[i]):
            if storage[cap*i+j]!=-1:
                k.append(storage[cap*i+j])
    k.sort()
    l=l+k
    print("La lista de los números obtenidos es: "+str(l))

def main():
    storage = Array('i', NPROD*cap)
    indices=Array('i',NPROD)
    last=Array('i',NPROD)
    queue=Queue()
    for i in range(NPROD):
        indices[i] = 0
        last[i]=0
    for i in range(NPROD*cap):
        storage[i]=0
    #print ("almacen inicial", storage[:], "indice", index.value)

    non_empty = [Semaphore(0) for _ in range(NPROD)]
    empty = [BoundedSemaphore(cap) for _ in range(NPROD)]
    mutex = Lock()

    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(storage, empty, non_empty, mutex,indices,last))
                for i in range(NPROD) ]

    conslst = [ Process(target=consumer,
                      name=f"cons_{i}",
                      args=(storage,empty, non_empty, mutex,queue,indices,last))]

    for p in prodlst + conslst:
        p.start()

    for p in prodlst + conslst:
        p.join()
        
    resultado=[queue.get() for i in range (queue.qsize())]
    return resultado

if __name__ == '__main__':
    main()