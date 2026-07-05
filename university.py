import csv
import os
from typing import List, Dict, Optional

class User:
    """کلاس پایه برای کاربران"""
    def __init__(self, username: str, password: str, role: str):
        self.username = username
        self.password = password
        self.role = role
        self.name = username

    def check_password(self, password: str) -> bool:
        return self.password == password


class Student(User):
    """کلاس دانشجو"""
    def __init__(self, username: str, password: str):
        super().__init__(username, password, "student")
        self.name = username

    def calculate_gpa(self, student_courses: List[Dict]) -> float:
        """محاسبه معدل دانشجو"""
        grades = []
        for course in student_courses:
            grade = course.get('grade')
            if grade and grade != '':
                try:
                    grades.append(float(grade))
                except ValueError:
                    continue
        
        if grades:
            return round(sum(grades) / len(grades), 2)
        return 0.0


class Teacher(User):
    """کلاس استاد"""
    def __init__(self, username: str, password: str):
        super().__init__(username, password, "teacher")
        self.name = username


class Course:
    """کلاس درس"""
    def __init__(self, course_name: str, teacher: str, prerequisites: str = ""):
        self.course_name = course_name
        self.teacher = teacher
        self.prerequisites = [p.strip() for p in prerequisites.split(',') if p.strip()]
        self.code = f"CRS-{hash(course_name) % 10000:04d}"


