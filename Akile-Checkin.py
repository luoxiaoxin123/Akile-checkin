import time
import sys
import os
import configparser
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from notice import Notice


class AkileCheckin:
    def __init__(self):
        # 优先读取环境变量（便于在 GitHub Actions 中直接运行）
        self.email = os.getenv('AKILE_EMAIL', '').strip()
        self.password = os.getenv('AKILE_PASSWORD', '').strip()
        self.push_key = os.getenv('AKILE_PUSH_KEY', '').strip()

        # 若环境变量未配置则回退到配置文件
        if not self.email or not self.password:
            config = configparser.ConfigParser()
            config.read('config.ini', encoding='utf-8')
            self.email = self.email or config.get('akile', 'email')
            self.password = self.password or config.get('akile', 'password')
            self.push_key = self.push_key or config.get('akile', 'push_key', fallback='')
        # Selenium防检测
        options = uc.ChromeOptions()
        # Selenium无头模式
        options.add_argument('--lang=zh-CN')
        options.add_experimental_option('prefs', {'intl.accept_languages': 'zh-CN,zh'})
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36")
        self.browser = uc.Chrome(options=options)

    def login(self):
        self.browser.get("https://akile.io/")
        self.browser.maximize_window()
        try:
            login_button = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/div/div[2]/div/div[2]/button'))
            )
            login_button.click()
        except TimeoutException as e:
            print(f"登录按钮没有加载出来: {e}")
            msg = f"登录按钮没有加载出来: {e}" + '\n' + "签到失败"
            Notice.serverJ(self.push_key, "Akile签到", msg)
            sys.exit(1)
        # 键入邮箱和密码
        try:
            email_input = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入邮箱"]'))
            )
            email_input.send_keys(self.email)
            password_input = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入密码"]'))
            )
            password_input.send_keys(self.password)
        except TimeoutException as e:
            self.browser.save_screenshot("邮箱.png")
            print(f"邮箱或密码输入框没有加载出来: {e}")
            msg = f"邮箱或密码输入框没有加载出来: {e}" + '\n' + "签到失败"
            Notice.serverJ(self.push_key, "Akile签到", msg)
            sys.exit(1)
        try:
            login_button = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[1]/div/div/div/div[1]/form/div[4]/div[1]/button'))
            )
            login_button.click()
        except TimeoutException as e:
            print(f"登录按钮没有加载出来: {e}")
            msg = f"登录按钮没有加载出来: {e}" + '\n' + "签到失败"
            Notice.serverJ(self.push_key, "Akile签到", msg)
            sys.exit(1)

    # 签到主逻辑
    def check_in(self):
        checkin_page = "https://akile.io/console/ak-coin-shop"
        self.browser.get(checkin_page)

        # 签到前的积分（对于已签到过的用户这个积分就是签到后的积分）
        try:
            prev_points = WebDriverWait(self.browser, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div[2]/div[2]/div/div[1]/div/div/div[2]'))
            ).text
            prev_points_num = int(prev_points.split('AK币')[0].strip())
        except TimeoutException as e:
            prev_points_num = -1

        # 签到
        try:
            checkin_button = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[1]/div[2]/div[2]/div/div[1]/div/div/div[2]/button'))
            )
            checkin_button.click()
            time.sleep(3) # 等到3s再执行下面操作, 防止点击签到按钮的动作没发出去
            try:
                cur_points = WebDriverWait(self.browser, 10).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div[2]/div[2]/div/div[1]/div/div/div[2]'))
                ).text
                cur_points_num = int(cur_points.split('AK币')[0].strip())
                if prev_points_num == -1:
                    print(f"签到成功, 当前有{cur_points_num}个AK币")
                    msg = f"签到成功, 当前有{cur_points_num}个AK币"
                else:
                    print(f"签到成功, 获得{cur_points_num-prev_points_num}个AK币, 当前有{cur_points_num}个AK币")
                    msg = f"签到成功, 获得{cur_points_num-prev_points_num}个AK币, 当前有{cur_points_num}个AK币"
                Notice.serverJ(self.push_key, "Akile签到", msg)
            except TimeoutException as e:
                print("签到成功, 但是无法获取当前AK币数量")
                msg = "签到成功, 但是无法获取当前AK币数量"
                Notice.serverJ(self.push_key, "Akile签到", msg)
            finally:
                sys.exit(0)
        except TimeoutException as e:
            # 签到按钮没有加载出来，检查是否已经签到过(通过检查已签到按钮是否存在实现)
            try:
                checkin_done_button = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div[2]/div[2]/div/div[1]/div/div/div[2]/button'))
                )
                print(f"今日已签到, 现在有{prev_points_num}AK币")
                msg = f"今日已签到, 现在有{prev_points_num}AK币"
                Notice.serverJ(self.push_key, "Akile签到", msg)
                sys.exit(0)
            except TimeoutException as e:
                print(f"签到按钮和已签到按钮都无法加载出来, 可能是网络原因, 可以等待一会再执行脚本")
                msg = f"签到按钮和已签到按钮都无法加载出来, 可能是网络原因, 可以等待一会再执行脚本"
                Notice.serverJ(self.push_key, "Akile签到", msg)
                sys.exit(1)

    def __del__(self):
        self.browser.quit()

if __name__ == "__main__":
    akile = AkileCheckin()
    try:
        akile.login()
        time.sleep(3) # 防止程序执行太快, 网站反应不过来导致需要二次登录
        akile.check_in()
    finally:
        akile.browser.quit()
