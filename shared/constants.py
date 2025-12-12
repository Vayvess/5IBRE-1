class TcpMsg:
    TYPE = '0'
    DATA = '1'
    STATUS = '2'
    ERROR = '3'
    
    # CLIENT TO SERVER
    ROOM_JOIN = '0'

    # SERVER TO CLIENT
    ROOM_JOINED = '0'