class UniversitySystem:
    """کلاس اصلی سیستم مدیریت دانشگاه"""
    
    def __init__(self):
        self.users: List[User] = []
        self.courses: List[Course] = []
        self.student_courses: List[Dict] = []
        self.data_path = "data"
        self.load_all_data()

    # ====================== بارگذاری داده‌ها ======================
    
    def load_all_data(self):
        self.load_users()
        self.load_courses()
        self.load_student_courses()

    def load_users(self):
        try:
            with open(f"{self.data_path}/users.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['role'] == 'student':
                        student = Student(row['username'], row['password'])
                        if 'name' in row and row['name']:
                            student.name = row['name']
                        self.users.append(student)
                    else:
                        teacher = Teacher(row['username'], row['password'])
                        if 'name' in row and row['name']:
                            teacher.name = row['name']
                        self.users.append(teacher)
            print(f"✅ {len(self.users)} کاربر لود شد")
        except FileNotFoundError:
            print("❌ فایل users.csv پیدا نشد!")

    def load_courses(self):
        try:
            with open(f"{self.data_path}/courses.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.courses.append(Course(
                        row['course_name'],
                        row['teacher'],
                        row.get('prerequisites', '')
                    ))
            print(f"✅ {len(self.courses)} درس لود شد")
        except FileNotFoundError:
            print("❌ فایل courses.csv پیدا نشد!")

    def load_student_courses(self):
        try:
            with open(f"{self.data_path}/student_courses.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.student_courses = list(reader)
            print(f"✅ {len(self.student_courses)} رکورد نمره لود شد")
        except FileNotFoundError:
            print("❌ فایل student_courses.csv پیدا نشد!")

    # ====================== ذخیره‌سازی داده‌ها ======================
    
    def save_student_courses(self):
        try:
            os.makedirs(self.data_path, exist_ok=True)
            
            fieldnames = ['username', 'course_name', 'grade']
            with open(f"{self.data_path}/student_courses.csv", 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.student_courses)
            print("✅ تغییرات نمرات ذخیره شد")
        except Exception as e:
            print(f"❌ خطا در ذخیره فایل: {e}")

    def save_all_data(self):
        self.save_student_courses()

    # ====================== متدهای احراز هویت ======================
    
    def login(self, username: str, password: str) -> Optional[User]:
        for user in self.users:
            if user.username == username and user.check_password(password):
                print(f"✅ لاگین موفق: {username} ({user.role})")
                return user
        print(f"❌ لاگین ناموفق: {username}")
        return None

    # ====================== متدهای کاربری ======================
    
    def get_user(self, username: str) -> Optional[User]:
        for user in self.users:
            if user.username == username:
                return user
        return None

    def get_all_students(self) -> List[Student]:
        return [user for user in self.users if user.role == "student"]

    def get_all_teachers(self) -> List[Teacher]:
        return [user for user in self.users if user.role == "teacher"]

    # ====================== متدهای درسی ======================
    
    def get_teacher_courses(self, teacher_username: str) -> List[Course]:
        return [c for c in self.courses if c.teacher == teacher_username]

    def get_student_courses(self, username: str) -> List[Dict]:
        return [c for c in self.student_courses if c.get('username') == username]

    def get_course_students(self, course_name: str) -> List[Dict]:
        return [s for s in self.student_courses if s['course_name'] == course_name]

    def get_student_grade(self, username: str, course_name: str) -> Optional[float]:
        for record in self.student_courses:
            if record['username'] == username and record['course_name'] == course_name:
                grade = record.get('grade')
                if grade and grade != '':
                    try:
                        return float(grade)
                    except ValueError:
                        return None
                return None
        return None

    def set_grade(self, username: str, course_name: str, grade: float) -> bool:
        for record in self.student_courses:
            if record['username'] == username and record['course_name'] == course_name:
                record['grade'] = grade
                self.save_student_courses()
                return True
        return False

    # ====================== متدهای بررسی پیش‌نیاز ======================
    
    def check_prerequisites(self, username: str, course_name: str) -> tuple:
        """
        بررسی پیش‌نیازهای یک درس برای دانشجو
        
        Args:
            username: نام کاربری دانشجو
            course_name: نام درس مورد نظر
            
        Returns:
            tuple: (وضعیت, پیام) - (True/False, "پیام توضیحی")
        """
        # پیدا کردن درس
        course = None
        for c in self.courses:
            if c.course_name == course_name:
                course = c
                break
        
        if not course:
            return False, "درس مورد نظر پیدا نشد!"
        
        if not course.prerequisites:
            return True, "این درس پیش‌نیاز ندارد."
        
        # دریافت دروس گذرانده شده دانشجو با نمره قبولی
        student_courses = self.get_student_courses(username)
        passed_courses = []
        for sc in student_courses:
            grade = sc.get('grade')
            if grade and grade != '':
                try:
                    if float(grade) >= 10:  # نمره قبولی
                        passed_courses.append(sc['course_name'])
                except ValueError:
                    continue
        
        # بررسی هر پیش‌نیاز
        missing_prereqs = []
        for prereq in course.prerequisites:
            if prereq not in passed_courses:
                missing_prereqs.append(prereq)
        
        if missing_prereqs:
            return False, f"پیش‌نیازهای زیر گذرانده نشده‌اند: {', '.join(missing_prereqs)}"
        
        return True, "تمامی پیش‌نیازها گذرانده شده است."

    # ====================== متدهای آماری و گزارش‌گیری ======================
    
    def calculate_gpa(self, username: str) -> float:
        student = self.get_user(username)
        if not student or student.role != "student":
            return 0.0
        
        courses = self.get_student_courses(username)
        return student.calculate_gpa(courses)

    def get_ranking(self) -> List[tuple]:
        students = self.get_all_students()
        ranking = []
        
        for student in students:
            gpa = self.calculate_gpa(student.username)
            ranking.append((student.username, gpa))
        
        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking

    def get_course_report(self, course_name: str) -> Dict:
        """
        دریافت گزارش آماری برای یک درس
        
        Args:
            course_name: نام درس
            
        Returns:
            Dict: شامل آمار درس
        """
        students = self.get_course_students(course_name)
        
        grades = []
        for s in students:
            grade = s.get('grade')
            if grade and grade != '':
                try:
                    grades.append(float(grade))
                except ValueError:
                    continue
        
        return {
            'course_name': course_name,
            'student_count': len(students),
            'graded_count': len(grades),
            'average': round(sum(grades) / len(grades), 2) if grades else 0,
            'min': min(grades) if grades else None,
            'max': max(grades) if grades else None
        }

    def get_all_grades_report(self, course_name: str = None) -> Dict:
        if course_name:
            return self.get_course_report(course_name)
        else:
            report = {}
            for course in self.courses:
                report[course.course_name] = self.get_course_report(course.course_name)
            return report


if __name__ == "__main__":
    system = UniversitySystem()
    print("\n" + "="*50)
    print("📊 سیستم مدیریت دانشگاه - تست اولیه")
    print("="*50)
    
    print(f"\n👥 تعداد کاربران: {len(system.users)}")
    for user in system.users:
        print(f"  - {user.username} ({user.role})")
    
    print(f"\n📚 تعداد دروس: {len(system.courses)}")
    for course in system.courses:
        prereq = course.prerequisites[0] if course.prerequisites else "ندارد"
        print(f"  - {course.course_name} (استاد: {course.teacher}, پیش‌نیاز: {prereq})")
    
    print(f"\n🎯 تعداد نمرات ثبت شده: {len(system.student_courses)}")
    
    print(f"\n🏆 رتبه‌بندی دانشجویان:")
    ranking = system.get_ranking()
    for i, (username, gpa) in enumerate(ranking, 1):
        print(f"  {i}. {username} - معدل: {gpa}")