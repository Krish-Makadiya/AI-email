INSERT INTO email_actions (id, payload, scheduling_status) 
VALUES (99999, '{"sender_mail": "tanishq-test@example.com", "subject": "Test Signal"}', 'New') 
ON CONFLICT (id) DO UPDATE SET scheduling_status = 'New';
