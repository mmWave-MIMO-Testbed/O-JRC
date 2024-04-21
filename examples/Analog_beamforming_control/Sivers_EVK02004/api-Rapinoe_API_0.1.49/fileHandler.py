class FH:
    import json
    
    def __init__(self, fname):
        self.fname = fname

    def read(self, print_error=True):
        try:
            f = open(self.fname)
        except IOError as e:
            if print_error:
                print (self.fname + ' does not exist!')
            raise IOError
        
        res=self.json.load(f)
        f.close()
        return res

    def write(self, a, print_error=True):
        try:
            f = open(self.fname, 'w')
        except IOError as e:
            if print_error:
                print (self.fname + ' does not exist!')
        
        self.json.dump(a,f)
        f.close()

def read(fname, print_error=True):
    fh=FH(fname)
    try:
        return fh.read(print_error)
    except IOError as e:
        raise IOError

def write(fname, data, print_error=True):
    fh=FH(fname)
    try:
        return fh.write(data, print_error)
    except IOError as e:
        raise IOError
