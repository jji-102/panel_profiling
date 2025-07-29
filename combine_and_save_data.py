import pandas as pd
import os


current_month = '2025-06-01'
output_summary_file = 'monthly_profiling_summary.csv'
processed_data_folder = './processed_data/'

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

ds_processed_file = f"{processed_data_folder}temp_ds_data_{current_month.replace('-', '')[:6]}.csv"
ms_processed_file = f"{processed_data_folder}temp_ms_data_{current_month.replace('-', '')[:6]}.csv"

try:
    df_ds_result = pd.read_csv(ds_processed_file)
    df_ms_result = pd.read_csv(ms_processed_file)
except FileNotFoundError:
    print("Error: Processed temporary files not found.")
    print("Please ensure you have run process_ds_data.py and process_ms_data.py successfully for this month.")
    exit()
except Exception as e:
    print(f"Error reading processed data: {e}")
    exit()

df_ds_final = df_ds_result.reindex(columns=all_common_data_model_columns).fillna(0)
df_ms_final = df_ms_result.reindex(columns=all_common_data_model_columns).fillna(0)

df_current_month_combined = pd.concat([df_ds_final, df_ms_final], ignore_index=True)

print("\nCombined Data for Current Month:")
print(df_current_month_combined)

try:

    df_existing_summary = pd.read_csv(output_summary_file)

    df_existing_summary = df_existing_summary[df_existing_summary['Collected_Month'] != current_month]

    df_updated_summary = pd.concat([df_existing_summary, df_current_month_combined], ignore_index=True)

except FileNotFoundError:
    print(f"'{output_summary_file}' not found. Creating a new summary file.")
    df_updated_summary = df_current_month_combined
except Exception as e:
    print(f"Error processing existing summary file: {e}")
    exit()
2
df_updated_summary = df_updated_summary.reindex(columns=all_common_data_model_columns).fillna(0)
df_updated_summary.to_csv(output_summary_file, index=False, encoding='utf-8')

print(f"\nSuccessfully updated '{output_summary_file}' with data for {current_month}.")
print(f"Total rows in {output_summary_file}: {len(df_updated_summary)}")