#%%
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v1 as components
from shapely import wkt
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
from PIL import Image
import pickle as pkle
import numpy as np
import os
#%% functions for cache
st.cache(persist = True)
def read_province_df():
  #thailand's all provinces; province getmetry, province, name, region_en, lat, lon, plane, bus, train, driving
  df = pd.read_csv('./th_province.csv')
  df['geometry'] = df['geometry'].apply(wkt.loads)
  df = gpd.GeoDataFrame(df, geometry = 'geometry')
  return df

st.cache(persist = True)
def read_park_df():
  #all national parks; national park name (th, en), star, review, img_url, google_map_url, geometry, region_en, province_en
  df = pd.read_csv('./th_national_park.csv')
  df['geometry'] = df['geometry'].apply(wkt.loads)
  df = gpd.GeoDataFrame(df, geometry = 'geometry')
  return df

st.cache(persist = True)
def read_park_treemap():
  df = pd.read_csv('./th_national_park_treemap.csv')
  return df

st.cache(persist = True)
def read_rank_df():
  df = pd.read_csv('./national_park_ranking.csv')
  return df

st.cache(persist = True)
def read_travel_stat_df():
  df = pd.read_csv('./travel_stat.csv')
  return df

st.cache(persist = True)
def read_coordinate_json():
  coordinate_json = json.load(open('./th_coordinates.json'))
  return coordinate_json

st.cache(persist = True)
def read_park_description_json():
  park_detail_dict = json.load(open('./national_park_description.json'))
  return park_detail_dict

st.cache(persist = True)
def create_region_dict(df = pd.read_csv('./th_province.csv')):
  region_dict = {region: df[df['region_en'] == region].name.to_list() for region in df.region_en.unique()}
  return region_dict

st.cache(persist = True)
def create_park_region_dict():
  df = read_park_df()
  park_region_dict = {region: list(df[df['region_en'] == region].province_en.unique()) for region in df.region_en.unique()}
  return park_region_dict

st.cache(persist = True)
def plot_scattermapbox(coordinate_dict = read_coordinate_json(), province_df = read_province_df(), park_df = read_province_df(), area = 'Thailand'):
  fig = go.Figure(data = [go.Choroplethmapbox(geojson = coordinate_dict,
                                              locations = province_df['name'],  # Spatial coordinates
                                              z = province_df["count"],
                                              featureidkey = "properties.name",
                                              colorscale = 'ice',
                                              reversescale = True,
                                              colorbar_title = "#parks",
                                              hoverinfo = 'skip')
                          ],
                  layout = go.Layout(
                                    paper_bgcolor = 'rgba(0,0,0,0)', 
                                    plot_bgcolor = 'rgba(0,0,0,0)',
                                    width=500,
                                    height=500))


  fig.update_layout(mapbox_style="carto-positron", 
                      mapbox_zoom= 3.75 if area == 'Thailand' else 6.5, 
                      mapbox_center = {'lat': 13.0110763, 'lon': 100.9952628} if area == 'Thailand' else {'lat': province_df['lat'][0], 'lon': province_df['lon'][0]},
                      margin={"r":0,"t":0,"l":0,"b":0})
  fig.update_traces(showscale=False)
      
  fig.add_trace(
          go.Scattermapbox(
              lon = park_df.long, 
              lat = park_df.lat,
              mode = 'markers',
              marker_color = park_df['star_normalize'],
              marker_colorscale = px.colors.sequential.YlOrRd,
              textposition = 'top right',
              textfont = dict(size=16, color='black'),
              text = park_df['national_park_en'],
              marker = dict(size = park_df['review_for_plot'], opacity = 0.6)
              )
              )
  fig.update_traces(hovertemplate='<b>%{text}</b>')
  return fig

