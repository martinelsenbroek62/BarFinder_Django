class IPOverUsageException(Exception):
    pass
    '''
    Raise this exception if too much times IP used during the last hour.
    '''


class IPOverTimeException(Exception):
    pass
    '''
    Raise this exception if too little time has passed since last IP usage. 
    '''
