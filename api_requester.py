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
  match selection:
    case 1:
      preDf, duringDf, postDf, totalDf = hmongFilters(df)
    case 2:
      preDf, duringDf, postDf, totalDf = covidKiddosFilters(df)
    case 3:
      preDf, duringDf, postDf, totalDf = covidWinterFilters(df)

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

def hmongFilters(df):
  during_hmong_dates = df.loc['2021-11-01':'2021-12-10']
  pre_hmong_dates = df.loc['2021-09-19':'2021-10-31']
  after_hmong_dates = df.loc['2021-12-11':'2022-01-22']
  total_dates = df.loc['2021-09-19':'2022-01-22']

  is_asian_pre = pre_hmong_dates['demographic_value'] == 'Asian'
  is_asian_during = during_hmong_dates['demographic_value'] == 'Asian'
  is_asian_after = after_hmong_dates['demographic_value'] == 'Asian'
  is_asian_total = total_dates['demographic_value'] == 'Asian'

  filtered_df_pre = pre_hmong_dates[is_asian_pre]
  filtered_df_during = during_hmong_dates[is_asian_during]
  filtered_df_after = after_hmong_dates[is_asian_after]
  filtered_df_total = total_dates[is_asian_total]

  pre_average = dfData(filtered_df_pre)
  during_average = dfData(filtered_df_during)
  after_average = dfData(filtered_df_after)
  total_average = dfData(filtered_df_total)

  print(f'Pre Avg = {pre_average}')
  print(f'During Avg = {during_average}')
  print(f'After Avg = {after_average}')
  print(f'Total Avg = {total_average}')

  return filtered_df_pre, filtered_df_during, filtered_df_after, filtered_df_total

def covidKiddosFilters(df):
  during_kiddos_dates = df.loc['2021-12-08':'2021-12-31']
  pre_kiddos_dates = df.loc['2021-11-17':'2021-12-07']
  after_kiddos_dates = df.loc['2022-01-01':'2022-01-22']
  total_kiddos_dates = df.loc['2021-11-17':'2022-01-22']

  is_5_11_pre = pre_kiddos_dates['demographic_value'] == '5-11'
  is_5_11_during = during_kiddos_dates['demographic_value'] == '5-11'
  is_5_11_after = after_kiddos_dates['demographic_value'] == '5-11'
  is_5_11_total = total_kiddos_dates['demographic_value'] == '5-11'

  filtered_df_pre = pre_kiddos_dates[is_5_11_pre]
  filtered_df_during = during_kiddos_dates[is_5_11_during]
  filtered_df_after = after_kiddos_dates[is_5_11_after]
  filtered_df_total = total_kiddos_dates[is_5_11_total]

  pre_average = dfData(filtered_df_pre)
  during_average = dfData(filtered_df_during)
  after_average = dfData(filtered_df_after)
  total_average = dfData(filtered_df_total)

  print(f'Pre Avg = {pre_average}')
  print(f'During Avg = {during_average}')
  print(f'After Avg = {after_average}')
  print(f'Total Avg = {total_average}')

  return filtered_df_pre, filtered_df_during, filtered_df_after, filtered_df_total

def covidWinterFilters(df):
  during_winter_dates = df.loc['2022-01-01':'2022-02-28']
  pre_winter_dates = df.loc['2021-11-01':'2021-12-31']
  after_winter_dates = df.loc['2022-03-01':'2022-04-30']
  total_winter_dates = df.loc['2021-11-01':'2022-04-30']

  filter_list = ['5-11', '12-17']

  is_under_18_pre = pre_winter_dates['demographic_value'].isin(filter_list)
  is_under_18_during = during_winter_dates['demographic_value'].isin(filter_list)
  is_under_18_after = after_winter_dates['demographic_value'].isin(filter_list)
  is_under_18_total = total_winter_dates['demographic_value'].isin(filter_list)

  filtered_df_pre = pre_winter_dates[is_under_18_pre]
  filtered_df_during = during_winter_dates[is_under_18_during]
  filtered_df_after = after_winter_dates[is_under_18_after]
  filtered_df_total = total_winter_dates[is_under_18_total]

  pre_average = dfData(filtered_df_pre)
  during_average = dfData(filtered_df_during)
  after_average = dfData(filtered_df_after)
  total_average = dfData(filtered_df_total)

  print(f'Pre Avg = {pre_average}')
  print(f'During Avg = {during_average}')
  print(f'After Avg = {after_average}')
  print(f'Total Avg = {total_average}')

  return filtered_df_pre, filtered_df_during, filtered_df_after, filtered_df_total

def covidVaccineFilters(df):
  during_dates = df.loc['2022-01-01':'2022-02-28']
  pre_dates = df.loc['2021-11-01':'2021-12-31']
  after_dates = df.loc['2022-03-01':'2022-04-30']
  total_dates = df.loc['2021-11-01':'2022-04-30']

  filter_list = ['5-11', '12-17']

  is_under_18_pre = pre_dates['demographic_value'].isin(filter_list)
  is_under_18_during = during_dates['demographic_value'].isin(filter_list)
  is_under_18_after = after_dates['demographic_value'].isin(filter_list)
  is_under_18_total = total_dates['demographic_value'].isin(filter_list)

  filtered_df_pre = pre_dates[is_under_18_pre]
  filtered_df_during = during_dates[is_under_18_during]
  filtered_df_after = after_dates[is_under_18_after]
  filtered_df_total = total_dates[is_under_18_total]

  pre_average = dfData(filtered_df_pre)
  during_average = dfData(filtered_df_during)
  after_average = dfData(filtered_df_after)
  total_average = dfData(filtered_df_total)

  print(f'Pre Avg = {pre_average}')
  print(f'During Avg = {during_average}')
  print(f'After Avg = {after_average}')
  print(f'Total Avg = {total_average}')

  return filtered_df_pre, filtered_df_during, filtered_df_after, filtered_df_total

def covidEvolutionFilters(df):
  during_dates = df.loc['2021-09-01':'2021-11-30']
  pre_dates = df.loc['2021-06-01':'2021-08-31']
  after_dates = df.loc['2021-12-01':'2022-02-28']
  total_dates = df.loc['2021-06-01':'2022-02-28']

  filter_list = ['5-11', '12-17']

  is_under_18_pre = pre_dates['demographic_value'].isin(filter_list)
  is_under_18_during = during_dates['demographic_value'].isin(filter_list)
  is_under_18_after = after_dates['demographic_value'].isin(filter_list)
  is_under_18_total = total_dates['demographic_value'].isin(filter_list)

  filtered_df_pre = pre_dates[is_under_18_pre]
  filtered_df_during = during_dates[is_under_18_during]
  filtered_df_after = after_dates[is_under_18_after]
  filtered_df_total = total_dates[is_under_18_total]

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
preDf, duringDf, postDf, totalDf = filterData(df, 2)
column = 'fully_vaccinated'
plotData(preDf, duringDf, postDf, totalDf, column)