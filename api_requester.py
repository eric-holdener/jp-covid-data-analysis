from itertools import filterfalse
import json
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
import datetime
import seaborn as sns
import scipy.stats as stats

url = 'https://data.chhs.ca.gov/api/3/action/datastore_search?resource_id=71729331-2f09-4ea4-a52f-a2661972e146&q=Fresno&limit=12000'

def getData():
  fileobj = urllib.request.urlopen(url)
  response_dict = json.loads(fileobj.read())

  for i in response_dict['result']['records']:
    print(i)

  with open('counties.json', 'w') as json_file:
    json.dump(response_dict, json_file)

def convertToCsv():
  with open('counties.json', 'r') as f:
    data = json.load(f)
  
  correct_data = data["result"]["records"]
  df = pd.DataFrame(correct_data)
  
  df.to_excel('covid_data.xlsx', index=None, header=True)

def readData():
  with open('counties.json', 'r') as f:
    data = json.load(f)

  # clean dataframe
  correct_data = data["result"]["records"]
  df = pd.DataFrame(correct_data)
  df['administered_date'] = pd.to_datetime(df['administered_date'])
  df = df.set_index('administered_date')
  df = df.sort_index()
  df = df.astype({'fully_vaccinated': 'float', 'cumulative_fully_vaccinated': 'float'})
  df = df.astype({'fully_vaccinated': 'int', 'cumulative_fully_vaccinated': 'int'})

  return df

def filterData(df, selection):
  # selection numbers are as follows:
  # 1: hmong new years
  # 2: covid kiddos
  # 3: covid winter
  # 4: covid evolution
  # 5: covid vaccine
  match selection:
    case 1:
      preDf, duringDf, postDf, totalDf = processData(df, '2021-09-19', '2021-10-31', '2021-11-01', '2021-12-10', '2021-12-11', '2022-01-22', ['Asian'])
    case 2:
      preDf, duringDf, postDf, totalDf = processData(df, '2021-11-17', '2021-12-07', '2021-12-08', '2021-12-31', '2022-01-01', '2022-01-22', ['5-11'])
    case 3:
      preDf, duringDf, postDf, totalDf = processData(df, '2021-11-01', '2021-12-31', '2022-01-01', '2022-02-28', '2022-03-01', '2022-04-30', ['5-11', '12-17'])
    case 4:
      preDf, duringDf, postDf, totalDf = processData(df, '2021-06-01', '2021-08-31', '2021-09-01', '2021-11-30', '2021-12-01', '2022-02-28')
    case 5:
      preDf, duringDf, postDf, totalDf = processData(df, '2021-02-01', '2021-04-30', '2021-05-01', '2021-07-31', '2021-08-01', '2021-11-30')

  return preDf, duringDf, postDf, totalDf  
  