st.cache(persist = True)
def country_treemap(df = read_park_treemap(), region_dict = create_region_dict(), region = 'Thailand', traveler_group_radio = 'Total'):
  if region == 'Thailand':
    df = df[(national_park_treemap_df['parent'] == 'Thailand') | (national_park_treemap_df['parent'].isnull())]
  else:
    df = df[(national_park_treemap_df['parent'].isin(region_dict[region])) | (df['id'].isin(region_dict[region]))].reset_index(drop = True)
  
  fig = go.Figure(data = [
                  go.Treemap(
                      labels = df['id'],
                      parents = df['parent'],
                      values = df['total_value'] if traveler_group_radio == 'Total' \
                              else df['thai_value'] if traveler_group_radio == 'Thai' \
                              else df['foreign_value'],
                      branchvalues='total',
                      marker_colorscale='blues' if traveler_group_radio == 'Total' else 'greens' if traveler_group_radio == 'Thai' else 'oranges',
                      hovertemplate='<b>%{label} </b> <br> #'+traveler_group_radio + 'Visitors: %{value}',
                      name=''
                      )],
                    layout = go.Layout(
                                      width=500,
                                      height=400
                                      ))
  fig.update_layout(margin = dict(t=0, l=0, r=0, b=0))
  return fig
#%%##########################################################
st.set_page_config(
  page_title="Thailand National Park",
  page_icon=Image.open('/home/cpu1700/Desktop/stockfun/streamlit_app1111/thailand_national_park/layout-fluid.png'),
  layout="centered", #centered, wide
  initial_sidebar_state="expanded",
  menu_items={'Get Help': 'https://www.extremelycoolapp.com/help',
              'Report a bug': "https://www.extremelycoolapp.com/bug",
              'About': """This web app started from my wondering about the popular traveling locations in Thailand. I could only find "Top 20 places to go in Thailand" with tons of text. And that's about it. I created this app (thanks to Streamlit) and hope it will help you find your targeted destination in Thailand."""
              }
              )

with st.sidebar:
  st.header(':round_pushpin: Dashboard')
  sidebar_radio = st.radio('sidebar_radio',
                          ['About', 'Thailand Info', 'National Park'],
                          # index = 0,
                          label_visibility = 'collapsed',
                          key = 'disabled')

  with st.expander('Coming soon ...'):
    st.write('Food and Temples are coming soon. :grinning:')
# %%
st.header(f'{sidebar_radio}')
#%%##########################################################
if sidebar_radio == 'About':
  
  st.write("""Thailand is one of the top  10 countries with the most tourism. 
            The top targeted Thailand provinces of international tourists are Bangkok, 
            Phuket, Surat Thani, and Songkhla. This web app is to help you explore 
            and list out your targeted destinations without scrolling down through tons of text.""")
  
  st.markdown("<h2 style='text-align: center;'>✌🏼 sections</h2>", unsafe_allow_html=True)
  
  img_section11, img_section12 = st.columns(2)
  with img_section11:
    st.image(Image.open('./tab-01.png'), use_column_width='always')
    st.write("If you are interested in coming to Thailand have don’t have a targeted destination just yet, you can skim through the interactive chart of popular provinces in Thailand.")
  
  with img_section12:
    st.image(Image.open('./tab-02.png'), use_column_width='always')
    st.write('There are 155 national parks in Thailand. The parks’ areas vary from mountains, cliffs, waterfalls, and caves, to beaches. Choose “National Park” on the sidebar to see more.')

  st.markdown("<h2 style='text-align: center;'>✌🏼 more to come</h2>", unsafe_allow_html=True)
  img_section21, img_section22 = st.columns(2)
  with img_section21:
    st.image(Image.open('./tab-03.png'), use_column_width='always')
    st.write('One of the targeted places for international tourists is temples. There are 43,180 temples in Thailand. The temple section is coming soon. 😬')

  with img_section22:
    st.image(Image.open('./tab-04.png'), use_column_width='always')
    st.write('Spicy Papaya Salad, Pad Thai, and Spicy Shrimp Soup are well-known Thai food. There are more. 441 Michelin Stars places in Thailand for you to try. The food section is coming soon. 😬')


