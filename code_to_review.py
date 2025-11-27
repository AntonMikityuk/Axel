import time

data_STORAGE = []

def create_user(name, age, tags=[]):
    user = {
        "name": name,
        "age": age,
        "id": int(time.time()),
        "tags": tags
    }
    data_STORAGE.append(user)
    return user

def calculate_average_age():
    total = 0
    count = len(data_STORAGE)
    
    for user in data_STORAGE:
        total += user['age']
        
    return total / count

def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(len(items)):
            if i != j and items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates

def process_data():
    try:
        u1 = create_user("Alex", 25)
        u1['tags'].append("admin")
        
        u2 = create_user("Bob", 30)
        
        print(f"Average age: {calculate_average_age()}")
        
    except:
        print("Something went wrong")

process_data()
