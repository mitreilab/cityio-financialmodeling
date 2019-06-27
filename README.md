# cityio-finmod

### Introduction
Welcome to the Urban Development Financial Simulation Project.

This project was developed by the MIT Real Estate Innovation Lab in conjunction with the MIT Media Lab CityScope 
Platform. 
We developed a model to assess the financial performance of a simulated development project. Our model investigates new 
construction for particular real estate uses in the East Cambridge, Massachusetts market. This project seeks to provide
city stakeholders with a tool to make quantified, informed decisions.

We expect this project to evolve in functionality and complexity. Our long term goal is to develop a platform that 
simulates the first order and second order effects to financial performance of an urban layout. Currently, our first 
version model simulates the development of an independent office building. 

### Model Overview
Our model requires the inputs for an office development pro forma. To obtain these inputs, we use a combination of 
assumptions and data analysis. We use three data sets for analysis. 

To predict rents from the Boston Compstak dataset, we create yearly, OLS regressions for each real estate use case. We 
transform building characteristics into a feature list, and predict an index for rents commencing from 2007 to 2020. 
We use the 2019 prediction as our base rent and the average index growth as the rent growth rate.

To predict operating expenses from the Boston NCREIF dataset, we separate the data by real estate use and calculate 
the operating margin. Then, we apply the mean operating margin to predicted rents to get operating expenses and net 
operating income. We assume operating expenses grow with long-run inflation at 2%.

To predict property terminal values, we analyize cap rates from the Boston RCA dataset. We separate the data by use and 
take the mean cap rates for our model's reversion cap rate.

Since the project is new construction, we assume zero vacancy. For our office development yield, we looked at typical yields for public office REITs and took a value of 7%. For our 
discount rate, we back into the value using exit cap rates, average rent index growth, and a growing perpetuity assumption.


### Software Overview
This project's code is broken up into many seperate modules with particular functions. All modules fall into one of two
categories. First, libraries hold code that the model uses to run. This code supports the data analysis and model setup.
Second, scripts hold code that acts as a wrapper on library methods. The scripts call the module operations to analyize 
the data and simulate the pro forma.



