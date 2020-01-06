#!/usr/bin/env python
# Copyright (c) 2019 Jack Morton <jhm@jemscout.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from nhlscrappo import GameType, ReportType
from nhlscrappo.parsers import ShotParser, RosterParser, HomeTOIParser, \
        EventParser, PlayParser
import nhlscrappo.constants as C

def connect_sql(**params):
    sql_conn = psycopg2.connect(**params)
    sql_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return sql_conn, sql_conn.cursor()

def disconnect_sql(sql_cur, sql_conn):
    sql_cur.close()
    sql_conn.close()
   
def main():
    sql_params = {
        "dbname": "postgres",
        "user": "postgres",
        "password": "REDACTED",
        "host": "nhlscrappo-db.cpmwmqjbkju3.us-east-1.rds.amazonaws.com",
        "port": 5432
    }

    s_start = 2018
    s_end = 2018

    # XXX: check these values fall within an acceptable range

    sql_conn, sql_cur = connect_sql(**sql_params)

    for s in range(s_start, s_end + 1):
        # create regular season database
        nhl_dicto = {"season":s}
        try:
            sql_params["dbname"] = str(nhl_dicto["season"]) + "r"
            sql_command = "CREATE DATABASE \"" + sql_params["dbname"] \
                + "\" OWNER " + sql_params["user"]
            sql_cur.execute(sql_command)
        except psycopg2.errors.DuplicateDatabase:
            pass
        # reconnect to the this database 
        disconnect_sql(sql_cur, sql_conn)
        sql_params["dbname"] = str(nhl_dicto["season"]) + "r"
        sql_conn, sql_cur = connect_sql(**sql_params)

        # create a domain to check unsigned integers
        try:
            sql_command = "CREATE DOMAIN uint2 AS int4 CHECK (VALUE >= 0 " \
                "AND VALUE < 65536)"
            sql_cur.execute(sql_command)
        except psycopg2.errors.DuplicateObject:
            pass

        # iterate through regular season games
        for g in range(1, C.GAME_CT_DICT[s] + 1):
            nhl_dicto = {"season":s, "game_num":g, "game_type":GameType.Regular}
            # create roster tables
            try:
                sql_command = "CREATE TABLE \"" + ("%04i" % g) \
                    + "_roster\" (\"Name\" text, \"Team\" text, " \
                    + "\"Number\" uint2, \"Position\" char)"
                sql_cur.execute(sql_command)
            except psycopg2.errors.DuplicateTable:
                pass
            # fill roster tables
            roster = RosterParser(**nhl_dicto)
            roster.make_soup(local = \
                "/home/j/workspace/nhl-workbook/2018-2019/roster/RO02" \
                 + ("%04i" %g) + ".HTM")
            roster.load_teams()
            roster.load_players()
            # XXX: check for duplicates before INSERT
            for player in roster.rosters["home"]:
                sql_command = "INSERT INTO \"" + ("%04i" % g) + "_roster\" " \
                    + "(\"Name\", \"Team\", \"Number\", \"Position\") " \
                    + "VALUES (\'" + player + "\', \'" + roster.teams["home"] \
                    + "\', " + roster.rosters["home"][player]["num"] + ", " \
                    + "\'" + roster.rosters["home"][player]["pos"] + "\')"
                sql_cur.execute(sql_command)
            for player in roster.rosters["away"]:
                sql_command = "INSERT INTO \"" + ("%04i" % g) + "_roster\" " \
                    + "(\"Name\", \"Team\", \"Number\", \"Position\") " \
                    + "VALUES (\'" + player + "\', \'" + roster.teams["away"] \
                    + "\', " + roster.rosters["away"][player]["num"] + ", " \
                    + "\'" + roster.rosters["away"][player]["pos"] + "\')"
                sql_cur.execute(sql_command)

    disconnect_sql(sql_cur, sql_conn)

if __name__ == "__main__":
    main()
