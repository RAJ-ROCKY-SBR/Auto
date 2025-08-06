import threading
from queue import Queue
import requests
import random
import string
import hashlib
from faker import Faker
import time
import json

print(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓           
> › Github :- @jatintiwari0 
> › By      :- JATIN TIWARI
> › Proxy Support Added by @coopers-lab
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛                """)
print('\x1b[38;5;208m⇼'*60)
print('\x1b[38;5;22m•'*60)
print('\x1b[38;5;22m•'*60)
print('\x1b[38;5;208m⇼'*60)

def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def get_mail_domains(proxy=None):
    url = "https://api.mail.tm/domains"
    try:
        response = requests.get(url, proxies=proxy, timeout=15)
        if response.status_code == 200:
            return response.json()['hydra:member']
        else:
            print(f'[×] E-mail Error : {response.text}')
            return None
    except Exception as e:
        print(f'[×] Error : {e}')
        return None

def create_mail_tm_account(proxy=None):
    fake = Faker()
    mail_domains = get_mail_domains(proxy)
    if not mail_domains:
        return None, None, None, None, None
        
    domain = random.choice(mail_domains)['domain']
    username = generate_random_string(10)
    password = fake.password()
    birthday = fake.date_of_birth(minimum_age=18, maximum_age=45)
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    url = "https://api.mail.tm/accounts"
    headers = {"Content-Type": "application/json"}
    data = {"address": f"{username}@{domain}", "password": password}       
    
    try:
        response = requests.post(url, headers=headers, json=data, proxies=proxy, timeout=15)
        if response.status_code == 201:
            return f"{username}@{domain}", password, first_name, last_name, birthday
        else:
            print(f'[×] Email Error : {response.text}')
            return None, None, None, None, None
    except Exception as e:
        print(f'[×] Error : {e}')
        return None, None, None, None, None

def register_facebook_account(email, password, first_name, last_name, birthday, proxy=None):
    api_key = '882a8490361da98702bf97a021ddc14d'
    secret = '62f8ce9f74b12f84c123cc23437a4a32'
    gender = random.choice([1, 2])  # 1 for female, 2 for male
    device_id = generate_random_string(16)
    
    req = {
        'api_key': api_key,
        'attempt_login': True,
        'birthday': birthday.strftime('%Y-%m-%d'),
        'client_country_code': 'US',
        'fb_api_caller_class': 'com.facebook.account.creation.protocol.Controller',
        'fb_api_req_friendly_name': 'registerAccount',
        'firstname': first_name,
        'format': 'json',
        'gender': gender,
        'lastname': last_name,
        'email': email,
        'locale': 'en_US',
        'method': 'user.register',
        'password': password,
        'reg_instance': device_id,
        'return_multiple_errors': True,
        'device_id': device_id,
        'generate_machine_id': '1',
        'generate_session_cookies': '1',
        'source': 'android'
    }
    
    # Generate signature
    sorted_req = sorted(req.items(), key=lambda x: x[0])
    sig = ''.join(f'{k}={v}' for k, v in sorted_req)
    ensig = hashlib.md5((sig + secret).encode()).hexdigest()
    req['sig'] = ensig
    
    api_url = 'https://graph.facebook.com/v17.0/device/register'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 10; SM-G975F Build/QP1A.190711.020)',
        'X-FB-Friendly-Name': 'registerAccount',
        'X-FB-Connection-Bandwidth': str(random.randint(20000000, 50000000)),
        'X-FB-Net-HNI': str(random.randint(20000, 40000)),
        'X-FB-SIM-HNI': str(random.randint(20000, 40000)),
        'X-FB-Connection-Type': 'WIFI',
        'Accept-Encoding': 'gzip, deflate'
    }
    
    try:
        response = requests.post(api_url, data=req, headers=headers, proxies=proxy, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if 'account_id' in result:
                print(f'''
-----------GENERATED-----------
EMAIL : {email}
ID : {result["account_id"]}
PASSWORD : {password}
NAME : {first_name} {last_name}
BIRTHDAY : {birthday} 
GENDER : {"Female" if gender == 1 else "Male"}
-----------GENERATED-----------
Token : {result.get("access_token", "N/A")}
-----------GENERATED-----------''')
                with open('accounts.txt', 'a') as f:
                    f.write(f"{email}:{password}\n")
                return True
            else:
                print(f'[×] Facebook Registration Error: {result}')
        else:
            print(f'[×] Facebook Error [{response.status_code}]: {response.text}')
    except Exception as e:
        print(f'[×] Facebook Connection Error: {e}')
    
    return False

def test_proxy(proxy, q, valid_proxies):
    try:
        response = requests.get(
            'https://www.facebook.com/',
            proxies=proxy,
            timeout=10
        )
        if response.status_code < 400:
            print(f'[✓] Proxy Working: {proxy["http"]}')
            valid_proxies.append(proxy)
        else:
            print(f'[✗] Proxy Failed ({response.status_code}): {proxy["http"]}')
    except:
        print(f'[✗] Proxy Failed: {proxy["http"]}')
    
    q.task_done()

def load_proxies():
    try:
        with open('proxies.txt', 'r') as file:
            proxies = [line.strip() for line in file if ':' in line]
        return [{'http': f'http://{proxy}'} for proxy in proxies]
    except:
        print('[✗] Error loading proxies.txt')
        return []

def get_working_proxies():
    proxies = load_proxies()
    if not proxies:
        print('[✗] No proxies found in proxies.txt')
        return []
    
    valid_proxies = []
    q = Queue()
    
    for proxy in proxies:
        q.put(proxy)
    
    for _ in range(min(50, len(proxies))):  # Up to 50 threads
        worker = threading.Thread(target=test_proxy, args=(q, valid_proxies))
        worker.daemon = True
        worker.start()
    
    q.join()
    print(f'\n[+] Found {len(valid_proxies)} working proxies')
    return valid_proxies

# Main execution
if __name__ == "__main__":
    working_proxies = get_working_proxies()
    
    if not working_proxies:
        print('[✗] No working proxies found. Please check your proxies.txt')
    else:
        num_accounts = int(input('[+] How Many Accounts You Want: '))
        success_count = 0
        
        for i in range(num_accounts):
            print(f'\n[•] Creating Account {i+1}/{num_accounts}')
            proxy = random.choice(working_proxies)
            
            # Try to create account with up to 3 different proxies
            for attempt in range(3):
                email, password, first_name, last_name, birthday = create_mail_tm_account(proxy)
                if email:
                    if register_facebook_account(email, password, first_name, last_name, birthday, proxy):
                        success_count += 1
                        break
                    else:
                        print(f'[!] Retrying with new proxy...')
                        proxy = random.choice(working_proxies)
                else:
                    print(f'[!] Retrying email creation...')
                    proxy = random.choice(working_proxies)
            
            # Add delay between account creations
            time.sleep(1)
        
        print(f'\n[✓] Successfully created {success_count}/{num_accounts} accounts')
    
    print('\x1b[38;5;208m⇼'*60)
