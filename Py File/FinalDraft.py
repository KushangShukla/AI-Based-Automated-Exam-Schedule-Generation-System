#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pymysql
import pandas as pd
from datetime import datetime, timedelta
from IPython.display import display
import matplotlib.pyplot as plt
import seaborn as sns

# MySQL connection details
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Add your MySQL password if set
    'database': 'exam_scheduler'
}

# Create connection
conn = pymysql.connect(**db_config)
print("✅ Connected to MySQL database!")

# Load tables directly from MySQL
classrooms = pd.read_sql('SELECT * FROM classrooms', conn)
courses = pd.read_sql('SELECT * FROM courses', conn)
students = pd.read_sql('SELECT * FROM students', conn)
preferences = pd.read_sql('SELECT * FROM preferences', conn)

# Close connection after loading data
conn.close()

# Confirm data loaded correctly
print("\nClassrooms Table:")
display(classrooms.head())

print("\nCourses Table:")
display(courses.head())

print("\nStudents Table:")
display(students.head())

print("\nPreferences Table:")
display(preferences.head())

# 1. Clean classrooms table
classrooms = classrooms[pd.to_numeric(classrooms['capacity'], errors='coerce').notna()]
classrooms['capacity'] = classrooms['capacity'].astype(int)
classrooms['classroom_name'] = classrooms['classroom_name'].str.strip()

# 2. Clean courses table
courses = courses[pd.to_numeric(courses['students_registered'], errors='coerce').notna()]
courses['students_registered'] = courses['students_registered'].astype(int)
courses['course_name'] = courses['course_name'].str.strip()

# 3. Clean students table
students = students[pd.to_numeric(students['course_id'], errors='coerce').notna()]
students['student_id'] = pd.to_numeric(students['student_id'], errors='coerce').fillna(0).astype(int)
students['course_id'] = students['course_id'].astype(int)
students['name'] = students['name'].str.strip()
students['preference'] = students['preference'].str.strip()

# 4. Clean preferences table
preferences = preferences[pd.to_numeric(preferences['student_id'], errors='coerce').notna()]
preferences['student_id'] = preferences['student_id'].astype(int)
preferences['preferred_time_slot'] = preferences['preferred_time_slot'].str.strip()

# ✅ Confirm Cleaned Data
print("\nCleaned Data:")
display(classrooms.head())
display(courses.head())
display(students.head())
display(preferences.head())

def schedule_exams(courses, students, classrooms, preferences):
    schedule = []
    time_slots = ["09:00-11:00", "12:00-14:00", "15:00-17:00"]
    day_count = 1
    start_date = datetime.today()

    for index, course in courses.iterrows():
        scheduled = False
        
        while not scheduled:
            for time_slot in time_slots:
                # Get available classroom
                available_classrooms = classrooms[classrooms['capacity'] >= course['students_registered']]
                
                if not available_classrooms.empty:
                    classroom = available_classrooms.iloc[0]
                    
                    # Create schedule entry
                    schedule.append({
                        'day': f'Day {day_count}',
                        'date': start_date.strftime('%Y-%m-%d'),
                        'time_slot': time_slot,
                        'course_id': course['course_id'],
                        'course_name': course['course_name'],
                        'classroom_id': classroom['classroom_id'],
                        'classroom_name': classroom['classroom_name'],
                        'students_registered': course['students_registered']
                    })
                    
                    # Remove course and classroom after scheduling
                    classrooms = classrooms.drop(classroom.name)
                    scheduled = True
                    break

            # If no classroom is available, move to next day
            if not scheduled:
                start_date += timedelta(days=1)
                day_count += 1
                classrooms = classrooms = pd.read_sql('SELECT * FROM classrooms', conn)  # Reset available classrooms

    return pd.DataFrame(schedule)

# Generate schedule
exam_schedule = schedule_exams(courses, students, classrooms, preferences)

# Preview generated schedule
display(exam_schedule)

