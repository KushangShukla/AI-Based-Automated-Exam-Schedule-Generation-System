<!-- # AI-Based-Automated-Exam-Schedule-Generation-System
AI-Based Exam Scheduler using Python and MySQL. Automates exam scheduling, minimizes conflicts, and handles large datasets. Includes a data entry window for courses, students, and classrooms.-->

# 🏫 AI-Based Automated Exam Scheduling System

This project is an **AI-based exam scheduling system** designed to automate the scheduling of exams based on course requirements, student preferences, and classroom availability. It features a Python-based backend integrated with MySQL and a user-friendly Tkinter-based GUI for data entry and schedule viewing.

---

## 🚀 Features
- **AI-Based Scheduling:** Automatically generates an optimized exam schedule considering student preferences and classroom availability.  
- **Conflict Resolution:** Detects and resolves scheduling conflicts.  
- **Manual Adjustment:** Modify schedules manually via the GUI.  
- **Data Entry:** Add courses, classrooms, students, and preferences directly through the interface.  
- **Multi-Window GUI:** Separate windows for scheduling and data entry.  
- **Excel Export:** Export the schedule and student report as Excel files.  

---

<!--## 📁 Project Structure
```
├── main.py                   # Main scheduling GUI and logic
├── data_entry.py             # Data entry GUI (linked to main.py)
├── requirements.txt          # Required dependencies
├── stored_procedure.sql      # SQL for creating stored procedure
├── Exam_Reports/             # Folder to store exported reports
└── README.md                 # Project documentation
```-->

---

## 💻 Technologies Used
- **Python**  
- **MySQL**  
- **Pandas**  
- **Tkinter**  
- **Seaborn**  
- **Matplotlib**  

---

## ⚙️ Prerequisites
Ensure the following are installed:
1. Python (>= 3.8)  
2. MySQL Server  
3. pip (Python package manager)  

---

## 🛠️ Setup Instructions
### 1. Clone the Repository
```bash
git clone https://github.com/YourUsername/AI-Based-Exam-Scheduler.git
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create MySQL Database and Tables
- Open MySQL and create the database and tables using the provided SQL scripts.

### 4. Add Stored Procedure
- Create the stored procedure using the `stored_procedure.sql` file.

---

## 🖥️ How to Run
### **1. Start MySQL Server**
Ensure the MySQL server is running.

### **2. Run the Main GUI**
```bash
python main.py
```

### **3. Generate Schedule**
- Open the main GUI and click **"Generate Schedule"** to create the schedule.

### **4. Add Data**
- Use the **"Add"** button to open the data entry window.
- Enter classrooms, courses, students, and preferences.

### **5. Export to Excel**
- The schedule and student report are saved in the `Exam_Reports/` folder.

---

<!--## 📸 Screenshots
### **Main Window**  
![Main Window](screenshots/main_window.png)

### **Data Entry Window**  
![Data Entry Window](screenshots/data_entry.png)

----->

## 🧪 Testing
1. Test scheduling with a small dataset.
2. Test conflict detection and resolution.
3. Test manual adjustment through the GUI.

---

## ✅ Best Practices
- Ensure all MySQL connections are closed properly.  
- Keep the database schema consistent.  
- Handle large datasets efficiently using indexing.  

---

<!--## 🏆 Acknowledgments
Special thanks to contributors and the open-source community for supporting Python and MySQL.  

---

## 📝 License
This project is licensed under the MIT License.

--- -->

✅ **Happy Coding!** 😎
