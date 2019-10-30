# useful tutorial on click: https://www.youtube.com/watch?v=kNke39OZ2k0&feature=youtu.be

# -*- coding: utf-8 -*-

import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import os

INPUT_FILE = './data/raw/who_suicide_statistics.csv'
POPULATION_FILE = './data/raw/total_pop_1960_2018.csv'
META_DATA = './data/raw/meta_data.csv'
PROCESSED_FILE = './data/processed/enriched_df.csv'


def add_age_group_fractions(data_frame):
    assert 'year' in data_frame, 'year column must be in dataframe'
    assert 'country' in data_frame, 'country column must be in dataframe'

    # get rid of all rows with nan values in the population column
    data_frame = data_frame.dropna(subset=['population'], how='any', axis=0)
    assert len(data_frame) % 12 == 0, f'length of data frame must be multiple of 12, not {len(data_frame)}'

    # add total population size column
    total_pop = data_frame.groupby(['country', 'year'])['population'].sum().reset_index() \
        .rename(columns={'population': 'total_population'})
    assert min(total_pop['total_population']) > 0, 'need valid total population count'
    df = pd.merge(data_frame, total_pop, how='left', on=['country', 'year'])

    # add column for relative pop size of each age group
    df['fraction_pop'] = df['population'] / df['total_population']
    assert ((df['fraction_pop'] >= 0) & df['fraction_pop'] <= 1).sum() == len(df)

    return df


def get_age_group_stats(data_frame):
    assert 'fraction_pop' in data_frame, 'dataframe needs to have column fraction_pop'
    assert data_frame['fraction_pop'].isna().sum() == 0, 'there are nans in dataframe..'

    grouped = data_frame.groupby(['age', 'sex'])['fraction_pop'].mean().reset_index()
    total_fraction = grouped['fraction_pop'].sum()
    assert 1.01 >= total_fraction >= 0.99  # check whether overall fraction roughly 1

    # normalize to exactly 1.0 overall fraction
    grouped['fraction_pop'] = grouped['fraction_pop'] / grouped['fraction_pop'].sum()

    return grouped


def clean_population_stats(data_frame):
    df_pop = data_frame.drop(['Country Code', 'Indicator Name', 'Indicator Code', 'Unnamed: 63'], axis=1)
    df_pop = df_pop.rename(columns={'Country Name': 'country'})
    df_pop = df_pop.melt(id_vars=["country"], var_name="year", value_name='total_population')

    df_pop['year'] = df_pop['year'].astype('float')

    return df_pop


def fill_in_missing_populations(data_frame, df_population, df_age_statistics):
    added_age_stats = pd.merge(data_frame, df_age_statistics, how='left', on=['sex', 'age'])
    added_total_pop = pd.merge(added_age_stats, df_population, how='left', on=['country', 'year'])

    # now replace any missing values in population with the product of total population and fraction in age group
    mask = added_total_pop['population'].isnull()

    added_total_pop.loc[mask, 'population'] = added_total_pop['fraction_pop'][mask] \
                                              * added_total_pop['total_population'][mask]

    # drop total population column and fraction_pop columns
    added_total_pop.drop(columns=['fraction_pop', 'total_population'], inplace=True)

    return added_total_pop


@click.command()
def main():
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    print(os.getcwd())
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    logger.info('reading in data...')
    df = pd.read_csv(INPUT_FILE)
    df_population = pd.read_csv(POPULATION_FILE, skiprows=4)

    logger.info('processing data...')
    age_stats = get_age_group_stats(add_age_group_fractions(df))
    df_pop = clean_population_stats(df_population)
    enriched_df = fill_in_missing_populations(df, df_pop, age_stats)

    logger.info(f'saving enriched dataframe to {PROCESSED_FILE}')
    enriched_df.to_csv(PROCESSED_FILE, index=False)
    logger.info('saved dataframe')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
