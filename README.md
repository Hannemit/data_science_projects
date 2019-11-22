Suicide statistics
==============================

In this project, we analyse data from WHO on suicide statistics from 1980 to roughly 2014, for about 140 countries. The analysis is done in a set of notebooks in `/notebooks/`, each prepended with a number (1 to 4), which do the following:
* `1_data_enrichment` some initial exploration of the data (missing values, combining with other datasets ..), which led to the functions now in src/data/make_dataset.py  
* `2_data_exploration` creating graphs and tables showing suicide statistics  
* `3_make_world_map` creating interactive world maps (made with plotly) showing suicides rates per country over a range of years   
* `4_suicides_and_other_stats` correlating suicide statistics with other statistics related to the countries, such as levels of happiness, economic factors, etc.. This notebook is not finished yet and I'll hopefully continue this in the future   
* `5_more_data_exploration` Continuing notebook 2, performing some extra analyses and looking at some more global overall trends.  

We tried to answer the following questions
1. What are the countries with highest levels of suicide? 
2. What are the countries with lowest levels of suicide?
3. How do suicide rates compare between different age groups? 
4. What is the best way to visualize this data?

To answer these questions we first had to clean the data, more details on that are given in the data section below. Briefly, we found the following results:
1. This question immediately leads to more questions. What exactly do we mean by "highest levels of suicide"? Are we looking for highest average rate, averaged over many years? Or do we want to know the highest levels in a single year? Or are we looking for the countries wich are most often in the top 5? Do we want overall suicide rate, or do we search for countries with the highest male or female rates? The answers to these questions may all be different. For example, we found that the countries with highest averaged (over the years) and combined (over both genders) suicide rates were (from high to low): Lithuania, Hungary, Russia, Sri Lanka and Latvia. If we look at the countries with highest rates in individual years, then the top 5 (again from high to low) becomes: Lithuania, Hungary, Latvia, Estonia and Russia. The highest male suicide rate was found in Lithuania, but Hungary had the highest female rates
2. This question of course has similar subtleties to the previous one. Additionally, many countries with low suicide rates only had low rates due to little data. For example, some countries had 0 or 1 suicides in a year which was probably mostly due to their low population size. It's hard to get a good idea of suicide rate when less than 2 million people live in a country.. Overall though, we found that countries in the Caribbean and Latin America tended to have the lowest rates. 
3. In general, the older you get the higher your suicide rate. However, these claims are not true on a per-country basis, in some countries middle-aged people are a lot more likely to commit suicide than old people. 
4. There are a lot of things to look at in this data and I found myself constantly wondering "ah, but what does this look like for this country? And what about this other country?" I therefore decided that interactive plots are very useful here, with e.g. a dropdown to select different countries. I made a few interactive plots (some of which are shown below).  


![Alt text](./notebooks/figures/highest_rates.png?raw=true "Countries with highest overall rate")


![Alt text](./reports/figures/interactive_age.png?raw=true "")


![Alt text](./reports/figures/interactive_worldmap.png?raw=true "")



Project Organization
=========================

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be
    ├── tests              <- a folder with unit tests
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>

Requirements
=================

## Windows
First, create a virtual environment with conda
`conda create -n my_env python=3.7.4 numpy==1.17.2 scipy==1.3.1`

then install the requirements (`cd` into `data_science_projects` and run the command below) 
`pip install -r requirements.txt`

## Linux
Create the virual environment
`conda create -n my_env python=3.7.4`

and install the requirements (`cd` into `data_science_projects` and run the command below) 
`pip install -r requirements.txt`


How to use
=================
* make sure the requirements in requirements.txt are installed (see above)
* run the following command to be able to import src anywhere in the project:
    `pip install -e .` 
* run `python -m ipykernel install --user --name my_env --display-name "Python (my_env)"` to be able to easily use the virtual environment in a jupyter notebook
* unzip the zip file in data/raw/
* run `python src/data/make_dataset.py` from the root directory. This will read in the raw data in data/raw, process it, and save it in data/processed. These processed data files are used in the notebooks
* we're ready to run the notebooks! From within the virtual environment, just run `jupyter notebook` and this will open a web browser. The notebooks in `/notebooks/` can now be opened and run




Data used
==============================
* `who_suicide_statistics.csv` [[Szamil]. (2017). Suicide in the Twenty-First Century [dataset]. Retrieved from [https://www.kaggle.com/szamil/suicide-in-the-twenty-first-century/notebook]
* `total_pop_1960_2018.csv` and `meta_data.csv` [https://data.worldbank.org/indicator/SP.POP.TOTL?view=map]

#### Cleaning the data

Below is an overview of the data in `who_suicide_statistics.csv`

We have data on the number of suicides and the population size per country per year per gender. However, many of the population sizes are missing. I tried to impute these values using extra population data (as described below). Using this extra data got rid of a lot of our missing values (yay!) but there were still some left. In some of the analyses I had to drop all rows with Nans because sometimes it was the case that i) the population size of a country was not available but ii) there _was_ data on suicide numbers. When aggregating data over multiple years, I cannot simply sum the populations and the suicide numbers over those years because in that case I might e.g. have a 0 (unkown) population size and 20 suicides, which will massively skew the overall rate. 

To find countries with low suicide rates, some extra filtering had to be performed. I removed countries with very little data (e.g. Zimbabwe only had data for a single year), and also countries with a population size below one million (because these countries could have e.g. 1, 2 or 3 suicides in a year, just by chance the rate could be three times as high from one year to another). Sometimes I also removed rows of data where the suicide number was 0 (this happened in Lithuania once, where normally suicide rates are very high. I find it very unlikely that there are suddenly no suicides at all, so I treated it as missing data). 


#### src/data/make_dataset.py
As is shown in notebook (1), there are quite a lot of missing values for the population size of the countries in the suicide dataset. The suicide dataset provides population sizes for different age ranges (e.g. the number of people in France in the 5-14 age range, in the 14-25 age range, etc..). It was a bit hard to find population data for these specific age ranges elsewhere, so instead I used total_pop_1960_2018.csv which has data on the total population size per country. I calculated the average population fractions of each of the age groups (using the countries in who_suicide_statistics.csv that did have age-specific population sizes), and used these averages to infer the age-specific population sizes of the countries where these values were originally missing (using their total population sizes from total_pop_1960_2018.csv.
    
Besides fusing two datasets together, in `make_dataset.py` I enrich the dataset with some new columns and clean up the data, e.g.
* add column with the alpha_3 country code (e.g. FRA for France), which is required for choropleth plots in plotly
* the suicide rate per 100,000 people (the original data only contains absolute numbers)
* in some of the processed datasets I removed the years 2015 and 2016 because they contained very little data



TODO
==============================
* remove folders/files I'm not using
* update requirements.txt and check whether it actually works
* Add some more stuff about what is done in make_dataset.py
