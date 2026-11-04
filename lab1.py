def evaluate_student(marks, presence, project_status):
    if marks >= 65 and presence >= 80 and project_status == "Submitted":
        print("Result: Student is Qualified")
    else:
        print("Result: Student is Not Qualified")


print("Example 1: Successful Student")
evaluate_student(88, 95, "Submitted")

print("\nExample 2: Low Marks")
evaluate_student(55, 90, "Submitted")

print("\nExample 3: Low Attendance")
evaluate_student(75, 65, "Submitted")

print("\nExample 4: Minimum Requirements")
evaluate_student(65, 80, "Submitted")
