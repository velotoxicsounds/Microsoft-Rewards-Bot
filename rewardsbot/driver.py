import os
import platform
import zipfile

import requests
from selenium import webdriver


class Driver(object):

    def __init__(self, config):
        self.config = config

    @staticmethod
    def download_driver(driver_path, system):
        # determine latest chromedriver version
        url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
        r = requests.get(url)
        latest_version = r.text
        if system == "Windows":
            url = "https://chromedriver.storage.googleapis.com/{}/chromedriver_win32.zip".format(latest_version)
        elif system == "Darwin":
            url = "https://chromedriver.storage.googleapis.com/{}/chromedriver_mac64.zip".format(latest_version)
        elif system == "Linux":
            url = "https://chromedriver.storage.googleapis.com/{}/chromedriver_linux64.zip".format(latest_version)

        response = requests.get(url, stream=True)
        zip_file_path = os.path.join(os.path.dirname(driver_path), os.path.basename(url))
        with open(zip_file_path, "wb") as handle:
            for chunk in response.iter_content(chunk_size=512):
                if chunk:  # filter out keep alive chunks
                    handle.write(chunk)
        extracted_dir = os.path.splitext(zip_file_path)[0]
        with zipfile.ZipFile(zip_file_path, "r") as zip_file:
            zip_file.extractall(extracted_dir)
        os.remove(zip_file_path)

        driver = os.listdir(extracted_dir)[0]
        os.rename(os.path.join(extracted_dir, driver), driver_path)
        os.rmdir(extracted_dir)

        os.chmod(driver_path, 0o755)
        # way to note which chromedriver version is installed
        open(os.path.join(os.path.dirname(driver_path), "{}.txt".format(latest_version)), "w").close()

    def check_chromedriver(self):
        path = os.path.join('drivers', 'chromedriver')
        os.makedirs('drivers', exist_ok=True)
        system = platform.system()
        if system == "Windows":
            if not path.endswith(".exe"):
                path += ".exe"
        if not os.path.exists(path):
            self.download_driver(path, system)
        return path

    def get_webdriver(self, user_agent=None):
        """
        Inits the chrome browser with headless setting and user agent
        :param user_agent: String
        :return: webdriver obj
        """
        options = webdriver.ChromeOptions()
        if self.config.headless:
            options.add_argument('--headless')

        options.add_argument('--whitelisted-ips')
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--disable-extensions")
        options.add_argument('--disable-infobars')
        options.add_argument('--incognito')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.geolocation": 1,
            "profile.default_content_setting_values.notifications": 2})
        # geolocation permission, 0=Ask, 1=Allow, 2=Deny
        path = self.check_chromedriver()
        chrome_obj = webdriver.Chrome(path, chrome_options=options)

        return chrome_obj
