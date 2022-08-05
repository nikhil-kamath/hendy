from typing import List, Tuple
import mysql.connector
from pypika import Query, Column, Table
import logging
import pandas as pd

default_configuration = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'unix_socket': '/Applications/MAMP/tmp/mysql/mysql.sock',
    'raise_on_warnings': True
}

def create_table(table_name: str, database: str, data_types: List[Tuple[str, int]], configuration: dict=None):
    """creates table with given name and columns. currently only uses string data. creates auto-increment id column by default.
    
    Args:
        table_name (str): name of table to create
        database (str): name of database to create the table in
        data_types (List[Tuple[str, int]]): list of column names and their varchar size
        configuration (dict, optional): connection configuration to use in mysql.connector.connect. 
    """
    # create sql query to access server
    if configuration is None:
        configuration = default_configuration
    configuration['database'] = database    

    query = f'CREATE TABLE {table_name} (\
        Id int(11) NOT NULL AUTO_INCREMENT, '
    query += ", ".join(f"{name} varchar({size}) NOT NULL" for name, size in data_types)
    query += ", PRIMARY KEY (Id))"
    
    connection = cursor = None
    try:
        connection = mysql.connector.connect(**configuration)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        connection.commit()
        logging.info(f"table {table_name} has been created in database {database}")
    except mysql.connector.Error as error:
        logging.error(f"failed to create SQL table: {error}")
    finally:
        cursor.close()
        connection.close()
        logging.info("closed sql connection")

def create_entry(table_name: str, database: str, data: dict | pd.Series, configuration=None):
    """create an entry in a table

    Args:
        table_name (str): table name
        database (str): database name
        data (_type_): data to create (do not put value for id)
        configuration (_type_, optional): sql connection configuration.
    """
    print(type(data))
    if configuration is None:
        configuration = default_configuration
    configuration['database'] = database
    
    if isinstance(data, pd.Series):
        data = data.to_dict()
    
    table = Table(table_name)
    column_names = data.keys()
    column_values = data.values()
    query = Query \
        .into(table) \
        .columns(*column_names) \
        .insert(*column_values) \
        .get_sql(quote_char=None)
    
    connection = cursor = None
    try:
        connection = mysql.connector.connect(**configuration)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        connection.commit()
        logging.info(f"data {data} has been added to table {table_name} in database {database}")
    except mysql.connector.Error as error:
        logging.error(f"failed to add data: {error}")
    finally:
        cursor.close()
        connection.close()
        logging.info("sql connection closed")
        
def random_rows(table_name: str, database: str, num=1, configuration=None):
    if configuration is None:
        configuration = default_configuration
    configuration["database"] = database
    
    query = f"SELECT * FROM {table_name} \
            ORDER BY RAND() \
            LIMIT {num}"
    
    connection = cursor = None
    result = None
    try:
        connection = mysql.connector.connect(**configuration)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchone()
    except mysql.connector.Error as error:
        logging.error(f"failed to get random column: {error}")
    finally:
        cursor.close()
        connection.close()
        logging.info("sql connection closed")
        return result

def get_row(table_name: str, database: str, column: str, data: str, configuration=None):
    if configuration is None:
        configuration = default_configuration
    configuration["database"] = database
    
    query = f'SELECT * FROM {table_name} \
        WHERE {column}="{data}" \
        LIMIT 1'
    
    connection = cursor = None
    result = None
    try:
        connection = mysql.connector.connect(**configuration)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchone()
    except mysql.connector.Error as error:
        logging.error(f"failed to get column: {error}")
    finally:
        cursor.close()
        connection.close()
        logging.info("sql connection closed")
        return result

    