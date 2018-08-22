students = [
        (20120577, '안가빈', '여', 3273),
        (20170215, '류치곤', '남', 4879),
        (20170633, '조재구', '남', 1299)
]

for i in range(len(students)):
    student = students[i]
    name = student[1]
    student_id = student[0]
    # string formatting
    print ("%d번째 %s 학생의 학번은 %d 입니다." % (i, name, student_id))

for student in students:
    print (student[1] + ' 학생의 학번은 ' + str(student[0]) + '입니다.')
