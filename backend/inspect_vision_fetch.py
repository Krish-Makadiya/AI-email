import requests, json
resp = requests.get('http://127.0.0.1:8000/process-email', timeout=10)
print('Status', resp.status_code)
data = resp.json()
for i, e in enumerate(data.get('emails', [])[:12]):
    print('---')
    print(i, 'ID:', e.get('id'))
    print('Subject:', e.get('subject'))
    print('Attachment:', e.get('attachment_analysis')[:80] if e.get('attachment_analysis') else '')
    vd = e.get('vision_data')
    if vd:
        print('Vision amounts:', vd.get('amounts'))
        print('Vision dates:', vd.get('dates'))
        print('Vision action:', vd.get('action'))
        print('Raw snippet:', (vd.get('raw') or '')[:120])
    else:
        print('No vision data')
