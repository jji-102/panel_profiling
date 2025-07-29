import pandas as pd
import os

# --- 0. ตั้งค่าพื้นฐาน (ปรับค่าเหล่านี้ทุกเดือน) ---
current_month = '2025-05-01' # ตัวอย่าง: May 2025. คุณจะเปลี่ยนเป็น 2025-06-01, 2025-07-01, ...
ms_data_folder = './data/ms_data/' # โฟลเดอร์ที่เก็บไฟล์ MS (แก้ไขให้ตรงกับตำแหน่งไฟล์ของคุณ)
processed_data_folder = './processed_data/' # โฟลเดอร์สำหรับเก็บผลลัพธ์ (แก้ไขให้ตรงกับตำแหน่งไฟล์ของคุณ)
ms_file_name = f"ms_data_202505.csv" # ชื่อไฟล์ MS ที่คุณเตรียมไว้


# --- 1. เตรียม Common Data Model Columns ทั้งหมด (จาก CSV Template ที่คุณสร้างไว้) ---
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

# --- 2. ฟังก์ชันและ Mapping สำหรับ Data Transformation (กำหนดครั้งเดียว) ---

def map_income_range_to_ses(income_range_str):
    income_range_str = str(income_range_str).lower().strip()
    if '100,000 thb or higher' in income_range_str or '100,000 - 200,000 thb' in income_range_str or '200,001 - 300,000 thb' in income_range_str:
        return 'A'
    elif '50,000 - 99,999 thb' in income_range_str or '50,001 - 75,000 thb' in income_range_str or '70,000 - 79,999 thb' in income_range_str or '60,000 - 69,999 thb' in income_range_str:
        return 'B+'
    elif '30,000 - 49,999 thb' in income_range_str or '40,000 - 49,999 thb' in income_range_str:
        return 'B'
    elif '20,000 - 29,999 thb' in income_range_str:
        return 'C+'
    elif '10,000 - 19,999 thb' in income_range_str or '10,000 - 14,999 thb' in income_range_str:
        return 'C'
    elif '5,000 - 9,999 thb' in income_range_str or '<10,000 thb' in income_range_str:
        return 'D'
    elif 'less than 5,000 thb' in income_range_str:
        return 'E'
    elif 'don\'t know' in income_range_str or 'i do not want to answer' in income_range_str or 'have not answered yet' in income_range_str or pd.isna(income_range_str) or 'ไม่ระบุ' in income_range_str or 'nan' in income_range_str:
        return 'Unspecified'
    else:
        return 'Unspecified'

def map_ms_age_to_ds_standard(age):
    try:
        age = int(age)
    except (ValueError, TypeError):
        return 'Unspecified'

    if 18 <= age <= 19:
        return '18_19'
    elif 20 <= age <= 29:
        return '20_29'
    elif 30 <= age <= 39:
        return '30_39'
    elif 40 <= age <= 49:
        return '40_49'
    elif 50 <= age <= 59:
        return '50_59'
    elif 60 <= age <= 69:
        return '60_69'
    elif 70 <= age <= 99:
        return '70_99'
    else:
        return 'Unspecified'

