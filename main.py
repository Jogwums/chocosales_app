import streamlit as st 
import pandas as pd 
import plotly.express as px
import altair as alt 

@st.cache_data
def load_data():
    df = pd.read_csv("chocosales.csv")
    # convert Date col to datetime datatype
    df.Date= pd.to_datetime(df.Date, format="%d-%b-%y")
    # convert the Amount col to float datatype
    df.Amount= df.Amount.str.replace("$","").str.replace(",","").str.strip().astype("float")
    df["Price/Box"] = round(df.Amount / df["Boxes Shipped"],2)
    return df

df = load_data()

# App title
st.title("Chocolate Sales App")
# Data table preview
# st.dataframe(df.head(10))

# create filters 
filters = {
    "Sales Person": df["Sales Person"].unique(),
    "Country": df["Country"].unique(),
    "Product": df["Product"].unique(),
}

# store user selection 
selected_filters = {}

# generate multi-select widgets dynamically 
for key, options in filters.items():
    selected_filters[key]=st.sidebar.multiselect(key,options)

# lets have the full data 
filtered_df = df.copy()

# apply filter selection to the data
for key, selected_values in selected_filters.items():
    if selected_values:
        filtered_df = filtered_df[filtered_df[key].\
                                  isin(selected_values)]

# display the data
# st.dataframe(filtered_df.head())

# calculations 
no_of_transactions = len(filtered_df)
total_revenue = filtered_df["Amount"].sum()
total_boxes = filtered_df["Boxes Shipped"].sum()
no_of_products = filtered_df["Product"].nunique()
pert_of_boxes = f"{(total_boxes/df["Boxes Shipped"].sum())*100:,.2f}%"

# st.write("%_boxes_for_selection:",pert_of_boxes)

# streamlit column component
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Transactions", no_of_transactions)

with col2:
    st.metric("Total Revenue", f"${total_revenue:,.0f}")

with col3: 
    st.metric("Total boxes", f"{total_boxes:,.0f}", delta="")

with col4:
    st.metric("Products", no_of_products)

st.subheader("Sales Trends")

# mini-visuals 
# to be displayed in columns
col5, col6 = st.columns(2)


with col5:
    monthly_revenue = filtered_df.groupby(filtered_df['Date'].dt.month_name())['Amount'].sum().reset_index()
    fig = px.line(monthly_revenue, x='Date', y='Amount', title="Monthly Revenue Trend")
    st.plotly_chart(fig)

with col6:
    qtr = filtered_df["Date"].dt.quarter.unique()
    qtrly_revenue = filtered_df.groupby(filtered_df["Date"].dt.quarter)["Amount"].sum().reset_index()
    # st.write(qtrly_revenue)
    fig = px.line(qtrly_revenue, x='Date', y='Amount', title="Qtrly Revenue Trend",
                  labels=["Qtr","Sales"])
    st.plotly_chart(fig)


# charts 
st.subheader("Products with largest revenue")

top_products = filtered_df.groupby("Product")["Amount"].\
    sum().nlargest(5).reset_index()

st.write(top_products)

# altair plotting library 
import altair as alt # put this at the top

st.subheader("Top 5 Products by Revenue")
# configure the bar chart
chart1 = alt.Chart(top_products).mark_bar().encode(
    x=alt.X('Amount:Q', title="Revenue ($)"),
    y=alt.Y("Product:N"),
    color=alt.Color("Product:N",legend=None)
).properties(height=300)

# display the chart
st.altair_chart(chart1, use_container_width=True)

# Q3 sales by country
# Group by country and sum the revenue
sales_by_country = filtered_df.groupby('Country')['Amount'].sum().sort_values(ascending=False)

# chart 3
col7, col8 = st.columns(2)
sales_by_country = filtered_df.groupby('Country')['Amount'].sum().reset_index()
sales_by_country.columns = ["Country","Amount"]
# st.write(sales_by_country)

with col7:
    st.subheader("Sales by Country")
    fig = px.pie(sales_by_country, values='Amount', names='Country', hole=0.3)
    st.plotly_chart(fig)

# Q4 Group by salesperson
top_salespersons = filtered_df.groupby('Sales Person')['Amount'].sum().sort_values(ascending=False).head(3)

# chart 4
top_salespersons = filtered_df.groupby('Sales Person')['Amount'].sum().nlargest(3).reset_index()
with col8:
    st.subheader("Top 3 Salespersons")
    fig = px.bar(top_salespersons, x='Sales Person', y='Amount', color='Sales Person')
    st.plotly_chart(fig)