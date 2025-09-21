
from random import randint #genera id
import time #
import threading #per concorrenza


MAX_QUEUE_SIZE = 5
NUM_CONS = 15
NUM_PROD = 20

def is_empty(queue1):
    return len(queue1) == 0
def is_space(queue1):
    return len(queue1) < MAX_QUEUE_SIZE

def consume(queue1):
    return queue1.pop(0)

def produce(queue1):
    item = randint(0, 100)
    queue1.append(item)
    return item



class Consumer (threading.Thread):
    def __init__(self, queue1, consumer_cv, producer_cv, name):

        threading.Thread.__init__(self, name = name)
        self.queue = queue1
        self.consumer_cv = consumer_cv
        self.producer_cv = producer_cv

    def run(self):
        with self.consumer_cv:
            while is_empty(self.queue):
                self.consumer_cv.wait()

            time.sleep(1)
            print(consume(self.queue))
            self.producer_cv.notify()

class Producer (threading.Thread):
    def __init__(self, queue1, cv_producer, cv_consumer, name):
        threading.Thread.__init__(self, name = name)

        self.queue= queue1
        self.consumer_cv = cv_consumer
        self.producer_cv = cv_producer

    def run (self):
        with self.producer_cv:
            while not is_space(self.queue):
                self.producer_cv.wait()

            time.sleep(1)
            print (produce(self.queue))
            self.consumer_cv.notify()


def main():
    queue = []

    consumers = []

    producers = []

    lock = threading.Lock()
    consumers_cv = threading.Condition(lock=lock)
    producers_cv = threading.Condition(lock=lock)

    for i in range(NUM_CONS) :
        nome = "consumer" + str(i)
        c = Consumer(queue, consumers_cv, producers_cv, nome)

        consumers.append(c)
        c.start()

    for i in range (NUM_PROD) :
        nome = "pRODUCER" + str(i)
        p = Producer(queue, producers_cv, consumers_cv, nome)
        producers.append(p)
        p.start()

    for i in range (15):
        consumers[i].join()
        producers[i].join()
    pass


if __name__ == '__main__':
    main()

