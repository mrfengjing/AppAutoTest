from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
import time

# 1. 配置真机和 IPA 信息（核心：Bundle ID 必须正确）
options = XCUITestOptions()
options.set_capability('udid', '你的真机UDID')          # 真机唯一标识
options.set_capability('bundleId', 'com.xxx.testapp')   # 从 IPA 提取的 Bundle ID
options.set_capability('deviceName', 'iPhone 15')       # 真机名称
options.set_capability('platformVersion', '17.0')       # 真机 iOS 版本
options.set_capability('noReset', True)                 # 不重置 App 状态
# 关键：无源码时禁用 XCTest 源码依赖
options.set_capability('usePrebuiltWDA', True)          # 使用预编译的 WebDriverAgent
options.set_capability('skipDeviceInitialization', True)# 跳过设备初始化（加速）

# 2. 连接 Appium 服务
driver = webdriver.Remote('http://localhost:4723/wd/hub', options=options)

try:
    # 3. 无源码场景的元素定位（核心适配）
    # 场景1：通过 XPath 定位（根据控件类型+文本）
    # 示例：定位“登录”按钮（文本为“登录”的按钮）
    login_btn = driver.find_element(
        AppiumBy.XPATH,
        '//XCUIElementTypeButton[@name="登录"]'
    )
    login_btn.click()
    time.sleep(2)

    # 场景2：通过坐标定位（万不得已时用，稳定性差）
    # 示例：点击屏幕 (200, 600) 位置（需根据真机分辨率调整）
    # driver.tap([(200, 600)], 100)

    # 场景3：通过 Class Name 定位（适合同类控件）
    # 示例：获取所有文本控件，筛选目标内容
    text_elems = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeStaticText')
    for elem in text_elems:
        if elem.text == '首页':
            print('登录成功，跳转到首页！')
            break

except Exception as e:
    print(f'测试失败：{e}')
finally:
    # 4. 关闭驱动
    driver.quit()