def save_schedule(schedule):
    conn = pymysql.connect(**db_config)
    with conn.cursor() as cursor:
        # Drop table if exists
        cursor.execute("DROP TABLE IF EXISTS exam_schedule")
        cursor.execute("""
            CREATE TABLE exam_schedule (
                day VARCHAR(20),
                date DATE,
                time_slot VARCHAR(20),
                course_id INT,
                course_name VARCHAR(100),
                classroom_id INT,
                classroom_name VARCHAR(100),
                students_registered INT
            )
        """)

        for _, row in schedule.iterrows():
            sql = """
                INSERT INTO exam_schedule (
                    day, date, time_slot, course_id, course_name, classroom_id, classroom_name, students_registered
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, tuple(row))

        conn.commit()
    conn.close()

save_schedule(exam_schedule)
print("✅ Exam schedule saved to MySQL!")

students['course_id'] = students['course_id'].astype(str).str.strip()
exam_schedule['course_id'] = exam_schedule['course_id'].astype(str).str.strip()

# Try merge first
try:
    student_schedule = pd.merge(
        students,
        exam_schedule,
        left_on='course_id',
        right_on='course_id'
    )
    print("✅ Merge successful!")
except Exception as e:
    print(f"❌ Merge failed: {e}")
    
    # Fallback to concat if merge fails
    print("👉 Trying concat instead...")
    student_schedule = pd.concat([students, exam_schedule], axis=1)

# Save report to Excel
student_schedule.to_excel('student_schedule.xlsx', index=False)
print("✅ Student exam schedule report saved as 'student_schedule.xlsx'")

import os

output_dir = "Exam_Reports"
os.makedirs(output_dir, exist_ok=True)

exam_schedule.to_excel(f"{output_dir}/exam_schedule.xlsx", index=False)
student_schedule.to_excel(f"{output_dir}/student_schedule.xlsx", index=False)

print("✅ Reports saved in 'Exam_Reports' folder!")

try:
    exam_schedule = schedule_exams(courses, students, classrooms, preferences)
except Exception as e:
    print(f"❌ Error during scheduling: {e}")


# In[ ]:


import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
import pandas as pd

# MySQL connection details
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'exam_scheduler'
}

# Function to load schedule data from MySQL
def load_schedule():
    try:
        conn = pymysql.connect(**db_config)
        query = "SELECT * FROM exam_schedule"
        schedule = pd.read_sql(query, conn)
        conn.close()
        return schedule
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load schedule: {e}")
        return None

# Function to display schedule in the table
def display_schedule():
    # Clear existing data
    for row in tree.get_children():
        tree.delete(row)

    # Load data
    schedule = load_schedule()
    if schedule is not None:
        for _, row in schedule.iterrows():
            tree.insert("", "end", values=(
                row['day'], row['date'], row['time_slot'],
                row['course_name'], row['classroom_name'], row['students_registered']
            ))

# Function to generate the schedule (calls the AI-based scheduling function)
def refresh_data():
    display_schedule()

def generate_schedule():
    try:
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            cursor.execute("CALL generate_exam_schedule()")
            conn.commit()
        conn.close()
        display_schedule()
        messagebox.showinfo("Success", "Exam schedule generated successfully!")
    except pymysql.MySQLError as e:
        if e.args[0] == 1305:  # Error code for missing procedure
            messagebox.showwarning("Missing Procedure", "Stored procedure not found. Using Python-based scheduling.")
            generate_schedule_fallback()
        else:
            messagebox.showerror("Error", f"Failed to generate schedule: {e}")

def generate_schedule_fallback():
    try:
        # Load data from the database
        conn = pymysql.connect(**db_config)
        courses = pd.read_sql("SELECT * FROM courses", conn)
        students = pd.read_sql("SELECT * FROM students", conn)
        classrooms = pd.read_sql("SELECT * FROM classrooms", conn)
        preferences = pd.read_sql("SELECT * FROM preferences", conn)
        conn.close()

        schedule = []
        available_classrooms = classrooms.to_dict(orient='records')
        time_slots = ["09:00-11:00", "11:00-01:00", "02:00-04:00"]
        day_counter = 1
        start_date = pd.Timestamp('2025-03-12')

        for _, course in courses.iterrows():
            assigned = False
            for day_offset in range(7):
                exam_date = (start_date + pd.Timedelta(days=day_offset)).strftime('%Y-%m-%d')

                for time_slot in time_slots:
                    for room in available_classrooms:
                        if room['capacity'] >= course['students_registered']:
                            # Add to schedule
                            schedule.append((
                                f"Day {day_counter}",
                                exam_date,
                                time_slot,
                                course['course_name'],
                                room['classroom_name'],
                                course['students_registered']
                            ))
                            assigned = True
                            break

                    if assigned:
                        break

                if assigned:
                    break

            if assigned:
                day_counter += 1

        # Insert schedule into MySQL table
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM exam_schedule")  # Clear existing schedule
            for item in schedule:
                sql = """
                    INSERT INTO exam_schedule (day, date, time_slot, course_name, classroom_name, students_registered)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, item)
            conn.commit()
        conn.close()

        # Update the UI Table
        generated_table.delete(*generated_table.get_children())

        for data in schedule:
            generated_table.insert("", "end", values=data)

        messagebox.showinfo("Success", "Python-based schedule generated successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate fallback schedule: {e}")

