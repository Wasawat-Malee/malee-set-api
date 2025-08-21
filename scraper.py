# scraper.py (เวอร์ชันอัปเดต เพิ่ม Change และ % Change)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
from datetime import datetime
import pytz

def scrape_malee_stock_price(url):
    """
    Scrapes the stock price and change data of MALEE from the SET website.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    scraped_data = None
    try:
        driver.get(url)
        
        # --- CSS Selectors สำหรับข้อมูลทั้งหมด ---
        price_selector = 'div.value.text-white.mb-0.me-2.lh-1.stock-info'
        # Selector สำหรับ h3 ที่ครอบข้อมูล change ทั้งหมด
        change_container_selector = 'h3.d-flex.mb-0.pb-2'

        # --- รอให้ element หลักปรากฏขึ้นก่อน ---
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, price_selector))
        )
        
        # --- ดึงข้อมูลราคา (เหมือนเดิม) ---
        price_element = driver.find_element(By.CSS_SELECTOR, price_selector)
        price_text = price_element.text.strip()
        price = float(price_text.replace(',', ''))

        # --- [เพิ่ม] ดึงค่า Change และ Percent Change ---
        change_container = driver.find_element(By.CSS_SELECTOR, change_container_selector)
        # ดึงค่า change จาก span ตัวแรก
        change_value_text = change_container.find_element(By.CSS_SELECTOR, 'span:nth-of-type(1)').text.strip()
        # ดึงค่า percent change จาก span ตัวที่สอง
        percent_change_text = change_container.find_element(By.CSS_SELECTOR, 'span:nth-of-type(2)').text.strip()

        # --- [เพิ่ม] ทำความสะอาดและแปลงข้อมูล ---
        change_value = float(change_value_text)
        # ลบวงเล็บและเครื่องหมาย % แล้วแปลงเป็น float
        percent_change_value = float(percent_change_text.replace('(', '').replace(')', '').replace('%', ''))
        
        # --- จัดการเรื่องเวลา (เหมือนเดิม) ---
        bkk_timezone = pytz.timezone('Asia/Bangkok')
        utc_now = datetime.now(pytz.utc)
        bkk_now = utc_now.astimezone(bkk_timezone)
        formatted_timestamp = bkk_now.strftime("%Y-%m-%d %H:%M:%S")

        # --- [อัปเดต] เพิ่มข้อมูลใหม่ลงใน Dictionary ---
        scraped_data = {
            "symbol": "MALEE",
            "price": price,
            "change": change_value,           # <-- เพิ่มเข้ามา
            "percent_change": percent_change_value, # <-- เพิ่มเข้ามา
            "timestamp": formatted_timestamp
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
    
    save_to_file(result_data)
