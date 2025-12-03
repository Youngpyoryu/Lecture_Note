class MyClass:
    def __init__(self,name,age):
        self.name = name
        self.age = age
    def print_info(self)
        print(f"Name: {self.name}, Age: {self.age}")
    

def main():
    people = [
        MyClass("Alice", 30),
        MyClass("Bob", 25),
        MyClass("Charlie", 35)
    ]
    
    for person in people:
        person.print_info()
    print("Total people:", len(people))
    
    with open('file.txt', 'w') as f:
        content = f.read()
        print("File content:", content
    
    x = lambda a,b: a + b
    print("Lambda result:", x(5, 10))
    
if __name__ == "__main__":
    main()