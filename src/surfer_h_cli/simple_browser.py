from io import BytesIO
import time

from PIL import Image
from pydantic import BaseModel
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait


def chrome_viewport_size(driver: Chrome) -> tuple[int, int]:
    """Get viewport size of chrome browser"""

    return tuple(driver.execute_script("return [window.innerWidth, window.innerHeight];"))


def resize_chrome(driver: Chrome, width: int, height: int):
    """Resize a selenium chromedriver window."""
    current_width, current_height = chrome_viewport_size(driver)
    if width != current_width or height != current_height:
        driver.set_window_size(width, height)
        current_width, current_height = chrome_viewport_size(driver)
        driver.set_window_size(width + width - current_width, height + height - current_height)


class Tab:
    """Tab object."""

    def __init__(self, index: str) -> None:
        """Build a tab with an index."""
        self.index = index


class WebTabs(BaseModel):
    titles: list[str]


class WebException(Exception):
    """Custom exception for web-related errors"""

    pass


class SimpleWebBrowserTools:
    """Selenium-based web environment for executing web actions"""

    def __init__(self):
        """
        Initialize the Selenium web environment

        Args:
            headless: Whether to run browser in headless mode
            wait_timeout: Default timeout for waiting operations
        """

    def open_browser(self, headless: bool, width: int, height: int, action_timeout: int, **kwargs):
        """Setup the Selenium WebDriver"""
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={width},{height}")
        options.add_argument("--force-device-scale-factor=1")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")

        try:
            self.driver = Chrome(options=options)
            self.wait = WebDriverWait(self.driver, action_timeout)
            self.headless = headless
            self.width = width
            self.height = height
            self.action_timeout = action_timeout

            resize_chrome(self.driver, self.width, self.height)

        except Exception as e:
            raise WebException(f"Failed to initialize WebDriver: {e}")

    def get_screenshot_size(self) -> tuple[int, int]:
        """Get the size of the current screenshot/viewport"""
        assert self.driver

        size = self.driver.get_window_size()
        return size["width"], size["height"]

    def get_tab_url(self) -> str:
        return self.driver.current_url

    def get_tabs(self) -> list[Tab]:
        """Return description of the tabs   opened with the current tab being focused."""
        return [Tab(index=handle) for handle in self.driver.window_handles]

    def get_tabs_titles(self) -> WebTabs:
        return WebTabs(titles=self.driver.window_handles)

    @staticmethod
    def find_newer_tab(previous_tabs: list[Tab], new_tabs: list[Tab]) -> Tab:
        """Find one newer tab from the previous tabs"""
        assert len(new_tabs) > len(previous_tabs)
        previous_indexes = [tab.index for tab in previous_tabs]
        for tab in new_tabs[-1::-1]:
            if tab.index not in previous_indexes:
                return tab
        raise WebException("No newer tab found")

    def click_at(self, x: int, y: int):
        """Click at specific coordinates"""
        assert self.driver
        
        # Check for alerts and accept them first
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            time.sleep(0.2)
        except:
            pass
        
        # Find element at coordinates
        element = self.driver.execute_script(f"return document.elementFromPoint({x}, {y});")
        if element:
            # Debug: print what element we found
            tag = element.tag_name
            elem_id = element.get_attribute('id')
            elem_class = element.get_attribute('class')
            placeholder = element.get_attribute('placeholder')
            print(f"🔍 DEBUG: Clicking at ({x}, {y}) -> <{tag}> id='{elem_id}' class='{elem_class}' placeholder='{placeholder}'")
            
            # Check if it's a submit button - trigger form submission directly
            tag_name = element.tag_name.lower()
            element_type = element.get_attribute('type')
            
            if tag_name == 'button' and (element_type == 'submit' or not element_type):
                # Find the form and trigger submit event
                self.driver.execute_script("""
                    var button = arguments[0];
                    var form = button.closest('form');
                    if (form) {
                        // Trigger the form's onsubmit handler if it exists
                        if (form.onsubmit) {
                            var event = new Event('submit', {bubbles: true, cancelable: true});
                            form.dispatchEvent(event);
                        } else {
                            form.submit();
                        }
                    } else {
                        button.click();
                    }
                """, element)
                time.sleep(0.5)
                return
            
            # Regular click for non-submit elements
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.1)
            try:
                element.click()
            except:
                self.driver.execute_script("arguments[0].click();", element)
                time.sleep(0.1)

    def write(self, text: str, n_backspaces: int = 0):
        """Write text, optionally clearing with backspaces first"""
        assert self.driver
        
        # Check for alerts and accept them
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except:
            pass
        
        active_element = self.driver.switch_to.active_element
        
        # If no element is focused or it's the body, we failed to click on an input
        if active_element is None or active_element.tag_name.lower() == 'body':
            print(f"⚠️  WARNING: No input field is focused! Cannot write text.")
            return
        
        # Verify we're on an input or textarea
        if active_element.tag_name.lower() not in ['input', 'textarea']:
            print(f"⚠️  WARNING: Focused element is <{active_element.tag_name}>, not an input field!")
            return
        
        # Clear the field first using Selenium's clear method
        try:
            active_element.clear()
        except:
            pass
        
        active_element.send_keys(text)

    def scroll(self, direction: str):
        """Scroll the page in the specified direction"""

        assert self.driver
        body = self.driver.find_element(By.TAG_NAME, "body")
        if direction == "down":
            body.send_keys(Keys.PAGE_DOWN)
        elif direction == "up":
            body.send_keys(Keys.PAGE_UP)
        elif direction == "left":
            body.send_keys(Keys.ARROW_LEFT)
        elif direction == "right":
            body.send_keys(Keys.ARROW_RIGHT)
        else:
            raise WebException(f"Invalid scroll direction: {direction}")

    def goback(self):
        """Navigate back to previous page"""
        assert self.driver
        self.driver.back()

    def goto(self, url: str):
        """Navigate to a specific URL"""
        assert self.driver
        self.driver.get(url)

    def change_tab(self, title: str):
        """Switch to tab with specific title"""
        assert self.driver

        try:
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                if self.driver.title == title:
                    return

        except Exception as e:
            raise WebException(f"Failed to change tab: {e}")

    def focus_tab(self, element: str):
        """Focus on a tab (using element as identifier)"""
        self.change_tab(element)

    def quit(self):
        """Quit the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None

    def refresh(self):
        """Refresh the current page"""
        assert self.driver
        self.driver.refresh()

    def restart(self):
        """Restart the browser"""
        self.quit()
        if not hasattr(self, "headless"):
            raise ValueError("Browser not initialized")
        self.open_browser(
            headless=self.headless, width=self.width, height=self.height, action_timeout=self.action_timeout
        )

    def screenshot(self) -> Image.Image:
        assert self.driver
        screenshot = self.driver.get_screenshot_as_png()

        bytestream = BytesIO(screenshot)
        bytestream.seek(0)
        return Image.open(bytestream)

    def get_webpage(self) -> tuple[str, Image.Image]:
        assert self.driver is not None
        url = self.get_tab_url()
        screenshot = self.screenshot()
        return url, screenshot