def plotData(preDf, duringDf, postDf, totalDf, column):
  fig, ax = plt.subplots(2, 2, figsize=(9, 7), sharex=False, sharey=True)

  # Pre Campaign
  ax[0,0].plot(preDf.index, preDf[column])

  preDf.index = preDf.index.map(datetime.date.toordinal)
  slope, y0, r, p, stderr = stats.linregress(preDf.index, preDf[column])

  pre_x_endpoints = pd.DataFrame([preDf.index[0], preDf.index[-1]], index = [0, 1])
  pre_y_endpoints = y0 + slope * pre_x_endpoints
  pre_x_endpoints[0] = pre_x_endpoints[0].map(datetime.date.fromordinal)

  ax[0,0].plot(pre_x_endpoints.iloc[0:2].values, pre_y_endpoints.iloc[0:2].values, c='r')
  ax[0,0].set_title('Weeks leading up to campaign', fontsize=12)

  print(f'Pre Slope = {slope}')

  # During Campaign
  ax[0,1].plot(duringDf.index, duringDf[column])

  duringDf.index = duringDf.index.map(datetime.date.toordinal)
  slope, y0, r, p, stderr = stats.linregress(duringDf.index, duringDf[column])

  during_x_endpoints = pd.DataFrame([duringDf.index[0], duringDf.index[-1]], index = [0, 1])
  during_y_endpoints = y0 + slope * during_x_endpoints
  during_x_endpoints[0] = during_x_endpoints[0].map(datetime.date.fromordinal)

  ax[0,1].plot(during_x_endpoints.iloc[0:2].values, during_y_endpoints.iloc[0:2].values, c='r')
  ax[0,1].set_title('Weeks during the campaign', fontsize=12)

  print(f'During Slope = {slope}')

  # Post Campaign
  ax[1,0].plot(postDf.index, postDf[column])

  postDf.index = postDf.index.map(datetime.date.toordinal)
  slope, y0, r, p, stderr = stats.linregress(postDf.index, postDf[column])

  post_x_endpoints = pd.DataFrame([postDf.index[0], postDf.index[-1]], index = [0, 1])
  post_y_endpoints = y0 + slope * post_x_endpoints
  post_x_endpoints[0] = post_x_endpoints[0].map(datetime.date.fromordinal)

  ax[1,0].plot(post_x_endpoints.iloc[0:2].values, post_y_endpoints.iloc[0:2].values, c='r')
  ax[1,0].set_title('Weeks after the campaign', fontsize=12)

  print(f'After Slope = {slope}')

  # Total Graph
  ax[1,1].plot(totalDf.index, totalDf[column])

  totalDf.index = totalDf.index.map(datetime.date.toordinal)
  slope, y0, r, p, stderr = stats.linregress(totalDf.index, totalDf[column])

  total_x_endpoints = pd.DataFrame([totalDf.index[0], totalDf.index[-1]], index = [0, 1])
  total_y_endpoints = y0 + slope * total_x_endpoints
  total_x_endpoints[0] = total_x_endpoints[0].map(datetime.date.fromordinal)

  ax[1,1].plot(total_x_endpoints.iloc[0:2].values, total_y_endpoints.iloc[0:2].values, c='r')
  ax[1,1].set_title('Total timeline', fontsize=12)

  print(f'Total Slope = {slope}')

  ax[0,0].tick_params(axis="x", rotation=45, labelsize=8)
  ax[1,0].tick_params(axis="x", rotation=45, labelsize=8)
  ax[0,1].tick_params(axis="x", rotation=45, labelsize=8)
  ax[1,1].tick_params(axis="x", rotation=45, labelsize=8)

  fig.tight_layout()

  plt.show()

def processData(df, start_pre, end_pre, start_during, end_during, start_after, end_after, filter=None):
  during_dates = df.loc[start_during:end_during]
  pre_dates = df.loc[start_pre:end_pre]
  after_dates = df.loc[start_after:end_after]
  total_dates = df.loc[start_pre:end_after]

  if filter != None:
    filter_pre = pre_dates['demographic_value'].isin(filter) 
    filter_during = during_dates['demographic_value'].isin(filter)
    filter_after = after_dates['demographic_value'].isin(filter)
    filter_total = total_dates['demographic_value'].isin(filter)

    filtered_df_pre = pre_dates[filter_pre]
    filtered_df_during = during_dates[filter_during]
    filtered_df_after = after_dates[filter_after]
    filtered_df_total = total_dates[filter_total]
  else:
    filtered_df_pre = pre_dates
    filtered_df_during = during_dates
    filtered_df_after = after_dates
    filtered_df_total = total_dates

  pre_average = dfData(filtered_df_pre)
  during_average = dfData(filtered_df_during)
  after_average = dfData(filtered_df_after)
  total_average = dfData(filtered_df_total)

  print(f'Pre Avg = {pre_average}')
  print(f'During Avg = {during_average}')
  print(f'After Avg = {after_average}')
  print(f'Total Avg = {total_average}')

  return filtered_df_pre, filtered_df_during, filtered_df_after, filtered_df_total

def inspectData(df):
  # print(monthDf.head())
  print(df.head())
  print(df.info())
  print(df['demographic_value'])

def dfData(df):
  fully_vaccinated_average = df['fully_vaccinated'].mean()
  return fully_vaccinated_average

df = readData()
preDf, duringDf, postDf, totalDf = filterData(df, 3)
column = 'fully_vaccinated'
plotData(preDf, duringDf, postDf, totalDf, column)