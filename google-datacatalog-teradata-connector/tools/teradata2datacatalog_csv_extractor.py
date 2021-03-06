#!/usr/bin/python
#
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import logging
import pandas as pd
import teradatasql


def __extract(host, user, password, csv_file_name):
    con = teradatasql.connect(host=host, user=user, password=password)
    cur = con.cursor()

    query = """ SELECT 
                        d.DatabaseName as database_name, d.CreatorName as database_creator, d.OwnerName as database_owner,
                        d.CommentString as database_desc, d.CreateTimeStamp as database_create_time,
                        d.LastAlterTimeStamp as database_update_time,
                        d.LastAlterName as database_update_user,
                        t.TableName as table_name, t.CreatorName as table_creator,
                        t.CommentString as table_desc, t.CreateTimeStamp as table_create_time,
                        t.LastAlterTimeStamp as table_update_time,
                        t.LastAlterName as table_update_user,
                        c.ColumnName as column_name, c.CreatorName as column_creator,
                        c.CommentString as column_desc, c.CreateTimeStamp as column_create_time,
                        c.LastAlterTimeStamp as column_update_time,
                        c.LastAlterName as column_update_user,
                        c.ColumnFormat as column_format, c.ColumnTitle as column_title,
                        c.ColumnType as column_type, c.ColumnLength as column_length,
                        c.DefaultValue as column_default_value, c.Nullable as column_nullable,
                        c.DecimalTotalDigits as column_decimal_total_digits,
                        c.DecimalFractionalDigits as column_decimal_fractional_digits,
                        c.ColumnId as column_id                                           
                    FROM DBC.DatabasesV d
                        JOIN DBC.TablesV t ON t.DataBaseName = d.DataBaseName
                        JOIN DBC.ColumnsV c ON c.TableName = t.TableName
                    WHERE (t.TableKind = 'T' OR t.TableKind = 'V')
                        AND D.DatabaseName NOT IN ('All', 'Crashdumps', 'DBC', 'dbcmngr', 
                            'Default', 'External_AP', 'EXTUSER', 'LockLogShredder', 'PUBLIC', 'SQLJ', 
                            'Sys_Calendar', 'SysAdmin', 'SYSBAR', 'SYSJDBC', 'SYSLIB', 'SYSSPATIAL', 
                            'SystemFe', 'SYSUDTLIB', 'SYSUIF', 'TD_SERVER_DB', 'TD_SYSFNLIB', 
                            'TD_SYSGPL', 'TD_SYSXML', 'TDMaps', 'TDPUSER', 'TDQCD', 'TDStats', 'tdwm')
                    ORDER BY d.DatabaseName, t.TableName, c.columnname;
            """

    # Execute query
    cur.execute(query)

    # Put it all to a data frame
    sql_data = pd.DataFrame(cur.fetchall())
    sql_data.columns = [item[0] for item in cur.description]

    # Close the session
    con.close()

    # Show the data
    logging.info(sql_data.head())

    sql_data.to_csv(csv_file_name, sep=',', encoding='utf-8')


def __parse_args():
    parser = argparse.ArgumentParser(
        description='Command line to sync Teradata metadata to Datacatalog')
    parser.add_argument('--teradata-host',
                        help='Your Teradata server host',
                        required=True)
    parser.add_argument('--teradata-user',
                        help='Your Teradata credentials user',
                        required=True)
    parser.add_argument('--teradata-pass',
                        help='Your Teradata credentials password',
                        required=True)
    parser.add_argument('--raw-metadata-csv',
                        help='Name of the csv that is going to be created',
                        required=True)
    return parser.parse_args()


if __name__ == '__main__':
    # Enable logging
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    args = __parse_args()

    __extract(args.teradata_host, args.teradata_user, args.teradata_pass,
              args.raw_metadata_csv)
