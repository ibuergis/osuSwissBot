from sqlalchemy import create_engine, Engine, Connection
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text

import entities
from entities import Entity


class DB:
    __engine: Engine

    __connection: Connection

    def __init__(self, config):
        sqlalchemy_database_URL = f'mysql+pymysql://{config["DBUser"]}:{config["DBPassword"]}@{config["DBServer"]}'
        self.__engine = create_engine(sqlalchemy_database_URL)
        self.__connection = self.__engine.connect()
        self.__execute = lambda a: self.__connection.execute(text(a))

    def getObjectFromEntity(self, entityName: str, values: list):
        Entity = getattr(entities, entityName)
        return Entity(values)

    def get(self, table: str, row: str = '*', filter: dict = None):
        table = table.lower()
        allFilter = []
        for rowName, value in filter.items():
            if type(value) is str:
                value = f'"{value}"'
            else:
                value = str(value)
            allFilter.append(f'`{table}`.`{rowName}`={value}')
        if allFilter != []:
            finishedFilter = f' WHERE {" AND ".join(allFilter)}'
        else:
            finishedFilter = ''
        return self.__execute(f'SELECT {row} FROM {table}{finishedFilter}').all()

    def getObjects(self, table: str, row: str = '*', filter: dict = {}):
        values = self.get(table, row, filter)
        entityName = table[0].upper() + table[1:].lower()
        objects = []
        for value in values:
            objects.append(self.getObjectFromEntity(entityName, value))

        return objects

    def setObject(self, object: Entity):
        data = object.__dict__
        name = object.__class__.__name__.lower()

        tempString = []
        for column, value in data.items():
            if type(value) is str:
                value = f'"{value}"'
            tempString.append(f'`{name}`.`{column}`={value}')

        tempString = ", ".join(tempString)
        self.__execute(f'UPDATE `{name}` SET {tempString} WHERE `{name}`.`id`={data["id"]};')

    def addObject(self, object: Entity):
        data = object.__dict__
        name = object.__class__.__name__.lower()

        columns = []
        values = []
        for column, value in data.items():
            if column == 'id':
                continue
            columns.append(f'`{column}`')

            if type(value) is str:
                value = f'"{value}"'
            else:
                value = str(value)
            values.append(value)

        self.__execute(f'INSERT INTO `{name}` ({", ".join(columns)}) VALUE ({", ".join(values)});')

    def addObjects(self, objects: list[Entity]):
        allValues = []
        for object in objects:
            data = object.__dict__
            name = object.__class__.__name__.lower()

            columns = []
            values = []

            for column, value in data.items():
                if column == 'id':
                    continue
                columns.append(f'`{column}`')

                if type(value) is str:
                    value = f'"{value}"'
                else:
                    value = str(value)
                values.append(value)

            allValues.append(f'({", ".join(values)})')

        self.__execute(f'INSERT INTO `{name}` ({", ".join(columns)}) VALUES {", ".join(allValues)};')

    def deleteObject(self, object):
        name = object.__class__.__name__.lower()
        self.__execute(f'DELETE FROM {name} WHERE {name}.id={object.id}')

    def deleteObjects(self, objects):
        name = objects[0].__class__.__name__.lower()

        values = []
        for object in objects:
            values.append(str(object.id))

        self.__execute(f'DELETE FROM {name} WHERE {name}.id IN ({", ".join(values)})')

    def begin(self):
        self.__connection.begin()

    def commit(self):
        self.__connection.commit()

    def rollBack(self):
        self.__connection.rollback()