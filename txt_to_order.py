import os, sys, zipfile, smtplib, chardet, codecs
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

class order_to_frf:

    def __init__(self):

        self.cwd = os.path.split(os.path.realpath(__file__))[0]
        self.file = os.path.join(self.cwd, 'order.frf')
        #get settings from file to copy from path1 to path2
        with open(os.path.join(self.cwd, 'text_order.config'), 'r') as settings_file:
            settings = settings_file.readlines()
     
        #initialize path variables with data from settings file
        for line in settings:
            setting = line.rstrip('\n')
            if '#' in line:
                continue
            
            if 'mail_server' in line:
                self.mail_server = setting[setting.index('=') + 1:]
       
            elif 'user' in line:
                self.user = setting[setting.index('=') + 1:]

            elif 'password' in line:
                self.password = setting[setting.index('=') + 1:]
    
            elif 'subject' in line:
                self.subject = setting[setting.index('=') + 1:]

            elif 'from_email' in line:
                self.from_email = setting[setting.index('=') + 1:]

            elif 'to_email' in line:
                self.to_email = setting[setting.index('=') + 1:].split(';')
        
        self.file = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'order.frf')
        

    def txt_to_frf(self, path_to_txt=sys.argv[1], path_to_frf=os.path.split(os.path.realpath(__file__))[0]):
        """Gets the file path and zip it into frf format, storing in script dir by default.

            Args:
            path_to_txt -- Gets path to file, which you droped on script by default.
            path_to_frf -- Gets the current script file path by default.
        """
        
        path_to_result = os.path.join(os.path.split(path_to_txt)[0], 'result.txt')
        BLOCKSIZE = 1048576
        with open(path_to_txt, 'rb') as text:
            file_encoding = chardet.detect(text.read())['encoding']
        
        with codecs.open(path_to_txt, 'r', file_encoding) as source:
            with codecs.open(path_to_result, 'w', 'windows-1251') as result:
                while True:
                    contents = source.read(BLOCKSIZE)
                    if not contents:
                        break
                    result.write(contents)
            
            
        with zipfile.ZipFile(self.file, "w") as order:
            order.write(path_to_result,'order')


    def send_order(self):
        """Sends order by email to the specified address.

            frf_path -- Path to frf file with order.
        """

        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = COMMASPACE.join(self.to_email)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = self.subject

        
        with open(self.file,'rb') as f:
            
            part = MIMEApplication(f.read(), Name=basename(self.file))

            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(self.file)
            msg.attach(part)
        
        with smtplib.SMTP_SSL(self.mail_server, 0, self.from_email) as smtp:
            smtp.login(self.user, self.password)
            smtp.sendmail(self.from_email, self.to_email, msg.as_string())
            

    
if __name__=="__main__":

    order = order_to_frf()
    order.txt_to_frf()
    order.send_order()