# Function to adjust schedule manually
def adjust_schedule():
    course = course_dropdown.get()
    date = date_entry.get()
    time = time_dropdown.get()
    classroom = classroom_dropdown.get()

    if not (course and date and time and classroom):
        messagebox.showwarning("Invalid Input", "Please fill all fields.")
        return
    
    try:
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            sql = """
                UPDATE exam_schedule 
                SET date = %s, time_slot = %s, classroom_name = %s
                WHERE course_name = %s
            """
            cursor.execute(sql, (date, time, classroom, course))
            conn.commit()
        conn.close()
        display_schedule()
        messagebox.showinfo("Success", f"Schedule updated for {course}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to adjust schedule: {e}")

# Function to check for conflicts
def check_conflicts():
    try:
        conn = pymysql.connect(**db_config)
        query = """
            SELECT course_name, date, time_slot, COUNT(*) as conflict_count
            FROM exam_schedule
            GROUP BY date, time_slot, classroom_name
            HAVING COUNT(*) > 1
        """
        conflicts = pd.read_sql(query, conn)
        conn.close()

        if conflicts.empty:
            status_label.config(text="✅ No conflicts detected", fg="green")
        else:
            status_label.config(text="❌ Conflicts detected!", fg="red")
            messagebox.showwarning("Conflicts Detected", conflicts.to_string(index=False))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to check conflicts: {e}")

# Function to load course names for dropdown
def load_courses():
    try:
        conn = pymysql.connect(**db_config)
        query = "SELECT DISTINCT course_name FROM exam_schedule"
        courses = pd.read_sql(query, conn)
        conn.close()
        return courses['course_name'].tolist()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load courses: {e}")
        return []

# Function to load classroom names for dropdown
def load_classrooms():
    try:
        conn = pymysql.connect(**db_config)
        query = "SELECT DISTINCT classroom_name FROM classrooms"
        classrooms = pd.read_sql(query, conn)
        conn.close()
        return classrooms['classroom_name'].tolist()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load classrooms: {e}")
        return []

# GUI Setup
root = tk.Tk()
root.title("AI-Based Exam Scheduling System")
root.geometry("1000x600")

# Title Label
title = tk.Label(root, text="AI-Based Exam Scheduling System", font=("Arial", 20))
title.pack(pady=10)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack()

import threading
import os
import sys

def close_app():
    # Close all active MySQL connections
    try:
        conn = pymysql.connect(**db_config)
        conn.close()
    except Exception:
        pass  # Ignore if no active connection
    
    # Stop any active threads (important for background data loading)
    for thread in threading.enumerate():
        if thread != threading.main_thread():
            try:
                thread.join(0.1)  # Gracefully stop background threads
            except:
                pass

    # Destroy all widgets in Tkinter to clear resources
    for widget in root.winfo_children():
        widget.destroy()

    # Properly quit Tkinter and force exit if needed
    try:
        root.quit()    # Graceful exit
        root.destroy() # Force widget closure
    except:
        pass

    # Emergency exit (if all else fails)
    os._exit(0)  # Guaranteed kill process (last resort)

generate_btn = tk.Button(btn_frame, text="Generate Schedule", command=generate_schedule, width=20, bg="green", fg="white")
generate_btn.grid(row=0, column=0, padx=10)

#generate_btn = tk.Button(btn_frame, text="Generate Schedule", command=generate_schedule, width=20, bg="green", fg="white")
#generate_btn.grid(row=0, column=0, padx=10)

view_btn = tk.Button(btn_frame, text="View Schedule", command=display_schedule, width=20, bg="blue", fg="white")
view_btn.grid(row=0, column=1, padx=10)

conflict_btn = tk.Button(btn_frame, text="Check Conflicts", command=check_conflicts, width=20, bg="orange", fg="white")
conflict_btn.grid(row=0, column=2, padx=10)

