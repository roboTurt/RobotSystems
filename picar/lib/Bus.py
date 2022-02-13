
from readerwriterlock import rwlock

class Bus():


    def __init__(self) -> None:
        self.lock = rwlock.RWLockWriteD()
        self.message = None

    def write(self, message) -> None:

        with self.lock.gen_wlock():
            self.message = message 
    
    def read(self):

        with self.lock.gen_rlock():    
        
            if self.message is not None:
                message = self.message
                return message