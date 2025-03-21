-- Insert more users
INSERT INTO user (email, first_name, last_name) 
VALUES
    ('john.doe@example.com', 'John', 'Doe'),
    ('jane.smith@example.com', 'Jane', 'Smith'),
    ('tra0163@vsb.cz', 'Phat', 'Tran Dai'),
    ('michael.brown@example.com', 'Michael', 'Brown'),
    ('sarah.lee@example.com', 'Sarah', 'Lee'),
    ('david.wilson@example.com', 'David', 'Wilson'),
    ('emma.taylor@example.com', 'Emma', 'Taylor');

-- Insert more emails  
INSERT INTO email (sender_id, subject, body, status) 
VALUES
    (1, 'Project Update', 'Here is the latest update on the project.', 'sent'),
    (2, 'Meeting Reminder', 'Don’t forget our meeting tomorrow.', 'sent'),
    (1, 'Invoice Attached', 'Please find the invoice attached.', 'sent'),
    (4, 'Weekly Report', 'Please review the attached weekly report.', 'sent'),
    (5, 'Follow-Up', 'Following up on our last conversation.', 'sent'),
    (6, 'Team Meeting', 'Scheduled team meeting for next Monday.', 'sent'),
    (1, 'Product Launch', 'Exciting news! Our product is launching soon.', 'sent'),
    (3, 'Collaboration Request', 'Would you be interested in collaborating?', 'draft');

-- Insert additional recipients (including tra0163@vsb.cz)  
INSERT INTO email_recipient (email_id, recipient_id) 
VALUES
    (1, 3), -- tra0163@vsb.cz receives "Project Update"
    (2, 3), -- tra0163@vsb.cz receives "Meeting Reminder"
    (3, 3), -- tra0163@vsb.cz receives "Invoice Attached"
    (4, 3), -- tra0163@vsb.cz receives "Weekly Report"
    (4, 2), -- Jane Smith also receives "Weekly Report"
    (5, 3), -- tra0163@vsb.cz receives "Follow-Up"
    (6, 3), -- tra0163@vsb.cz receives "Team Meeting"
    (6, 5), -- Sarah Lee also receives "Team Meeting"
    (7, 3), -- tra0163@vsb.cz receives "Product Launch"
    (8, 2), -- Jane Smith receives "Collaboration Request"
    (8, 4); -- Michael Brown receives "Collaboration Request"

-- Insert more attachments  
INSERT INTO attachment (filename, filepath, data) 
VALUES
    ('report.pdf', '/attachments/report.pdf', X'89504E470D0A1A0A0000'),
    ('invoice.pdf', '/attachments/invoice.pdf', X'255044462D312E350D0A25E2E3'),
    ('notes.txt', '/attachments/notes.txt', X'5468697320697320612074657374'),
    ('weekly_report.pdf', '/attachments/weekly_report.pdf', X'89504E470D0A1A0A0000'),
    ('presentation.pptx', '/attachments/presentation.pptx', X'255044462D312E350D0A25E2E3'),
    ('contract.docx', '/attachments/contract.docx', X'446F63756D656E7420636F6E74'),
    ('agenda.pdf', '/attachments/agenda.pdf', X'505944462D312E350D0A25E2E3'),
    ('logo.png', '/attachments/logo.png', X'89504E470D0A1A0A0000');

-- Link additional attachments to emails  
INSERT INTO email_attachment (email_id, attachment_id) 
VALUES
    (1, 1), -- "Project Update" has "report.pdf"
    (3, 2), -- "Invoice Attached" has "invoice.pdf"
    (3, 3), -- "Invoice Attached" also has "notes.txt"
    (4, 1), -- "Weekly Report" email has "weekly_report.pdf"
    (5, 2), -- "Follow-Up" email has "presentation.pptx"
    (6, 3), -- "Team Meeting" email has "contract.docx"
    (6, 4), -- "Team Meeting" also has "agenda.pdf"
    (7, 5); -- "Product Launch" email has "logo.png"

