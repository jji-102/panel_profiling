import os
import pandas as pd

# --- 0. ตั้งค่าพื้นฐาน ---
current_month = '2025-06-01'
ds_data_folder = './data/ds_data/'
processed_data_folder = './processed_data/'

# --- 1. Common Data Model Columns ---
all_common_data_model_columns = [
    "Panel_Source", "Collected_Month", "Total_Respondents_Count", "Gender_Male_Count", "Gender_Female_Count",
    "Age_18_19_Count", "Age_20_29_Count", "Age_30_39_Count", "Age_40_49_Count", "Age_50_59_Count",
    "Age_60_69_Count", "Age_70_99_Count",
    "SES_Personal_A_Count", "SES_Personal_B_Plus_Count", "SES_Personal_B_Count", "SES_Personal_C_Plus_Count",
    "SES_Personal_C_Count", "SES_Personal_D_Count", "SES_Personal_E_Count", "SES_Personal_Unspecified_Count",
    "SES_Household_A_Count", "SES_Household_B_Plus_Count", "SES_Household_B_Count", "SES_Household_C_Plus_Count",
    "SES_Household_C_Count", "SES_Household_D_Count", "SES_Household_E_Count", "SES_Household_Unspecified_Count",
    "Occupation_Government_Count", "Occupation_Professional_Count", "Occupation_Commercial_Service_Count",
    "Occupation_Student_Count", "Occupation_General_Labor_Count", "Occupation_Unemployed_Count",
    "Occupation_Housewife_Count", "Occupation_Others_Count", "Occupation_Unspecified_Count",
    "Employment_Employed_Someone_Else_More_30_Hrs_Count", "Employment_Employed_Someone_Else_Less_30_Hrs_Count",
    "Employment_Self_Employed_Count", "Employment_Not_Employed_Looking_Count", "Employment_Student_Count",
    "Employment_Housewife_Count", "Employment_Not_Employed_Other_Count", "Employment_Unspecified_Count",
    "Region_Bangkok_Metropolitan_Count", "Region_Central_Count", "Region_Northeast_Count", "Region_North_Count",
    "Region_East_Count", "Region_West_Count", "Region_South_Count", "Region_Unspecified_Count",
    "Cars_At_Home_0_Count", "Cars_At_Home_1_Count", "Cars_At_Home_2_Count", "Cars_At_Home_3_Or_More_Count",
    "Cars_At_Home_Unspecified_Count",
    "Car_Owner_Yourself_Count", "Car_Owner_Spouse_Count", "Car_Owner_Parent_Count", "Car_Owner_Child_Count",
    "Car_Owner_Grandparents_Count", "Car_Owner_Brothers_Sisters_Count", "Car_Owner_Others_Count", "Car_Owner_Dont_Know_Count"
]

# --- 2. แก้ไขฟังก์ชัน mapping SES ---
def map_income_range_to_ses(income_range_str):
    income_range_str = str(income_range_str).lower().strip()
    
    if '150,000 thb or higher' in income_range_str or '100,000 thb or higher' in income_range_str:
        return 'A'
    elif '100,000 - 149,999 thb' in income_range_str or '75,000 - 99,999 thb' in income_range_str or '50,000 - 74,999 thb' in income_range_str or '50,000 - 99,999 thb' in income_range_str:
        return 'B_Plus'
    elif '30,000 - 49,999 thb' in income_range_str:
        return 'B'
    elif '20,000 - 29,999 thb' in income_range_str:
        return 'C_Plus'
    elif '10,000 - 19,999 thb' in income_range_str:
        return 'C'
    elif '5,000 - 9,999 thb' in income_range_str:
        return 'D'
    elif 'less than 5,000 thb' in income_range_str:
        return 'E'
    else:
        return 'Unspecified'

# --- 3. อ่านไฟล์ข้อมูล ---
month_code = current_month.replace('-', '')[:6]

# Gender
df_ds_gender = pd.read_csv(f"{ds_data_folder}ds_gender_{month_code}.csv", encoding='utf-8')

# Age
df_ds_age = pd.read_csv(f"{ds_data_folder}ds_age_{month_code}.csv", encoding='utf-8')
df_ds_age = df_ds_age[df_ds_age['Age'] != 'I do not want to answer']

