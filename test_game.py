# nolint start: line_length_linter, trailing_whitespace_linter, indentation_linter, object_name_linter.

import os
import time
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

async def test_insurance_game():
    """Test the Insurance Simulation Game running in the browser."""
    # Create test directories
    os.makedirs('test_screenshots', exist_ok=True)
    
    # Set up headless Chrome
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--window-size=1280,720')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Test 1: Load the game
        print("Test 1: Loading the game...")
        driver.get("http://localhost:8000")
        
        # Wait for canvas to load
        await asyncio.sleep(5)
        driver.save_screenshot("test_screenshots/test1_load_game.png")
        print("Screenshot saved: test1_load_game.png")
        
        # Test 2: Startup screen interaction - click on canvas and type company name
        print("Test 2: Interacting with startup screen...")
        canvas = driver.find_element(By.TAG_NAME, "canvas")
        actions = ActionChains(driver)
        
        # Click in center of canvas
        actions.move_to_element(canvas).click().perform()
        await asyncio.sleep(1)
        
        # Type company name
        actions.send_keys("Test Insurance Co").perform()
        await asyncio.sleep(1)
        
        # Click on California button (approximate position)
        canvas_width = canvas.size['width']
        canvas_height = canvas.size['height']
        x_pos = canvas_width * 0.3
        y_pos = canvas_height * 0.5
        actions.move_to_element_with_offset(canvas, x_pos, y_pos).click().perform()
        await asyncio.sleep(1)
        
        # Click on Start Game button (approximate position)
        x_pos = canvas_width * 0.5
        y_pos = canvas_height * 0.7
        actions.move_to_element_with_offset(canvas, x_pos, y_pos).click().perform()
        
        # Wait for game to initialize
        await asyncio.sleep(3)
        driver.save_screenshot("test_screenshots/test2_startup.png")
        print("Screenshot saved: test2_startup.png")
        
        # Test 3: Navigation
        print("Test 3: Testing navigation...")
        
        # Click on Investments button (approximate position)
        x_pos = canvas_width * 0.3
        y_pos = canvas_height * 0.05
        actions.move_to_element_with_offset(canvas, x_pos, y_pos).click().perform()
        await asyncio.sleep(2)
        driver.save_screenshot("test_screenshots/test3_investments.png")
        print("Screenshot saved: test3_investments.png")
        
        # Click on Reports button (approximate position)
        x_pos = canvas_width * 0.5
        y_pos = canvas_height * 0.05
        actions.move_to_element_with_offset(canvas, x_pos, y_pos).click().perform()
        await asyncio.sleep(2)
        driver.save_screenshot("test_screenshots/test4_reports.png")
        print("Screenshot saved: test4_reports.png")
        
        # Test 4: End turn
        print("Test 4: Testing end turn...")
        
        # Click on End Turn button (approximate position)
        x_pos = canvas_width * 0.8
        y_pos = canvas_height * 0.05
        actions.move_to_element_with_offset(canvas, x_pos, y_pos).click().perform()
        await asyncio.sleep(3)
        driver.save_screenshot("test_screenshots/test5_end_turn.png")
        print("Screenshot saved: test5_end_turn.png")
        
        # Click anywhere to close the summary popup
        actions.move_to_element_with_offset(canvas, canvas_width * 0.5, canvas_height * 0.5).click().perform()
        await asyncio.sleep(1)
        driver.save_screenshot("test_screenshots/test6_after_turn.png")
        print("Screenshot saved: test6_after_turn.png")
        
        print("All tests completed successfully!")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    asyncio.run(test_insurance_game()) 