`cassandra` **forecasts data in the future** using the best combination of trend, seasonality and  exponential smoothing, found with automatic train test split. Results can be saved easily, as text and plot.

These is the first version pubblished, better documentation will be written in the future. Here is a quick guide.

Cassandra creates a 'Forecast' folder in your home directory: add all the csv data to forecasts in its 'input' subfolder; the corespondent saved outputs will be placed in the 'output' subfolder. 

here is bluprint code
```
import cassandra as c

file_name = "my_data" # no need to specify csv extension or folder path

data = c.read_data(file_name, delimiter = ',', header = 1, form = "%Y-%m-%d") # delimiter is the character separating columns in the text file. form is the date time form specifying how to interpret datetime objects
# note: the first column is for date time data

data.set_name(file_name); data.set_unit('score') # these will appear in the plot

data.set_forecast_length(12); # it sets how many points in the future to forecasts from the last point

data.backup() # optionally to save the state of data before applying changes, the state can be recovered with data.restore()
# note that a string can be added to backup and restore different versions eg: data.backup('pre-fit'); data.restore('pre-fit')

data.auto() # this function automatically finds the best recepy to get best forecast
# its arguments are 
# trend = True to find and add best trend
# seasons = True to find and add best seasonality
# es = True, to find and add best exponential smoothing
# log = True, for verbosity on
# save = False, to save forecasting results 
# method = 'test' specifies how to find the best recipy, using the 'data' (original signal) 'test' component of train test split or 'Data' = train + test (more balanced error between train and test)

data.find_trend(method = 'test', order = 5, log = False, set = True) # to find the best trend alone up to order 5 (in this case), with given method (see above)'; set = True is used to fit or not the actuall best trend found 

data.find_seasons(threshold = 0, detrend = 3, log = False, set = True) # to find the seasonalities present in the signal. detrending helps the algorithm

data.find_es(method = 'data', depth = 1, log = False, set = True) # to find the best exponential smoothing that fits the data; depth specifies the depth of search


data.fit_trend(5); # to fit a particular trend

data.fit_seasons(11, 23, 17);  # to fit a given set of seasonalities (as many as you like, order matter)

data.fit_es(19);# to fit a particular exponential smoothing

data.fit_naive('mean') #to fit a naive prediction, 'mean' for mean predicted, 'zero' for zero predition, 'last' for last value predicted

forecasted = data.forecast() # to produce the timeseries for the forecast
extended = data.extend() # to get current data + forecast (= extension)


data.log() # prints the most important metrics relative to the signal like the R2 score, root mean squared, and mape for the original signal as well as train, test split and train + test combined  

data.plot() # it plots the data and possible prediction with error bars

data.save() # to save results as data and plots as well as log in output subfolder

new_data = data.copy() # for a copy of data

data.add(value) # to add a value or array to original data
data.sub(value) # to subtract a value or array to original data
```


