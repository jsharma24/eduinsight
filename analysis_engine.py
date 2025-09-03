def analyze_data(file_path):
    """
    ROBUST ANALYSIS FUNCTION that handles different file formats
    """
    try:
        results = analyze_data(save_path)
            
        # === DEBUG LINES ===
        print("=== DEBUG: ANALYSIS RESULTS ===")     
        print("All keys in results:", list(results.keys()))
        if 'status' in results:
            print("Status:", results['status'])
        if 'message' in results:
            print("Message:", results['message'])
            print("===============================")
            
         # Check if analysis was successful
        if results.get('status') == 'error':
            return f"Analysis Error: {results.get('message', 'Unknown error')}"
            
        # Check if we have the expected keys
        if 'subjects_found' not in results:
            return f"Unexpected results format. Analysis completed but returned: {list(results.keys())}"
            
        # If we get here, the analysis was successful
        result_html = "<h1>Analysis Complete! 🎉</h1>"
        result_html += "<h2>EduInsight Analysis Report</h2>"
        result_html += f"<p>{results.get('message', 'Analysis successful!')}</p>"
        result_html += f"<h3>Subjects Found:</h3>"
        result_html += f"<p>{', '.join(results.get('subjects_found', []))}</p>"
        result_html += f"<h3>Total Students:</h3>"
        result_html += f"<p>{results.get('total_students', 0)}</p>"
        result_html += f"<h3>Class Average:</h3>"
        result_html += f"<p>{results.get('class_average', 0):.2f} marks</p>"
            
        return result_html
            
    except Exception as e:
        return f"Error during analysis: {str(e)}. Please make sure your file has the correct format."