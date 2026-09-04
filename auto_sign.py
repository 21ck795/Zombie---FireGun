# -*- coding: utf-8 -*-
"""
批量自动签到脚本
目标网站: https://web.xjskp.vip:6688/pay/login
流程: 打开登录页 -> 输入账号密码 -> 选择区组 -> 登录 -> 点每日签到 -> 点立即签到

依赖安装:
    pip install selenium webdriver-manager

使用方法:
    1. 在下方 ACCOUNTS 列表中填入你的账号和密码
    2. 在 SERVERS 中指定要签到的区组（默认一区到七区全部）
    3. 运行: python auto_sign.py
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)

# ============================================================
#  配置区 —— 请修改这里
# ============================================================

# 账号列表：每个元素是 (账号, 密码)
ACCOUNTS = [
    ("13734329300", "9907967"),
    ("13734329311", "9907967"),
    ("13734329322", "9907967"),
    ("13734329333", "9907967"),
    ("13734329344", "9907967"),
    ("13734329355", "9907967"),
    ("13734329366", "9907967"),
    ("13734329699", "9907967"),
    ("13734329658", "9907967"),
    ("13734329668", "9907967"),
    ("13734329637", "9907967"),
    ("13734329636", "9907967"),
    ("13734329635", "9907967"),
    ("13734329634", "9907967"),
    ("13734329633", "9907967"),
    ("13734329632", "9907967"),
    ("13734329631", "9907967"),
    ("13734329630", "9907967"),
    ("13734329649", "9907967"),
    ("13734329648", "9907967"),
    ("13734329622", "9907967"),
    ("13734329623", "9907967"),
    ("13734329624", "9907967"),
    ("13734329625", "9907967"),
    ("13734329626", "9907967"),
    ("13734329627", "9907967"),
    ("13734329628", "9907967"),
    ("13734329411", "9907967"),
    ("13734329412", "9907967"),
    ("13734329413", "9907967"),
    ("13734329414", "9907967"),
    ("13734329415", "9907967"),
    ("13734329416", "9907967"),
    ("13734329417", "9907967"),
    ("13734329418", "9907967"),
    ("13734329419", "9907967"),
    ("13734329420", "9907967"),
    ("13734329421", "9907967"),
    ("13734329422", "9907967"),
    ("13734329423", "9907967"),
    ("13734329424", "9907967"),
    ("13734329425", "9907967"),
    ("13734329426", "9907967"),
    ("13734329427", "9907967"),
    ("13734329428", "9907967"),
    ("13734329429", "9907967"),
    ("13734329430", "9907967"),
    ("13734329431", "9907967"),
    ("13734329432", "9907967"),
    ("13734329433", "9907967"),
    ("13734329434", "9907967"),
    ("13734329435", "9907967"),
    ("13734329436", "9907967"),
    ("13734329437", "9907967"),
    ("13734329438", "9907967"),
    ("13734329439", "9907967"),
    ("13734329440", "9907967"),
    # 继续添加更多账号...
]

# 需要签到的区组（默认全部七个区，不需要的删掉即可）
SERVERS = ["一区", "二区", "三区", "四区", "五区", "六区", "七区"]

# 登录页 URL
LOGIN_URL = "https://web.xjskp.vip:6688/pay/login"

# 每步操作的等待超时（秒）
TIMEOUT = 15

# 每个账号签到完成后间隔（秒），避免请求过快
ACCOUNT_INTERVAL = 3

# 每个区组之间间隔（秒）
SERVER_INTERVAL = 2

# 是否以无头模式运行（True=不显示浏览器窗口，False=显示窗口方便观察）
HEADLESS = False

# ============================================================
#  日志配置
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("auto_sign")


# ============================================================
#  浏览器初始化
# ============================================================

def create_driver():
    """创建并返回 Chrome 浏览器实例"""
    chrome_options = Options()
    if HEADLESS:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,900")
    # 忽略证书错误（目标网站用的是自签名证书）
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-insecure-localhost")

    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        logger.warning(f"webdriver-manager 自动下载失败({e})，尝试使用系统已安装的 chromedriver")
        driver = webdriver.Chrome(options=chrome_options)

    driver.implicitly_wait(5)
    return driver


# ============================================================
#  核心操作函数
# ============================================================

def wait_and_click(driver, by, value, timeout=TIMEOUT, description=""):
    """等待元素可点击并点击"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        element.click()
        logger.info(f"  ✓ 点击: {description or value}")
        return True
    except TimeoutException:
        logger.warning(f"  ✗ 超时未找到可点击元素: {description or value}")
        return False
    except ElementClickInterceptedException:
        # 尝试用 JS 点击
        try:
            element = driver.find_element(by, value)
            driver.execute_script("arguments[0].click();", element)
            logger.info(f"  ✓ JS点击: {description or value}")
            return True
        except Exception:
            logger.warning(f"  ✗ 点击被拦截: {description or value}")
            return False


