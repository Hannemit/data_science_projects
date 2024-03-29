# useful tutorial on click: https://www.youtube.com/watch?v=kNke39OZ2k0&feature=youtu.be

# -*- coding: utf-8 -*-

import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import numpy as np
import os
from src.data import add_country_codes

INPUT_FILE = "./data/raw/who_suicide_statistics.csv"
POPULATION_FILE = "./data/raw/total_pop_1960_2018.csv"
META_DATA = "./data/raw/meta_data.csv"
PROCESSED_FILE = "./data/processed/enriched_df.csv"
CHOROPLETH_DATA_FILE = "./data/processed/choropleth_df.csv"
CLEANED_META_DATA_FILE = "./data/processed/cleaned_meta.csv"
CONVENIENT_DATA_FILE = "./data/processed/year_country_data.csv"


def add_age_group_fractions(data_frame):
    """
    Calculate, for each of our 12 age groups, the fraction they represent of the total population size. E.g. the
    0-5 year old group may represent 0.04 of the total population. We only do this for the countries for which we
    have population data (i.e. where the population data is not nan), so that later on we can calculate the average
    age distribution (averaged over the age distributions from different countries).
    :param data_frame: pandas dataframe
    :return: pandas dataframe with some nan rows dropped and an extra fraction_pop column
    """
    assert "year" in data_frame, "year column must be in dataframe"
    assert "country" in data_frame, "country column must be in dataframe"

    # get rid of all rows with nan values in the population column
    data_frame = data_frame.dropna(subset=["population"], how="any", axis=0)
    assert len(data_frame) % 12 == 0, f"length of data frame must be multiple of 12, not {len(data_frame)}"

    # add total population size column
    total_pop = data_frame.groupby(["country", "year"])["population"].sum().reset_index() \
        .rename(columns={"population": "total_population"})
    assert min(total_pop["total_population"]) > 0, "need valid total population count"
    df = pd.merge(data_frame, total_pop, how="left", on=["country", "year"])

    # add column for relative pop size of each age group
    df["fraction_pop"] = df["population"] / df["total_population"]
    assert ((df["fraction_pop"] >= 0) & df["fraction_pop"] <= 1).sum() == len(df)

    return df


def get_age_group_stats(data_frame):
    """
    We want to know, for each of our age groups (we have 6 of them, for both males and females), what fraction of the
    total population they form. E.g., on average the 20-35 female age group may form 7% of the total population size.
    We return a dataframe of length 12 containing the average (averaged over different countries and years) population
    size fraction of our age-sex groups.
    :param data_frame: pandas dataframe
    :return: pandas dataframe of length 12
    """
    assert "fraction_pop" in data_frame, "dataframe needs to have column fraction_pop"
    assert data_frame["fraction_pop"].isna().sum() == 0, "there are nans in dataframe.."

    grouped = data_frame.groupby(["age", "sex"])["fraction_pop"].mean().reset_index()
    total_fraction = grouped["fraction_pop"].sum()
    assert 1.01 >= total_fraction >= 0.99  # check whether overall fraction roughly 1

    # normalize to exactly 1.0 overall fraction
    grouped["fraction_pop"] = grouped["fraction_pop"] / grouped["fraction_pop"].sum()

    return grouped


def clean_population_stats(data_frame):
    """
    Clean our population dataframe. Rename some columns, drop some columns etc..
    :param data_frame: population dataframe
    :return: pandas dataframe, cleaned
    """
    df_pop = data_frame.drop(["Country Code", "Indicator Name", "Indicator Code", "Unnamed: 63"], axis=1)
    df_pop = df_pop.rename(columns={"Country Name": "country"})
    df_pop = df_pop.melt(id_vars=["country"], var_name="year", value_name="total_population")

    df_pop["year"] = df_pop["year"].astype("float")

    return df_pop


def fill_in_missing_populations(suicide_df, df_population, df_age_statistics):
    """
    Some population values were missing in the original suicide dataset (suicide_df), we fill in some of them with
    data obtained from df_population (containing population sizes for a range of countries). More details are provided
    in the readme.
    :param suicide_df: pandas dataframe, WHO suicide statistics
    :param df_population: pandas dataframe with population statistics per country per year
    :param df_age_statistics: pandas dataframe, relative population size (out of total) in a set of age groups
    :return: pandas dataframe, missing population values imputed
    """
    added_age_stats = pd.merge(suicide_df, df_age_statistics, how="left", on=["sex", "age"])
    added_total_pop = pd.merge(added_age_stats, df_population, how="left", on=["country", "year"])

    # now replace any missing values in population with the product of total population and fraction in age group
    mask = added_total_pop["population"].isnull()

    added_total_pop.loc[mask, "population"] = \
        added_total_pop["fraction_pop"][mask] * added_total_pop["total_population"][mask]

    # drop total population column and fraction_pop columns
    added_total_pop.drop(columns=["fraction_pop", "total_population"], inplace=True)

    return added_total_pop


