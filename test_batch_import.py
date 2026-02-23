import requests
import json

BASE_URL = 'http://127.0.0.1:8000'

# 登录获取token
response = requests.post(
    f'{BASE_URL}/user/token',
    data={'username': 'admin@example.com', 'password': '00000000'}
)
token = response.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}

# 先创建一个学校用于测试
school_response = requests.post(
    f'{BASE_URL}/school/',
    json={'name': '批量导入测试学校', 'address': '测试地址'},
    headers=headers
)
school_id = school_response.json().get('id')
print(f'创建学校: {school_id}')

# 测试批量导入班级
print('\n测试批量导入班级:')
batch_classes = {
    'school_id': school_id,
    'classes': [
        {'name': '高一(1)班', 'grade': '高一', 'description': '理科班'},
        {'name': '高一(2)班', 'grade': '高一', 'description': '文科班'},
        {'name': '高一(3)班', 'grade': '高一', 'description': '实验班'},
    ]
}
response = requests.post(f'{BASE_URL}/school/class/batch', json=batch_classes, headers=headers)
print(f'状态码: {response.status_code}')
print(f'结果: {json.dumps(response.json(), ensure_ascii=False, indent=2)}')

# 获取班级列表
class_response = requests.get(f'{BASE_URL}/school/class/', headers=headers)
classes = class_response.json()
class_id = None
for c in classes:
    if c['school_id'] == school_id:
        class_id = c['id']
        break
print(f'\n获取到班级ID: {class_id}')

# 测试批量导入学生
print('\n测试批量导入学生:')
batch_students = {
    'class_id': class_id,
    'students': [
        {'name': '张三', 'gender': '男', 'student_number': '2024001'},
        {'name': '李四', 'gender': '女', 'student_number': '2024002'},
        {'name': '王五', 'gender': '男', 'student_number': '2024003'},
        {'name': '赵六', 'gender': '女', 'student_number': '2024004'},
    ]
}
response = requests.post(f'{BASE_URL}/school/student/batch', json=batch_students, headers=headers)
print(f'状态码: {response.status_code}')
print(f'结果: {json.dumps(response.json(), ensure_ascii=False, indent=2)}')

# 测试重复学号
print('\n测试重复学号:')
batch_students_repeat = {
    'class_id': class_id,
    'students': [
        {'name': '张三2', 'gender': '男', 'student_number': '2024001'},  # 重复学号
        {'name': '钱七', 'gender': '男', 'student_number': '2024005'},
    ]
}
response = requests.post(f'{BASE_URL}/school/student/batch', json=batch_students_repeat, headers=headers)
print(f'状态码: {response.status_code}')
print(f'结果: {json.dumps(response.json(), ensure_ascii=False, indent=2)}')

# 清理测试数据
print('\n清理测试数据...')
# 删除学生
students_response = requests.get(f'{BASE_URL}/school/student/', headers=headers)
for item in students_response.json().get('items', []):
    if item['class_id'] == class_id:
        requests.delete(f'{BASE_URL}/school/student/{item["id"]}', headers=headers)
# 删除班级
for c in classes:
    if c['school_id'] == school_id:
        requests.delete(f'{BASE_URL}/school/class/{c["id"]}', headers=headers)
# 删除学校
requests.delete(f'{BASE_URL}/school/{school_id}', headers=headers)
print('清理完成')

print('\n✅ 批量导入功能测试完成!')
