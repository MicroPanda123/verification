import requests

url = 'http://127.0.0.1:5000/VerCode'
while True:
    code = int(input('Code: '))
    info = {'user_nick': 'MicroPanda123', 'code': code}
    r = requests.post(url, data=info)
    if r.json()['accept']:
        print("Kod zaakceptowany")
    else:
        print("Kod niewlasciwy")
