from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array, Queue
from time import sleep
from random import random, randint

"N es cuanto produce cada uno"
N = 20
K = 3
NPROD = 3
NCONS = 1


def delay(factor = 3):
    sleep(random()/factor)

"index es a quien le toca"
def add_data(storage, data, pid,  mutex):
    mutex.acquire()
    try:
        storage[pid] = randint(0,5) + data.value
        delay(6)
    finally:
        mutex.release()

"Cogemos el dato y lo cambiamos por 0, la idea del bucle es que te devuleve el min y la pos"
def get_data(storage,mutex,data):
    mutex.acquire()
    print(storage[0],storage[1],storage[2])
    i=1
    m=storage[0]
    pos=0
    while m==-1:
        m=storage[i]
        pos=i
        i=i+1
    try:
        for i,c in enumerate(storage):
            if c<m and c!=-1:
                m=c
                pos=i
        data.value=m
        storage[pos]=0
    finally:
        mutex.release()
    return data.value,pos

""
def producer(storage, empty, non_empty, mutex,data):
    for v in range(N):
        print (f"producer {current_process().name} produciendo")
        pid=int(current_process().name.split('_')[1])
        delay(6)
        empty[pid].acquire()
        try:
            add_data(storage,data, pid,
                     mutex)
        finally:    
            non_empty[pid].release()
        print (f"producer {current_process().name} almacenado {v}")
    empty[pid].acquire()
    storage[pid]=-1
    non_empty[pid].release()
    
def hay_productor(storage):
    res=False
    i=0
    while i<len(storage) and not(res):
        if storage[i]!=-1:
            res=True
        i=i+1
    return res

def consumer(storage, data, empty, non_empty, mutex):
    l=[]
    for i in non_empty:
        i.acquire()
    while hay_productor(storage):
        valor,pos=get_data(storage,mutex,data)
        l.append(valor)
        empty[pos].release()
        non_empty[pos].acquire()
    print("Ya no hay productores")
    print(l)

def main():
    storage = Array('i', K)
    data=Value('i',0)
    for i in range(K):
        storage[i] = 0
    #print ("almacen inicial", storage[:], "indice", index.value)

    non_empty = [Semaphore(0) for _ in range(NPROD)]
    empty = [Lock() for _ in range(NPROD)]
    mutex = Lock()

    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(storage, empty, non_empty, mutex,data))
                for i in range(NPROD) ]

    conslst = [ Process(target=consumer,
                      name=f"cons_{i}",
                      args=(storage, data,empty, non_empty, mutex))]

    for p in prodlst + conslst:
        p.start()

    for p in prodlst + conslst:
        p.join()
        

if __name__ == '__main__':
    main()
