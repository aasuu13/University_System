import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# حل مشکل import
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from university import UniversitySystem, Student

class UniversityGUI:
    def __init__(self):
        self.system = UniversitySystem()
        self.current_user = None
        self.root = tk.Tk()
        self.root.title("سامانه مدیریت دانشگاهی")
        self.root.geometry("1180x760")
        self.root.configure(bg="#e8f0f7")
        self.show_login_page()

    def show_login_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        frame = tk.Frame(self.root, bg="#e8f0f7")
        frame.pack(expand=True)

        tk.Label(frame, text="🎓 سامانه مدیریت دانشگاهی", 
                font=("Tahoma", 26, "bold"), bg="#e8f0f7", fg="#1e3a8a").pack(pady=50)

        tk.Label(frame, text="نام کاربری", font=("Tahoma", 12), bg="#e8f0f7").pack(pady=5)
        self.username_entry = tk.Entry(frame, font=("Tahoma", 12), width=35, justify="center")
        self.username_entry.pack(pady=5)

        tk.Label(frame, text="رمز عبور", font=("Tahoma", 12), bg="#e8f0f7").pack(pady=5)
        self.password_entry = tk.Entry(frame, font=("Tahoma", 12), width=35, show="*", justify="center")
        self.password_entry.pack(pady=5)

        tk.Button(frame, text="ورود", font=("Tahoma", 12, "bold"), bg="#1e40af", fg="white",
                  width=25, height=2, command=self.login).pack(pady=40)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        user = self.system.login(username, password)
        if user:
            self.current_user = user
            if user.role == "student":
                self.show_student_dashboard()
            else:
                self.show_teacher_dashboard()
        else:
            messagebox.showerror("خطا", "نام کاربری یا رمز عبور اشتباه است!")

    # ====================== پنل دانشجو ======================
    def show_student_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text=f"👨‍🎓 خوش آمدید {self.current_user.username}", 
                font=("Tahoma", 18, "bold"), bg="#e8f0f7").pack(pady=20)

        btn_frame = tk.Frame(self.root, bg="#e8f0f7")
        btn_frame.pack(pady=30)
        ttk.Button(btn_frame, text="📚 انتخاب واحد", command=self.show_course_selection).pack(side="left", padx=12)
        ttk.Button(btn_frame, text="📊 نمرات و معدل", command=self.show_grades).pack(side="left", padx=12)
        ttk.Button(btn_frame, text="🏆 رتبه‌بندی", command=self.show_ranking).pack(side="left", padx=12)
        ttk.Button(btn_frame, text="خروج", command=self.show_login_page).pack(side="left", padx=12)

    def show_course_selection(self):
        """نمایش لیست دروس با بررسی پیش‌نیاز"""
        win = tk.Toplevel(self.root)
        win.title("انتخاب واحد")
        win.geometry("1000x650")

        tk.Label(win, text="لیست دروس", font=("Tahoma", 14, "bold")).pack(pady=10)

        # ایجاد Treeview با ستون جدید برای وضعیت پیش‌نیاز
        tree = ttk.Treeview(win, columns=("course", "teacher", "prereq", "status"), show="headings", height=15)
        tree.heading("course", text="نام درس")
        tree.heading("teacher", text="استاد")
        tree.heading("prereq", text="پیش‌نیاز")
        tree.heading("status", text="وضعیت پیش‌نیاز")
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        # تنظیم عرض ستون‌ها
        tree.column("course", width=200)
        tree.column("teacher", width=150)
        tree.column("prereq", width=200)
        tree.column("status", width=200)

        for course in self.system.courses:
            prereq = course.prerequisites[0] if course.prerequisites else "ندارد"
            
            # بررسی وضعیت پیش‌نیاز برای دانشجو
            status, status_msg = self.system.check_prerequisites(
                self.current_user.username, 
                course.course_name
            )
            
            # نمایش وضعیت با آیکون
            if status:
                status_display = "✅ قابل انتخاب"
            else:
                status_display = f"❌ {status_msg}"
            
            tree.insert("", "end", values=(
                course.course_name, 
                course.teacher, 
                prereq,
                status_display
            ))

        def enroll():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("هشدار", "یک درس انتخاب کنید")
                return
            
            course_name = tree.item(selected[0])['values'][0]
            
            # بررسی مجدد پیش‌نیاز
            status, status_msg = self.system.check_prerequisites(
                self.current_user.username, 
                course_name
            )
            
            if not status:
                messagebox.showerror("خطا", f"❗ {status_msg}")
                return

            if any(sc['course_name'] == course_name and sc['username'] == self.current_user.username 
                   for sc in self.system.student_courses):
                messagebox.showinfo("اطلاعات", "این درس قبلاً انتخاب شده")
                return

            self.system.student_courses.append({
                'username': self.current_user.username, 
                'course_name': course_name, 
                'grade': ''
            })
            self.system.save_student_courses()
            messagebox.showinfo("✅ موفقیت", f"درس {course_name} با موفقیت انتخاب شد!")
            win.destroy()

        ttk.Button(win, text="انتخاب واحد", command=enroll).pack(pady=15)

    def show_grades(self):
        win = tk.Toplevel(self.root)
        win.title("نمرات و معدل")
        win.geometry("800x500")

        grades = self.system.get_student_courses(self.current_user.username)
        gpa = self.current_user.calculate_gpa(grades)

        tk.Label(win, text=f"معدل شما: {gpa}", font=("Tahoma", 16, "bold"), fg="darkblue").pack(pady=15)

        tree = ttk.Treeview(win, columns=("course", "grade"), show="headings")
        tree.heading("course", text="نام درس")
        tree.heading("grade", text="نمره")
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        for c in grades:
            tree.insert("", "end", values=(c['course_name'], c.get('grade', 'ثبت نشده')))

    def show_ranking(self):
        win = tk.Toplevel(self.root)
        win.title("رتبه‌بندی معدل")
        win.geometry("700x550")

        students = [u for u in self.system.users if isinstance(u, Student)]
        ranking = sorted([(s.username, s.calculate_gpa(self.system.get_student_courses(s.username))) 
                         for s in students], key=lambda x: x[1], reverse=True)

        tree = ttk.Treeview(win, columns=("rank", "student", "gpa"), show="headings")
        tree.heading("rank", text="رتبه")
        tree.heading("student", text="دانشجو")
        tree.heading("gpa", text="معدل")
        tree.pack(fill="both", expand=True, padx=30, pady=20)

        for i, (student, gpa) in enumerate(ranking, 1):
            tree.insert("", "end", values=(i, student, gpa))

    # ====================== پنل استاد ======================
    def show_teacher_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        header_frame = tk.Frame(self.root, bg="#1e3a8a", height=100)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text=f"👩‍🏫 پنل استاد - {self.current_user.username}",
            font=("Tahoma", 20, "bold"),
            bg="#1e3a8a",
            fg="white"
        ).pack(pady=30)
        
        btn_frame = tk.Frame(self.root, bg="#e8f0f7")
        btn_frame.pack(pady=40)
        
        tk.Button(
            btn_frame,
            text="📋 ثبت نمره دروس",
            font=("Tahoma", 14, "bold"),
            bg="#1e40af",
            fg="white",
            padx=40,
            pady=15,
            cursor="hand2",
            command=self.show_teacher_courses
        ).pack(pady=10)
        
        # ========== دکمه گزارش‌گیری ==========
        tk.Button(
            btn_frame,
            text="📊 گزارش‌گیری آماری",
            font=("Tahoma", 14, "bold"),
            bg="#059669",
            fg="white",
            padx=40,
            pady=15,
            cursor="hand2",
            command=self.show_reports
        ).pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="🚪 خروج",
            font=("Tahoma", 12),
            bg="#dc2626",
            fg="white",
            padx=30,
            pady=10,
            cursor="hand2",
            command=self.show_login_page
        ).pack(pady=10)

    def show_teacher_courses(self):
        """نمایش دروس استاد با امکان ثبت نمره"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # هدر
        header_frame = tk.Frame(self.root, bg="#1e3a8a", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="📚 ثبت نمره دانشجویان",
            font=("Tahoma", 18, "bold"),
            bg="#1e3a8a",
            fg="white"
        ).pack(pady=15)
        
        # دکمه بازگشت
        back_frame = tk.Frame(self.root, bg="#e8f0f7")
        back_frame.pack(fill="x", pady=10)
        
        tk.Button(
            back_frame,
            text="🔙 بازگشت",
            font=("Tahoma", 11),
            bg="#6b7280",
            fg="white",
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.show_teacher_dashboard
        ).pack(side="left", padx=20)
        
        # کانتینر با اسکرول
        main_container = tk.Frame(self.root, bg="#e8f0f7")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(main_container, bg="#e8f0f7", highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#e8f0f7")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # دریافت دروس استاد
        teacher_courses = self.system.get_teacher_courses(self.current_user.username)
        
        if not teacher_courses:
            tk.Label(
                scrollable_frame,
                text="📭 شما هیچ درسی ندارید!",
                font=("Tahoma", 16),
                bg="#e8f0f7",
                fg="#6b7280"
            ).pack(expand=True, pady=50)
            return
        
        # نمایش هر درس
        for course in teacher_courses:
            course_frame = tk.LabelFrame(
                scrollable_frame,
                text=f"📖 {course.course_name}",
                font=("Tahoma", 13, "bold"),
                bg="white",
                fg="#1e3a8a",
                padx=15,
                pady=15
            )
            course_frame.pack(fill="x", pady=12, padx=5)
            
            # دانشجویان این درس
            students = [
                s for s in self.system.student_courses 
                if s['course_name'] == course.course_name
            ]
            
            if not students:
                tk.Label(
                    course_frame,
                    text="⚠️ هیچ دانشجویی در این درس ثبت نام نکرده است.",
                    font=("Tahoma", 11),
                    bg="white",
                    fg="#f59e0b"
                ).pack(pady=15)
                continue
            
            # جدول دانشجویان
            table_frame = tk.Frame(course_frame, bg="white")
            table_frame.pack(fill="x", pady=5)
            
            # هدر
            headers = ["ردیف", "دانشجو", "نمره فعلی", "نمره جدید", "ثبت"]
            for col, header in enumerate(headers):
                tk.Label(
                    table_frame,
                    text=header,
                    font=("Tahoma", 10, "bold"),
                    bg="#2563eb",
                    fg="white",
                    padx=8,
                    pady=6
                ).grid(row=0, column=col, sticky="ew", padx=1)
            
            # تنظیم عرض
            table_frame.grid_columnconfigure(0, weight=1)
            table_frame.grid_columnconfigure(1, weight=4)
            table_frame.grid_columnconfigure(2, weight=2)
            table_frame.grid_columnconfigure(3, weight=2)
            table_frame.grid_columnconfigure(4, weight=1)
            
            # نمایش دانشجویان
            for row, student_data in enumerate(students, 1):
                student_user = self.system.get_user(student_data['username'])
                student_name = student_user.username if student_user else student_data['username']
                
                current_grade = student_data.get('grade', '')
                grade_display = current_grade if current_grade else "—"
                
                bg_color = "white" if row % 2 == 0 else "#f3f4f6"
                
                tk.Label(
                    table_frame,
                    text=str(row),
                    font=("Tahoma", 10),
                    bg=bg_color,
                    padx=5,
                    pady=5
                ).grid(row=row, column=0, sticky="ew")
                
                tk.Label(
                    table_frame,
                    text=student_name,
                    font=("Tahoma", 10),
                    bg=bg_color,
                    padx=5,
                    pady=5,
                    anchor="w"
                ).grid(row=row, column=1, sticky="w", padx=5)
                
                grade_color = "#16a34a" if current_grade and float(current_grade) >= 10 else "#dc2626" if current_grade else "#9ca3af"
                tk.Label(
                    table_frame,
                    text=grade_display,
                    font=("Tahoma", 10, "bold"),
                    bg=bg_color,
                    fg=grade_color,
                    padx=5,
                    pady=5
                ).grid(row=row, column=2, sticky="ew")
                
                grade_entry = tk.Entry(
                    table_frame,
                    font=("Tahoma", 10),
                    width=10,
                    justify="center"
                )
                grade_entry.grid(row=row, column=3, padx=5, pady=5, sticky="ew")
                
                tk.Button(
                    table_frame,
                    text="✅ ثبت",
                    font=("Tahoma", 9, "bold"),
                    bg="#22c55e",
                    fg="white",
                    padx=10,
                    pady=3,
                    cursor="hand2",
                    command=lambda u=student_data['username'], c=course.course_name, e=grade_entry: 
                        self.save_grade(u, c, e)
                ).grid(row=row, column=4, padx=5, pady=5)

    def save_grade(self, username, course_name, entry_widget):
        """ثبت نمره برای دانشجو"""
        try:
            grade_text = entry_widget.get().strip()
            
            if not grade_text:
                messagebox.showwarning("خطا", "لطفاً نمره را وارد کنید!")
                return
            
            grade = float(grade_text)
            
            if grade < 0 or grade > 20:
                messagebox.showerror("خطا", "نمره باید بین 0 تا 20 باشد!")
                entry_widget.delete(0, tk.END)
                return
            
            for record in self.system.student_courses:
                if record['username'] == username and record['course_name'] == course_name:
                    record['grade'] = grade
                    self.system.save_student_courses()
                    messagebox.showinfo("✅ موفقیت", f"نمره {grade} برای {username} ثبت شد!")
                    entry_widget.delete(0, tk.END)
                    self.show_teacher_courses()
                    return
            
            messagebox.showerror("خطا", "دانشجو در این درس یافت نشد!")
            
        except ValueError:
            messagebox.showerror("خطا", "لطفاً یک عدد معتبر وارد کنید!")
            entry_widget.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("خطا", f"مشکل در ثبت نمره: {str(e)}")

    # ====================== گزارش‌گیری آماری ======================
    def show_reports(self):
        """نمایش گزارش‌های آماری برای استاد"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # هدر
        header_frame = tk.Frame(self.root, bg="#1e3a8a", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="📊 گزارش‌گیری آماری دروس",
            font=("Tahoma", 18, "bold"),
            bg="#1e3a8a",
            fg="white"
        ).pack(pady=15)
        
        # دکمه بازگشت
        back_frame = tk.Frame(self.root, bg="#e8f0f7")
        back_frame.pack(fill="x", pady=10)
        
        tk.Button(
            back_frame,
            text="🔙 بازگشت",
            font=("Tahoma", 11),
            bg="#6b7280",
            fg="white",
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.show_teacher_dashboard
        ).pack(side="left", padx=20)
        
        # کانتینر اصلی
        main_frame = tk.Frame(self.root, bg="#e8f0f7")
        main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # دریافت دروس استاد
        teacher_courses = self.system.get_teacher_courses(self.current_user.username)
        
        if not teacher_courses:
            tk.Label(
                main_frame,
                text="📭 شما هیچ درسی ندارید!",
                font=("Tahoma", 16),
                bg="#e8f0f7",
                fg="#6b7280"
            ).pack(expand=True)
            return
        
        # نمایش گزارش هر درس
        for course in teacher_courses:
            report = self.system.get_course_report(course.course_name)
            
            report_frame = tk.LabelFrame(
                main_frame,
                text=f"📖 {course.course_name}",
                font=("Tahoma", 13, "bold"),
                bg="white",
                fg="#1e3a8a",
                padx=15,
                pady=15
            )
            report_frame.pack(fill="x", pady=10)
            
            # اطلاعات گزارش
            info_text = f"""
👥 تعداد دانشجویان: {report['student_count']}
📊 میانگین نمرات: {report['average']}
🟢 بالاترین نمره: {report['max'] if report['max'] is not None else '—'}
🔴 پایین‌ترین نمره: {report['min'] if report['min'] is not None else '—'}
📝 تعداد نمرات ثبت‌شده: {report['graded_count']}
            """
            
            tk.Label(
                report_frame,
                text=info_text,
                font=("Tahoma", 11),
                bg="white",
                fg="#374151",
                justify="left"
            ).pack(anchor="w", pady=5)
            
            # وضعیت ثبت نمرات با رنگ
            if report['student_count'] > 0:
                percent = (report['graded_count'] / report['student_count']) * 100
                status_color = "#16a34a" if percent == 100 else "#f59e0b" if percent > 50 else "#dc2626"
                status_text = f"وضعیت ثبت نمره: {report['graded_count']} از {report['student_count']} دانشجو ({percent:.0f}%)"
                
                tk.Label(
                    report_frame,
                    text=status_text,
                    font=("Tahoma", 10, "bold"),
                    bg="white",
                    fg=status_color
                ).pack(anchor="w")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = UniversityGUI()
    app.run()