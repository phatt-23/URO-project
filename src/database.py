from enum import StrEnum
from os import wait
import sqlite3
from typing import Any, Iterable, Optional, get_type_hints, overload
from lib.types import Singleton
from models import AttachmentModel, EmailAttachmentModel, UserModel, EmailModel, EmailRecipientModel, EmailStatus
from lib import event_bus as eb
from lib.logger import log


SQL_SCRIPT_DROP_TABLES_PATH = "db/scripts/drop_tables.sql"
SQL_SCRIPT_CREATE_TABLES_PATH = "db/scripts/create_tables.sql"
SQL_SCRIPT_INSERT_TABLES_PATH = "db/scripts/insert_tables.sql"



class EventNames(StrEnum):
    USER_INSERT                                  = "db.user#insert"
    EMAIL_INSERT                                 = "db.email#insert"
    EMAIL_RECIPIENT_INSERT                       = "db.email_recipient#insert"
    ATTACHMENT_INSERT                            = "db.attachment#insert"
    EMAIL_ATTACHMENT_INSERT                      = "db.email_attachment#insert"
    EMAIL_WITH_RECIPIENTS_INSERT                 = "db.email_with_recipients#insert"
    EMAIL_WITH_RECIPIENTS_AND_ATTACHMENTS_INSERT = "db.email_with_recipients_and_attachments#insert"

    EMAIL_UPDATE = "db.email#update"

    EMAIL_DELETE = "db.email#delete"
    ATTACHMENT_DELETE = "db.attachment#delete"
    EMAIL_RECIPIENTS_OF_EMAIL_DELETE = "db.email_recipients_of_email#delete"
    EMAIL_ATTACHMENTS_OF_EMAIL_DELETE = "db.email_attachments_of_email#delete"

class EventPublishingQueue():
    queue: list[eb.EventPublishment]

    def __init__(self):
        self.queue = []

    def front(self):
        return self.queue[0]

    def pop_front(self) -> eb.EventPublishment:
        first = self.queue[0]
        self.queue = self.queue[1:]
        return first

    def push(self, publishment: eb.EventPublishment):
        self.queue.append(publishment)

    def empty(self) -> bool:
        return len(self.queue) == 0

    def publish_front(self):
        eb.bus.publish(self.pop_front())

    def publish_all(self):
        while not self.empty():
            pub = self.pop_front()
            eb.bus.publish(pub)



class Database(Singleton):
    DATABASE_INITIALIZED = False

    event_publishment_queue: EventPublishingQueue

    def __init__(self, db_file="db/emails.db"):
        if self.DATABASE_INITIALIZED:
            return

        self.DATABASE_INITIALIZED = True

        self.event_publishment_queue = EventPublishingQueue()

        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._drop_tables()
        self._create_tables()
        self._insert_dummy_data()

    ########################################################
    #### Insert ############################################
    ########################################################

    """
    These will raise sqlite3 errors. (they dont catch exceptions)
    """

    def insert_user(self, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None, commit = True) -> UserModel:
        """Inserts a new user into the database."""
        self.cursor.execute("""
            INSERT INTO user(email, first_name, last_name)
            VALUES (?, ?, ?)
            RETURNING *
        """, (email, first_name, last_name))

        user = UserModel(*self.cursor.fetchone())

        pub = eb.EventPublishment(EventNames.USER_INSERT, data={ 
            "user": user 
        })
        self.event_publishment_queue.push(pub)

        if commit:
            self.conn.commit()
            self.event_publishment_queue.publish_front() 

        return user

    def insert_email(self, sender_id: int, subject: str, body: str, status = "sent", commit = True) -> EmailModel:
        """Inserts a new user into the database."""
        self.cursor.execute("""
            INSERT INTO email(sender_id, subject, body, status)
            VALUES (?, ?, ?, ?)
            RETURNING *
        """, (sender_id, subject, body, status))

        email = EmailModel(*self.cursor.fetchone())

        pub = eb.EventPublishment(EventNames.EMAIL_INSERT, data={
            "email": email
        })
        self.event_publishment_queue.push(pub)

        if commit:
            self.conn.commit()
            self.event_publishment_queue.publish_front() 

        return email 

    def insert_email_recipient(self, email_id: int, recipient_id: int, commit = True) -> EmailRecipientModel:
        """Inserts an email-recipient relationship."""
        self.cursor.execute("""
            INSERT INTO email_recipient(email_id, recipient_id)
            VALUES (?, ?)
            RETURNING *
        """, (email_id, recipient_id))

        email_recipient = EmailRecipientModel(*self.cursor.fetchone())

        pub = eb.EventPublishment(EventNames.EMAIL_RECIPIENT_INSERT, data={
            "email_recipient": email_recipient 
        })
        self.event_publishment_queue.push(pub)

        if commit:
            self.conn.commit()
            self.event_publishment_queue.publish_front() 

        return email_recipient

    def insert_attachment(self, filename, filepath, data, commit = True) -> AttachmentModel:
        self.cursor.execute("""
            INSERT INTO attachment(filename, filepath, data)
            VALUES (?, ?, ?)
            RETURNING *
        """, (filename, filepath, data))

        attachment = AttachmentModel(*self.cursor.fetchone())

        pub = eb.EventPublishment(EventNames.ATTACHMENT_INSERT, data={
            "attachment": attachment 
        })
        self.event_publishment_queue.push(pub)

        if commit:
            self.conn.commit()
            self.event_publishment_queue.publish_front() 

        return attachment

    def insert_email_attachment(self, email_id, attachment_id, commit = True) -> EmailAttachmentModel:
        self.cursor.execute("""
            INSERT INTO email_attachment(email_id, attachment_id)
            VALUES (?, ?)
            RETURNING *
        """, (email_id, attachment_id))

        email_attachment = EmailAttachmentModel(*self.cursor.fetchone())

        pub = eb.EventPublishment(EventNames.EMAIL_ATTACHMENT_INSERT, data={
            "email_attachment": email_attachment 
        })
        self.event_publishment_queue.push(pub)

        if commit:
            self.conn.commit()
            self.event_publishment_queue.publish_front() 

        return email_attachment

    ########################################################
    #### Delete ############################################
    ########################################################

    def delete_email_with_id(self, email_id: int, commit = True) -> Optional[EmailModel]:
        self.cursor.execute(""" 
        DELETE FROM email
        WHERE email_id = ?
        RETURNING *
        """, (email_id, ))

        row = self.cursor.fetchone()
        if not row:
            return None
        email = EmailModel(*row)

        pub = eb.EventPublishment(EventNames.EMAIL_DELETE, data={
            "email": email
        })
        self.event_publishment_queue.push(pub)

        if commit:
            self.conn.commit()
            self.event_publishment_queue.publish_front()

        return email



    def delete_recipients_of_email(self, email_id: int, commit=True) -> list[EmailRecipientModel]:
        self.cursor.execute(""" 
        DELETE FROM email_recipient
        WHERE email_id = ?
        RETURNING *
        """, (email_id, ))
       
        rows = self.cursor.fetchall()
        email_recipients = [EmailRecipientModel(*row) for row in rows]

        pub = eb.EventPublishment(EventNames.EMAIL_RECIPIENTS_OF_EMAIL_DELETE, data={
            "email_recipients": email_recipients 
        })
        self.event_publishment_queue.push(pub)

        if commit:
            self.conn.commit()
            self.event_publishment_queue.publish_front()

        return email_recipients 

    def delete_attachment_by_id(self, attachment_id: int, commit=True):
        self.cursor.execute("""
        DELETE attachment
        WHERE attachment_id = ?
        """, (attachment_id, ))
        row = self.cursor.fetchone()
        if not row:
            return None

        attch = AttachmentModel(*row)

        pub = eb.EventPublishment(EventNames.ATTACHMENT_DELETE, data={
            "attachment": attch
        })
        self.event_publishment_queue.push(pub)

        if commit:
            self.conn.commit()
            self.event_publishment_queue.publish_front()

        return attch

    def delete_attachments_of_email(self, email_id: int, commit=True):
        self.cursor.execute(""" 
        DELETE FROM email_attachment
        WHERE email_id = ?
        RETURNING *
        """, (email_id, ))

        rows = self.cursor.fetchall()
        deleted_email_attchs = [EmailAttachmentModel(*row) for row in rows]

        pub = eb.EventPublishment(EventNames.EMAIL_ATTACHMENTS_OF_EMAIL_DELETE, data={
            "deleted_email_attchs": deleted_email_attchs 
        })
        self.event_publishment_queue.push(pub)

        if commit:
            self.conn.commit()
            self.event_publishment_queue.publish_front()

        return [EmailAttachmentModel(*row) for row in self.cursor.fetchall()]



    ########################################################
    #### Update ############################################
    ########################################################

    def update_email_by_id(
        self, 
        email_id: int,
        subject: str,
        body: str,
        status: EmailStatus,
        commit = True
    ) -> Optional[EmailModel]:
        self.cursor.execute(""" 
        UPDATE email 
        SET sent_at = CURRENT_TIMESTAMP
        WHERE email_id = ?
        """, (email_id, ))

        self.cursor.execute(""" 
        UPDATE email 
        SET subject = ?, body = ?, status = ?
        WHERE email_id = ?
        RETURNING *
        """, (subject, body, status, email_id))


        row = self.cursor.fetchone()
        if not row:
            return None
        email = EmailModel(*row)

        pub = eb.EventPublishment(EventNames.EMAIL_UPDATE, data={
            "email": email
        })
        self.event_publishment_queue.push(pub)

        if commit:
            self.conn.commit()
            self.event_publishment_queue.publish_front()

        return email


    #################################################################
    #### Complex Insert #############################################
    #################################################################
    #### Publishing Queue ###########################################
    #################################################################
    
    def insert_email_with_recipients_and_attachments(
        self, sender_email: str, subject: str, body: str, 
        recipients: Iterable[str],
        attachments: Iterable[str],
        status: EmailStatus = EmailStatus.SENT,
        commit = True
    ) -> EmailModel:

        # exception not catched
        email = self.insert_email_with_recipients(sender_email, subject, body, recipients, status=status, commit=False)

        for attch_path in attachments:
            with open(attch_path, "rb") as f:
                blob = f.read()
                try:
                    attch = self.insert_attachment(attch_path, attch_path, blob, commit=False)
                    self.insert_email_attachment(email.email_id, attch.attachment_id, commit=False)
                except sqlite3.Error as e:
                    raise ValueError(f"Attachment not inserted: {attch_path}. Ended with error: {e}")

        pub = eb.EventPublishment(EventNames.EMAIL_WITH_RECIPIENTS_AND_ATTACHMENTS_INSERT, data={
            "email": email
        })
        self.event_publishment_queue.push(pub)

        if commit:
            self.conn.commit()
            self.event_publishment_queue.publish_all()

        return email


    def insert_email_with_recipients(
        self, sender_email: str, subject: str, body: str, 
        recipients: Iterable[str], 
        status: EmailStatus = EmailStatus.SENT,
        commit: bool = True
    ) -> EmailModel:

        """Creates an email and assigns recipients."""

        try:
            sender = self.fetch_user_by_email(sender_email)
            if sender is None:
                raise ValueError(f"Email not inserted. Sender's email {sender_email} not found.")

            email = self.insert_email(sender.user_id, subject, body, status=status, commit=commit)

            for rec_email in recipients:
                recipient = self.fetch_user_by_email(rec_email)

                if not recipient:
                    try:
                        recipient = self.insert_user(rec_email, commit=commit)
                    except sqlite3.Error as e:
                        raise ValueError(f"Failed to insert user: {rec_email}. Ended with error: {e}")
                        
                self.insert_email_recipient(email.email_id, recipient.user_id, commit=commit)
        except sqlite3.Error as e:
            raise ValueError(f"Inserting email from '{sender_email}' to recipients {recipients} failed: {e}")

        pub = eb.EventPublishment(EventNames.EMAIL_WITH_RECIPIENTS_INSERT, data={
            "emial": email
        })
        self.event_publishment_queue.push(pub)
        if commit:
            self.conn.commit()
            self.event_publishment_queue.publish_all()
        else:
            self.event_publishment_queue.push(pub)

        log.info(f"Inserted new email with recipients: {email}")
        return email


    ########################################################
    #### Fetch/Select ######################################
    ########################################################

    def fetch_all_users(self) -> list[UserModel]:
        self.cursor.execute("SELECT * FROM user")
        return [UserModel(*row) for row in self.cursor.fetchall()]

    def fetch_all_email(self) -> list[EmailModel]:
        self.cursor.execute("SELECT * FROM email")
        return [EmailModel(*row) for row in self.cursor.fetchall()]

    def fetch_user_by_email(self, email: str) -> Optional[UserModel]:
        """Fetches a user from an email address."""
        self.cursor.execute("""
            SELECT * 
            FROM user 
            WHERE email = ?
        """, (email,))
        user = self.cursor.fetchone()
        return UserModel(*user) if user else None

    def fetch_email_by_id(self, email_id: int) -> Optional[EmailModel]:
        self.cursor.execute(""" 
            SELECT *
            FROM email
            WHERE email_id = ?
        """, (email_id, ))
        email = self.cursor.fetchone()
        return EmailModel(*email) if email else None


    def fetch_email_from_user(self, user_id: int) -> Optional[str]:
        self.cursor.execute("""
            SELECT email 
            FROM user 
            WHERE user_id = ?
        """, (user_id,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def fetch_user_by_id(self, user_id: int) -> Optional[UserModel]:
        self.cursor.execute("""
            SELECT * 
            FROM user 
            WHERE user_id = ?
        """, (user_id,))
        row = self.cursor.fetchone()
        return UserModel(*row) if row else None

    def fetch_emails_from_user(self, user_id: int, status: Optional[EmailStatus] = None) -> list[EmailModel]:
        query = """
            SELECT *
            FROM email 
            WHERE email.sender_id = ?
            ORDER BY email.sent_at ASC
        """

        params = [str(user_id)]
        if status:
            query += "AND email.status = ?"
            params.append(status)

        self.cursor.execute(query, tuple(params))
        return [EmailModel(*row) for row in self.cursor.fetchall()]

    def fetch_emails_for_user(self, user_id: int, status: Optional[EmailStatus] = None) -> list[tuple[UserModel, EmailModel]]:
        query = """
            SELECT u.*, e.*
            FROM email e
            JOIN email_recipient er ON e.email_id = er.email_id 
            JOIN user u ON e.sender_id = u.user_id
            WHERE er.recipient_id = ?
            ORDER BY e.sent_at DESC
        """

        params = [str(user_id)]
        if status:
            query += "AND e.status = ?"
            params.append(status)

        email_field_count = len(EmailModel.__annotations__)
        user_field_count = len(UserModel.__annotations__)

        self.cursor.execute(query, tuple(params))

        return [ 
            (UserModel(*row[:user_field_count]), 
             EmailModel(*row[user_field_count:user_field_count + email_field_count])) 
            for row in self.cursor.fetchall()
        ]

    def fetch_recipients_by_email_id(self, email_id: int):
        self.cursor.execute("""
        SELECT u.*
        FROM user u 
        JOIN email_recipient er ON er.recipient_id = u.user_id
        WHERE er.email_id = ?
        """, (email_id, ))

        recipients = self.cursor.fetchall()
        return [UserModel(*r) for r in recipients]

    def fetch_attachments_by_email_id(self, email_id: int):
        self.cursor.execute("""
        SELECT a.*
        FROM attachment a
        JOIN email_attachment ea ON ea.attachment_id = a.attachment_id
        WHERE ea.email_id = ?
        """, (email_id, ))


        attchs = self.cursor.fetchall()
        log.info(f"Attachments of email with id {email_id}:")
        log.info(attchs)
        return [AttachmentModel(*r) for r in attchs]


    def fetch_attachments_by_filepath(self, filepath: str) -> list[AttachmentModel]:
        self.cursor.execute(""" 
        SELECT *
        FROM attachments
        WHERE filepath = ?
        """, (filepath, ))
        
        return [AttachmentModel(*a) for a in self.cursor.fetchall()]


    ########################################################
    #### Dummy Data ########################################
    ########################################################

    def _drop_tables(self):
        with open(SQL_SCRIPT_DROP_TABLES_PATH, "r") as f:
            content = f.read()
            log.info(f"Exectuted SQL script ({SQL_SCRIPT_DROP_TABLES_PATH}):")
            log.info("\n" + content)
            self.cursor.executescript(content)
            self.conn.commit()

    def _create_tables(self):
        with open(SQL_SCRIPT_CREATE_TABLES_PATH, "r") as f:
            content = f.read()
            log.info(f"Exectuted SQL script ({SQL_SCRIPT_CREATE_TABLES_PATH}):")
            log.info("\n" + content)
            self.cursor.executescript(content)
            self.conn.commit()

    def _insert_dummy_data(self):
        with open(SQL_SCRIPT_INSERT_TABLES_PATH, "r") as f:
            content = f.read()
            log.info(f"Exectuted SQL script ({SQL_SCRIPT_INSERT_TABLES_PATH}):")
            log.info("\n" + content)
            self.cursor.executescript(content)
            self.conn.commit()

        emails = [
            ("tra0163@vsb.cz", "Hello, world!", "Hello, how are you?", ["bob@example.com", "petr@vsb.cz"]),
            ("alice@example.com", "Meeting Reminder", "Don't forget our meeting.", ["bob@example.com", "charlie@example.com"]),
            ("bob@example.com", "Weekend Plans", "Are we going hiking?", ["diana@example.com"]),
            ("charlie@example.com", "Project Update", "Finished module X.", ["eric@example.com"]),
            ("diana@example.com", "Happy Birthday!", "Hope you have a great day!", ["alice@example.com"]),
            ("diana@example.com", "Long Message", 100 * "Hope you have a great day!", ["tra0163@vsb.cz"]),  # long body
        ]

        for sender, subject, body, recipients in emails:
            try:
                self.insert_user(sender)
            except sqlite3.IntegrityError as e:
                log.warning(f"Failed to insert dummy data ({sender}):", e)

            self.insert_email_with_recipients(sender, subject, body, recipients)

    ################################################################ 
    #### Close #####################################################
    ################################################################ 

    def close(self):
        """Closes the database connection."""
        self.conn.close()


# Global singleton instance
db = Database()
