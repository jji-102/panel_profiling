import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configure page
st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and prepare data
@st.cache_data
def load_data():
    # Load data from CSV file
    try:
        df = pd.read_csv('monthly_profiling_summary.csv')
    except FileNotFoundError:
        st.error("ไม่พบไฟล์ monthly_profiling_summary.csv กรุณาตรวจสอบที่ตั้งไฟล์")
        return pd.DataFrame()
    
    # Convert date column
    df['Collected_Month'] = pd.to_datetime(df['Collected_Month'])
    df['Month_Year'] = df['Collected_Month'].dt.strftime('%d-%m-%Y')
    
    # คำนวณ Silver Gen (Age 60+)
    df['Silver_Gen_Count'] = df['Age_60_69_Count'] + df['Age_70_99_Count']
    
    # คำนวณ Auto (คนที่มีรถยนต์ - Cars_At_Home มากกว่า 0)
    df['Auto_Count'] = df['Cars_At_Home_1_Count'] + df['Cars_At_Home_2_Count'] + df['Cars_At_Home_3_Or_More_Count']
    
    # คำนวณ UPC (Upcountry - ต่างจังหวัด ไม่รวมกรุงเทพฯ และปริมณฑล)
    df['UPC_Count'] = (df['Region_Central_Count'] + 
                       df['Region_Northeast_Count'] + 
                       df['Region_North_Count'] + 
                       df['Region_East_Count'] + 
                       df['Region_West_Count'] + 
                       df['Region_South_Count'])
    
    return df

# Helper function to get latest month data
def get_latest_month_data(df):
    if len(df) == 0:
        return df
    latest_month = df['Collected_Month'].max()
    return df[df['Collected_Month'] == latest_month]

# Load data
df = load_data()

if len(df) == 0:
    st.stop()

# Header
st.title("📊 Analytics Dashboard")
st.markdown("---")

# Sidebar Filters
with st.sidebar:
    st.header("🔍 Filters")
    
    # Panel Source Filter
    panel_sources = ['All'] + list(df['Panel_Source'].unique())
    selected_panel = st.selectbox('Panel Source', panel_sources)
    
    # Month Filter
    months = ['All'] + sorted(list(df['Month_Year'].unique()), reverse=True)
    selected_month = st.selectbox('Month', months)
    
    st.markdown("---")
    st.markdown("**📝 Filter Information**")
    st.markdown("- **DS**: Asian panel")
    st.markdown("- **MS**: Meow")
    
    st.markdown("---")
    st.markdown("**📈 Metrics Definition**")
    st.markdown("- **Overall**: Total Respondents")
    st.markdown("- **Silver Gen**: Age 60+ years")
    st.markdown("- **Auto**: Households with cars")
    st.markdown("- **UPC**: Upcountry (ต่างจังหวัด ไม่รวม กทม.)")

# Apply filters
filtered_df = df.copy()
if selected_panel != 'All':
    filtered_df = filtered_df[filtered_df['Panel_Source'] == selected_panel]
if selected_month != 'All':
    filtered_df = filtered_df[filtered_df['Month_Year'] == selected_month]

# Summary Cards Section - ใช้ข้อมูลเดือนล่าสุด
st.header("📈 Key Metrics Overview")

# ใช้ข้อมูลเดือนล่าสุดเสมอ ยกเว้นมีการเลือก filter เดือน
if selected_month == 'All':
    latest_data = get_latest_month_data(df)
    display_data = latest_data
    if len(latest_data) > 0:
        st.markdown(f"**Showing data for latest month: {latest_data['Month_Year'].iloc[0]}**")
else:
    display_data = filtered_df
    st.markdown(f"**Showing data for: {selected_month}**")