# Personal Income
df_ds_personal_income = pd.read_csv(f"{ds_data_folder}ds_personal_income_{month_code}.csv", encoding='utf-8')

# Household Income
df_ds_household_income = pd.read_csv(f"{ds_data_folder}ds_household_income_{month_code}.csv", encoding='utf-8')

# Occupation
df_ds_occupation = pd.read_csv(f"{ds_data_folder}ds_occupation_{month_code}.csv", encoding='utf-8')

# Employment
df_ds_employment = pd.read_csv(f"{ds_data_folder}ds_employment_{month_code}.csv", encoding='utf-8')

# Region
df_ds_region = pd.read_csv(f"{ds_data_folder}ds_region_{month_code}.csv", encoding='utf-8')

# Cars
df_ds_cars = pd.read_csv(f"{ds_data_folder}ds_cars_{month_code}.csv", encoding='utf-8')

# Car Owner
df_ds_car_owner = pd.read_csv(f"{ds_data_folder}ds_car_owner_{month_code}.csv", encoding='utf-8')

# --- 4. สร้าง Dictionary สำหรับเก็บผลลัพธ์ ---
ds_monthly_summary = {}
ds_monthly_summary['Panel_Source'] = 'DS'
ds_monthly_summary['Collected_Month'] = pd.to_datetime(current_month)
ds_monthly_summary['Total_Respondents_Count'] = df_ds_gender['Count'].sum()

# --- 5. ประมวลผล Gender ---
df_ds_gender['Gender'] = df_ds_gender['Gender'].astype(str).str.strip().str.capitalize()
male_count = df_ds_gender[df_ds_gender['Gender'] == 'Male']['Count'].sum()
female_count = df_ds_gender[df_ds_gender['Gender'] == 'Female']['Count'].sum()

ds_monthly_summary['Gender_Male_Count'] = male_count if pd.notna(male_count) else 0
ds_monthly_summary['Gender_Female_Count'] = female_count if pd.notna(female_count) else 0

# --- 6. ประมวลผล Age ---
age_mapping = {
    '18-19': 'Age_18_19_Count',
    '20-29': 'Age_20_29_Count',
    '30-39': 'Age_30_39_Count',
    '40-49': 'Age_40_49_Count',
    '50-59': 'Age_50_59_Count',
    '60-69': 'Age_60_69_Count',
    '70-99': 'Age_70_99_Count'
}

for index, row in df_ds_age.iterrows():
    age_group = row['Age']
    if age_group in age_mapping:
        ds_monthly_summary[age_mapping[age_group]] = row['N']

# --- 7. ประมวลผล SES ---
ses_personal_counts = {}
ses_household_counts = {}

# Personal Income
for index, row in df_ds_personal_income.iterrows():
    ses_category = map_income_range_to_ses(row['Personal Income'])
    ses_personal_counts[ses_category] = ses_personal_counts.get(ses_category, 0) + row['Count']

# Household Income
for index, row in df_ds_household_income.iterrows():
    ses_category = map_income_range_to_ses(row['Household income'])
    ses_household_counts[ses_category] = ses_household_counts.get(ses_category, 0) + row['Count']

# เติมค่า SES ลงใน summary
ses_categories_list = ['A', 'B_Plus', 'B', 'C_Plus', 'C', 'D', 'E', 'Unspecified']
for ses_cat in ses_categories_list:
    ds_monthly_summary[f'SES_Personal_{ses_cat}_Count'] = ses_personal_counts.get(ses_cat, 0)
    ds_monthly_summary[f'SES_Household_{ses_cat}_Count'] = ses_household_counts.get(ses_cat, 0)

# --- 8. ประมวลผล Occupation ---
occupation_map = {
    'Government worker (excluding Teacher)': 'Government',
    'Teacher': 'Government',  # รวมกับ Government
    'Official of association': 'Professional',
    'Self-owned business (Commercial service)': 'Commercial_Service',
    'Specialist (legal or management related, ex. lawyer, tax accountant)': 'Professional',
    'Specialist (medical worker, ex. doctor)': 'Professional',
    'Specialist (engineer, etc.)': 'General_Labor',
    'Others': 'Others',
    'Have not answered yet': 'Unspecified'
}

