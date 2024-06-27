import base64

with open('.dockerconfigjson', 'r') as file:
    print(base64.b64encode(file.read().encode()))