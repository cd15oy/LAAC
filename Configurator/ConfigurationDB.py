"""
Landscape Aware Algorithm Configurator
Copyright (C) 2021 Cody Dennis

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
Stores the collection of configurations that have been tested. Organized by run, which allows us to know the sequence in which configs were used.
"""
from Configurator.ConfigurationDefinition import Configuration
import time
from typing import Iterator, List, Union
from Configurator.Run import Run
import sqlite3
import pickle
from random import Random

"""
Wraps the information we have about a particular sequence of configurations 
"""
class RecordTemplate:
    def addRun(self, run: Run) -> None:
        raise NotImplementedError

    def getRuns(self) -> List[Run]:
        raise NotImplementedError

    def reRun(self, val:bool=None) -> Union[None, bool]:
       raise NotImplementedError

    def desirable(self, val:bool=None) ->  Union[None, bool]:
        raise NotImplementedError

    def updatedAt(self) -> int:
        raise NotImplementedError

    def problem(self) -> int:
        raise NotImplementedError

    def id(self) -> int:
        raise NotImplementedError

    def qualities(self) -> List[float]:
        raise NotImplementedError

"""
Defines our database of tested configurations
"""
class ConfigurationDB:

    #Add a run to the DB
    def addRun(self, run: Run) -> None:
        raise NotImplementedError

    #produces a list of configurations which have been flagged for an additional run
    def getReRuns(self) -> List[Run]:
        raise NotImplementedError

    #produces the current desirbale runs 
    def getDesirables(self) -> List[Run]:
        raise NotImplementedError

    #iterate through all records in the database
    def recordGenerator(self) -> Iterator[RecordTemplate]:
        raise NotImplementedError

    #returns any records as new as or newer than time 
    def getNew(self, time: int) -> Iterator[RecordTemplate]:
        raise NotImplementedError

    #returns a generator of generators, each generating all records for a specifc problem 
    def problemGenerator(self) -> Iterator[Iterator[RecordTemplate]]:
        raise NotImplementedError

    #Backup this DB to the specified PATH
    def backup(self, path:str) -> None:
        raise NotImplementedError

    #close the db
    def close(self) -> None:
        raise NotImplementedError
    
"""
A record implementation for accessing records from an sqlite3 backed configuration DB.
"""
class sqlite3Record(RecordTemplate):
    #id is the primary key of the record 
    #db is a connection to the underlying db 
    #problem is the identifier of the problem associated with this record
    def __init__(self, id:int, problem:int, db:sqlite3.Connection):
        #No internal state here, this is just a class for interfacing with out DB
        self._id = id
        self._db = db
        self._problem = problem
        self._qualities = []

    def problem(self) -> int:
        return self._problem 

    def id(self) -> int:
        return self._id 

    #add a run to the record
    def addRun(self, run: Run) -> None:
        cur = self._db.cursor()
        runBlob = pickle.dumps(run)
        cur.execute("  INSERT INTO runs        (run, record) \
                            VALUES                  ({},{},{})".format(runBlob, self._id))

        cur.execute("  UPDATE records \
                            SET modified = {} \
                            WHERE id = {}".format(int(time.time()*1000000), self._id))
        self._db.commit()
        self._qualities.append(run.quality())

    #list the runs associated with the record
    def getRuns(self) -> List[Run]:
        cur = self._db.cursor() 
        cur.execute("   SELECT run \
                        FROM runs \
                        WHERE record = {}".format(self._id))

        return [pickle.loads(row[0]) for row in cur]

    #check or set this records rerun flag
    def reRun(self, val:bool=None) -> Union[None, bool]:
        cur = self._db.cursor()
        if val is None:
            cur.execute("   SELECT rerun \
                            FROM records \
                            WHERE id = {}".format(self._id)) 
            return cur.fetchone()[0] != 0
        else:
            if val:
                rerun = 1 
            else:
                rerun = 0
            cur.execute("   UPDATE records \
                            SET modified = {}, rerun = {} \
                            WHERE id = {}".format(int(time.time()*1000000), rerun, self._id))
            self._db.commit()

    #check or set this records desirable flag
    def desirable(self, val:bool=None) ->  Union[None, bool]:
        cur = self._db.cursor()
        if val is None:
            cur.execute("   SELECT desirable \
                            FROM records \
                            WHERE id = {}".format(self._id)) 
            return cur.fetchone()[0] != 0 
        else:
            if val:
                desirable = 1 
            else:
                desirable = 0
            cur.execute("   UPDATE records \
                            SET modified = {}, desirable = {} \
                            WHERE id = {}".format(int(time.time()*1000000), desirable, self._id))
            self._db.commit()

    #retrieve the modified time of this record 
    def updatedAt(self) -> int:
        cur = self._db.cursor()
        cur.execute("   SELECT modified \
                        FROM records \
                        WHERE id = {}".format(self._id))
        return cur.fetchone()[0]
        
    def qualities(self) -> List[float]:
        return self._qualities
        