def open_data_entry_window():
    data_window = tk.Toplevel(root)
    data_window.title("Data Entry Window")
    data_window.geometry("1200x700")

    # Title
    title = tk.Label(data_window, text="AI-Based Exam Scheduling System", font=("Arial", 20))
    title.pack(pady=10)

    # Tabs for Data Entry
    tabs = ttk.Notebook(data_window)
    tabs.pack(expand=1, fill="both")

    # Tab 1: Classrooms
    classroom_tab = ttk.Frame(tabs)
    tabs.add(classroom_tab, text="Classrooms")

    tk.Label(classroom_tab, text="Classroom ID:").grid(row=0, column=0, padx=5, pady=5)
    classroom_id_entry = tk.Entry(classroom_tab)
    classroom_id_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(classroom_tab, text="Classroom Name:").grid(row=1, column=0, padx=5, pady=5)
    classroom_name_entry = tk.Entry(classroom_tab)
    classroom_name_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(classroom_tab, text="Capacity:").grid(row=2, column=0, padx=5, pady=5)
    classroom_capacity_entry = tk.Entry(classroom_tab)
    classroom_capacity_entry.grid(row=2, column=1, padx=5, pady=5)

    def insert_classroom():
        id = classroom_id_entry.get()
        name = classroom_name_entry.get()
        capacity = classroom_capacity_entry.get()

        if not (id and name and capacity):
            messagebox.showwarning("Invalid Input", "Please fill all fields.")
            return
        
        try:
            capacity = int(capacity)
            conn = pymysql.connect(**db_config)
            with conn.cursor() as cursor:
                sql = "INSERT INTO classrooms (classroom_id, classroom_name, capacity) VALUES (%s, %s, %s)"
                cursor.execute(sql, (id, name, capacity))
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Classroom added successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add classroom: {e}")

    tk.Button(classroom_tab, text="Add Classroom", command=insert_classroom, bg="green", fg="white").grid(row=3, column=0, columnspan=2, pady=5)

    # Tab 2: Courses
    course_tab = ttk.Frame(tabs)
    tabs.add(course_tab, text="Courses")

    tk.Label(course_tab, text="Course ID:").grid(row=0, column=0, padx=5, pady=5)
    course_id_entry = tk.Entry(course_tab)
    course_id_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(course_tab, text="Course Name:").grid(row=1, column=0, padx=5, pady=5)
    course_name_entry = tk.Entry(course_tab)
    course_name_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(course_tab, text="Students Registered:").grid(row=2, column=0, padx=5, pady=5)
    course_students_entry = tk.Entry(course_tab)
    course_students_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(course_tab, text="Duration:").grid(row=3, column=0, padx=5, pady=5)
    course_duration_entry = tk.Entry(course_tab)
    course_duration_entry.grid(row=3, column=1, padx=5, pady=5)

    def insert_course():
        id = course_id_entry.get()
        name = course_name_entry.get()
        students_registered = course_students_entry.get()
        duration = course_duration_entry.get()

        if not (id and name and students_registered and duration):
            messagebox.showwarning("Invalid Input", "Please fill all fields.")
            return
        
        try:
            students_registered = int(students_registered)
            duration = int(duration)
            conn = pymysql.connect(**db_config)
            with conn.cursor() as cursor:
                sql = "INSERT INTO courses (course_id, course_name, students_registered, duration) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (id, name, students_registered, duration))
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Course added successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add course: {e}")

    tk.Button(course_tab, text="Add Course", command=insert_course, bg="green", fg="white").grid(row=4, column=0, columnspan=2, pady=5)

    # Tab 3: Students
    student_tab = ttk.Frame(tabs)
    tabs.add(student_tab, text="Students")

    tk.Label(student_tab, text="Student ID:").grid(row=0, column=0, padx=5, pady=5)
    student_id_entry = tk.Entry(student_tab)
    student_id_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(student_tab, text="Name:").grid(row=1, column=0, padx=5, pady=5)
    student_name_entry = tk.Entry(student_tab)
    student_name_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(student_tab, text="Course ID:").grid(row=2, column=0, padx=5, pady=5)
    student_course_id_entry = tk.Entry(student_tab)
    student_course_id_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(student_tab, text="Preference:").grid(row=3, column=0, padx=5, pady=5)
    student_preference_entry = tk.Entry(student_tab)
    student_preference_entry.grid(row=3, column=1, padx=5, pady=5)

    def insert_student():
        id = student_id_entry.get()
        name = student_name_entry.get()
        course_id = student_course_id_entry.get()
        preference = student_preference_entry.get()

        if not (id and name and course_id and preference):
            messagebox.showwarning("Invalid Input", "Please fill all fields.")
            return
        
        try:
            conn = pymysql.connect(**db_config)
            with conn.cursor() as cursor:
                sql = "INSERT INTO students (student_id, name, course_id, preference) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (id, name, course_id, preference))
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Student added successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add student: {e}")

    tk.Button(student_tab, text="Add Student", command=insert_student, bg="green", fg="white").grid(row=4, column=0, columnspan=2, pady=5)
    # Tab 4: Preferences
    preferences_tab = ttk.Frame(tabs)
    tabs.add(preferences_tab, text="Preferences")

    tk.Label(preferences_tab, text="Student ID:").grid(row=0, column=0, padx=5, pady=5)
    preference_student_id_entry = tk.Entry(preferences_tab)
    preference_student_id_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(preferences_tab, text="Preferred Time Slot:").grid(row=1, column=0, padx=5, pady=5)
    preference_time_slot_entry = tk.Entry(preferences_tab)
    preference_time_slot_entry.grid(row=1, column=1, padx=5, pady=5)

    def insert_preference():
        student_id = preference_student_id_entry.get()
        time_slot = preference_time_slot_entry.get()

        if not (student_id and time_slot):
            messagebox.showwarning("Invalid Input", "Please fill all fields.")
            return
    
        try:
            conn = pymysql.connect(**db_config)
            with conn.cursor() as cursor:
                sql = "INSERT INTO preferences (student_id, preferred_time_slot) VALUES (%s, %s)"
                cursor.execute(sql, (student_id, time_slot))
                conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Preference added successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add preference: {e}")

    # Add Button for Preferences
    tk.Button(preferences_tab, text="Add Preference", command=insert_preference, bg="green", fg="white").grid(row=2, column=0, columnspan=2, pady=5)

