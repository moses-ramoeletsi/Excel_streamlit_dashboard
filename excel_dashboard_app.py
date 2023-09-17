import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="FNB SLA AND DRIVER COSTS", page_icon=":chart_with_upwards_trend:", layout="wide")
# Title and Subtitle
st.title(':chart_with_upwards_trend: Welcome To SLA Cost Analysis Dashboard')

# Create a file uploader widget to allow users to upload multiple files
uploaded_files = st.file_uploader("Upload Excel files (SLA Data and 'FNB_CARD_DRIVERS.xlsx')", type=["xlsx"], accept_multiple_files=True)

# Separate SLA data and Card Drivers data based on file names
uploaded_sla_files = [file for file in uploaded_files if "FNB_CARD_DRIVERS" not in file.name and "GROUP_CRIME_DRIVERS" not in file.name]
uploaded_cards_file = [file for file in uploaded_files if "FNB_CARD_DRIVERS" in file.name]
uploaded_group_crime_file = [file for file in uploaded_files if "GROUP_CRIME_DRIVERS" in file.name]

if uploaded_sla_files:
    # Combine SLA data from multiple uploaded files into a single DataFrame
    data = pd.concat([pd.read_excel(file) for file in uploaded_sla_files], ignore_index=True)

    # Load Card Drivers data from the 'FNB_CARD_DRIVERS.xlsx' file if available
    data1 = pd.read_excel(uploaded_cards_file[0]) if uploaded_cards_file else None
    data2 = pd.read_excel(uploaded_group_crime_file[0]) if uploaded_group_crime_file else None

    st.sidebar.subheader("Risk Department")
    st.subheader('Data from Excel file')

    # Create a multiselect widget for selecting columns in the sidebar
    available_SLA_columns = data.columns.tolist()  # Get a list of available column names
    available_CardsDrivers_columns = data1.columns.tolist() if data1 is not None else []
    available_group_crime_columns = data2.columns.tolist() if data2 is not None else []

    selected_SLA_columns = st.sidebar.multiselect('Select Cost Category:', available_SLA_columns)

    # Create two equal columns layout
    col1, col2 = st.columns((2))
    data["Date"] = pd.to_datetime(data["Date"])

    startDate = pd.to_datetime(data["Date"]).min()
    endDate = pd.to_datetime(data["Date"]).max()

    # Display Raw SLA Data (Column 1)
    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", startDate))
    # Display Raw Card Drivers Data (Column 2)
    with col2:
        date2 = pd.to_datetime(st.date_input("End Date", endDate))

    data = data[(data["Date"] >= date1) & (data["Date"] <= date2)].copy()

    st.markdown("---")

    if not selected_SLA_columns:
        st.sidebar.warning('Please select at least one column.')
    else:

        # Line Chart (Column 1)
        with col1:
            st.write('Line Chart:')
            fig_line = go.Figure()
            for col in selected_SLA_columns:
                if col in data.columns:
                    fig_line.add_trace(go.Scatter(x=data['Date'], y=data[col], mode='lines', name=col))
            st.plotly_chart(fig_line, use_container_width=True)

            # Bar Chart (Column 1)
            st.write('Bar Chart:')
            fig_bar = go.Figure()
            for col in selected_SLA_columns:
                if col in data.columns:
                    fig_bar.add_trace(go.Bar(x=data['Date'], y=data[col], name=col))
            st.plotly_chart(fig_bar, use_container_width=True)

            # Pie Chart (Column 1)
            st.write('Pie Chart:')
            pie_chart_data = data[selected_SLA_columns].sum()
            fig_pie = go.Figure(data=[go.Pie(labels=pie_chart_data.index, values=pie_chart_data.values)])
            st.plotly_chart(fig_pie, use_container_width=True)

            # Display specific content if "FNB Cards" is selected
            if "FNB Cards" in selected_SLA_columns:
                with col2:
                    st.write('Bar Chart for Card Drivers Data:')
                    
                    # Create a function to filter data based on selected date range
                    def filter_data_by_date(selected_start_date, selected_end_date):
                        filtered_data1 = data1[(data1["Date"] >= selected_start_date) & (data1["Date"] <= selected_end_date)]
                        return filtered_data1
                    
                    # Get the selected start and end dates
                    selected_start_date = date1
                    selected_end_date = date2
                    
                    # Filter data based on selected date range
                    filtered_data1 = filter_data_by_date(selected_start_date, selected_end_date)
                    
                    # Create the bar chart
                    fig_card_drivers = go.Figure()
                    for col in available_CardsDrivers_columns:
                        if col != "Date":  # Exclude the "Date" column
                            fig_card_drivers.add_trace(go.Bar(x=filtered_data1["Date"], y=filtered_data1[col], name=col))
                    
                    # Customize the layout of the bar chart
                    fig_card_drivers.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Value",
                        barmode='group',  # You can change the barmode as needed
                    )
                    
                    # Display the bar chart
                    st.plotly_chart(fig_card_drivers, use_container_width=True)

            # Display specific content if "Group Crime" is selected
            if "Group Crime" in selected_SLA_columns:
                st.write(f'Inside Group Crime section')
                with col2:
                    st.write('Bar Chart for Group Crime Drivers Data:')
                    
                    if data2 is not None:  # Check if Group Crime data is available
                        # Create a function to filter data based on selected date range
                        def filter_data_by_date(selected_start_date, selected_end_date):
                            filtered_data2 = data2[(data2["Date"] >= selected_start_date) & (data2["Date"] <= selected_end_date)]
                            return filtered_data2
                        
                        # Get the selected start and end dates
                        selected_start_date = date1
                        selected_end_date = date2
                        
                        # Filter data based on selected date range
                        filtered_data2 = filter_data_by_date(selected_start_date, selected_end_date)
                        
                        if not filtered_data2.empty:
                            # Create the bar chart
                            fig_group_crime = go.Figure()
                            for col in available_group_crime_columns:
                                if col != "Date":  # Exclude the "Date" column
                                    fig_group_crime.add_trace(go.Bar(x=filtered_data2['Date'], y=filtered_data2[col], name=col))
                            
                            # Customize the layout of the bar chart
                            fig_group_crime.update_layout(
                                xaxis_title="Date",
                                yaxis_title="Value",
                                barmode='group',  # You can change the barmode as needed
                            )
                            
                            # Display the bar chart
                            st.plotly_chart(fig_group_crime, use_container_width=True)
                        else:
                            st.warning("No data available for the selected date range.")
                    else:
                        st.warning("Group Crime Drivers data not available.")


        # Calculate and display statistical descriptions for selected columns
        if selected_SLA_columns:
            # Calculate statistical descriptions (min, std, max) for the selected columns
            with col2:
                statistical_data = {
                    "Column": [],
                    "Min": [],
                    "Std": [],
                    "Max": []
                }
                for col in selected_SLA_columns:
                    if col in data.columns:
                        min_val = data[col].min()
                        std_val = data[col].std()
                        max_val = data[col].max()

                        statistical_data["Column"].append(col)
                        statistical_data["Min"].append(min_val)
                        statistical_data["Std"].append(std_val)
                        statistical_data["Max"].append(max_val)

                # Create a DataFrame from the statistical data
                stats_df = pd.DataFrame(statistical_data)

                # Display the statistical descriptions in a table that fits the columns
                st.subheader("Statistical Descriptions:")
                st.dataframe(stats_df, use_container_width=True)

hide= """ 
    <style>
    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}
    header {visibility:hidden;}
</style

"""

st.markdown(hide,unsafe_allow_html=True)