"""
A configuration DB backed by sqlite 3.
"""
class sqlite3ConfigurationDB(ConfigurationDB):
    
    #Connect to the DB found at path. If initialize is true, a fresh DB will be initialized.
    def __init__(self, path:str=":memory:", initialize:bool=False, seed:int=None):
        self.rng = Random(seed)
        self.db = sqlite3.connect(path)
        cur = self.db.cursor()
        
        #Attempt to drop any tables that already exist and re-initialize them 
        if initialize:
            cur.execute("DROP TABLE IF EXISTS runs")
            cur.execute("DROP TABLE IF EXISTS records") 

            cur.execute("CREATE TABLE records ( \
                id          INTEGER PRIMARY KEY, \
                problem     INTEGER NOT NULL, \
                config      INTEGER NOT NULL, \
                desirable   INTEGER NOT NULL, \
                rerun       INTEGER NOT NULL, \
                modified    INTEGER NOT NULL \
            )")

            cur.execute("CREATE TABLE runs ( \
                run     BLOB NOT NULL, \
                record  INTEGER NOT NULL, \
                quality REAL NOT NULL, \
                FOREIGN KEY(record) REFERENCES records(id) \
            )")

            self.db.commit()

    #Add a run to the DB
    def addRun(self, run: Run) -> None:

        #TODO: probably need to do this -> stop pickling the entire run, its a waste of time
        #expand the runs table to store more info directly, pickle the alg output json, have run objects lazy load the alg data
        cur = self.db.cursor()

        config = run.runConfigID() 
        problem = run.problem()
        
        #Check for an exists record, and create if none
        cur.execute("SELECT id FROM records WHERE config = {} AND problem = {}".format(config,problem)) 
        result = cur.fetchone()
        if result is None:
            cur.execute(   "   INSERT INTO records    (config, problem, desirable, rerun, modified)\
                                    VALUES                  ({},{},{},{},{})".format(config, problem, 0, 0, int(time.time()*1000000)))
            #self.db.commit()
            cur.execute("SELECT id FROM records WHERE config = {} AND problem = {}".format(config,problem))
            result = cur.fetchone()

        rcrdID = result[0]
        

        runBlob = pickle.dumps(run)

        cur.execute("  INSERT INTO runs        (run, record, quality) \
                            VALUES                  (?,?,?)", (runBlob, rcrdID,run.quality()))

        cur.execute("  UPDATE records \
                            SET modified = {} \
                            WHERE id = {}".format(int(time.time()*1000000), rcrdID))
        self.db.commit()

    #produces a list of configurations which have been flagged for an additional run
    def getReRuns(self) -> List[Configuration]:
        cur = self.db.cursor()

        #grab an example run from each record flagged for rerun
        cur.execute("   SELECT run, record \
                        FROM    runs    INNER JOIN      (SELECT id \
                                                        FROM records \
                                                        WHERE rerun != 0) as RCRDS \
                                        ON runs.record = RCRDS.id  \
                        GROUP BY record ")

        ret = []
        #duplicate the initial config, and return
        for row in cur:
            run = pickle.loads(row[0])
            newConf = run.configurations[0].duplicateParams() 
            ret.append(newConf) 
        
        return ret
        
    #produces the current desirable runs 
    #limit gives the max number of results which should be returned. If there are more than limit results available, a random selection will be returned 
    def getDesirables(self, limit:int=None) -> List[Run]:
        cur = self.db.cursor()

        
        cur.execute("SELECT id \
                    FROM records \
                    WHERE desirable != 0") 

        ids = [row[0] for row in cur] 

        if limit is not None:
            #prevent too large of sample
            if limit > len(ids):
                limit = len(ids)
            ids = self.rng.sample(ids, limit)

        idList = "(" + ",".join([str(x) for x in ids]) + ")"

        #grab an example run from each record flagged for rerun
        cur.execute(f"   SELECT  run \
                        FROM    runs \
                        WHERE record IN {idList}")
                        
        ret = [] 
        for row in cur:
            run = pickle.loads(row[0]) 
            ret.append(run)
        return ret 

    def _generateRecordsForProblem(self, problem):
        cur = self.db.cursor()
        cur.execute("   SELECT id, problem \
                        FROM records \
                        WHERE problem = {}".format(problem))

        for id, problem in cur:
            yield sqlite3Record(id, problem, self.db) 

    #returns a generator of generators, each generating all records for a specifc problem 
    def problemGenerator(self) -> Iterator[Iterator[RecordTemplate]]:
        cur = self.db.cursor() 
        cur.execute("   SELECT DISTINCT problem \
                        FROM records") 

        problems =[row[0] for row in cur] 

        for problem in problems:
            yield self._generateRecordsForProblem(problem)
             
    #iterate through all records in the database
    def recordGenerator(self) -> Iterator[RecordTemplate]:
        return self.getNew(0)

    #returns any records as new as or newer than time 
    def getNew(self, time) -> Iterator[RecordTemplate]:
        cur = self.db.cursor() 
        cur.execute("   SELECT id,problem \
                        FROM records \
                        WHERE modified >= {}".format(time))

        for row in cur:
            yield sqlite3Record(row[0], row[1], self.db) 

        
    #Backup this DB to the specified PATH
    def backup(self, path:str) -> None:
        def progress(status, remaining, total):
            print(f'{remaining} of {total} pages remaining.', end="")
            print("\r", end="")
        bkup = sqlite3.connect(path) 
        print("Writing results")
        with bkup:
            self.db.backup(bkup, pages=1, progress=progress)
        bkup.close()
        print("") 

    #close the db
    def close(self) -> None:
        self.db.close()