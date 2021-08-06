from shareplum import Site, Office365
from shareplum.site import Version
import json, os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = 'config.json'

# read config file
with open(config_path) as config_file:
    config = json.load(config_file)
    config = config['share_point']

USERNAME = config['user']
PASSWORD = config['password']
SHAREPOINT_URL = config['url']
SHAREPOINT_SITE = config['site']
SHAREPOINT_DOC = config['doc_library']

class SharePoint:
    def auth(self):
        self.authcookie = Office365(SHAREPOINT_URL, username=USERNAME, password=PASSWORD).GetCookies()
        self.site = Site(SHAREPOINT_SITE, version=Version.v365, authcookie=self.authcookie)

        return self.site

    def connect_folder(self, folder_name):
        self.auth_site = self.auth()

        self.sharepoint_dir = '/'.join([SHAREPOINT_DOC, folder_name])
        self.folder = self.auth_site.Folder(self.sharepoint_dir)

        return self.folder

    def upload_file(self, file, file_name, folder_name):
        self._folder = self.connect_folder(folder_name)

        with open(file, mode='rb') as file_obj:
            file_content = file_obj.read()

        self._folder.upload_file(file_content, file_name)

    def delete_file(self, file_name, folder_name):

        self._folder = self.connect_folder(folder_name)

        self._folder.delete_file(file_name)

file_dir_path = 'ScrapedOutput.csv'

# this will be the file name that it will be saved in SharePoint as
file_name = 'ScrapedOutput.csv'

# The folder in SharePoint that it will be saved under
folder_name = 'Output'

# upload file
SharePoint().upload_file(file_dir_path, file_name, folder_name)
