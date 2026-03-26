import sys

from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from  appium.webdriver.mobilecommand import MobileCommand
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
APP_BUNDLE_ID="dadong.smartlock.com"

# 1. 配置真机和 IPA 信息（核心：Bundle ID 必须正确）
options = XCUITestOptions()
# options.set_capability('udid', '你的真机UDID')          # 真机唯一标识
# options.set_capability('bundleId', 'com.xxx.testapp')   # 从 IPA 提取的 Bundle ID
# options.set_capability('deviceName', 'iPhone 15')       # 真机名称
# options.set_capability('platformVersion', '17.0')       # 真机 iOS 版本
# options.set_capability('noReset', True)                 # 不重置 App 状态
# # 关键：无源码时禁用 XCTest 源码依赖
# options.set_capability('usePrebuiltWDA', True)          # 使用预编译的 WebDriverAgent
# options.set_capability('skipDeviceInitialization', True)# 跳过设备初始化（加速）

# options.set_capability("platformName","iOS")
# options.set_capability("appium:automationName","XCUITest")
# 2. 连接 Appium 服务
# 手机运行的端口是8100 driver不要直连手机/localhost:8100，否则driver command将无法发送
# driver = webdriver.Remote('http://localhost:8100', options=options)
# driver应该连接Appium 服务，使用appium指令启用appium服务，appium运行在4723端口
driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
driver.start_session(options)

button_clicked=[]

def command_test():
    try:
        # driver.activate_app(APP_BUNDLE_ID)
        # driver.execute_script('mobile: activateApp', {'appId': APP_BUNDLE_ID})

        print(f"driver.get_status: {driver.get_status()}")
        print(f"driver.orientation: {driver.orientation}")
        print(f"driver.query_app_state: {driver.query_app_state(APP_BUNDLE_ID)}")
        print(f"driver.touch_id: {driver.touch_id(True)}")
        driver.shake()
        # print(f"driver.app_strings: {driver.app_strings()}")
        # print(f"driver.get_log: {driver.get_log("client") }")

        # driver.get_log("client")
        # driver.back()
        # driver.activate_app(APP_BUNDLE_ID)
        # time.sleep(3)
        print(f"driver.terminate_app: {driver.terminate_app(APP_BUNDLE_ID)}")
        print(f"driver.is_app_installed: {driver.is_app_installed(APP_BUNDLE_ID)}")
        print(f"driver.background_app: {driver.background_app(3)}")

        # time.sleep(3)
        # driver.activate_app(APP_BUNDLE_ID)
        driver.remove_app(APP_BUNDLE_ID)
        # driver.install_app("/Users/smwl/Desktop/Projects/AppAutoTest/workplace/Payload.ipa")
        # driver.close()

    except Exception as e:
        print(f"\nException:\n{e}")


def click_button():
    all_elements = driver.find_elements(AppiumBy.XPATH, "//*")
    for index, element in enumerate(all_elements, 1):
        if element.text in ["Safari浏览器"]:
            driver.activate_app(APP_BUNDLE_ID)
            break
        # print(f"element:{element}")
        # print(f"element.id: {element.id} element.session_i: {element.session_id}")
        element_type = element.get_attribute("type")  # 元素类型（如 XCUIElementTypeButton）
        # element_text = element.text or "无文本"  # 元素文本
        # element_label = element.get_attribute("label") or "无Label"  # 元素 Label
        # print(f"[{index}] 类型: {element_type}")
        # print(f"    文本: {element_text}")
        # print(f"    Label: {element_label}\n")
        if element_type == "XCUIElementTypeButton" and element.id not in button_clicked:
            print(f"element.id: {element.id} element.session_i: {element.session_id} element.text: {element.text}")
            element.click()
            button_clicked.append(element.id)
            break
    else:
        print(f" all_elements:{all_elements}")

    # WebDriverWait(driver, 3).until(
    #     lambda d: d.execute_script("mobile: activeAppInfo")["bundleId"] != YOUR_APP_BUNDLE_ID
    # )
    time.sleep(3)

    # print(f"TOUCH_ID: {driver.execute(MobileCommand.TOUCH_ID)}")


    # 3. 如果跳转，立即激活原应用
    # print("检测到外部跳转，正在返回原应用...")
    # driver.execute_script("mobile: activateApp", {"bundleId": YOUR_APP_BUNDLE_ID})
    if len(button_clicked) > 10:
        return
    click_button()
# click_button()
command_test()

sys.exit(0)
try:
    print(f"get_status => {driver.get_status()}")
    all_elements = driver.find_elements(AppiumBy.XPATH, "//*")
    print(f"all_elements=>\n{all_elements}")
    for index,element in enumerate(all_elements, 1):
        # print(f"element:{element}")
        element_type = element.get_attribute("type")  # 元素类型（如 XCUIElementTypeButton）
        element_text = element.text or "无文本"  # 元素文本
        element_label = element.get_attribute("label") or "无Label"  # 元素 Label
        print(f"[{index}] 类型: {element_type}")
        print(f"    文本: {element_text}")
        print(f"    Label: {element_label}\n")
        if element_type == "XCUIElementTypeButton":
            element.click()
            # break

    # 3. 无源码场景的元素定位（核心适配）
    # 场景1：通过 XPath 定位（根据控件类型+文本）
    # 示例：定位“登录”按钮（文本为“登录”的按钮）
    # login_btn = driver.find_element(
    #     AppiumBy.XPATH,
    #     '//XCUIElementTypeButton[@name="登录"]'
    # )
    # login_btn.click()
    # time.sleep(2)

    # 场景2：通过坐标定位（万不得已时用，稳定性差）
    # 示例：点击屏幕 (200, 600) 位置（需根据真机分辨率调整）
    # driver.tap([(200, 600)], 100)

    # 场景3：通过 Class Name 定位（适合同类控件）
    # 示例：获取所有文本控件，筛选目标内容
    # text_elems = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeStaticText')
    # for elem in text_elems:
    #     if elem.text == '首页':
    #         print('登录成功，跳转到首页！')
    #         break

except Exception as e:
    print(f'测试失败：{e}')
finally:
    # 4. 关闭驱动
    driver.quit()