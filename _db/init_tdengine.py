from wtbonline._db.tsdb_facade import TDFC

def init_tdengine():
    TDFC.init_database()

if __name__ == '__main__':
    init_tdengine()