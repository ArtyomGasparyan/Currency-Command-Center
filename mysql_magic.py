import pandas as pd
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

class MySQLHandler:
    def __init__(self, host, user, password, database):
        """
        Initialize the MySQLHandler with connection parameters.
        
        :param host: MySQL server host
        :param user: MySQL user
        :param password: MySQL password
        :param database: MySQL database name
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')
    
    def check_data_exists(self, table_name, criteria):
        """
        Check if data exists in the table based on given criteria.
        Converts datetime values to date format for comparison.
        
        :param table_name: Name of the MySQL table
        :param criteria: A dictionary of column-value pairs to check for existing data
        :return: Boolean indicating if the data exists
        """
        query = f"SELECT EXISTS (SELECT 1 FROM {table_name} WHERE " + \
                " AND ".join([
                    f"DATE({col}) = :{col}" if isinstance(criteria[col], pd.Timestamp) else f"{col} = :{col}" 
                    for col in criteria.keys()
                ]) + ")"
        
        # Convert datetime values in criteria to date strings for SQL execution
        criteria = {
            col: (val.date() if isinstance(val, pd.Timestamp) else val) 
            for col, val in criteria.items()
        }
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), **criteria).scalar()
            return result == 1
        except SQLAlchemyError as e:
            print(f"Error checking data existence: {e}")
            return False

    def delete_existing_data(self, table_name, criteria):
        """
        Delete existing data from the table based on given criteria.
        Converts datetime values to date format for comparison.
        
        :param table_name: Name of the MySQL table
        :param criteria: A dictionary of column-value pairs to identify rows to delete
        """
        query = f"DELETE FROM {table_name} WHERE " + \
                " AND ".join([
                    f"DATE({col}) = :{col}" if isinstance(criteria[col], pd.Timestamp) else f"{col} = :{col}" 
                    for col in criteria.keys()
                ])
        
        # Convert datetime values in criteria to date strings for SQL execution
        criteria = {
            col: (val.date() if isinstance(val, pd.Timestamp) else val) 
            for col, val in criteria.items()
        }
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(query), **criteria)
        except SQLAlchemyError as e:
            print(f"Error deleting data: {e}")

    def insert_data(self, df, table_name):
        """
        Insert data from a DataFrame into the MySQL table.
        
        :param df: The DataFrame containing data to be inserted
        :param table_name: Name of the MySQL table
        """
        try:
            df.to_sql(name=table_name, con=self.engine, if_exists='append', index=False)
        except SQLAlchemyError as e:
            print(f"Error inserting data: {e}")

    def upsert_data(self, df, table_name, check_columns):
        """
        Check if data exists, delete it if found, and insert new data from the DataFrame.
        
        :param df: The DataFrame containing data to be upserted
        :param table_name: Name of the MySQL table
        :param check_columns: List of columns to check for existing data
        """
        try:
            with self.engine.begin() as conn:  # Transaction context
                for _, row in df.iterrows():
                    criteria = {col: row[col] for col in check_columns}
                    
                    # Convert datetime columns to date for comparison purposes
                    for col in check_columns:
                        if pd.api.types.is_datetime64_any_dtype(row[col]):
                            criteria[col] = row[col].date()
                    
                    if self.check_data_exists(table_name, criteria):
                        self.delete_existing_data(table_name, criteria)
                    
                    # Insert the new row
                    self.insert_data(pd.DataFrame([row]), table_name)
        except SQLAlchemyError as e:
            print(f"Error during upsert operation: {e}")
