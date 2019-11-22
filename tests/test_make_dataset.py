import pandas as pd
from src.data.make_dataset import CHOROPLETH_DATA_FILE, CONVENIENT_DATA_FILE
import src.data.make_dataset as make_dataset


def test_make_df_nicer_format():
    """
    Perform some checks on whether we didn't change anything weird in making the more convenient dataframe to work with
    It should contain the same information as the choropleth dataframe, just differently structured. We're here just
    checking that they're similar
    """

    try:
        df_choropleth = pd.read_csv(CHOROPLETH_DATA_FILE)
        df_convenient = pd.read_csv(CONVENIENT_DATA_FILE)
    except FileNotFoundError:
        make_dataset.main()
        df_choropleth = pd.read_csv(CHOROPLETH_DATA_FILE)
        df_convenient = pd.read_csv(CONVENIENT_DATA_FILE)
        # raise FileNotFoundError("Before running this test, run make_dataset.py to create our processed datafiles")

    both = df_choropleth.groupby(['year', 'country']).agg(population=pd.NamedAgg(column="population", aggfunc=sum),
                                                          suicides_no=pd.NamedAgg(column="suicides_no", aggfunc=sum),
                                                          code=pd.NamedAgg(column="code", aggfunc=lambda x: x[0]),
                                                          ).reset_index()
    both["overall_rate"] = both['suicides_no'] / both['population'] * 100000
    right = df_convenient[["year", "country", "code", "population", "overall_rate", "suicides_no"]]
    pd.testing.assert_frame_equal(both.sort_index(axis=1), right.sort_index(axis=1))  # sort_index to get same col order

    left = df_choropleth.loc[df_choropleth["sex"] == "female"].drop(columns=["sex"], axis=1)
    right = df_convenient[["year", "country", "code", "female_pop", "female_rate", "suicide_num_f"]]
    right.index = list(range(len(right)))
    left.index = list(range(len(left)))
    right = right.rename(columns={"female_rate": "suicides per 100,000",
                                  "suicide_num_f": "suicides_no",
                                  "female_pop": "population"})
    pd.testing.assert_frame_equal(left.sort_index(axis=1), right.sort_index(axis=1))

    left = df_choropleth.loc[df_choropleth["sex"] == "male"].drop(columns=["sex"], axis=1)
    right = df_convenient[["year", "country", "code", "male_pop", "male_rate", "suicide_num_m"]]
    right.index = list(range(len(right)))
    left.index = list(range(len(left)))
    right = right.rename(columns={"male_rate": "suicides per 100,000",
                                  "suicide_num_m": "suicides_no",
                                  "male_pop": "population"})
    pd.testing.assert_frame_equal(left.sort_index(axis=1), right.sort_index(axis=1))


def test_prepare_data_for_choropleth():
    try:
        df_choropleth = pd.read_csv(CHOROPLETH_DATA_FILE)
    except FileNotFoundError:

        raise FileNotFoundError("Before running this test, run make_dataset.py to create our processed datafiles")

    both = df_choropleth.groupby(['year', 'country']).agg(population=pd.NamedAgg(column="population", aggfunc=sum),
                                                          suicides_no=pd.NamedAgg(column="suicides_no", aggfunc=sum),
                                                          code=pd.NamedAgg(column="code", aggfunc=lambda x: x[0]),
                                                          ).reset_index()
    females = df_choropleth[df_choropleth["sex"] == "female"]
    males = df_choropleth[df_choropleth["sex"] == "male"]
    both["suicides per 100,000"] = both['suicides_no'] / both['population'] * 100000

    # pick some random countries and check that male and female population add up to total population
    countries = df_choropleth["country"].unique()

    for country in countries[:50]:
        female_pop = females.loc[(females["country"] == country) & (females["year"] == 1992), "population"].values
        if len(female_pop) == 0:
            continue  # might not have data for this country in the specific year we're looking at
        male_pop = males.loc[(males["country"] == country) & (males["year"] == 1992), "population"].values
        combined_pop = both.loc[(both["country"] == country) & (both["year"] == 1992), "population"].values
        assert combined_pop == female_pop + male_pop