def wait_and_input(driver, by, value, text, timeout=TIMEOUT, description=""):
    """等待元素可见并输入文本"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )
        element.clear()
        element.send_keys(text)
        logger.info(f"  ✓ 输入: {description or value}")
        return True
    except TimeoutException:
        logger.warning(f"  ✗ 超时未找到输入框: {description or value}")
        return False


def select_server(driver, server_name):
    """选择区组（下拉框）"""
    # 先点击下拉框展开
    if not wait_and_click(driver, By.XPATH, "//select", description="区组下拉框"):
        # 尝试通过 placeholder 或 class 定位
        try:
            dropdown = driver.find_element(By.XPATH, "//*[contains(@class,'select') or contains(@class,'dropdown')]")
            dropdown.click()
        except NoSuchElementException:
            logger.warning("  ✗ 未找到区组下拉框")
            return False

    time.sleep(0.5)

    # 选择对应区组
    option_xpath = f"//option[contains(text(),'{server_name}')]"
    if not wait_and_click(driver, By.XPATH, option_xpath, description=f"选择{server_name}"):
        # 尝试用 Select 类
        try:
            from selenium.webdriver.support.ui import Select
            select = Select(driver.find_element(By.TAG_NAME, "select"))
            select.select_by_visible_text(server_name)
            logger.info(f"  ✓ Select类选择: {server_name}")
            return True
        except Exception:
            logger.warning(f"  ✗ 无法选择{server_name}")
            return False
    return True


def login(driver, account, password, server):
    """执行登录操作"""
    logger.info(f"  → 打开登录页...")
    driver.get(LOGIN_URL)
    time.sleep(2)

    # 输入账号
    if not wait_and_input(driver, By.XPATH, "//input[@placeholder='请输入用户名']", account, description="账号"):
        # 备用定位方式
        wait_and_input(driver, By.XPATH, "//input[1]", account, description="账号(备用)")

    # 输入密码
    if not wait_and_input(driver, By.XPATH, "//input[@placeholder='请输入密码']", password, description="密码"):
        wait_and_input(driver, By.XPATH, "//input[2]", password, description="密码(备用)")

    # 选择区组
    select_server(driver, server)
    time.sleep(0.5)

    # 点击登录按钮（尝试多种定位）
    login_clicked = False
    for btn_text in ["登录", "登 录", "立即登录", "确认登录"]:
        if wait_and_click(driver, By.XPATH, f"//button[contains(text(),'{btn_text}')]", description=f"登录按钮({btn_text})"):
            login_clicked = True
            break
        if wait_and_click(driver, By.XPATH, f"//*[contains(@class,'btn') and contains(text(),'{btn_text}')]", description=f"登录按钮(class)"):
            login_clicked = True
            break

    if not login_clicked:
        # 最后尝试：页面上最后一个按钮
        wait_and_click(driver, By.XPATH, "//button[last()]", description="登录按钮(末位)")

    # 等待登录成功（检测是否跳转到商城页或出现"每日签到"按钮）
    time.sleep(3)
    try:
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'每日签到')]"))
        )
        logger.info(f"  ✓ 登录成功 [{account} / {server}]")
        return True
    except TimeoutException:
        # 检查是否有错误提示
        try:
            error_el = driver.find_element(By.XPATH, "//*[contains(@class,'error') or contains(@class,'tip') or contains(@class,'message')]")
            logger.warning(f"  ✗ 登录可能失败: {error_el.text}")
        except NoSuchElementException:
            logger.warning(f"  ✗ 登录后未检测到商城页，可能登录失败或页面加载慢")
        return False


def do_daily_sign(driver):
    """执行每日签到：点每日签到 -> 点立即签到"""
    # 第一步：点击"每日签到"按钮
    if not wait_and_click(driver, By.XPATH, "//*[contains(text(),'每日签到')]", description="每日签到按钮"):
        logger.warning("  ✗ 未找到每日签到按钮")
        return False

    time.sleep(2)

    # 第二步：检查今日状态，如果已签到则跳过
    try:
        status_el = driver.find_element(By.XPATH, "//*[contains(text(),'今日状态')]/following-sibling::* | //*[contains(text(),'已签到')]")
        if "已签到" in status_el.text:
            logger.info(f"  ℹ 今日已签到，跳过")
            return True
    except NoSuchElementException:
        pass

    # 第三步：点击"立即签到"按钮
    if not wait_and_click(driver, By.XPATH, "//*[contains(text(),'立即签到')]", description="立即签到按钮"):
        logger.warning("  ✗ 未找到立即签到按钮")
        return False

    time.sleep(2)
    logger.info(f"  ✓ 签到完成")
    return True


def logout_or_reset(driver):
    """签到完成后，清除登录状态以便下一个账号登录"""
    # 清除 localStorage 和 sessionStorage
    try:
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
    except Exception:
        pass
    # 删除所有 cookies
    driver.delete_all_cookies()
    time.sleep(1)


# ============================================================
#  主流程
# ============================================================

def main():
    logger.info("=" * 60)
    logger.info("批量自动签到脚本启动")
    logger.info(f"账号数量: {len(ACCOUNTS)} | 区组数量: {len(SERVERS)}")
    logger.info(f"区组列表: {', '.join(SERVERS)}")
    logger.info("=" * 60)

    if not ACCOUNTS or ACCOUNTS[0][0] == "你的账号1":
        logger.error("请先在脚本顶部 ACCOUNTS 中填入真实账号密码！")
        return

    driver = create_driver()
    success_count = 0
    fail_count = 0

    try:
        for idx, (account, password) in enumerate(ACCOUNTS, 1):
            logger.info("")
            logger.info(f"{'='*60}")
            logger.info(f"处理账号 [{idx}/{len(ACCOUNTS)}]: {account}")
            logger.info(f"{'='*60}")

            for server in SERVERS:
                logger.info(f"")
                logger.info(f"  --- {account} @ {server} ---")

                try:
                    # 登录
                    if not login(driver, account, password, server):
                        fail_count += 1
                        logout_or_reset(driver)
                        time.sleep(SERVER_INTERVAL)
                        continue

                    # 签到
                    if do_daily_sign(driver):
                        success_count += 1
                    else:
                        fail_count += 1

                except Exception as e:
                    logger.error(f"  ✗ 异常: {type(e).__name__}: {e}")
                    fail_count += 1

                # 重置状态，准备下一个区组
                logout_or_reset(driver)
                time.sleep(SERVER_INTERVAL)

            # 账号之间间隔
            if idx < len(ACCOUNTS):
                logger.info(f"  等待 {ACCOUNT_INTERVAL} 秒后处理下一个账号...")
                time.sleep(ACCOUNT_INTERVAL)

    except KeyboardInterrupt:
        logger.info("\n用户中断执行")
    except Exception as e:
        logger.error(f"致命错误: {e}")
    finally:
        driver.quit()
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"全部完成！成功: {success_count} | 失败: {fail_count}")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()
