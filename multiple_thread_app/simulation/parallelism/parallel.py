import threading


def parallel_construct(func,
                       p1, p2,
                       p_size=20,
                       c_size=4):
    threads = []
    for i in range(c_size):
        
        t = threading.Thread(target=func, args=args)
        t.start()
        hreads.append(t)

    for t in threads:
        t.join()



def populate(p1=[], p2=[], i):
    p1[i] = 'AAAAAAAAAAAAAAAA'
    p2[i] = 'BBBBBBBBBBBBBBBB'



x = ['????????????' for _ in range(10)]
y = x[:]


for i in range(4):
    