province_to_region_map = {
    'กรุงเทพมหานคร': 'Bangkok_Metropolitan', 'สมุทรปราการ': 'Bangkok_Metropolitan', 'นนทบุรี': 'Bangkok_Metropolitan',
    'ปทุมธานี': 'Bangkok_Metropolitan', 'นครปฐม': 'Bangkok_Metropolitan', 'สมุทรสาคร': 'Bangkok_Metropolitan',
    'กาญจนบุรี': 'Central', 'ชัยนาท': 'Central', 'นครนายก': 'Central', 'พระนครศรีอยุธยา': 'Central', 'ลพบุรี': 'Central',
    'สระบุรี': 'Central', 'สิงห์บุรี': 'Central', 'อ่างทอง': 'Central', 'ราชบุรี': 'Central', 'สุพรรณบุรี': 'Central',
    'สมุทรสงคราม': 'Central', 'เชียงใหม่': 'North', 'เชียงราย': 'North', 'ลำปาง': 'North', 'ลำพูน': 'North',
    'แม่ฮ่องสอน': 'North', 'น่าน': 'North', 'พะเยา': 'North', 'แพร่': 'North', 'อุตรดิตถ์': 'North', 'ตาก': 'North',
    'สุโขทัย': 'North', 'พิษณุโลก': 'North', 'พิจิตร': 'North', 'กำแพงเพชร': 'North', 'เพชรบูรณ์': 'North',
    'นครสวรรค์': 'North', 'อุทัยธานี': 'North', 'ขอนแก่น': 'Northeast', 'นครราชสีมา': 'Northeast', 'กาฬสินธุ์': 'Northeast',
    'ชัยภูมิ': 'Northeast', 'นครพนม': 'Northeast', 'บึงกาฬ': 'Northeast', 'บุรีรัมย์': 'Northeast', 'มหาสารคาม': 'Northeast',
    'มุกดาหาร': 'Northeast', 'ยโสธร': 'Northeast', 'ร้อยเอ็ด': 'Northeast', 'เลย': 'Northeast', 'ศรีสะเกษ': 'Northeast',
    'สกลนคร': 'Northeast', 'สุรินทร์': 'Northeast', 'หนองคาย': 'Northeast', 'หนองบัวลำภู': 'Northeast', 'อำนาจเจริญ': 'Northeast',
    'อุดรธานี': 'Northeast', 'อุบลราชธานี': 'Northeast', 'ชลบุรี': 'East', 'จันทบุรี': 'East', 'ฉะเชิงเทรา': 'East',
    'ตราด': 'East', 'ปราจีนบุรี': 'East', 'ระยอง': 'East', 'สระแก้ว': 'East', 'กระบี่': 'South', 'ชุมพร': 'South',
    'ตรัง': 'South', 'นครศรีธรรมราช': 'South', 'นราธิวาส': 'South', 'ปัตตานี': 'South', 'พังงา': 'South',
    'พัทลุง': 'South', 'ภูเก็ต': 'South', 'ยะลา': 'South', 'ระนอง': 'South', 'สงขลา': 'South', 'สตูล': 'South',
    'สุราษฎร์ธานี': 'South', 'ไม่ระบุ': 'Unspecified', 'อื่นๆ': 'Unspecified', 'Unknown': 'Unspecified',
    None: 'Unspecified', '': 'Unspecified'
}

# --- 3. อ่านข้อมูลจากไฟล์ MS ---
ms_file_path = f"{ms_data_folder}{ms_file_name}"
try:
    df_ms_raw = pd.read_csv(ms_file_path, encoding='utf-8')
except FileNotFoundError:
    print(f"Error: MS file not found at {ms_file_path}. Please check file path and name.")
    exit()
except Exception as e:
    print(f"Error reading MS file: {e}")
    exit()

# --- 4. Clean & Rename คอลัมน์ ---
df_ms_raw = df_ms_raw.rename(columns={
    'Resp ID': 'Respondent_ID', 'Q1_Age': 'Age', 'Q2_Gender': 'Gender',
    'Q3_Personal_Income': 'Personal_Income', 'Q4_Household_Income': 'Household_Income',
    'Q5_Occupation': 'Occupation', 'Q6_Employment': 'Employment_Status',
    'Q7_Province': 'Province', 'Q8_Car_Num': 'Number_of_Cars_at_Home',
    'Q9_Car_Owner': 'Owner_of_Car',
})

print("MS Raw Data Columns after Rename:", df_ms_raw.columns)

# --- 5. สร้าง Dictionary เพื่อเก็บผลลัพธ์ ---
ms_monthly_summary = {}
ms_monthly_summary['Panel_Source'] = 'MS'
ms_monthly_summary['Collected_Month'] = pd.to_datetime(current_month)
ms_monthly_summary['Total_Respondents_Count'] = len(df_ms_raw)

# --- 6. ประมวลผล Gender ---
df_ms_raw['Gender_Cleaned'] = df_ms_raw['Gender'].astype(str).str.strip().str.lower().replace({'ชาย': 'male', 'หญิง': 'female'})
ms_monthly_summary['Gender_Male_Count'] = (df_ms_raw['Gender_Cleaned'] == 'male').sum()
ms_monthly_summary['Gender_Female_Count'] = (df_ms_raw['Gender_Cleaned'] == 'female').sum()

