import cassandra as c

file_name = "download"
data = c.read_data(file_name, header = 1, form = "%m/%d/%Y")
data.set_name(file_name)
data.set_unit('m')


#data.auto(log = False)

#data.find_trend(log = True)
#data.find_seasons(threshold = 1, detrend = 3, log = True)
#data.find_all(log = True)

#data.fit_trend(2)
#data.fit_seasons(13, 39)
#data.fit_es(12)
#data.fit_naive('mean')

data.log()
data.log_split()

#data.plot()
#data.save()
#data.extend()
data.forecast()
