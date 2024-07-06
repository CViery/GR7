from database import conection


class FaturamentoDb:
    def __init__(self):
        self.conn = conection.Database()
        self.conn