# --- 7. ประมวลผล Age ---
df_ms_raw['Age_DS_Standard'] = df_ms_raw['Age'].apply(map_ms_age_to_ds_standard)
age_counts = df_ms_raw['Age_DS_Standard'].value_counts()
age_categories_list = ['18_19', '20_29', '30_39', '40_49', '50_59', '60_69', '70_99']
for age_cat in age_categories_list:
    ms_monthly_summary[f'Age_{age_cat}_Count'] = age_counts.get(age_cat, 0)

# --- 8. ประมวลผล SES ---
df_ms_raw['SES_Personal_Category'] = df_ms_raw['Personal_Income'].apply(map_income_range_to_ses)
df_ms_raw['SES_Household_Category'] = df_ms_raw['Household_Income'].apply(map_income_range_to_ses)
ses_personal_counts = df_ms_raw['SES_Personal_Category'].value_counts()
ses_household_counts = df_ms_raw['SES_Household_Category'].value_counts()
ses_categories_list_with_unspecified = ['A', 'B_Plus', 'B', 'C_Plus', 'C', 'D', 'E', 'Unspecified']
for ses_cat in ses_categories_list_with_unspecified:
    key = ses_cat if ses_cat != 'B_Plus' else 'B+'
    ms_monthly_summary[f'SES_Personal_{ses_cat}_Count'] = ses_personal_counts.get(key, 0)
    ms_monthly_summary[f'SES_Household_{ses_cat}_Count'] = ses_household_counts.get(key, 0)

# --- 9. ประมวลผล Occupation ---
occupation_map = {
    'ข้าราชการ/พนักงานรัฐวิสาหกิจ': 'Government',
    'พนักงานบริษัท': 'Professional',
    'พนักงานบริษัท/ลูกจ้างเอกชน': 'Professional',
    'พนักงานประจำโรงงาน': 'General_Labor',
    'นักเรียน/นักศึกษา': 'Student',
    'แม่บ้าน/พ่อบ้าน': 'Housewife',
    'เกษตรกร/ประมง': 'General_Labor',
    'รับจ้างทั่วไป': 'General_Labor',
    'ไม่ได้ทำงาน/เกษียณ': 'Unemployed',
    'ว่างงาน': 'Unemployed',
    'ผู้ประกอบอาชีพอิสระ': 'Others',
    'กลุ่มอาชีพ รายได้ไม่ประจำ เช่น \nฟรีแลนซ์ , อาชีพอิสระ': 'Others',
    'อื่นๆ': 'Others',
    'ไม่ระบุ': 'Unspecified',
}
df_ms_raw['Occupation_Cleaned'] = df_ms_raw['Occupation'].astype(str).str.strip().map(occupation_map).fillna('Unspecified')
occupation_counts = df_ms_raw['Occupation_Cleaned'].value_counts()
occupation_categories = [
    'Government', 'Professional', 'Commercial_Service', 'Student', 'General_Labor',
    'Unemployed', 'Housewife', 'Others', 'Unspecified'
]
for occ_cat in occupation_categories:
    ms_monthly_summary[f'Occupation_{occ_cat}_Count'] = occupation_counts.get(occ_cat, 0)

# --- 10. ประมวลผล Employment Status ---
employment_map = {
    'ทำงานเต็มเวลา (30 ชั่วโมงขึ้นไป/สัปดาห์)': 'Employed_Someone_Else_More_30_Hrs',
    'ทำงานนอกเวลา (น้อยกว่า 30 ชั่วโมง/สัปดาห์)': 'Employed_Someone_Else_Less_30_Hrs',
    'เจ้าของกิจการ/ทำงานอิสระ': 'Self_Employed',
    'นักเรียน/นักศึกษา': 'Student',
    'แม่บ้าน/พ่อบ้าน': 'Housewife',
    'ว่างงาน/กำลังหางาน': 'Not_Employed_Looking',
    'เกษียณ': 'Not_Employed_Other'
}
# FIX: แปลงคอลัมน์เป็น string ก่อนใช้ .str เพื่อป้องกัน error กรณีคอลัมน์ว่าง
df_ms_raw['Employment_Cleaned'] = df_ms_raw['Employment_Status'].astype(str).str.strip().map(employment_map).fillna('Unspecified')
employment_counts = df_ms_raw['Employment_Cleaned'].value_counts()
employment_categories = [
    'Employed_Someone_Else_More_30_Hrs', 'Employed_Someone_Else_Less_30_Hrs', 'Self_Employed',
    'Not_Employed_Looking', 'Student', 'Housewife', 'Not_Employed_Other', 'Unspecified'
]
for emp_cat in employment_categories:
    ms_monthly_summary[f'Employment_{emp_cat}_Count'] = employment_counts.get(emp_cat, 0)

