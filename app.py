from flask import Flask, render_template, request
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part in the request. Please go back and select a file."
    
    file = request.files['file']
    
    if file.filename == '':
        return "No file selected. Please go back and choose a file."
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Read the file
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
            
            print(f"✅ File read successfully!")
            print(f"📊 Columns: {list(df.columns)}")
            print(f"📈 First 3 rows:\n{df.head(3)}")
            
            # === ADVANCED COLUMN DETECTION ===
            subject_columns = []
            name_column = None
            rollno_column = None
            
            # Strategy: Identify columns by content and naming
            for col in df.columns:
                col_lower = col.lower()
                
                # Check for roll number columns
                if any(word in col_lower for word in ['roll', 'id', 'number', 'reg']):
                    rollno_column = col
                    print(f"📋 Roll Number column: {col}")
                
                # Check for name columns
                elif any(word in col_lower for word in ['name', 'student', 'candidate']):
                    name_column = col
                    print(f"📋 Name column: {col}")
                
                # Check for subject columns
                else:
                    # Try to convert to numeric
                    original_data = df[col].copy()
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    if df[col].notna().any():
                        subject_columns.append(col)
                        print(f"📚 Subject column: {col}")
                    else:
                        df[col] = original_data
                        # If not numeric and not identified, assume it's a name column
                        if name_column is None:
                            name_column = col
                            print(f"📋 Assuming name column: {col}")
            
            # Fallback: If no subjects found, use common sense
            if not subject_columns:
                name_column = df.columns[0]
                subject_columns = list(df.columns[1:])
                for col in subject_columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                print(f"ℹ️ Using fallback: Name='{name_column}', Subjects={subject_columns}")
            
            if not subject_columns:
                return "Error: No subject columns with marks found. Please check your file format."
            
            # === ADVANCED ANALYSIS ===
            # Calculate totals and percentages
            df['Total'] = df[subject_columns].sum(axis=1)
            df['Percentage'] = (df['Total'] / (len(subject_columns) * 100)) * 100
            
            # Assign grades
            def assign_grade(percentage):
                if percentage >= 90: return 'A'
                elif percentage >= 75: return 'B'
                elif percentage >= 60: return 'C'
                elif percentage >= 40: return 'D'
                else: return 'F'
            
            df['Grade'] = df['Percentage'].apply(assign_grade)
            
            # Calculate subject statistics
            subject_stats = {}
            for subject in subject_columns:
                subject_stats[subject] = {
                    'average': df[subject].mean(),
                    'highest': df[subject].max(),
                    'lowest': df[subject].min(),
                    'pass_rate': (df[subject] >= 40).mean() * 100
                }
            
            # Get top and bottom performers
            top_3 = df.nlargest(3, 'Total')[[name_column, 'Total', 'Percentage', 'Grade']]
            
            # Grade distribution
            grade_counts = df['Grade'].value_counts().to_dict()
            
            # === DATA VISUALIZATION ===
            # Create charts folder if it doesn't exist
            chart_folder = 'static/charts'
            if not os.path.exists(chart_folder):
                os.makedirs(chart_folder)
            
            # Chart 1: Subject-wise averages
            plt.figure(figsize=(10, 6))
            subjects = list(subject_stats.keys())
            averages = [subject_stats[s]['average'] for s in subjects]
            plt.bar(subjects, averages, color=['#ff6b6b', '#4ecdc4', '#45b7d1'])
            plt.title('Subject-wise Average Marks')
            plt.xlabel('Subjects')
            plt.ylabel('Average Marks (%)')
            plt.ylim(0, 100)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            chart1_path = os.path.join(chart_folder, 'subject_avg.png')
            plt.savefig(chart1_path)
            plt.close()
            
            # Chart 2: Grade distribution
            plt.figure(figsize=(8, 8))
            colors = ['#4caf50', '#8bc34a', '#ffc107', '#ff9800', '#f44336']
            plt.pie(grade_counts.values(), labels=grade_counts.keys(), autopct='%1.1f%%', 
                   colors=colors, startangle=90)
            plt.title('Grade Distribution')
            chart2_path = os.path.join(chart_folder, 'grade_pie.png')
            plt.savefig(chart2_path)
            plt.close()
            
            # === GENERATE BEAUTIFUL REPORT ===
            result_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>EduInsight Report</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                <style>
                    body {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        padding: 20px;
                    }}
                    .report-container {{
                        background: white;
                        border-radius: 15px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                        overflow: hidden;
                        margin: 20px auto;
                        max-width: 1200px;
                    }}
                    .report-header {{
                        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }}
                    .card {{
                        border: none;
                        border-radius: 10px;
                        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                        margin-bottom: 20px;
                    }}
                    .card-header {{
                        border-radius: 10px 10px 0 0 !important;
                        font-weight: bold;
                    }}
                    .subject-card {{
                        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
                        color: white;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 10px 0;
                    }}
                    .table-responsive {{
                        max-height: 500px;
                        overflow-y: auto;
                    }}
                    .badge-custom {{
                        font-size: 0.9em;
                        padding: 8px 15px;
                        border-radius: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="container-fluid">
                    <div class="report-container">
                        <div class="report-header">
                            <h1><i class="fas fa-graduation-cap me-2"></i>EduInsight Analytics Report</h1>
                            <p class="lead">Comprehensive Performance Analysis</p>
                            <div class="badge bg-light text-dark p-2">
                                <i class="fas fa-file-excel me-1"></i> {filename} | 
                                <i class="fas fa-users me-1 ms-2"></i> {len(df)} Students
                            </div>
                        </div>
                        
                        <div class="container mt-4">
                            <!-- Summary Cards -->
                            <div class="row">
                                <div class="col-md-4">
                                    <div class="card text-white bg-success text-center p-3">
                                        <i class="fas fa-chart-line fa-3x mb-2"></i>
                                        <h4>Class Average</h4>
                                        <h2>{df['Percentage'].mean():.1f}%</h2>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card text-white bg-info text-center p-3">
                                        <i class="fas fa-user-graduate fa-3x mb-2"></i>
                                        <h4>Total Students</h4>
                                        <h2>{len(df)}</h2>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card text-white bg-warning text-center p-3">
                                        <i class="fas fa-star fa-3x mb-2"></i>
                                        <h4>Top Score</h4>
                                        <h2>{df['Total'].max()}</h2>
                                    </div>
                                </div>
                            </div>

                            <!-- Subject-wise Performance -->
                            <div class="card mt-4">
                                <div class="card-header bg-primary text-white">
                                    <h4><i class="fas fa-book me-2"></i>Subject-wise Performance</h4>
                                </div>
                                <div class="card-body">
                                    <div class="row">
            """

            for subject, stats in subject_stats.items():
                result_html += f"""
                                        <div class="col-md-4">
                                            <div class="subject-card">
                                                <h5><i class="fas fa-bookmark me-2"></i>{subject}</h5>
                                                <div>Average: <strong>{stats['average']:.1f}%</strong></div>
                                                <div>Highest: <strong>{stats['highest']}</strong></div>
                                                <div>Lowest: <strong>{stats['lowest']}</strong></div>
                                                <div>Pass Rate: <strong>{stats['pass_rate']:.1f}%</strong></div>
                                            </div>
                                        </div>
                """
            
            result_html += f"""
                                    </div>
                                </div>
                            </div>

                            <!-- Top Performers -->
                            <div class="card mt-4">
                                <div class="card-header bg-success text-white">
                                    <h4><i class="fas fa-trophy me-2"></i>Top 3 Performers</h4>
                                </div>
                                <div class="card-body">
                                    <div class="row">
            """
            
            for i, (_, row) in enumerate(top_3.iterrows(), 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                student_id = f"({row[rollno_column]}) " if rollno_column and rollno_column in row else ""
                result_html += f"""
                                        <div class="col-md-4">
                                            <div class="text-center p-3 border rounded">
                                                <h3>{medal}</h3>
                                                <h5>{student_id}{row[name_column]}</h5>
                                                <div class="text-success">
                                                    <strong>{row['Total']} marks</strong><br>
                                                    ({row['Percentage']:.1f}%)<br>
                                                    <span class="badge bg-primary badge-custom">Grade: {row['Grade']}</span>
                                                </div>
                                            </div>
                                        </div>
                """
            
            result_html += f"""
                                    </div>
                                </div>
                            </div>

                            <!-- Visual Analytics -->
                            <div class="card mt-4">
                                <div class="card-header bg-info text-white">
                                    <h4><i class="fas fa-chart-pie me-2"></i>Visual Analytics</h4>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-6 text-center">
                                            <h5><i class="fas fa-chart-bar me-2"></i>Subject Averages</h5>
                                            <img src='/static/charts/subject_avg.png' class='img-fluid rounded' style='max-height: 300px;'>
                                        </div>
                                        <div class="col-md-6 text-center">
                                            <h5><i class="fas fa-chart-pie me-2"></i>Grade Distribution</h5>
                                            <img src='/static/charts/grade_pie.png' class='img-fluid rounded' style='max-height: 300px;'>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Complete Student Data -->
                            <div class="card mt-4">
                                <div class="card-header bg-secondary text-white">
                                    <h4><i class="fas fa-table me-2"></i>Complete Student Data</h4>
                                </div>
                                <div class="card-body">
                                    <div class="table-responsive">
                                        {df.to_html(classes='table table-striped table-hover table-bordered', index=False)}
                                    </div>
                                </div>
                            </div>
                            
                            <div class="text-center mt-4 mb-4">
                                <div class="badge bg-light text-dark p-3">
                                    <i class="fas fa-code me-1"></i> Generated by EduInsight | 
                                    <i class="fas fa-clock me-1 ms-2"></i> Report Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            </body>
            </html>
            """
            
            return result_html
            
        except Exception as e:
            return f"<div class='alert alert-danger'><h4>Error during analysis:</h4><p>{str(e)}</p><p>Please ensure your Excel file has the correct format with student names and marks.</p></div>"
    
    return "Invalid file type. Please upload CSV or Excel file."

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    if not os.path.exists('static/charts'):
        os.makedirs('static/charts')
    app.run(debug=True)