# คำนวณ metrics รวม
if len(display_data) > 0:
    total_respondents = display_data['Total_Respondents_Count'].sum()
    total_silver_gen = display_data['Silver_Gen_Count'].sum()
    total_auto = display_data['Auto_Count'].sum()
    total_upc = display_data['UPC_Count'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Overall", f"{total_respondents:,}")
    
    with col2:
        st.metric("Silver Gen", f"{total_silver_gen:,}")
    
    with col3:
        st.metric("Auto", f"{total_auto:,}")
    
    with col4:
        st.metric("UPC", f"{total_upc:,}")

st.markdown("---")

# Data Visualization Section - แสดงเป็นตารางตามรูปแบบที่ต้องการ
st.header("📊 Data Visualization")

# สร้างตารางแสดงข้อมูลแยกตาม Panel Source
if len(display_data) > 0:
    
    # ดึงชื่อเดือนสำหรับหัวตาราง
    month_display = display_data['Month_Year'].iloc[0] if len(display_data) > 0 else "N/A"
    
    # สร้าง 3 คอลัมน์สำหรับตาราง
    col1, col2, col3 = st.columns(3)
    
    # คอลัมน์ที่ 1: Meow Panel
    with col1:
        st.subheader("🐱 Meow Panel")
        ms_data = display_data[display_data['Panel_Source'] == 'MS']
        if len(ms_data) > 0:
            ms_summary = ms_data.iloc[0]
            
            # สร้างข้อมูลสำหรับ DataFrame
            meow_table_data = {
                'Metric': ['Overall', 'Silver Gen', 'Auto', 'UPC'],
                month_display: [
                    f"{ms_summary['Total_Respondents_Count']:,}",
                    f"{ms_summary['Silver_Gen_Count']:,}",
                    f"{ms_summary['Auto_Count']:,}",
                    f"{ms_summary['UPC_Count']:,}"
                ]
            }
            
            meow_df = pd.DataFrame(meow_table_data)
            st.dataframe(meow_df, hide_index=True, use_container_width=True)
        else:
            st.info("No data available for Meow panel")
    
    # คอลัมน์ที่ 2: Asian Panel
    with col2:
        st.subheader("🌏 Asian Panel")
        ds_data = display_data[display_data['Panel_Source'] == 'DS']
        if len(ds_data) > 0:
            ds_summary = ds_data.iloc[0]
            
            # สร้างข้อมูลสำหรับ DataFrame
            asian_table_data = {
                'Metric': ['Overall', 'Silver Gen', 'Auto', 'UPC'],
                month_display: [
                    f"{ds_summary['Total_Respondents_Count']:,}",
                    f"{ds_summary['Silver_Gen_Count']:,}",
                    f"{ds_summary['Auto_Count']:,}",
                    f"{ds_summary['UPC_Count']:,}"
                ]
            }
            
            asian_df = pd.DataFrame(asian_table_data)
            st.dataframe(asian_df, hide_index=True, use_container_width=True)
        else:
            st.info("No data available for Asian panel")
    
    # คอลัมน์ที่ 3: Combined Panel
    with col3:
        st.subheader("🔄 Meow + Asian")
        ms_data = display_data[display_data['Panel_Source'] == 'MS']
        ds_data = display_data[display_data['Panel_Source'] == 'DS']
        
        if len(ms_data) > 0 or len(ds_data) > 0:
            # สร้างข้อมูลสำหรับ DataFrame
            combined_table_data = {
                'Metric': ['Overall', 'Silver Gen', 'Auto', 'UPC'],
                month_display: [
                    f"{total_respondents:,}",
                    f"{total_silver_gen:,}",
                    f"{total_auto:,}",
                    f"{total_upc:,}"
                ]
            }
            
            combined_df = pd.DataFrame(combined_table_data)
            st.dataframe(combined_df, hide_index=True, use_container_width=True)
        else:
            st.info("No data available for combined panels")
# Monthly Comparison Table Section
st.markdown("---")
st.header("📅 Monthly Comparison 2025")

# สร้างข้อมูลสำหรับตารางเปรียบเทียบรายเดือนแบบกว้างพร้อม trend indicators
def create_wide_monthly_comparison_tables_with_trends():
    # สร้างรายการเดือนทั้งปี 2025
    all_months_2025 = [
        ('01-01-2025', 'Jan 25'),
        ('01-02-2025', 'Feb 25'),
        ('01-03-2025', 'Mar 25'),
        ('01-04-2025', 'Apr 25'),
        ('01-05-2025', 'May 25'),
        ('01-06-2025', 'Jun 25'),
        ('01-07-2025', 'Jul 25'),
        ('01-08-2025', 'Aug 25'),
        ('01-09-2025', 'Sep 25'),
        ('01-10-2025', 'Oct 25'),
        ('01-11-2025', 'Nov 25'),
        ('01-12-2025', 'Dec 25')
    ]
    
    # ฟังก์ชันสำหรับสร้าง trend indicator
    def get_trend_indicator(current_value, previous_value):
        if current_value == '-' or previous_value == '-':
            return ''
        
        try:
            current_num = int(current_value.replace(',', ''))
            previous_num = int(previous_value.replace(',', ''))
            
            if current_num > previous_num:
                percentage = ((current_num - previous_num) / previous_num) * 100
                return f" 📈 (+{percentage:.1f}%)"
            elif current_num < previous_num:
                percentage = ((previous_num - current_num) / previous_num) * 100
                return f" 📉 (-{percentage:.1f}%)"
            else:
                return " ➡️ (0%)"
        except:
            return ''
    
    # สร้างตารางสำหรับ Meow Panel
    meow_data = {'Metric': ['Overall', 'Silver Gen', 'Auto', 'UPC']}
    meow_raw_data = {'Overall': [], 'Silver Gen': [], 'Auto': [], 'UPC': []}
    
    for month_key, month_display in all_months_2025:
        month_data = df[(df['Panel_Source'] == 'MS') & (df['Month_Year'] == month_key)]
        
        if len(month_data) > 0:
            row = month_data.iloc[0]
            values = [
                row['Total_Respondents_Count'],
                row['Silver_Gen_Count'],
                row['Auto_Count'],
                row['UPC_Count']
            ]
            formatted_values = [f"{val:,}" for val in values]
            meow_raw_data['Overall'].append(values[0])
            meow_raw_data['Silver Gen'].append(values[1])
            meow_raw_data['Auto'].append(values[2])
            meow_raw_data['UPC'].append(values[3])
        else:
            formatted_values = ['-', '-', '-', '-']
            meow_raw_data['Overall'].append(None)
            meow_raw_data['Silver Gen'].append(None)
            meow_raw_data['Auto'].append(None)
            meow_raw_data['UPC'].append(None)
        
        # เพิ่ม trend indicators (เฉพาะจากเดือนที่ 2 เป็นต้นไป)
        if len(meow_raw_data['Overall']) > 1:
            trends = []
            for i, metric in enumerate(['Overall', 'Silver Gen', 'Auto', 'UPC']):
                current = meow_raw_data[metric][-1]
                previous = meow_raw_data[metric][-2]
                
                if current is not None and previous is not None:
                    if current > previous:
                        percentage = ((current - previous) / previous) * 100
                        trends.append(f"{current:,} 📈 (+{percentage:.1f}%)")
                    elif current < previous:
                        percentage = ((previous - current) / previous) * 100
                        trends.append(f"{current:,} 📉 (-{percentage:.1f}%)")
                    else:
                        trends.append(f"{current:,} ➡️ (0%)")
                else:
                    trends.append(formatted_values[i])
            
            meow_data[month_display] = trends
        else:
            meow_data[month_display] = formatted_values
    
    # สร้างตารางสำหรับ Asian Panel
    asian_data = {'Metric': ['Overall', 'Silver Gen', 'Auto', 'UPC']}
    asian_raw_data = {'Overall': [], 'Silver Gen': [], 'Auto': [], 'UPC': []}
    
    for month_key, month_display in all_months_2025:
        month_data = df[(df['Panel_Source'] == 'DS') & (df['Month_Year'] == month_key)]
        
        if len(month_data) > 0:
            row = month_data.iloc[0]
            values = [
                row['Total_Respondents_Count'],
                row['Silver_Gen_Count'],
                row['Auto_Count'],
                row['UPC_Count']
            ]
            formatted_values = [f"{val:,}" for val in values]
            asian_raw_data['Overall'].append(values[0])
            asian_raw_data['Silver Gen'].append(values[1])
            asian_raw_data['Auto'].append(values[2])
            asian_raw_data['UPC'].append(values[3])
        else:
            formatted_values = ['-', '-', '-', '-']
            asian_raw_data['Overall'].append(None)
            asian_raw_data['Silver Gen'].append(None)
            asian_raw_data['Auto'].append(None)
            asian_raw_data['UPC'].append(None)
        
        # เพิ่ม trend indicators
        if len(asian_raw_data['Overall']) > 1:
            trends = []
            for i, metric in enumerate(['Overall', 'Silver Gen', 'Auto', 'UPC']):
                current = asian_raw_data[metric][-1]
                previous = asian_raw_data[metric][-2]
                
                if current is not None and previous is not None:
                    if current > previous:
                        percentage = ((current - previous) / previous) * 100
                        trends.append(f"{current:,} 📈 (+{percentage:.1f}%)")
                    elif current < previous:
                        percentage = ((previous - current) / previous) * 100
                        trends.append(f"{current:,} 📉 (-{percentage:.1f}%)")
                    else:
                        trends.append(f"{current:,} ➡️ (0%)")
                else:
                    trends.append(formatted_values[i])
            
            asian_data[month_display] = trends
        else:
            asian_data[month_display] = formatted_values
    
    # สร้างตารางสำหรับ Combined (Meow + Asian)
    combined_data = {'Metric': ['Overall', 'Silver Gen', 'Auto', 'UPC']}
    combined_raw_data = {'Overall': [], 'Silver Gen': [], 'Auto': [], 'UPC': []}
    
    for month_key, month_display in all_months_2025:
        month_data = df[df['Month_Year'] == month_key]
        
        if len(month_data) > 0:
            values = [
                month_data['Total_Respondents_Count'].sum(),
                month_data['Silver_Gen_Count'].sum(),
                month_data['Auto_Count'].sum(),
                month_data['UPC_Count'].sum()
            ]
            formatted_values = [f"{val:,}" for val in values]
            combined_raw_data['Overall'].append(values[0])
            combined_raw_data['Silver Gen'].append(values[1])
            combined_raw_data['Auto'].append(values[2])
            combined_raw_data['UPC'].append(values[3])
        else:
            formatted_values = ['-', '-', '-', '-']
            combined_raw_data['Overall'].append(None)
            combined_raw_data['Silver Gen'].append(None)
            combined_raw_data['Auto'].append(None)
            combined_raw_data['UPC'].append(None)
        
        # เพิ่ม trend indicators
        if len(combined_raw_data['Overall']) > 1:
            trends = []
            for i, metric in enumerate(['Overall', 'Silver Gen', 'Auto', 'UPC']):
                current = combined_raw_data[metric][-1]
                previous = combined_raw_data[metric][-2]
                
                if current is not None and previous is not None:
                    if current > previous:
                        percentage = ((current - previous) / previous) * 100
                        trends.append(f"{current:,} 📈 (+{percentage:.1f}%)")
                    elif current < previous:
                        percentage = ((previous - current) / previous) * 100
                        trends.append(f"{current:,} 📉 (-{percentage:.1f}%)")
                    else:
                        trends.append(f"{current:,} ➡️ (0%)")
                else:
                    trends.append(formatted_values[i])
            
            combined_data[month_display] = trends
        else:
            combined_data[month_display] = formatted_values
    
    return pd.DataFrame(meow_data), pd.DataFrame(asian_data), pd.DataFrame(combined_data)

# สร้างตารางทั้ง 3 พร้อม trend indicators
meow_monthly_df, asian_monthly_df, combined_monthly_df = create_wide_monthly_comparison_tables_with_trends()

# เพิ่มคำอธิบาย trend indicators
st.markdown("""
**📊 Trend Indicators:**
- 📈 **Increasing**: Data increased from previous month
- 📉 **Decreasing**: Data decreased from previous month  
- ➡️ **Stable**: No change from previous month
- **Percentage**: Shows the rate of change compared to previous month
""")

# แสดงตาราง Meow Panel
st.subheader("🐱 Meow Panel")
st.dataframe(meow_monthly_df, hide_index=True, use_container_width=True)

# แสดงตาราง Asian Panel
st.subheader("🌏 Asian Panel")
st.dataframe(asian_monthly_df, hide_index=True, use_container_width=True)

# แสดงตาราง Combined
st.subheader("🔄 Meow + Asian")
st.dataframe(combined_monthly_df, hide_index=True, use_container_width=True)

# เพิ่มปุ่ม Download
st.markdown("### 📥 Download Monthly Comparison Data")
col1, col2, col3 = st.columns(3)

with col1:
    if len(meow_monthly_df) > 0:
        csv_meow = meow_monthly_df.to_csv(index=False)
        st.download_button(
            label="📥 Meow Monthly Data",
            data=csv_meow,
            file_name='meow_monthly_trends_2025.csv',
            mime='text/csv'
        )

with col2:
    if len(asian_monthly_df) > 0:
        csv_asian = asian_monthly_df.to_csv(index=False)
        st.download_button(
            label="📥 Asian Monthly Data",
            data=csv_asian,
            file_name='asian_monthly_trends_2025.csv',
            mime='text/csv'
        )

with col3:
    if len(combined_monthly_df) > 0:
        csv_combined = combined_monthly_df.to_csv(index=False)
        st.download_button(
            label="📥 Combined Monthly Data",
            data=csv_combined,
            file_name='combined_monthly_trends_2025.csv',
            mime='text/csv'
        )

# Charts Section
st.markdown("---")
st.header("📈 Demographic Analysis Charts")

if len(display_data) > 0:
    # สร้าง tabs สำหรับแต่ละประเภทข้อมูล
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🚗 Car Owner", "💰 Personal Income", "🏠 Household Income", 
        "🎂 Age Groups", "👥 Gender", "🌍 Region"
    ])
    
    with tab1:
        st.subheader("🚗 Car Ownership Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            # Car ownership distribution
            car_data = []
            for _, row in display_data.iterrows():
                panel_name = 'Meow' if row['Panel_Source'] == 'MS' else 'Asian Panel'
                car_data.extend([
                    {'Panel': panel_name, 'Car Count': '0 Cars', 'Respondents': row['Cars_At_Home_0_Count']},
                    {'Panel': panel_name, 'Car Count': '1 Car', 'Respondents': row['Cars_At_Home_1_Count']},
                    {'Panel': panel_name, 'Car Count': '2 Cars', 'Respondents': row['Cars_At_Home_2_Count']},
                    {'Panel': panel_name, 'Car Count': '3+ Cars', 'Respondents': row['Cars_At_Home_3_Or_More_Count']}
                ])
            
            if car_data:
                car_df = pd.DataFrame(car_data)
                fig_car = px.bar(car_df, 
                               x='Car Count', 
                               y='Respondents',
                               color='Panel',
                               title='Car Ownership Distribution',
                               barmode='group',
                               color_discrete_map={'Meow': '#FF6B35', 'Asian Panel': '#28A745'})
                st.plotly_chart(fig_car, use_container_width=True)
        
        with col2:
            # Car ownership pie chart (combined)
            total_car_data = {
                'Car Count': ['0 Cars', '1 Car', '2 Cars', '3+ Cars'],
                'Count': [
                    display_data['Cars_At_Home_0_Count'].sum(),
                    display_data['Cars_At_Home_1_Count'].sum(),
                    display_data['Cars_At_Home_2_Count'].sum(),
                    display_data['Cars_At_Home_3_Or_More_Count'].sum()
                ]
            }
            car_pie_df = pd.DataFrame(total_car_data)
            fig_car_pie = px.pie(car_pie_df, 
                               values='Count', 
                               names='Car Count',
                               title='Overall Car Ownership Distribution')
            st.plotly_chart(fig_car_pie, use_container_width=True)
        
    with tab2:
        st.subheader("💰 Personal Income (SES) Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            # Personal SES distribution
            personal_ses_data = []
            for _, row in display_data.iterrows():
                panel_name = 'Meow' if row['Panel_Source'] == 'MS' else 'Asian Panel'
                personal_ses_data.extend([
                    {'Panel': panel_name, 'SES Level': 'A', 'Respondents': row['SES_Personal_A_Count']},
                    {'Panel': panel_name, 'SES Level': 'B+', 'Respondents': row['SES_Personal_B_Plus_Count']},
                    {'Panel': panel_name, 'SES Level': 'B', 'Respondents': row['SES_Personal_B_Count']},
                    {'Panel': panel_name, 'SES Level': 'C+', 'Respondents': row['SES_Personal_C_Plus_Count']},
                    {'Panel': panel_name, 'SES Level': 'C', 'Respondents': row['SES_Personal_C_Count']},
                    {'Panel': panel_name, 'SES Level': 'D', 'Respondents': row['SES_Personal_D_Count']},
                    {'Panel': panel_name, 'SES Level': 'E', 'Respondents': row['SES_Personal_E_Count']}
                ])
            
            if personal_ses_data:
                personal_ses_df = pd.DataFrame(personal_ses_data)
                fig_personal_ses = px.bar(personal_ses_df, 
                                        x='SES Level', 
                                        y='Respondents',
                                        color='Panel',
                                        title='Personal Income Distribution (SES)',
                                        barmode='group',
                                        color_discrete_map={'Meow': '#FF6B35', 'Asian Panel': '#28A745'})
                st.plotly_chart(fig_personal_ses, use_container_width=True)
        
        with col2:
            # Personal SES pie chart
            total_personal_ses = {
                'SES Level': ['A', 'B+', 'B', 'C+', 'C', 'D', 'E'],
                'Count': [
                    display_data['SES_Personal_A_Count'].sum(),
                    display_data['SES_Personal_B_Plus_Count'].sum(),
                    display_data['SES_Personal_B_Count'].sum(),
                    display_data['SES_Personal_C_Plus_Count'].sum(),
                    display_data['SES_Personal_C_Count'].sum(),
                    display_data['SES_Personal_D_Count'].sum(),
                    display_data['SES_Personal_E_Count'].sum()
                ]
            }
            personal_ses_pie_df = pd.DataFrame(total_personal_ses)
            fig_personal_ses_pie = px.pie(personal_ses_pie_df, 
                                        values='Count', 
                                        names='SES Level',
                                        title='Overall Personal Income Distribution')
            st.plotly_chart(fig_personal_ses_pie, use_container_width=True)
    
    with tab3:
        st.subheader("🏠 Household Income (SES) Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            # Household SES distribution
            household_ses_data = []
            for _, row in display_data.iterrows():
                panel_name = 'Meow' if row['Panel_Source'] == 'MS' else 'Asian Panel'
                household_ses_data.extend([
                    {'Panel': panel_name, 'SES Level': 'A', 'Respondents': row['SES_Household_A_Count']},
                    {'Panel': panel_name, 'SES Level': 'B+', 'Respondents': row['SES_Household_B_Plus_Count']},
                    {'Panel': panel_name, 'SES Level': 'B', 'Respondents': row['SES_Household_B_Count']},
                    {'Panel': panel_name, 'SES Level': 'C+', 'Respondents': row['SES_Household_C_Plus_Count']},
                    {'Panel': panel_name, 'SES Level': 'C', 'Respondents': row['SES_Household_C_Count']},
                    {'Panel': panel_name, 'SES Level': 'D', 'Respondents': row['SES_Household_D_Count']},
                    {'Panel': panel_name, 'SES Level': 'E', 'Respondents': row['SES_Household_E_Count']}
                ])
            
            if household_ses_data:
                household_ses_df = pd.DataFrame(household_ses_data)
                fig_household_ses = px.bar(household_ses_df, 
                                         x='SES Level', 
                                         y='Respondents',
                                         color='Panel',
                                         title='Household Income Distribution (SES)',
                                         barmode='group',
                                         color_discrete_map={'Meow': '#FF6B35', 'Asian Panel': '#28A745'})
                st.plotly_chart(fig_household_ses, use_container_width=True)
        
        with col2:
            # Household SES pie chart
            total_household_ses = {
                'SES Level': ['A', 'B+', 'B', 'C+', 'C', 'D', 'E'],
                'Count': [
                    display_data['SES_Household_A_Count'].sum(),
                    display_data['SES_Household_B_Plus_Count'].sum(),
                    display_data['SES_Household_B_Count'].sum(),
                    display_data['SES_Household_C_Plus_Count'].sum(),
                    display_data['SES_Household_C_Count'].sum(),
                    display_data['SES_Household_D_Count'].sum(),
                    display_data['SES_Household_E_Count'].sum()
                ]
            }
            household_ses_pie_df = pd.DataFrame(total_household_ses)
            fig_household_ses_pie = px.pie(household_ses_pie_df, 
                                         values='Count', 
                                         names='SES Level',
                                         title='Overall Household Income Distribution')
            st.plotly_chart(fig_household_ses_pie, use_container_width=True)
    
    with tab4:
        st.subheader("🎂 Age Groups Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            # Age distribution
            age_data = []
            for _, row in display_data.iterrows():
                panel_name = 'Meow' if row['Panel_Source'] == 'MS' else 'Asian Panel'
                age_data.extend([
                    {'Panel': panel_name, 'Age Group': '18-19', 'Respondents': row['Age_18_19_Count']},
                    {'Panel': panel_name, 'Age Group': '20-29', 'Respondents': row['Age_20_29_Count']},
                    {'Panel': panel_name, 'Age Group': '30-39', 'Respondents': row['Age_30_39_Count']},
                    {'Panel': panel_name, 'Age Group': '40-49', 'Respondents': row['Age_40_49_Count']},
                    {'Panel': panel_name, 'Age Group': '50-59', 'Respondents': row['Age_50_59_Count']},
                    {'Panel': panel_name, 'Age Group': '60-69', 'Respondents': row['Age_60_69_Count']},
                    {'Panel': panel_name, 'Age Group': '70+', 'Respondents': row['Age_70_99_Count']}
                ])
            
            if age_data:
                age_df = pd.DataFrame(age_data)
                fig_age = px.bar(age_df, 
                               x='Age Group', 
                               y='Respondents',
                               color='Panel',
                               title='Age Distribution',
                               barmode='group',
                               color_discrete_map={'Meow': '#FF6B35', 'Asian Panel': '#28A745'})
                st.plotly_chart(fig_age, use_container_width=True)
        
        with col2:
            # Age pie chart
            total_age_data = {
                'Age Group': ['18-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70+'],
                'Count': [
                    display_data['Age_18_19_Count'].sum(),
                    display_data['Age_20_29_Count'].sum(),
                    display_data['Age_30_39_Count'].sum(),
                    display_data['Age_40_49_Count'].sum(),
                    display_data['Age_50_59_Count'].sum(),
                    display_data['Age_60_69_Count'].sum(),
                    display_data['Age_70_99_Count'].sum()
                ]
            }
            age_pie_df = pd.DataFrame(total_age_data)
            fig_age_pie = px.pie(age_pie_df, 
                               values='Count', 
                               names='Age Group',
                               title='Overall Age Distribution')
            st.plotly_chart(fig_age_pie, use_container_width=True)
    
    with tab5:
        st.subheader("👥 Gender Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            # Gender distribution
            gender_data = []
            for _, row in display_data.iterrows():
                panel_name = 'Meow' if row['Panel_Source'] == 'MS' else 'Asian Panel'
                gender_data.extend([
                    {'Panel': panel_name, 'Gender': 'Male', 'Respondents': row['Gender_Male_Count']},
                    {'Panel': panel_name, 'Gender': 'Female', 'Respondents': row['Gender_Female_Count']}
                ])
            
            if gender_data:
                gender_df = pd.DataFrame(gender_data)
                fig_gender = px.bar(gender_df, 
                                  x='Gender', 
                                  y='Respondents',
                                  color='Panel',
                                  title='Gender Distribution',
                                  barmode='group',
                                  color_discrete_map={'Meow': '#FF6B35', 'Asian Panel': '#28A745'})
                st.plotly_chart(fig_gender, use_container_width=True)
        
        with col2:
            # Gender pie chart
            total_gender_data = {
                'Gender': ['Male', 'Female'],
                'Count': [
                    display_data['Gender_Male_Count'].sum(),
                    display_data['Gender_Female_Count'].sum()
                ]
            }
            gender_pie_df = pd.DataFrame(total_gender_data)
            fig_gender_pie = px.pie(gender_pie_df, 
                                  values='Count', 
                                  names='Gender',
                                  title='Overall Gender Distribution',
                                  color_discrete_map={'Male': '#4A90E2', 'Female': '#E24A8A'})
            st.plotly_chart(fig_gender_pie, use_container_width=True)
    
    with tab6:
        st.subheader("🌍 Regional Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            # Regional distribution
            region_data = []
            for _, row in display_data.iterrows():
                panel_name = 'Meow' if row['Panel_Source'] == 'MS' else 'Asian Panel'
                region_data.extend([
                    {'Panel': panel_name, 'Region': 'Bangkok Metro', 'Respondents': row['Region_Bangkok_Metropolitan_Count']},
                    {'Panel': panel_name, 'Region': 'Central', 'Respondents': row['Region_Central_Count']},
                    {'Panel': panel_name, 'Region': 'Northeast', 'Respondents': row['Region_Northeast_Count']},
                    {'Panel': panel_name, 'Region': 'North', 'Respondents': row['Region_North_Count']},
                    {'Panel': panel_name, 'Region': 'East', 'Respondents': row['Region_East_Count']},
                    {'Panel': panel_name, 'Region': 'West', 'Respondents': row['Region_West_Count']},
                    {'Panel': panel_name, 'Region': 'South', 'Respondents': row['Region_South_Count']}
                ])
            
            if region_data:
                region_df = pd.DataFrame(region_data)
                fig_region = px.bar(region_df, 
                                  x='Region', 
                                  y='Respondents',
                                  color='Panel',
                                  title='Regional Distribution',
                                  barmode='group',
                                  color_discrete_map={'Meow': '#FF6B35', 'Asian Panel': '#28A745'})
                fig_region.update_xaxes(tickangle=45)
                st.plotly_chart(fig_region, use_container_width=True)
        
        with col2:
            # Regional pie chart
            total_region_data = {
                'Region': ['Bangkok Metro', 'Central', 'Northeast', 'North', 'East', 'West', 'South'],
                'Count': [
                    display_data['Region_Bangkok_Metropolitan_Count'].sum(),
                    display_data['Region_Central_Count'].sum(),
                    display_data['Region_Northeast_Count'].sum(),
                    display_data['Region_North_Count'].sum(),
                    display_data['Region_East_Count'].sum(),
                    display_data['Region_West_Count'].sum(),
                    display_data['Region_South_Count'].sum()
                ]
            }
            region_pie_df = pd.DataFrame(total_region_data)
            fig_region_pie = px.pie(region_pie_df, 
                                  values='Count', 
                                  names='Region',
                                  title='Overall Regional Distribution')
            st.plotly_chart(fig_region_pie, use_container_width=True)

    # เพิ่มส่วนสรุปข้อมูล demographic
    st.markdown("---")
    st.subheader("📊 Demographic Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🚗 Car Ownership Highlights**")
        total_with_cars = (display_data['Cars_At_Home_1_Count'].sum() + 
                          display_data['Cars_At_Home_2_Count'].sum() + 
                          display_data['Cars_At_Home_3_Or_More_Count'].sum())
        total_respondents_demo = display_data['Total_Respondents_Count'].sum()
        car_ownership_rate = (total_with_cars / total_respondents_demo * 100) if total_respondents_demo > 0 else 0
        st.write(f"• Car Ownership Rate: {car_ownership_rate:.1f}%")
        st.write(f"• Households with Cars: {total_with_cars:,}")
        st.write(f"• No Car Households: {display_data['Cars_At_Home_0_Count'].sum():,}")
    
    with col2:
        st.markdown("**👥 Gender & Age Highlights**")
        male_count = display_data['Gender_Male_Count'].sum()
        female_count = display_data['Gender_Female_Count'].sum()
        gender_ratio = (female_count / male_count * 100) if male_count > 0 else 0
        silver_gen_rate = (display_data['Silver_Gen_Count'].sum() / total_respondents_demo * 100) if total_respondents_demo > 0 else 0
        st.write(f"• Female/Male Ratio: {gender_ratio:.1f}%")
        st.write(f"• Silver Gen (60+): {silver_gen_rate:.1f}%")
        st.write(f"• Young Adults (20-29): {(display_data['Age_20_29_Count'].sum() / total_respondents_demo * 100):.1f}%")
    
    with col3:
        st.markdown("**🌍 Regional Highlights**")
        bangkok_count = display_data['Region_Bangkok_Metropolitan_Count'].sum()
        upc_count = display_data['UPC_Count'].sum()
        bangkok_rate = (bangkok_count / total_respondents_demo * 100) if total_respondents_demo > 0 else 0
        upc_rate = (upc_count / total_respondents_demo * 100) if total_respondents_demo > 0 else 0
        st.write(f"• Bangkok Metro: {bangkok_rate:.1f}%")
        st.write(f"• Upcountry (UPC): {upc_rate:.1f}%")
        st.write(f"• Most Represented Region: {['Central', 'Northeast', 'North', 'East', 'West', 'South'][0]}")

# Monthly Trend (แสดงเฉพาะเมื่อมีข้อมูลหลายเดือน)
if selected_month == 'All' and len(df['Month_Year'].unique()) > 1:
    st.subheader("📈 Monthly Trend")
    
    trend_data = []
    for _, row in filtered_df.iterrows():
        panel_name = 'Meow' if row['Panel_Source'] == 'MS' else 'Asian panel'
        trend_data.append({
            'Month': row['Month_Year'],
            'Panel': panel_name,
            'Overall': row['Total_Respondents_Count'],
            'Silver Gen': row['Silver_Gen_Count'],
            'Auto': row['Auto_Count'],
            'UPC': row['UPC_Count']
        })
    
    if trend_data:
        trend_df = pd.DataFrame(trend_data)
        
        # สร้างกราฟเส้นสำหรับแต่ละ metric
        metrics_to_plot = ['Overall', 'Silver Gen', 'Auto', 'UPC']
        
        fig_trend = make_subplots(rows=2, cols=2, 
                                 subplot_titles=metrics_to_plot,
                                 specs=[[{"secondary_y": False}, {"secondary_y": False}],
                                       [{"secondary_y": False}, {"secondary_y": False}]])
        
        colors = {'Meow': '#FF6B35', 'Asian panel': '#28A745'}
        panels = trend_df['Panel'].unique()
        
        for i, metric in enumerate(metrics_to_plot):
            row = (i // 2) + 1
            col = (i % 2) + 1
            
            for panel in panels:
                panel_data = trend_df[trend_df['Panel'] == panel]
                if len(panel_data) > 0:
                    fig_trend.add_trace(
                        go.Scatter(x=panel_data['Month'], 
                                  y=panel_data[metric],
                                  mode='lines+markers',
                                  name=f'{panel} - {metric}',
                                  line=dict(color=colors.get(panel, 'blue')),
                                  showlegend=(i == 0)),  # แสดง legend เฉพาะกราฟแรก
                        row=row, col=col
                    )
        
        fig_trend.update_layout(height=600, title_text="Monthly Trends by Panel")
        st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# Data Table Section
st.header("📋 Raw Data")

# แสดงข้อมูลดิบที่ถูกกรอง
display_cols = ['Panel_Source', 'Month_Year', 'Total_Respondents_Count', 
                'Silver_Gen_Count', 'Auto_Count', 'UPC_Count']
raw_display_df = filtered_df[display_cols].copy()
raw_display_df.columns = ['Panel Source', 'Month', 'Overall', 'Silver Gen', 'Auto', 'UPC']

# แปลชื่อ Panel Source
raw_display_df['Panel Source'] = raw_display_df['Panel Source'].map({'MS': 'Meow', 'DS': 'Asian panel'})

st.dataframe(raw_display_df, use_container_width=True)

# Additional Data Details
with st.expander("📊 View Additional Data Details"):
    st.subheader("Gender Distribution")
    gender_cols = ['Panel_Source', 'Month_Year', 'Gender_Male_Count', 'Gender_Female_Count']
    gender_df = filtered_df[gender_cols].copy()
    gender_df.columns = ['Panel Source', 'Month', 'Male', 'Female']
    gender_df['Panel Source'] = gender_df['Panel Source'].map({'MS': 'Meow', 'DS': 'Asian panel'})
    st.dataframe(gender_df, use_container_width=True)
    
    st.subheader("Age Distribution")
    age_cols = ['Panel_Source', 'Month_Year', 'Age_18_19_Count', 'Age_20_29_Count', 
                'Age_30_39_Count', 'Age_40_49_Count', 'Age_50_59_Count', 'Age_60_69_Count', 'Age_70_99_Count']
    age_df = filtered_df[age_cols].copy()
    age_df.columns = ['Panel Source', 'Month', '18-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70+']
    age_df['Panel Source'] = age_df['Panel Source'].map({'MS': 'Meow', 'DS': 'Asian panel'})
    st.dataframe(age_df, use_container_width=True)
    
    st.subheader("Regional Distribution")
    region_cols = ['Panel_Source', 'Month_Year', 'Region_Bangkok_Metropolitan_Count', 'Region_Central_Count',
                   'Region_Northeast_Count', 'Region_North_Count', 'Region_East_Count', 'Region_West_Count', 'Region_South_Count']
    region_df = filtered_df[region_cols].copy()
    region_df.columns = ['Panel Source', 'Month', 'Bangkok Metro', 'Central', 'Northeast', 'North', 'East', 'West', 'South']
    region_df['Panel Source'] = region_df['Panel Source'].map({'MS': 'Meow', 'DS': 'Asian panel'})
    st.dataframe(region_df, use_container_width=True)

# Download button
if len(raw_display_df) > 0:
    csv = raw_display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download filtered data as CSV",
        data=csv,
        file_name=f'analytics_data_{selected_panel}_{selected_month}.csv',
        mime='text/csv'
    )

# Footer
st.markdown("---")
st.markdown("**📊 Analytics Dashboard** | Built with Streamlit & Plotly")
st.markdown("**Data Source:** monthly_profiling_summary.csv")