#%%##########################################################
elif sidebar_radio == 'Thailand Info':
  st.subheader("Region's Highlight")
  df = pd.DataFrame({'region': ['Northern', 'Northeastern', 'Central', 'Western', 'Eastern', 'Southern'],
                        'highlight': ['mountains, humble culture', 'uniqueness of food style', 'temples', 'beach (gulf of Thailand)', 'islands, forests, waterfall', 'beach (Andaman sea)']})

  hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
  st.markdown(hide_table_row_index, unsafe_allow_html=True)
  st.markdown(f'''<div align="center">
                    {df.style.set_properties(color="white", align="right").to_html(table_uuid="table_1")}''', 
                unsafe_allow_html=True)
  st.write('\n')
  st.write('Thailand has six regions; Northern, Northeastern, Central, Eastern, Western, and Southern. The different region has different uniqueness.')

  st.subheader('🌳Tourist number treemap')
  travel_stat_df = read_travel_stat_df()

  traveler_group = st.radio('select traveler group', ('Total', 'Thai', 'Foreigner'), horizontal=True)    
  thai_traveler_treemap_fig = go.Figure(data = [go.Treemap(
                                          labels=travel_stat_df.Province,
                                          values=travel_stat_df.Total if traveler_group == 'Total' else travel_stat_df.Thai if traveler_group == 'Thai' else travel_stat_df.Foreigner,
                                          parents=travel_stat_df.Parent,
                                          marker_colorscale='blues' if traveler_group == 'Total' else 'greens' if traveler_group == 'Thai' else 'Oranges'
                                      )],
                                      layout = go.Layout(
                                                          width=500,
                                                          height=400,
                                                          ))
  thai_traveler_treemap_fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
  st.plotly_chart(thai_traveler_treemap_fig, use_container_width=True)
  st.markdown(
    f"""<div class="data_source1" style="text-align: right;">
          <p>data source: 
            <a class="mention" href="https://www.mots.go.th/more_news_new.php?cid=411">mots.go.th</a>
          </p>
        </div>
    """,
    unsafe_allow_html=True,
)
  st.write('''The treemap shows the number of tourists in Thailand. The bigger the box, the more tourists. The boxes have three layers. 
1. The outer box shows the total number of tourists in Thailand.
2. Six second-tier boxes show the total number of each region’s tourists.
3. The third-tier boxes are the number of tourists in each province in each region.

On top of the treemap, you can select the tourist group (Total, Thai, Foreigner) to see the group’s popular targeted provinces.
''')


