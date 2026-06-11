from peewee import *

db = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = db

class Station(BaseModel):
    station_id = AutoField(primary_key=True)
    station_name = CharField(unique=True, max_length=255)
    class Meta:
        table_name = 'Stations'

    def __str__(self):
        return self.station_name

class Rental(BaseModel):
    rental_id = IntegerField(primary_key=True)
    bike_number = IntegerField()
    start_time = DateTimeField()
    end_time = DateTimeField(null=True)
    duration = IntegerField(null=True)
    rental_station = ForeignKeyField(Station, column_name='rental_station_id')
    return_station = ForeignKeyField(Station, column_name='return_station_id', null=True)

    class Meta:
        table_name = 'Rentals'

def init_db(name):
    path = name if name.endswith('.sqlite3') else name + '.sqlite3'
    db.init(path, pragmas={'foreign_keys': 1})
    db.connect(reuse_if_open=True)
    db.create_tables([Station, Rental], safe=True)
    return db
