# analysis_engine.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def analyze_data(file_path):
    """
    This is the MAIN function that runs all analytics on the uploaded file.
    It returns a dictionary containing all the results and chart paths.
    """
    # Read the data based on file extension
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else: # .xlsx or .xls
        df = pd.read_excel(file_path)
    
    # Assume columns are: StudentID, Name, Math, Science, English, etc.
    # First, let's identify which columns contain marks (are numeric)
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    subject_columns = [col for col in numeric_columns if col not in ['StudentID']] # Adjust based on your CSV
    
    # 1. BASIC STATS: Calculate average, max, min for each subject
    subject_wise_avg = df[subject_columns].mean().to_dict()
    subject_wise_max = df[subject_columns].max().to_dict()
    subject_wise_min = df[subject_columns].min().to_dict()
    
    # 2. OVERALL PERFORMANCE: Add a total column
    df['Total'] = df[subject_columns].sum(axis=1)
    df['Percentage'] = (df['Total'] / (len(subject_columns) * 100)) * 100 # Assuming max marks per subject=100
    
    # 3. GRADE ASSIGNMENT (Enhanced Analytics)
    grades = []
    for percent in df['Percentage']:
        if percent >= 90: grades.append('A')
        elif percent >= 75: grades.append('B')
        elif percent >= 60: grades.append('C')
        elif percent >= 40: grades.append('D')
        else: grades.append('F')
    df['Grade'] = grades
    
    # Count grade distribution
    grade_counts = df['Grade'].value_counts().to_dict()
    
    # 4. TOP & BOTTOM PERFORMERS
    top_3_students = df.nlargest(3, 'Total')[['Name', 'Total', 'Percentage']].to_dict('records')
    bottom_3_students = df.nsmallest(3, 'Total')[['Name', 'Total', 'Percentage']].to_dict('records')
    
    # 5. CREATE VISUALIZATIONS (This is the key part)
    # Create a folder for charts if it doesn't exist
    chart_folder = 'static/img'
    if not os.path.exists(chart_folder):
        os.makedirs(chart_folder)
    
    # Chart 1: Subject-wise Average Bar Chart
    plt.figure(figsize=(10, 6))
    plt.bar(subject_wise_avg.keys(), subject_wise_avg.values(), color='skyblue')
    plt.title('Subject-Wise Average Marks')
    plt.xlabel('Subjects')
    plt.ylabel('Average Marks')
    plt.ylim(0, 100)
    plt.tight_layout()
    chart1_path = os.path.join(chart_folder, 'subject_avg.png')
    plt.savefig(chart1_path)
    plt.close()
    
    # Chart 2: Grade Distribution Pie Chart
    plt.figure(figsize=(8, 8))
    plt.pie(grade_counts.values(), labels=grade_counts.keys(), autopct='%1.1f%%', startangle=140)
    plt.title('Grade Distribution of Class')
    chart2_path = os.path.join(chart_folder, 'grade_pie.png')
    plt.savefig(chart2_path)
    plt.close()

    # 6. Compile all results into a dictionary to return
    results = {
        'subject_wise_avg': subject_wise_avg,
        'subject_wise_max': subject_wise_max,
        'subject_wise_min': subject_wise_min,
        'top_students': top_3_students,
        'bottom_students': bottom_3_students,
        'grade_distribution': grade_counts,
        'chart_subject_avg': chart1_path,
        'chart_grade_pie': chart2_path,
        'data_frame': df.to_html(classes='table table-striped') # Optional: to display the whole table on results page
    }
    
    return results