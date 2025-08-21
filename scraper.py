# scraper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

def scrape_malee_stock_price(url):
    """
    Scrapes the stock price of MALEE from the SET website.
    """
    # Options เหล่านี้จำเป็นมากสำหรับการรันในสภาพแวดล้อมที่ไม่มีหน้าจอแบบ GitHub Actions
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1920,1080") # กำหนดขนาดหน้าจอเผื่อบางเว็บจำเป็น

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    scraped_data = None
    try:
        driver.get(url)
        element_css_selector = 'div.value.text-white.mb-0.me-2.lh-1.stock-info'
        
        # เพิ่มเวลารอเป็น 20 วินาที เพื่อความแน่นอน
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, element_css_selector))
        )
        
        price_element = driver.find_element(By.CSS_SELECTOR, element_css_selector)
        price_text = price_element.text.strip()
        price = float(price_text.replace(',', ''))

        scraped_data = {
            "symbol": "MALEE",
            "price": price,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
    finally:
        driver.quit()
        return scraped_data

def save_to_file(data, filename="price.json"):
    """Saves the scraped data to a JSON file."""
    if data:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Data successfully saved to {filename}")
    else:
        print("No data to save.")

# --- Main execution block ---
if __name__ == "__main__":
    target_url = "https://www.set.or.th/th/market/product/stock/quote/MALEE/price"
    print(f"Attempting to scrape price from: {target_url}")
    
    result_data = scrape_malee_stock_price(target_url)
    
    # บันทึกผลลัพธ์ลงไฟล์ price.json แทนการ print
    save_to_file(result_data)