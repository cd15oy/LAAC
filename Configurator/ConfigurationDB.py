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

#TODO: We want to store up to N runs from the top X percent of observed runs. Basically we hope that through the first random, but progressively more targeted sampling we do, we'll end up with a variety of configurations which produced strong performance and obviously, as time goes on we should collect more and more runs. We want to limit the total amount of data we hold on to though, so instead we need to store the quality of the Xth best run for each problem, then any runs with better (or maybe close) quality can be kept. Once the total number of stored runs reachs/exceeds N we can start also deleteing random/or the worse stored runs to make room for new examples.
#strat: store the total number of runs consider over all time, and store the actual position of the Xth best. Anything worse than the Xth best can just be dropped after we updated the total runs count 
#anything better than the xth best can be kept, but we need to update the total count, and the estimated position of the xth best relative to all considered runs
#ex, if we find a new run better than the xth best, then the position of the xth best should move down by 1 
#Once we have N stored runs, we can just assume our threshold value is sufficient/does not need to be updated 
#after that we can replace a random store run with any new run which is better than our threshold
#alternatively, we could replace the worst and update the threshold
#or just replace random runs among the 50% worse stored runs 
##this option means we're still storing the N/2 best runs we EVER observed, but also a random sampling of "good" runs, sounds like a nice balance between exploration and exploitation
#BEFORE you spend a lot of time on this, try deleting the stored solutions/states first, since we don't need them after calculating characteristics
#though regardless we still need to update this to avoid walking the entire DB of stored runs over and over


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
    #TODO: a record should know which problem it's associated with 
    #id is the primary key of the record 
    #con is a connection to the underlying db 
    def __init__(self, id:int, problem:int, db:sqlite3.Connection):
        #No internal state here, this is just a class for interfacing with out DB
        self.id = id
        self.db = db
        self.problem = problem

    #add a run to the record
    def addRun(self, run: Run) -> None:
        cur = self.db.cursor()
        runBlob = pickle.dumps(run)
        cur.execute("  INSERT INTO runs        (run, record) \
                            VALUES                  ({},{},{})".format(runBlob, self.id))

        cur.execute("  UPDATE records \
                            SET modified = {} \
                            WHERE id = {}".format(int(time.time()*1000000), self.id))
        self.db.commit()

    #list the runs associated with the record
    def getRuns(self) -> List[Run]:
        cur = self.db.cursor() 
        cur.execute("   SELECT run \
                        FROM runs \
                        WHERE record = {}".format(self.id))

        return [pickle.loads(row[0]) for row in cur]

    #check or set this records rerun flag
    def reRun(self, val:bool=None) -> Union[None, bool]:
        cur = self.db.cursor()
        if val is None:
            cur.execute("   SELECT rerun \
                            FROM records \
                            WHERE id = {}".format(self.id)) 
            return cur.fetchone()[0] != 0
        else:
            if val:
                rerun = 1 
            else:
                rerun = 0
            cur.execute("   UPDATE records \
                            SET modified = {}, rerun = {} \
                            WHERE id = {}".format(int(time.time()*1000000), rerun, self.id))
            self.db.commit()

    #check or set this records desirable flag
    def desirable(self, val:bool=None) ->  Union[None, bool]:
        cur = self.db.cursor()
        if val is None:
            cur.execute("   SELECT desirable \
                            FROM records \
                            WHERE id = {}".format(self.id)) 
            return cur.fetchone()[0] != 0 
        else:
            if val:
                desirable = 1 
            else:
                desirable = 0
            cur.execute("   UPDATE records \
                            SET modified = {}, desirable = {} \
                            WHERE id = {}".format(int(time.time()*1000000), desirable, self.id))
            self.db.commit()

    #retrieve the modified time of this record 
    def updatedAt(self) -> int:
        cur = self.db.cursor()
        cur.execute("   SELECT modified \
                        FROM records \
                        WHERE id = {}".format(self.id))
        return cur.fetchone()[0]

"""
A configuration DB backed by sqlite 3.
"""
class sqlite3ConfigurationDB(ConfigurationDB):
    
    #Connect to the DB found at path. If initialize is true, a fresh DB will be initialized.
    def __init__(self, path:str=":memory:", initialize:bool=False):
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
                FOREIGN KEY(record) REFERENCES records(id) \
            )")

            self.db.commit()

    #Add a run to the DB
    def addRun(self, run: Run) -> None:
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

        cur.execute("  INSERT INTO runs        (run, record) \
                            VALUES                  (?,?)", (runBlob, rcrdID))

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
        
    #TODO: this should be updated to accept a param for how many, and return a random selection 
    #see google for efficient ways to grab random or randomish selections from tables in sqlite
    #produces the current desirable runs 
    def getDesirables(self) -> List[Run]:
        cur = self.db.cursor()

        #grab an example run from each record flagged for rerun
        cur.execute("   SELECT run \
                        FROM    runs    INNER JOIN      (SELECT id \
                                                        FROM records \
                                                        WHERE desirable != 0) as RCRDS \
                                        ON runs.record = RCRDS.id ")

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