
seed = 0

def init(s=1337):
    global seed
    seed = s

def integer(low, high):
    """ Return a pseudorandom number from interval [low, high]
    """
    global seed
    seed *= 65537
    seed %= 3571
    return seed % (high - low + 1) + low

def choice(list):
    return list[integer(0, len(list) - 1)]
    
