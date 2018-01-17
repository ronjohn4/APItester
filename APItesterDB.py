from sqlalchemy import schema, types
from sqlalchemy.engine import create_engine
# import sqlalchemy
# import sys
import datetime
from sqlalchemy.sql import text


class DB():
    def __init__(self):
        # self.tdetail = None
        self.db = create_engine('sqlite:///data/APItester.db')
        self.db.echo = False  # Try changing this to True and see what happens
        self.metadata = schema.MetaData()


        if self.db.dialect.has_table(self.db, 'detail'):
            # print('Table: "detail" was found')
            self.tdetail = schema.Table('detail', self.metadata, autoload=True, autoload_with=self.db)
            self.metadata.bind = self.db
        else:
            self.tdetail = schema.Table('detail', self.metadata,
                            schema.Column('id', types.Integer, primary_key=True),
                            schema.Column('config', types.String),
                            schema.Column('datetime', types.String),
                            schema.Column('threads', types.Integer),
                            schema.Column('calls', types.Integer),
                            schema.Column('host', types.String(256)),
                            schema.Column('api', types.String(256)),
                            schema.Column('total_duration', types.String),
                          )
            self.metadata.bind = self.db
            self.metadata.create_all(checkfirst=True)
            print('Table: "detail" was NOT found, was created')


    def dbwriterow(self, config, datetime, threads, calls, host, api, total_duration):
        i = self.tdetail.insert()
        i.execute(config=config, datetime=datetime, threads=threads, calls=calls, host=host, api=api, total_duration=total_duration)

    # todo - execute() against a dictionary
    # must fill in datetime before calling this function()
    def dbwriterows(self):
        i = self.tdetail.insert()
        execute_datetime = datetime.datetime.now()
        # i.execute(datetime=execute_datetime, threads=30, host='host IP', api='', total_duration=0)
        i.execute(
            {'datetime': execute_datetime, 'threads': 42, 'calls': 2, 'host': None, 'api': 'api call', 'total_duration': 0},
            {'datetime': execute_datetime, 'threads': 42, 'calls': 2, 'host': None, 'api': 'api call', 'total_duration': 0},
            {'datetime': execute_datetime, 'threads': 42, 'calls': 2, 'host': None, 'api': 'api call', 'total_duration': 0},
        )


    # todo - this is a sample read, delete when not needed
    # def dbprintfirst(self):
    #     s = self.tdetail.select()
    #     rs = s.execute()
    #
    #     row = rs.fetchone()
    #     print('datetime:', row[0])
    #     print('tbreads:', row['threads'])
    #     print('iterations:', row['iterations'])
    #     print('host:', row.host)
    #     print('api:', row[self.tdetail.c.api])
    #     print('duration:', row.duration)

        # for row in rs:
        #     print(row.name, 'is', row.age, 'years old')


    def dbhostlist(self):
        results = self.db.engine.execute(text('select * from detail group by host order by host'))
        rs = results.fetchall()
        return(rs)

    def dbhosttimestamp(self, host):
        results = self.db.engine.execute(text('select datetime, api, sum(total_duration)/sum(calls) from detail where host="{0}" group by api, datetime order by api, datetime'.format(host)))
        rs = results.fetchall()
        return(rs)

    def dbhosttimestampthreads(self, host):
        results = self.db.engine.execute(text('select datetime, threads from detail where host="{0}" group by datetime order by datetime'.format(host)))
        rs = results.fetchall()
        return(rs)