# --- 11. ประมวลผล Region ---
df_ms_raw['Region_Mapped'] = df_ms_raw['Province'].astype(str).str.strip().apply(lambda x: province_to_region_map.get(x, 'Unspecified'))
region_counts = df_ms_raw['Region_Mapped'].value_counts()
region_categories_list = ['Bangkok_Metropolitan', 'Central', 'Northeast', 'North', 'East', 'West', 'South', 'Unspecified']
for region_cat in region_categories_list:
    ms_monthly_summary[f'Region_{region_cat}_Count'] = region_counts.get(region_cat, 0)

# --- 12. ประมวลผล Number of Cars at Home ---
cars_at_home_map = {
    '0': '0', '1': '1', '2': '2', '3': '3_Or_More', '4': '3_Or_More',
    '3 or more': '3_Or_More', 'ไม่มี': '0',
    'ไม่ระบุ': 'Unspecified'
}
df_ms_raw['Cars_Cleaned'] = df_ms_raw['Number_of_Cars_at_Home'].astype(str).str.strip().map(cars_at_home_map).fillna('Unspecified')
cars_counts = df_ms_raw['Cars_Cleaned'].value_counts()
cars_categories = ['0', '1', '2', '3_Or_More', 'Unspecified']
for car_cat in cars_categories:
    ms_monthly_summary[f'Cars_At_Home_{car_cat}_Count'] = cars_counts.get(car_cat, 0)

# --- 13. ประมวลผล Car Owner ---
car_owner_map = {
    'ตนเอง': 'Yourself', 'คู่สมรส': 'Spouse', 'บิดา/มารดา': 'Parent', 'บุตร': 'Child',
    'ปู่ย่า/ตายาย': 'Grandparents', 'พี่น้อง': 'Brothers_Sisters',
    'อื่นๆ': 'Others', 'ไม่ทราบ': 'Dont_Know', 'ไม่มี': 'Dont_Know',
    'ไม่ระบุ': 'Dont_Know'
}
df_ms_raw['Car_Owner_Cleaned'] = df_ms_raw['Owner_of_Car'].astype(str).str.strip().map(car_owner_map).fillna('Dont_Know')
car_owner_counts = df_ms_raw['Car_Owner_Cleaned'].value_counts()
car_owner_categories = [
    'Yourself', 'Spouse', 'Parent', 'Child', 'Grandparents',
    'Brothers_Sisters', 'Others', 'Dont_Know'
]
for owner_cat in car_owner_categories:
    ms_monthly_summary[f'Car_Owner_{owner_cat}_Count'] = car_owner_counts.get(owner_cat, 0)

# --- 14. สร้าง DataFrame สุดท้ายสำหรับ MS ---
df_ms_result = pd.DataFrame([ms_monthly_summary])
df_ms_result = df_ms_result.reindex(columns=all_common_data_model_columns).fillna(0)

# แปลงคอลัมน์ Count ทั้งหมดให้เป็น integer
for col in df_ms_result.columns:
    if '_Count' in col:
        df_ms_result[col] = df_ms_result[col].astype(int)

print("\nMS Monthly Summary (Preview):")
print(df_ms_result.transpose())

if not os.path.exists(processed_data_folder):
   os.makedirs(processed_data_folder)
output_file_path = f"{processed_data_folder}temp_ms_data_{current_month.replace('-', '')[:6]}.csv"
df_ms_result.to_csv(output_file_path, index=False, encoding='utf-8')
print(f"\nProcessed MS data saved to {output_file_path}")