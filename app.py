import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout= "wide",page_title='StartUp Analysis')

df = pd.read_csv('startup_cleaned.csv', parse_dates=['date'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month

def load_overall_analysis():

    st.title('Overall Analysis')

    # Cards -> Total + Max + Avg -> Total funded startups
    col1,col2 = st.columns(2)
    with col1:
        total_invested_amount = np.round(df['amount'].sum(),decimals= 2)
        st.metric(label='Total Investment', value= str(total_invested_amount) + ' Cr')
    with col2:
        maxmium_invested_amount = np.round(df.groupby('startup')['amount'].sum().max(), decimals= 2)
        st.metric(label= 'Max Investment', value= str(maxmium_invested_amount) + ' Cr')

    col1,col2 = st.columns(2)
    with col1:
        avg_invested_amount = np.round(df.groupby('startup')['amount'].sum().mean(), decimals= 2)
        st.metric(label= 'Average Investment', value= str(avg_invested_amount) + ' Cr')
    with col2:
        total_funded_startups = df['startup'].nunique()
        st.metric(label= 'Total Funded StartUps', value= total_funded_startups)

    # MoM chart -> Total + Count
    st.subheader('Month_On_Month (MOM) Investments')
    selected_option = st.selectbox('Select',['MOM Investment', 'MOM StartUps'])

    if selected_option == 'MOM Investment':
        temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index()
        temp_df['x_axis'] = temp_df['month'].astype('str') + '-' + temp_df['year'].astype('str')
        fig, ax = plt.subplots()
        ax.plot(temp_df['x_axis'], temp_df['amount'])
        st.pyplot(fig)

    else:
        temp_df = df.groupby(['year', 'month'])['startup'].count().reset_index()
        temp_df['x_axis'] = temp_df['month'].astype('str') + '-' + temp_df['year'].astype('str')
        fig, ax = plt.subplots()
        ax.plot(temp_df['x_axis'], temp_df['startup'])
        st.pyplot(fig)

    # Sector Analysis Pie -> top sectors(Count + Sum)
    vertical_series = df.groupby('vertical')['vertical'].count().sort_values(ascending=False).head(10)
    st.subheader('Top Sector Vise Investments')
    fig1, ax1 = plt.subplots()
    ax1.pie(vertical_series, labels=vertical_series.index, autopct='%1.1f%%')
    st.pyplot(fig1)

    # Type of funding
    temp_df = df.groupby('round')['round'].count().sort_values(ascending=False).head(15)
    temp_df.name = 'Count'
    temp_df = temp_df.reset_index()
    temp_df.rename(columns={'round': 'Round'}, inplace=True)

    st.subheader('Top Funding Types')
    st.dataframe(temp_df)

    # City wise funding
    stage_series = df.groupby('city')['amount'].sum().sort_values(ascending=False).head(6)
    st.subheader('Top City Vise Investments')
    fig2, ax2 = plt.subplots()
    ax2.bar(stage_series.index, stage_series.values)
    st.pyplot(fig2)

    # Top Startups -> year wise -> Overall
    st.subheader('Top StartUps Per Year')

    year_option = st.selectbox('Select Year', options=[2015, 2016, 2017, 2018, 2019, 2020,'Overall'])
    if year_option != 'Overall':
        top_startups_per_year = df[df['year'] == year_option].groupby('startup', as_index=False)['amount'].sum().sort_values(
            by='amount', ascending=False).reset_index(drop=True).head(10)
        top_startups_per_year.rename(columns={'startup': 'StartUp', 'amount': 'Amount'}, inplace=True)
    else:
        top_startups_per_year = df.groupby('startup', as_index=False)['amount'].sum().sort_values(by='amount',
            ascending=False).head(20).reset_index(drop=True)

    st.dataframe(top_startups_per_year)

    # Top investors
    top_investors = df.groupby('investors')['amount'].sum().sort_values(ascending=False).head(9)
    st.subheader('Top Investors')
    fig2, ax2 = plt.subplots()
    ax2.pie(top_investors, labels=top_investors.index, autopct='%1.1f%%')
    st.pyplot(fig2)

def load_start_up_analysis(startup):
    st.title('StartUp Analysis')

    col1,col2,col3 = st.columns(3)
    with col1:
        startup_name = startup
        st.metric(label='StartUp Name', value= startup_name)
    with col2:
        startup_vertical = df[df['startup'] == startup]['vertical'].values[0]
        st.metric(label='StartUp Vertical', value=  startup_vertical)
    with col3:
        startup_location = df[df['startup'] == startup]['city'].values[0]
        st.metric(label='StartUp location', value= startup_location)

    startup_sub_vertical = df[df['startup'] == startup]['subvertical'].values[0]
    st.metric(label='StartUp Sub Vertical', value= startup_sub_vertical)

    startup_brand = df[df['startup'] == startup].copy()
    startup_brand['total_amount_per_round'] = startup_brand.groupby('round')['amount'].transform('sum')
    startup_brand = startup_brand.sort_values(by='round', ascending=True).reset_index()[
        ['date', 'investors', 'city', 'round', 'amount']]
    startup_brand.rename(
        columns={'date': 'Date', 'investors': 'Investors', 'city': 'City', 'round': 'Round', 'amount': 'Amount'},
        inplace=True)

    st.subheader('Funding Rounds')
    st.dataframe(startup_brand)

    invested_in_verticals = df[df['startup'] == startup]['vertical'].unique()
    same_vertical_startups = \
    df[(df['vertical'].isin(invested_in_verticals)) & (df['startup'] != startup)].groupby(['vertical', 'startup'], as_index=False)[
        'amount'].sum().sort_values(by=['vertical', 'amount'], ascending=[True, False]).reset_index(drop=True)
    same_vertical_startups = same_vertical_startups.groupby('vertical').head(3)
    same_vertical_startups.rename(columns={'vertical': 'Vertical', 'startup': 'Startup', 'amount': 'Amount'},
                                  inplace=True)

    st.subheader('Similar Startups')
    st.dataframe(same_vertical_startups)

def load_investor(investor):
    st.title(investor)
    # Recent Investments
    last_5_df = df[df['investors'].str.contains(investor)].head()[['date', 'startup', 'vertical', 'city', 'round', 'amount']]
    st.subheader('Most Recent Investments')
    st.dataframe(last_5_df)

    col1,col2 = st.columns(2)
    with col1:
        # Biggest investments
        big_invt_series = df[df['investors'].str.contains(investor)].groupby('vertical')['amount'].sum().sort_values(
            ascending=False).head()
        st.subheader('Biggest Investments')
        fig, ax = plt.subplots()
        ax.bar(big_invt_series.index,big_invt_series.values)
        st.pyplot(fig)

    with col2:
        # sector ->pie
        vertical_series = df[df['investors'].str.contains(investor)].groupby('vertical')['amount'].sum()
        st.subheader('Sector Vise Investments')
        fig1, ax1 = plt.subplots()
        ax1.pie(vertical_series, labels = vertical_series.index,autopct='%1.1f%%')
        st.pyplot(fig1)

    col1,col2 = st.columns(2)
    with col1:
        # stage ->pie
        stage_series = df[df['investors'].str.contains(investor)].groupby('round')['amount'].sum()
        st.subheader('City Vise Investments')
        fig2, ax2 = plt.subplots()
        ax2.pie(stage_series, labels = stage_series.index,autopct='%1.1f%%')
        st.pyplot(fig2)
    with col2:
        # city -> pie
        city_series = df[df['investors'].str.contains(investor)].groupby('city')['amount'].sum()
        st.subheader('Stage Vise Investments')
        fig3, ax3 = plt.subplots()
        ax3.pie(city_series, labels=city_series.index, autopct='%1.1f%%')
        st.pyplot(fig3)

    col1, col2 = st.columns(2)
    with col1:
        # YoY investment graph
        years_series = df[df['investors'].str.contains(investor)].groupby('year')['amount'].sum().sort_index()
        st.subheader('Year_On_Year (YOY)  Investments')
        fig, ax = plt.subplots()
        ax.plot(years_series.index, years_series.values)
        st.pyplot(fig)

    # Similar Investors
    df['Seperate_investors'] = df['investors'].str.split(',')
    temp_df = df.explode('Seperate_investors')

    temp_df = temp_df.groupby('vertical')

    all_invtr_invtmt = temp_df['Seperate_investors'].value_counts(ascending=False).reset_index()
    all_invtr_invtmt = all_invtr_invtmt.sort_values(by='count', ascending=False)
    input_invtr_invtmt = df[df['investors'].str.contains(investor)].groupby('vertical')[
        'amount'].sum().reset_index()

    top5_invt_per_vertical = all_invtr_invtmt[(all_invtr_invtmt['vertical'].isin(input_invtr_invtmt['vertical'])) & (
            all_invtr_invtmt['Seperate_investors'] != investor)][
        ['vertical', 'Seperate_investors', 'count']].sort_values(by=['vertical', 'count'],
        ascending=[True, False]).groupby('vertical').head(3).reset_index(drop=True)

    top5_invt_per_vertical.rename(columns={'Seperate_investors': 'Investors', 'count': 'No of Times'}, inplace=True)

    st.dataframe(top5_invt_per_vertical)





st.sidebar.title('Startup Funding Analysis')

option = st.sidebar.selectbox('Select One', ['Overall Analysis', 'StartUP', 'Investor'])
if option == 'Overall Analysis':
#     btn0 = st.sidebar.button('Show Overall Analysis')
#     if btn0:
    load_overall_analysis()

elif option == 'StartUP':
    selected_startup = st.sidebar.selectbox('Select StartUp', sorted(df['startup'].unique().tolist()))
    btn1 = st.sidebar.button('Find StartUP Details')
    if btn1:
        load_start_up_analysis(selected_startup)

else:
    selected_investor = st.sidebar.selectbox('Select Investor', sorted(set(df['investors'].str.split(',').sum())))
    btn2 = st.sidebar.button('Find Investors Details')
    if btn2:
        load_investor(selected_investor)
