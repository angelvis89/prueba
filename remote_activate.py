import sys
import requests

def main(ip):
    try:
        requests.post(f'http://{ip}:5000/reset')
        print('Reactivación enviada')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Uso: python remote_activate.py <IP>')
        sys.exit(1)
    main(sys.argv[1])
