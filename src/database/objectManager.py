from sqlalchemy import Engine, create_engine, select
from sqlalchemy.orm import Session

class ObjectManager:

    __engine: Engine

    orm = Session

    def __init__(self, config):
        link = f'{config["DBServer"]}/{config["DBName"]}'
        sqlalchemy_database_URL = f'mysql+pymysql://{config["DBUser"]}:{config["DBPassword"]}@{link}'
        self.__engine = create_engine(sqlalchemy_database_URL)
        self.orm = Session(self.__engine)

    def get(self, object, id):
        return self.orm.get(object, id)

    def select(self, Class):
        return select(Class)

    def execute(self, select):
        return self.orm.execute(select)

    def add(self, object):
        self.orm.add(object)

    def delete(self, object):
        self.orm.delete(object)

    def commit(self):
        self.orm.commit()

    def rollback(self):
        self.orm.rollback()

    def flush(self):
        self.orm.commit()
        self.orm.flush()