for index, row in df_ds_occupation.iterrows():
    occupation_clean = row['Occupation Category'].strip()
    mapped_occupation = occupation_map.get(occupation_clean, 'Unspecified')
    col_name = f'Occupation_{mapped_occupation}_Count'
    if col_name in all_common_data_model_columns:
        ds_monthly_summary[col_name] = ds_monthly_summary.get(col_name, 0) + row['Count']

# --- 9. ประมวลผล Employment ---
employment_map = {
    'Employed by someone else, working 30 hours or more per week': 'Employed_Someone_Else_More_30_Hrs',
    'Employed part-time by someone else, working less than 30 hours per week': 'Employed_Someone_Else_Less_30_Hrs',
    'Self-employed, working outside your home': 'Self_Employed',
    'Self-employed, working in our home': 'Self_Employed',
    'Middle school student': 'Student',
    'High school student': 'Student',
    'University student': 'Student',
    'Graduate student': 'Student',
    'Retired': 'Not_Employed_Other',
    'Housewife': 'Housewife',
    'Not currently employed': 'Not_Employed_Looking',
    'Others': 'Not_Employed_Other',
    'Have not answered yet': 'Unspecified'
}

for index, row in df_ds_employment.iterrows():
    employment_clean = row['Employment Status'].strip()
    mapped_employment = employment_map.get(employment_clean, 'Unspecified')
    col_name = f'Employment_{mapped_employment}_Count'
    if col_name in all_common_data_model_columns:
        ds_monthly_summary[col_name] = ds_monthly_summary.get(col_name, 0) + row['Region Area Count']

# --- 10. ประมวลผล Region ---
region_map = {
    'Bangkok Metropolitan': 'Bangkok_Metropolitan',
    'Sub-Central': 'Central',
    'Northern': 'North',
    'Northeastern': 'Northeast',
    'Eastern': 'East',
    'Western': 'West',
    'Southern': 'South'
}

for index, row in df_ds_region.iterrows():
    region_clean = row['Region Area'].strip()
    mapped_region = region_map.get(region_clean, 'Unspecified')
    col_name = f'Region_{mapped_region}_Count'
    if col_name in all_common_data_model_columns:
        ds_monthly_summary[col_name] = ds_monthly_summary.get(col_name, 0) + row['Region Area Count']

# --- 11. ประมวลผล Cars ---
cars_map = {
    '0': '0',
    '1': '1',
    '2': '2',
    '3 or more': '3_Or_More'
}

for index, row in df_ds_cars.iterrows():
    cars_clean = str(row['Number of cars at home']).strip()
    mapped_cars = cars_map.get(cars_clean, 'Unspecified')
    col_name = f'Cars_At_Home_{mapped_cars}_Count'
    if col_name in all_common_data_model_columns:
        ds_monthly_summary[col_name] = ds_monthly_summary.get(col_name, 0) + row['Count']

# --- 12. ประมวลผล Car Owner ---
car_owner_map = {
    'Yourself': 'Yourself',
    'Spouse': 'Spouse',
    'Parent': 'Parent',
    'Child': 'Child',
    'Grand parents': 'Grandparents',
    'Brothers and sisters': 'Brothers_Sisters',
    'Others': 'Others',
    "Don't Know": 'Dont_Know'
}

for index, row in df_ds_car_owner.iterrows():
    owner_clean = row['Owner of car'].strip()
    mapped_owner = car_owner_map.get(owner_clean, 'Dont_Know')
    col_name = f'Car_Owner_{mapped_owner}_Count'
    if col_name in all_common_data_model_columns:
        ds_monthly_summary[col_name] = ds_monthly_summary.get(col_name, 0) + row['Count']

# --- 13. สร้าง DataFrame สุดท้าย ---
df_ds_result = pd.DataFrame([ds_monthly_summary])
df_ds_result = df_ds_result.reindex(columns=all_common_data_model_columns).fillna(0)

# แสดงผลลัพธ์
print("DS Monthly Summary (Preview):")
print(df_ds_result.transpose())

# บันทึกไฟล์
if not os.path.exists(processed_data_folder):
    os.makedirs(processed_data_folder)
    
df_ds_result.to_csv(f"{processed_data_folder}temp_ds_data_{month_code}.csv", index=False, encoding='utf-8')
print(f"Processed DS data saved to {processed_data_folder}temp_ds_data_{month_code}.csv")