CREATE TABLE IF NOT EXISTS user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    first_name TEXT NULL,
    last_name TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS email (
    email_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    status TEXT CHECK(status IN ('sent', 'draft', 'deleted', 'sent_draft')) DEFAULT 'sent',
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES user(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS email_recipient (
    email_id INTEGER NOT NULL,
    recipient_id INTEGER NOT NULL,
    PRIMARY KEY (email_id, recipient_id),
    FOREIGN KEY (email_id) REFERENCES email(email_id) ON DELETE CASCADE,
    FOREIGN KEY (recipient_id) REFERENCES user(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_email_recipient_recepient_id ON email_recipient(recipient_id);

CREATE TABLE IF NOT EXISTS attachment (
    attachment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    data BLOB NOT NULL,
    create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS email_attachment (
    email_id INTEGER NOT NULL,
    attachment_id INTEGER NOT NULL, -- this should maybe be unique
    PRIMARY KEY (email_id, attachment_id),
    FOREIGN KEY (email_id) REFERENCES email(email_id) ON DELETE CASCADE,
    FOREIGN KEY (attachment_id) REFERENCES attachment(attachment_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_email_attachment_email_id ON email_attachment(email_id);
CREATE INDEX IF NOT EXISTS idx_email_attachment_attachment_id ON email_attachment(attachment_id);

