import threading
import os
import time

locker = threading.Lock()

class Parallelism:
    def __init__(self, x=([], [])):
        self.active = 0
        self.data = x
        self.CPUs = os.cpu_count()


    def thread_func(self, v):
        # with locker:
        #    pass
        
        target = (self.active + 1) % 2
        for i in range(v):
            for j in range(v):
                self.data[target][i][j] = self.data[self.active][i][j] + v


    def start_parallel(self):
        threads = []
        for i in range(self.CPUs):
            t = threading.Thread(target=self.thread_func, args=(i, ))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        print("Goodbye ...")
        self.active = (self.active + 1) % 2

d1 = [[0 for _ in range(10)] for _ in range(10)]
d2 = [[-1 for _ in range(10)] for _ in range(10)]
pp = Parallelism((d1, d2))


print("active =", pp.active)
for r in d1:
    print(r)
print()
for r in d2:
    print(r)

pp.start_parallel()

print('-'*19)

print("active =", pp.active)
for r in d1:
    print(r)
print()
for r in d2:
    print(r)


print("active =", pp.active)
for r in d1:
    print(r)
print()
for r in d2:
    print(r)

pp.start_parallel()

print('-'*19)

print("active =", pp.active)
for r in d1:
    print(r)
print()
for r in d2:
    print(r)



"""

def bubble_sort(a=[], reverse=False):
    pointer = 1
    for i in range(len(a)- pointer):
        for j in range(1, len(a)-i):
            if reverse:
                cond = a[j] > a[j-1]
            else:
                cond = a[j] < a[j-1]
            if cond:
                a[j], a[j-1] = a[j-1], a[j]
        pointer = pointer + 1
    return a



def merge_sort(L):
    if len(L) < 2:
        return L
    pivot = len(L) // 2
    LL = merge_sort(L[:pivot])
    RL = merge_sort(L[pivot:])

    sl = []

    while LL and RL:
        hl, *tl = LL
        hr, *tr = RL
        if hl < hr:
            sl.append(hl)
            LL = tl
        elif hl == hr:
            sl.append(hl)
            sl.append(hr)
            LL = tl
            RL = tr
        else:
            sl.append(hr)
            RL = tr
    return sl + LL + RL

import random

x = list(range(20))
random.shuffle(x)
print(x)


print(bubble_sort(x, 0))
print(bubble_sort(x, 1))

print()

print(merge_sort(x))
"""
