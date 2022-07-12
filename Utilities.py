import json

# removes line from file
def f_remove(filepath, line):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    with open(filepath, 'w') as f:
        for line in lines:
            if line.strip('\n') != line:
                f.write(line)

def store(filepath, data):
    with open(filepath, 'w') as file:
        json.dump(data, file)