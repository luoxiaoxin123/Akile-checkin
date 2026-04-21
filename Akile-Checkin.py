import time
import sys
import os
import re
import subprocess
import configparser
import shutil
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from notice import Notice


class AkileCheckin:
    def __init__(self):
        self.browser = None

        # 优先读取环境变量（便于在 GitHub Actions 中直接运行）
        self.email = os.getenv("AKILE_EMAIL", "").strip()
        self.password = os.getenv("AKILE_PASSWORD", "").strip()
        self.push_key = os.getenv("AKILE_PUSH_KEY", "").strip()

        # 若环境变量未配置则回退到配置文件
        if not self.email or not self.password:
            config = configparser.ConfigParser()
            config.read("config.ini", encoding="utf-8")
            self.email = self.email or config.get("akile", "email")
            self.password = self.password or config.get("akile", "password")
            self.push_key = self.push_key or config.get("akile", "push_key", fallback="")

        options = uc.ChromeOptions()
        options.add_argument("--lang=zh-CN")
        options.add_experimental_option("prefs", {"intl.accept_languages": "zh-CN,zh"})
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
        )

        # 在 CI 中显式指定 Chrome 二进制与主版本，避免多版本并存导致的版本错配
        chrome_path, chrome_major = self._get_chrome_info()
        if chrome_path:
            options.binary_location = chrome_path
            print(f"Using Chrome binary: {chrome_path} (major={chrome_major})")

        if chrome_major:
            self.browser = uc.Chrome(options=options, version_main=chrome_major)
        else:
            self.browser = uc.Chrome(options=options)

    @staticmethod
    def _get_chrome_info():
        candidates = ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"]

        for binary in candidates:
            binary_path = shutil.which(binary)
            if not binary_path:
                continue

            try:
                output = subprocess.check_output(
                    [binary_path, "--version"], stderr=subprocess.STDOUT, text=True
                ).strip()
                match = re.search(r"(\d+)\.", output)
                if match:
                    return binary_path, int(match.group(1))
            except Exception:
                continue

        return None, None

    def login(self):
        self.browser.get("https://akile.ai/")
        self.browser.maximize_window()

        # 等待弹窗加载并尝试关闭
        time.sleep(2)
        try:
            close_btn = self.browser.find_element(By.CSS_SELECTOR, '.arco-modal-close-btn, .arco-modal-close, [class*="close"]')
            close_btn.click()
            time.sleep(0.5)
        except Exception:
            pass

        # 强制移除所有可能的遮挡层
        self.browser。execute_script("""
            document.querySelectorAll('.arco-modal-wrapper, .arco-modal-mask, .arco-modal').forEach(m => m.remove());
            document.body.style.overflow = '';
        """)

        try:
            login_button = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/div/div[2]/div/div[2]/button')
                )
            )
            # 使用 JS 点击，绕过 ElementClickInterceptedException
            self.browser.execute_script("arguments[0].click();", login_button)
        except TimeoutException as e:
            print(f"登录按钮没有加载出来: {e}")
            msg = f"登录按钮没有加载出来: {e}\n签到失败"
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
            msg = f"邮箱或密码输入框没有加载出来: {e}\n签到失败"
            Notice.serverJ(self.push_key, "Akile签到", msg)
            sys.exit(1)

        try:
            submit_button = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="app"]/div[1]/div/div/div/div[1]/form/div[4]/div[1]/button')
                )
            )
            submit_button.click()
        except TimeoutException as e:
            print(f"登录按钮没有加载出来: {e}")
            msg = f"登录按钮没有加载出来: {e}\n签到失败"
            Notice.serverJ(self.push_key, "Akile签到", msg)
            sys.exit(1)

    # 签到主逻辑
    def check_in(self):
        checkin_page = "https://akile.ai/console/ak-coin-shop"
        self.browser.get(checkin_page)

        # 签到前的积分（对于已签到过的用户这个积分就是签到后的积分）
        try:
            prev_points = WebDriverWait(self.browser, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="app"]/div[1]/div[2]/div[2]/div/div[1]/div/div/div[2]')
                )
            ).text
            prev_points_num = int(prev_points.split("AK币")[0].strip())
        except TimeoutException:
            prev_points_num = -1

        # 签到
        try:
            checkin_button = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH， '//*[@id="app"]/div[1]/div[2]/div[2]/div/div[1]/div/div/div[2]/button')
                )
            )
            checkin_button.click()
            time.sleep(3)  # 防止点击签到动作未发出

            try:
                cur_points = WebDriverWait(self.browser, 10).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="app"]/div[1]/div[2]/div[2]/div/div[1]/div/div/div[2]')
                    )
                ).text
                cur_points_num = int(cur_points.split("AK币")[0].strip())

                if prev_points_num == -1:
                    msg = f"签到成功, 当前有{cur_points_num}个AK币"
                else:
                    gain = cur_points_num - prev_points_num
                    msg = f"签到成功, 获得{gain}个AK币, 当前有{cur_points_num}个AK币"

                print(msg)
                Notice.serverJ(self.push_key, "Akile签到", msg)

            except TimeoutException:
                msg = "签到成功, 但是无法获取当前AK币数量"
                print(msg)
                Notice.serverJ(self.push_key, "Akile签到", msg)
            finally:
                sys.exit(0)

        except TimeoutException:
            # 签到按钮没有加载出来，检查是否已经签到过
            try:
                WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="app"]/div[1]/div[2]/div[2]/div/div[1]/div/div/div[2]/button')
                    )
                )
                msg = f"今日已签到, 现在有{prev_points_num}AK币"
                print(msg)
                Notice.serverJ(self.push_key, "Akile签到", msg)
                sys.exit(0)
            except TimeoutException:
                msg = "签到按钮和已签到按钮都无法加载出来, 可能是网络原因, 可以等待一会再执行脚本"
                print(msg)
                Notice.serverJ(self.push_key, "Akile签到", msg)
                sys.exit(1)

    def __del__(self):
        if self.browser:
            self.browser。quit()


if __name__ == "__main__":
    akile = AkileCheckin()
    try:
        akile.login()
        time.sleep(3)  # 防止执行太快导致需要二次登录
        akile.check_in()
    finally:
        if akile.browser:
            akile.browser.quit()