#%% ########################################################
elif sidebar_radio == 'National Park':
  
  coordinate_dict = read_coordinate_json()
  province_df = read_province_df()
  park_df = read_park_df()
  national_park_treemap_df = read_park_treemap().fillna(0)
  
  #thailand country scattermapbox function
  st.subheader('⛰ All Natonal Parks in Thailand')
  st.write('''The most popular places for international tourists are Phuket,and ChiangMai. But do you know that there are 150s more for you to explore? This section shows you all of the National Parks in Thailand.''')
  mapbox_fig = plot_scattermapbox(coordinate_dict=coordinate_dict, province_df=province_df, park_df=park_df, area = 'Thailand')
  st.plotly_chart(mapbox_fig, use_container_width=True)
  st.markdown(
      f"""<div class="data_source1" style="text-align: right;">
            <p>data source: 
              <a class="mention" href="https://www.google.com/maps/">Google Maps</a>
            </p>
          </div>
      """,
      unsafe_allow_html=True,
  )
  st.write('''This map shows the location and popularity of 155 National Parks in Thailand. Hover through the map to see the National Park name. The size of the map shows the popularity of the spot (size shows the number of comments in Google Maps). The color shows the rating star. The lighter the color means the higher the rating star. Although the color varies from blue to yellow, the rating stars mostly range from 3 to 5.''')
  
  #country treemap
  st.subheader('🌳 Thailand National Park Treemap')
  traveler_group_radio1 = st.radio('select travelers group', 
                                ['Total', 'Thai', 'Foreigner'],
                                horizontal = True,
                                key = 'travel_group_radio1')
  country_treemap_fig = country_treemap(df = read_park_treemap(), region_dict = create_region_dict(), region = 'Thailand', traveler_group_radio = traveler_group_radio1)
  st.plotly_chart(country_treemap_fig, use_container_width=True)
  st.markdown(
      f"""<div class="data_source" style="text-align: right;">
            <p>data source: 
              <a class="mention" href="https://portal.dnp.go.th/Content/nationalpark?contentId=20014">dnp.go.th</a>
            </p>
          </div>
      """,
      unsafe_allow_html=True,
  )
  st.write('''This treemap shows the number of tourists to national parks in each region. The bigger size of the box means a larger amount of tourists. The regions with the most tourists to their National Parks are Southern, Northern, and Northeaster. Note that number of parks in the region affects the size. The central area’s size is the smallest one because there are only xxx national parks in this region.
  
  Select the tourist group (Total, Thai, Foreigner) to see their popular targeted region with national parks.
''')

  #region_treemap
  
  st.subheader('🌳 Region Treemap')
  region_dict = create_park_region_dict()
  region_option = st.selectbox('select the region', 
                                region_dict.keys())
  traveler_group_radio2 = st.radio('select travelers group', 
                              ['Total', 'Thai', 'Foreigner'],
                              horizontal = True,
                              key = 'traveler_group_radio2')
  
  region_treemap_fig = country_treemap(df = read_park_treemap(), region_dict = create_region_dict(), region = region_option, traveler_group_radio = traveler_group_radio2)
  st.plotly_chart(region_treemap_fig, use_container_width=True)
  st.markdown(
      f"""<div class="data_source" style="text-align: right;">
            <p>data source: 
              <a class="mention" href="https://portal.dnp.go.th/Content/nationalpark?contentId=20014">dnp.go.th</a>
            </p>
          </div>
      """,
      unsafe_allow_html=True,
  )
  st.write('''The treemap shows the number of tourists in provinces and national parks in the selected region. Hover through the map to see popular provinces and parks in the selected region.

On top of the treemap, you can select the tourist group (Total, Thai, Foreigner) to see their popular targeted provinces.
''')

  #select province
  rank_df = read_rank_df()
  st.subheader(f'👉🏼 Province in {region_option} region')
  province_option = st.selectbox(
                              f'Select province in {region_option} region',
                              region_dict[region_option])
  


  province_df1 = province_df[province_df['name'] == province_option].reset_index(drop = True)
  park_df1 = park_df[park_df['province_en'] == province_option].reset_index(drop = True)
  province_fig = plot_scattermapbox(coordinate_dict = read_coordinate_json(), province_df = province_df1, park_df = park_df1, area = province_option)
  st.plotly_chart(province_fig, use_container_width=True)


  
  #select national park
  national_park_df = read_park_df()
  park_detail_dict = read_park_description_json()
  st.subheader(f'👉🏼 Select National Parks in {province_option}.')
  national_park = st.selectbox(f'select national park in {province_option}',
                                national_park_df[national_park_df['province_en'] == province_option.replace(
                                  ' ', '')]['national_park_en'].to_list())

  st.write('Ranking by number of tourists:')
  st.write(f'🔸 Total: ', str(int(rank_df[rank_df['id'] == national_park.replace(' National Park', '')].total_rank.values.tolist()[0])))
  st.write(f'🔸 Thai tourists: ', str(int(rank_df[rank_df['id'] == national_park.replace(' National Park', '')].thai_rank.values.tolist()[0])))
  st.write(f'🔸 Foreign tourists: ', str(int(rank_df[rank_df['id'] == national_park.replace(' National Park', '')].foreign_rank.values.tolist()[0])))

  view_point_count = str(len(park_detail_dict[national_park]['peak_view_list'].keys()))
  st.subheader(f'✨ {view_point_count} view points in {national_park}')
  view_point = st.radio(f'choose view point in {national_park}',
                        list(park_detail_dict[national_park]['peak_view_list']),
                        horizontal=False)

  st.subheader(national_park + ' | ' + view_point)

  #img part
  national_park_lower = national_park.lower().replace(' ', '_')
  view_point_lower = view_point.lower().replace(' ', '_')

  pic_folder_path = f'./pics/{national_park_lower}/{view_point_lower}'
  pic_file_ls = [entry for entry in os.listdir(pic_folder_path) if os.path.isfile(os.path.join(pic_folder_path, entry))]

  pages = ['Page'+str(i+1) for i in range(len(pic_file_ls))]
  image_path_dict = {'Page'+str(i+1): f'./pics/{national_park_lower}/{view_point_lower}/' + f for i, f in enumerate(pic_file_ls)}
  #%%
  if os.path.isfile('next_pic.p'):
    next_clicked = pkle.load(open('next_pic.p', 'rb'))  #read file
    if next_clicked == len(pages):
      next_clicked = 0
  else:
    next_clicked = 0

  if os.path.isfile('prev_pic.p'):
    prev_clicked = pkle.load(open('prev_pic.p', 'rb'))
    if prev_clicked < 0:
      next_clicked = len(pages) - 1
  else:
    prev_clicked = len(pages) - 1

  if len(pages) > 1:
    im_col1, im_col2 = st.columns(2)

    with im_col1:
      prev_pic_click = st.button('prev')
    with im_col2:
          next_pic_click = st.button('next')

    # with img_col:
    if next_pic_click:
      next_clicked = next_clicked + 1
      prev_clicked = prev_clicked + 1
      if next_clicked == len(pages):
        next_clicked = 0

      choice = [p for p in pages if pages.index(p) == next_clicked]
      pkle.dump(pages.index(choice[0]), open('next_pic.p', 'wb'))

    elif prev_pic_click:
      next_clicked = prev_clicked - 1
      prev_clicked = prev_clicked - 1
      if prev_clicked < 0:
        prev_clicked = len(pages) - 1

      choice = [p for p in pages if pages.index(p) == prev_clicked]
      pkle.dump(pages.index(choice[0]), open('prev_pic.p', 'wb'))

    else:
      choice = [pages[0]]
    
    st.image(Image.open(image_path_dict[choice[0]]), use_column_width='always')
    img_text = ('Pic : ' + choice[0].replace('Page', '') + '/' + str(len(pages)))
    st.markdown(f"<h4 style='text-align: center;'>{img_text}</h4>", unsafe_allow_html=True)

  else:
    st.image(Image.open(image_path_dict[pages[0]]), use_column_width='always')
    img_text = ('Pic : 1/1')
    st.markdown(f"<h5 style='text-align: center;'>{img_text}</h5>", unsafe_allow_html=True)

  park_detail_dict = read_park_description_json()

  url = park_detail_dict[national_park]['peak_view_list'][view_point]['url']
  st.markdown(
    f"""<div class="data_source" style="text-align: right;">
          <p>data source: 
            <a class="mention" href="{url}">dnp.go.th</a>
          </p>
        </div>
    """,
    unsafe_allow_html=True,
)
  st.write(park_detail_dict[national_park]['peak_view_list'][view_point]['description_en'])
  
  customized_button = st.markdown("""
      <style >
      .stDownloadButton, div.stButton {text-align:center}
      .stDownloadButton button, div.stButton > button:first-child {
          line-height: 1.5;
          display: inline-block;
          vertical-align: middle;
          horizontal-align: middle;
      }
          }
      </style>""", unsafe_allow_html=True)
#%%
