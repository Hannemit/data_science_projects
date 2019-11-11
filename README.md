Suicide statistics
==============================

In this project, we analyse data from WHO on suicide statistics from 1985 to roughly 2014, for about 140 countries. The analysis is done in a set of notebooks, each prepended with a number (1 to 4), which do the following:
1. some initial exploration of the data (missing values, combining with other datasets ..), which led to the functions now in src/data/make_dataset.py
2. creating graphs and tables showing suicide statistics
3. creating interactive world maps (made with plotly) showing suicides rates per country over a range of years 
4. correlating suicide statistics with other statistics related to the countries, such as levels of happiness, economic factors, etc.. 

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
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
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

## First, create a virtual environment:

#### Windows
First, create a virtual environment with conda  
`conda create -n my_env python=3.7.4 numpy==1.17.2 scipy==1.3.1`

#### Linux
Create the virual environment  
`conda create -n my_env python=3.7.4`

## Then install the requirements

Activate the virtual environment with  
`conda activate my_env`  

then `cd` into `data_science_projects` and run the command below  
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