add_btn = tk.Button(btn_frame, text="Add", command=open_data_entry_window, width=20, bg="purple", fg="white")
add_btn.grid(row=0, column=3, padx=10)

# Adjust Exit button position to avoid overlap
#exit_btn.grid(row=0, column=4, padx=10)


""" import subprocess
    subprocess.Popen(["python", "ClassroomsandCourses.py"])

# Add Button to open Data Entry Window
add_btn = tk.Button(btn_frame, text="Add", command=open_data_entry_window, width=20, bg="purple", fg="white")
add_btn.grid(row=0, column=3, padx=10)"""

exit_btn = tk.Button(btn_frame, text="Exit", command=close_app, width=20, bg="red", fg="white")
# Adjust Exit button position to avoid overlap
exit_btn.grid(row=0, column=4, padx=10)
#exit_btn.grid(row=0, column=3, padx=10)

root.bind('<Escape>', lambda e: close_app())

# Schedule Table (Treeview)
tree_frame = tk.Frame(root)
tree_frame.pack(pady=10)

columns = ("Day", "Date", "Time", "Course", "Classroom", "Students")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)

tree.pack()

# Manual Adjustment Panel
adjust_frame = tk.Frame(root)
adjust_frame.pack(pady=10)

tk.Label(adjust_frame, text="Course:").grid(row=0, column=0, padx=5)
course_dropdown = ttk.Combobox(adjust_frame, values=load_courses())
course_dropdown.grid(row=0, column=1, padx=5)

tk.Label(adjust_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=2, padx=5)
date_entry = tk.Entry(adjust_frame)
date_entry.grid(row=0, column=3, padx=5)

tk.Label(adjust_frame, text="Time Slot:").grid(row=0, column=4, padx=5)
time_dropdown = ttk.Combobox(adjust_frame, values=["09:00-11:00", "12:00-14:00", "15:00-17:00"])
time_dropdown.grid(row=0, column=5, padx=5)

tk.Label(adjust_frame, text="Classroom:").grid(row=0, column=6, padx=5)
classroom_dropdown = ttk.Combobox(adjust_frame, values=load_classrooms())
classroom_dropdown.grid(row=0, column=7, padx=5)

adjust_btn = tk.Button(adjust_frame, text="Update", command=adjust_schedule, bg="purple", fg="white")
adjust_btn.grid(row=0, column=8, padx=5)

# Conflict Status Label
status_label = tk.Label(root, text="✅ No conflicts detected", fg="green", font=("Arial", 12))
status_label.pack(pady=10)

# Start GUI Loop
root.mainloop()


# In[ ]:




