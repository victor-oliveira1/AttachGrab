#!/bin/python3
#victor.oliveira@gmx.com
#TODO: implement pop protocol

import imaplib
import email
import os.path
import argparse

class IMAP:
    def __init__(self, server, user, password, ssl=False, port=None, mailbox='INBOX'):
        self.server = server
        self.user = user
        self.password = password

        if ssl and not port:
            port = imaplib.IMAP4_SSL_PORT
        elif not port:
            port = imaplib.IMAP4_PORT

        if ssl:
            self.mailserver = imaplib.IMAP4_SSL(self.server, port)
        else:
            self.mailserver = imaplib.IMAP4(self.server, port)

        self.mailserver.login(self.user, self.password)
        tmp = self.mailserver.select(mailbox)
        self.messages = tmp[1][0]

    def grab(self, filetype=None):
        for num in range(1, int(self.messages) + 1):
            print(num, end='\r', flush=True)
            data = self.mailserver.fetch(str(num), 'RFC822')[1][0][1]
            msg = email.message_from_bytes(data)
            msgtype = msg.get_content_maintype()

            if msgtype == 'multipart':
                for part in msg.walk():
                    filename = part.get_filename()
                    if filename:
                        if filetype:
                            if filename.casefold().endswith(filetype.casefold()):
                                pass
                            else:
                                break
                        if os.path.exists(filename):
                            name, ext = os.path.splitext(filename)
                            count = 1
                            while os.path.exists(filename):
                                filename = '{}_{}{}'.format(name, count, ext)
                                count += 1
                        print(filename)
                        with open(filename, 'wb') as file:
                            file.write(part.get_payload(decode=True))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('server',
                        help='Server host')
    parser.add_argument('user',
                        help='User email')
    parser.add_argument('password',
                        help='User password')
    parser.add_argument('-s',
                        '--ssl',
                        help='Enable SSL',
                        action='store_true',
                        default=False)
    parser.add_argument('-f',
                        '--filetype',
                        help='Filetype extension',
                        default=None)
    parser.add_argument('-p',
                        metavar='port',
                        help='Connection port',
                        default=None)
    parser.add_argument('-m',
                        metavar='mailbox',
                        help='Mailbox to work on',
                        default='INBOX')
    
    args = parser.parse_args()

    mail = IMAP(args.server, args.user, args.password, args.ssl, args.p)
    mail.grab(args.filetype)
