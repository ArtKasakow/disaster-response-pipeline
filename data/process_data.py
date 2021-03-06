import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    """
    Loading dataset from multiple csv files.
    Next step merging files into one dataframe and returning it.
    
    Input:
    messages_filepath: CSV filepath with stored messages
    categories_filepath: CSV filepath with stored categories
    
    Output:
    df: Merged dataframe of messages and categories data
    """
    
    # load messages dataset
    messages = pd.read_csv(messages_filepath)
    
    # load categories dataset
    categories = pd.read_csv(categories_filepath)
    
    # merge datasets and store in df
    df = messages.merge(categories)
    
    return df

def clean_data(df):
    """ 
    Data cleaning process to remove missing values,
    categorize columns and remove outliers for analyizing data.
  
    Output: 
    df: outputs dataframe with a cleaning process for automated analysis.
  
    """
    
    # create a dataframe of the 36 individual category columns
    categories = df.categories.str.split(';', expand=True)

    # select the first row of the categories dataframe
    row = categories.iloc[0, :]

    # use this row to extract a list of new column names for categories.
    # one way is to apply a lambda function that takes everything 
    # up to the second to last character of each string with slicing
    category_colnames = row.apply(lambda x: x.split('-')[0])
    
    # rename the columns of `categories`
    categories.columns = category_colnames

    # convert category values to just numbers 0 or 1
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].str.split('-').str[1]
    
        # convert column from string to numeric
        categories[column] = categories[column].astype(int)
    
    # clip(limit) values to be either 0 or 1
    categories = categories.clip(0, 1)

    # remove columns with only one value
    one_val_cols = [
        column for column in categories.columns if len(categories[column].unique()) == 1
    ]

    categories = categories.drop(one_val_cols, axis=1)
    
    # drop the original categories column from `df`
    df.drop('categories', axis=1, inplace=True)
    
    # concatenate df and categories into one dataframe
    df = pd.concat([df, categories], axis=1)
    
    # drop duplicates
    df = df.drop_duplicates(subset=['message', 'original'])
    
    return df
    
def save_data(df, database_filename):
    """
    Save the clean dataset into an sqlite database.
    
    """

    # formatting database name properly
    db_name = 'sqlite:///{}'.format(database_filename)

    # initiating SQLAlchemy Engine
    engine = create_engine(db_name)

    # using pandas to save the DataFrame to the database
    df.to_sql('DisasterResponse', engine, index=False, if_exists='replace')

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()