def make_df_nicer_format(data_frame):
    """
    Here we take in the dataframe that comes out "prepare_data_for_choropleth" and transform it so that we have
    one row for every unique (country, year) combination, and columns that gives us the male suicide number and rate,
    the female suicide number and rate, and the combined suicide rate
    :param data_frame: pd Dataframe
    :return: pd Dataframe, restructured.
    """
    df = data_frame.copy()

    # create a column with no duplicates, so that we can use df.pivot with this column as index.
    df["year_country_code"] = df["year"].map(str) + "_" + df["country"] + "_" + df["code"]

    suic_rate_by_sex = df.pivot(index="year_country_code", columns="sex", values="suicides per 100,000").reset_index()
    population_by_sex = df.pivot(index="year_country_code", columns="sex", values="population").reset_index()
    suicide_num_by_sex = df.pivot(index="year_country_code", columns="sex", values="suicides_no").reset_index()

    combined = pd.merge(suic_rate_by_sex, population_by_sex, on="year_country_code", suffixes=("_rate", "_pop"))
    combined = pd.merge(combined, suicide_num_by_sex, on="year_country_code")
    combined = combined.rename(columns={"female": "suicide_num_f", "male": "suicide_num_m"})

    # get year and country columns back
    combined["split"] = combined["year_country_code"].str.split('_')
    combined[["year", "country", "code"]] = pd.DataFrame(combined.split.values.tolist())

    combined = combined.drop(columns=["year_country_code", "split"], axis=1)
    del combined.index.name
    combined.loc[combined["female_pop"] == 0, "female_pop"] = np.nan
    combined.loc[combined["male_pop"] == 0, "male_pop"] = np.nan

    combined["overall_rate"] = (combined["suicide_num_f"] + combined["suicide_num_m"]) / (
                combined["female_pop"] + combined["male_pop"]) * 100000

    # add some extra columns for convenience
    combined["population"] = combined["female_pop"] + combined["male_pop"]
    combined["suicides_no"] = combined["suicide_num_f"] + combined["suicide_num_m"]

    return combined


def prepare_data_for_choropleth(enriched_df):
    """
    TODO: I'm not really using the output dataframe of this function anymore, combine this function with the one above
        here.
    Prepare data for our choropleth world map plot of suicide statistics. We don't care about age groups here, we just
    want to show the total number of suicides per year per country. An alpha-3 country code needs to be added to
    be able to use the choropleth plot. Also we re-format some columns so that the plot looks nicer
    :param enriched_df: pd dataframe, our enriched data, so already applied some transformations on the raw data
    :return: pd dataframe
    """
    df_suicides = enriched_df.copy()

    # drop all rows which have nans, it might happen that the population is Nan but suicides_no is not
    df_suicides = df_suicides.dropna(how="any")

    # total number of suicides per year per sex per country (so summing over different age groups)
    df_suicides = df_suicides.groupby(["year", "sex", "country"]).sum().reset_index()
    df_suicides.loc[df_suicides["population"] == 0, "population"] = np.nan  # otherwise get inf for suicide rate
    df_suicides["suicides per 100,000"] = df_suicides["suicides_no"] / df_suicides["population"] * 100000

    # little data in 2015 and 2016, drop them for plotting purposes
    df_suicides = df_suicides[df_suicides["year"] < 2015]

    # for choropleth hover option, better to use scientific notation / few decimals
    df_suicides["suicides per 100,000"] = df_suicides["suicides per 100,000"].apply(lambda x: "%.2f" % x).astype(float)

    # add alpha-3 country codes for choropleth
    df_suicides["code"] = df_suicides["country"].apply(add_country_codes.get_alpha3_code)

    return df_suicides


def clean_meta_data(meta_data_frame):
    """
    Clean the meta data we have. Remove an unnamed column, rename some other columns, drop some columns
    :param meta_data_frame: pd dataframe
    :return: cleaned pd dataframe
    """
    meta = meta_data_frame.loc[:, ~meta_data_frame.columns.str.contains("^Unnamed")]
    meta = meta.rename(columns={"Country Code": "code", "Region": "region", "IncomeGroup": "income"})
    meta = meta.drop(columns=["SpecialNotes", "TableName"])
    return meta


@click.command()
def main():
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    print(os.getcwd())
    logger = logging.getLogger(__name__)
    logger.info("making final data set from raw data")

    logger.info("reading in data...")
    df = pd.read_csv(INPUT_FILE)
    df_population = pd.read_csv(POPULATION_FILE, skiprows=4)
    meta_data = pd.read_csv(META_DATA)

    logger.info("processing data...")
    age_stats = get_age_group_stats(add_age_group_fractions(df))
    df_pop = clean_population_stats(df_population)
    enriched_df = fill_in_missing_populations(df, df_pop, age_stats)
    meta = clean_meta_data(meta_data)

    logger.info(f"saving enriched dataframe to {PROCESSED_FILE}")
    enriched_df.to_csv(PROCESSED_FILE, index=False)
    logger.info("saved enriched dataframe")

    logger.info(f"saving cleaned meta data to {CLEANED_META_DATA_FILE}")
    meta.to_csv(CLEANED_META_DATA_FILE, index=False)
    logger.info("saved cleaned meta data")

    logger.info(f"Creating data for choropleth plot, saving to {CHOROPLETH_DATA_FILE}")
    choropleth_df = prepare_data_for_choropleth(enriched_df)
    choropleth_df.to_csv(CHOROPLETH_DATA_FILE, index=False)
    logger.info("saved choropleth dataframe")

    logger.info(f"Creating another dataframe in convenient format, saving to {CONVENIENT_DATA_FILE}")
    year_country_df = make_df_nicer_format(choropleth_df)
    year_country_df.to_csv(CONVENIENT_DATA_FILE, index=False)
    logger.info("saved more convenient dataframe")


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
