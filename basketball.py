from cgitb import html
import streamlit as st
import pandas as pd
import base64  
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime as dt

#css
page_bg_img="""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@300&display=swap');

html, body, [class*="css"]  {
font-family: 'Noto Sans', sans-serif;
</style>
<style>
[data-testid="stAppViewContainer"]{
background-image: url(https://media.istockphoto.com/photos/basketball-on-gray-background-picture-id1291987302?b=1&k=20&m=1291987302&s=170667a&w=0&h=GXsbWjqAe--RQ7iOkKlntsFe-klP7zDADSNdMwjWAmA=);
background-size: cover;
}
</style>"""
st.markdown(page_bg_img,unsafe_allow_html=True)



st.title('NBA Players Stats Explorer') 

st.markdown("""
* **Data Source:** [basketball-reference.com](http://www.basketball-reference.com/).
""")

st.sidebar.header('User Input Features')
#year selector
selected_year=st.sidebar.selectbox('Year',list(reversed(range(1950,dt.date.today().year))))

#web scraping of NBA players stats
@st.cache
def load_data(year):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    html = pd.read_html(url,header=0)
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index) #deletes repeating headers
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'],axis = 1)
    return playerstats
playerstats = load_data(selected_year)

#sidebar - team selection
sorted_unique_teams = sorted(playerstats.Tm.unique())
selected_team = st.sidebar.multiselect('Team',sorted_unique_teams)

#sidebar - Position selection
unique_pos = ['C','PF','SF','PG','SG']
selected_pos = st.sidebar.multiselect('Position',unique_pos,unique_pos)

#Filtering data
df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

if len(selected_team)>1:
    st.header('Player Stats of Selected Teams')
else: st.header('Player Stats of Selected Team')

st.write('Data Dimension: '+str(df_selected_team.shape[0])+' rows and '+str(df_selected_team.shape[1])+' colums')
st.dataframe(df_selected_team)

#download data
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode() #strings <-> conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team),unsafe_allow_html=True)

if st.button('Intercorrelation Heatmap'):
    st.header('Intercorrelation Heatmap Matrix')
    df_selected_team.to_csv('output.csv',index=False)
    df = pd.read_csv('output.csv')

    corr = df_selected_team.corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style('white'):
        f, ax = plt.subplots(figsize=(7,5))
        ax = sns.heatmap(corr, mask=mask,vmax=1,square=True)
    st.pyplot(f)