import requests, json
resp = requests.get('http://127.0.0.1:8000/process-email', timeout=10)
print('Status', resp.status_code)
data = resp.json()
for i, e in enumerate(data.get('emails', [])[:12]):
    print('---')
    print(i, 'ID:', e.get('id'))
    print('Subject:', e.get('subject'))
    print('Attachment:', e.get('attachment_analysis'))
    print('Vision amounts:', e.get('vision_data', {}).get('amounts'))
    print('Vision dates:', e.get('vision_data', {}).get('dates'))
    print('Vision action:', e.get('vision_data', {}).get('action'))
    print(json.dumps(e.get('vision_data'), indent=2))
