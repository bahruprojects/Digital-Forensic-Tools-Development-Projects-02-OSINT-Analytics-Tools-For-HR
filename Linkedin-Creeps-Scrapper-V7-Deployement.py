# Linkedin-Creeps-Scrapper-V7 (Buat Github)

import os
import time
import random
import json
import csv
import logging
from zipfile import ZipFile
from urllib.parse import urljoin, urlparse
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pdfkit
from PIL import Image
import io

class LinkedInScraperPro:
    def __init__(self, profile_url, email=None, password=None, headless=False, max_scrolls=15):
        """
        Initialize LinkedIn Creeps Scraper
        
        Parameters:
            profile_url (str): LinkedIn profile URL
            email (str, optional): Email for login
            password (str, optional): Password for login
            headless (bool): Run browser in headless mode
            max_scrolls (int): Maximum scroll attempts to load content
        """
        self.profile_url = self._validate_url(profile_url)
        self.email = email
        self.password = password
        self.headless = headless
        self.max_scrolls = max_scrolls
        self.data_dir = "linkedin_data"
        self.driver = None
        self.wait_time = random.uniform(2, 5)
        self.max_retries = 3
        self.logger = self._setup_logging()
        
        # Create data directory
        os.makedirs(self.data_dir, exist_ok=True)

    def _setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.data_dir, 'scraper.log')),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

    def _validate_url(self, url):
        """Validate and normalize LinkedIn profile URL"""
        if not url:
            raise ValueError("Profile URL cannot be empty")
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        parsed = urlparse(url)
        if 'linkedin.com' not in parsed.netloc:
            raise ValueError("URL must be a valid LinkedIn profile")
            
        return url.rstrip('/')

    def start_driver(self):
        """Initialize WebDriver with optimal configuration"""
        try:
            options = webdriver.ChromeOptions()
            
            # Basic configuration
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Stability settings
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            
            # Natural user agent
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            if self.headless:
                options.add_argument("--headless=new")
            else:
                options.add_argument("--start-maximized")
            
            # Automatic ChromeDriver installation
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Set implicit wait
            self.driver.implicitly_wait(10)
            
            # Hide webdriver
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("WebDriver initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise

    def linkedin_login(self):
        """Login to LinkedIn with improved error handling"""
        if not self.email or not self.password:
            self.logger.info("No login credentials provided")
            return False
        
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Attempting LinkedIn login (attempt {attempt + 1})")
                self.driver.get("https://www.linkedin.com/login")
                
                # Wait for page to load
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                
                # Input credentials
                email_field = self.driver.find_element(By.ID, "username")
                email_field.clear()
                email_field.send_keys(self.email)
                
                password_field = self.driver.find_element(By.ID, "password")
                password_field.clear()
                password_field.send_keys(self.password)
                
                # Click login button
                login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                login_button.click()
                
                # Wait for successful login or CAPTCHA
                try:
                    WebDriverWait(self.driver, 20).until(
                        lambda driver: "/feed/" in driver.current_url or "/challenge/" in driver.current_url
                    )
                    
                    if "/challenge/" in self.driver.current_url:
                        self.logger.warning("CAPTCHA or additional verification required. Please complete manually.")
                        input("Press Enter after completing verification...")
                    
                    # Verify login success
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search' or @placeholder='Cari']"))
                    )
                    
                    self.logger.info("Login successful!")
                    time.sleep(random.uniform(2, 4))
                    return True
                    
                except TimeoutException:
                    self.logger.warning("Login may have failed or requires additional verification")
                    continue
                    
            except Exception as e:
                self.logger.error(f"Login failed (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    return False
                time.sleep(random.uniform(3, 6))
        
        return False

    def safe_find_elements(self, by, value, timeout=15, parent=None):
        """Find elements with error handling"""
        try:
            if parent:
                WebDriverWait(parent, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
                return parent.find_elements(by, value)
            else:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
                return self.driver.find_elements(by, value)
        except TimeoutException:
            self.logger.warning(f"Elements not found: {value}")
            return []
        except Exception as e:
            self.logger.error(f"Error while finding elements: {str(e)}")
            return []

    def safe_get_text(self, element):
        """Get element text with error handling"""
        try:
            return element.text.strip()
        except Exception:
            return ""

    def safe_get_attribute(self, element, attribute):
        """Get element attribute with error handling"""
        try:
            return element.get_attribute(attribute)
        except Exception:
            return ""

    def scroll_page(self, scroll_pause_time=1, max_scrolls=None):
        """Scroll page to load more content"""
        max_scrolls = max_scrolls or self.max_scrolls
        self.logger.info(f"Scrolling page (max {max_scrolls} times)...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        no_change_count = 0
        
        while scrolls < max_scrolls and no_change_count < 3:
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            
            # Calculate new height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                no_change_count += 1
                # Try clicking "See more" button if available
                try:
                    see_more_buttons = self.safe_find_elements(
                        By.XPATH, 
                        "//button[contains(@aria-label, 'Lihat selengkapnya') or contains(@aria-label, 'See more')]",
                        timeout=2
                    )
                    if see_more_buttons:
                        see_more_buttons[0].click()
                        time.sleep(2)
                except:
                    pass
            else:
                no_change_count = 0
                
            last_height = new_height
            scrolls += 1
            
            # Random delay to avoid bot detection
            time.sleep(random.uniform(0.5, 2))

    def save_profile_as_pdf(self):
        """Save profile as PDF with HTML fallback"""
        try:
            self.logger.info("Saving profile as PDF...")
            pdf_path = os.path.join(self.data_dir, "profile.pdf")
            
            # PDF configuration
            try:
                config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
            except:
                config = None
            
            options = {
                'quiet': '',
                'page-size': 'A4',
                'margin-top': '0mm',
                'margin-right': '0mm',
                'margin-bottom': '0mm',
                'margin-left': '0mm',
                'encoding': "UTF-8",
            }
            
            # Use HTML as fallback if PDF fails
            try:
                if config:
                    pdfkit.from_url(self.profile_url, pdf_path, configuration=config, options=options)
                    self.logger.info(f"Profile PDF saved: {pdf_path}")
                else:
                    raise Exception("wkhtmltopdf not configured")
            except Exception as e:
                self.logger.warning(f"Failed to save PDF, switching to HTML: {str(e)}")
                html_content = self.driver.page_source
                html_path = os.path.join(self.data_dir, "profile.html")
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                self.logger.info(f"Profile HTML saved: {html_path}")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to save profile: {str(e)}")
            return False

    def scrape_basic_profile_info(self):
        """Scrape basic profile information"""
        try:
            self.logger.info("Collecting basic profile info...")
            self.driver.get(self.profile_url)
            time.sleep(self.wait_time)
            
            profile_info = {}
            
            # Name
            name_element = self.safe_find_elements(By.XPATH, "//h1[contains(@class, 'text-heading-xlarge')]")[0]
            profile_info['name'] = self.safe_get_text(name_element)
            
            # Headline/Title
            headline_element = self.safe_find_elements(By.XPATH, "//div[contains(@class, 'text-body-medium')]")[0]
            profile_info['headline'] = self.safe_get_text(headline_element)
            
            # Location
            location_element = self.safe_find_elements(
                By.XPATH, 
                "//span[contains(@class, 'text-body-small') and contains(@class, 'inline')]"
            )
            profile_info['location'] = self.safe_get_text(location_element[0]) if location_element else "Not found"
            
            # About section
            try:
                show_more = self.safe_find_elements(By.XPATH, "//button[contains(@aria-label, 'Lihat selengkapnya')]")
                if show_more:
                    show_more[0].click()
                    time.sleep(1)
                
                about_element = self.safe_find_elements(By.XPATH, "//div[contains(@class, 'display-flex') and contains(@class, 'full-width')]")
                profile_info['about'] = self.safe_get_text(about_element[0]) if about_element else "Not found"
            except:
                profile_info['about'] = "Not found"
            
            # Save data
            self.save_to_json(profile_info, "profile_info.json")
            self.logger.info(f"Successfully collected profile info: {profile_info['name']}")
            
            return profile_info
            
        except Exception as e:
            self.logger.error(f"Failed to collect profile info: {str(e)}")
            return {}

    def download_profile_image(self):
        """Download profile picture"""
        try:
            self.logger.info("Downloading profile picture...")
            self.driver.get(self.profile_url)
            time.sleep(self.wait_time)
            
            # Find profile image
            img_element = self.safe_find_elements(
                By.XPATH,
                "//img[contains(@class, 'profile-photo-edit__preview')] | " +
                "//img[contains(@class, 'pv-top-card-profile-picture')] | " +
                "//img[contains(@alt, 'profile') or contains(@alt, 'Photo')]",
                timeout=15
            )
            
            if not img_element:
                self.logger.warning("Profile picture not found")
                return False
            
            img_url = self.safe_get_attribute(img_element[0], "src")
            if not img_url:
                self.logger.warning("Profile picture URL not found")
                return False
            
            # Download high quality image
            if '=' in img_url:  # URL with parameters
                img_url = img_url.split('=')[0] + '=photo-size-800x800'
            
            response = requests.get(img_url, timeout=10)
            if response.status_code == 200:
                img_path = os.path.join(self.data_dir, "profile_picture.jpg")
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                self.logger.info(f"Profile picture downloaded: {img_path}")
                return True
            else:
                self.logger.warning(f"Failed to download profile picture. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to download profile picture: {str(e)}")
            return False

    def scrape_activity(self, activity_type="posts"):
        """
        Scrape activities (posts, comments, reactions)
        
        Parameters:
            activity_type (str): posts, comments, reactions
        """
        type_names = {
            "posts": "posts",
            "comments": "comments",
            "reactions": "reactions"
        }
        
        self.logger.info(f"Collecting {type_names.get(activity_type, 'activities')}...")
        activities = []
        
        try:
            activity_url = f"{self.profile_url}/details/activity/"
            self.driver.get(activity_url)
            time.sleep(self.wait_time)
            
            # Select appropriate tab
            if activity_type != "posts":
                try:
                    tab_button = self.safe_find_elements(
                        By.XPATH,
                        f"//button[contains(@aria-label, '{activity_type.capitalize()}') or contains(@aria-label, '{type_names.get(activity_type, '')}')]",
                        timeout=15
                    )[0]
                    tab_button.click()
                    time.sleep(self.wait_time)
                except:
                    self.logger.warning(f"{activity_type} tab not found")
                    return []
            
            # Scroll to load content
            self.scroll_page()
            
            # Find all activities
            activities_container = self.safe_find_elements(
                By.XPATH,
                "//div[contains(@class, 'scaffold-finite-scroll__content')] | " +
                "//div[contains(@class, 'profile-detail-activity')]",
                timeout=15
            )
            
            if not activities_container:
                self.logger.warning("Activities container not found")
                return []
            
            posts = self.safe_find_elements(
                By.XPATH,
                ".//div[contains(@class, 'update-components-text')] | " +
                ".//div[contains(@class, 'feed-shared-update-v2')]",
                parent=activities_container[0]
            )
            
            for i, post in enumerate(posts, 1):
                try:
                    # Get link
                    link_element = self.safe_find_elements(
                        By.XPATH,
                        ".//a[contains(@href, '/posts/') or contains(@href, '/activity-')]",
                        parent=post
                    )
                    
                    if not link_element:
                        continue
                        
                    link = self.safe_get_attribute(link_element[0], "href").split('?')[0]
                    
                    # Get text
                    text_content = ""
                    text_element = self.safe_find_elements(
                        By.XPATH,
                        ".//div[contains(@class, 'feed-shared-text')] | " +
                        ".//div[contains(@class, 'update-components-text')]",
                        parent=post
                    )
                    
                    if text_element:
                        text_content = self.safe_get_text(text_element[0])
                    
                    # For comments, get comment text
                    comment_text = ""
                    if activity_type == "comments":
                        comment_element = self.safe_find_elements(
                            By.XPATH,
                            ".//div[contains(@class, 'comment-text')]",
                            parent=post
                        )
                        if comment_element:
                            comment_text = self.safe_get_text(comment_element[0])
                    
                    activities.append({
                        "no": i,
                        "link": link,
                        "text": text_content[:500] + "..." if len(text_content) > 500 else text_content,
                        "comment": comment_text,
                        "type": activity_type,
                        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process {activity_type} {i}: {str(e)}")
                    continue
            
            # Save data
            filename = f"{activity_type}.csv"
            self.save_to_csv(activities, filename)
            self.save_to_json(activities, f"{activity_type}.json")
            
            self.logger.info(f"Successfully collected {len(activities)} {type_names.get(activity_type, 'activities')}")
            return activities
            
        except Exception as e:
            self.logger.error(f"Failed to collect {type_names.get(activity_type, 'activities')}: {str(e)}")
            return []

    def scrape_connections(self, connection_type="connections"):
        """
        Scrape connections (connections, followers, following)
        
        Parameters:
            connection_type (str): connections, followers, following
        """
        type_names = {
            "connections": "connections",
            "followers": "followers", 
            "following": "following"
        }
        
        self.logger.info(f"Collecting {type_names.get(connection_type, 'connections')}...")
        connections = []
        
        try:
            # Construct URL based on connection type
            if connection_type == "connections":
                connections_url = f"{self.profile_url}/details/connections/"
            else:
                connections_url = f"{self.profile_url}/details/{connection_type}/"
            
            self.driver.get(connections_url)
            time.sleep(self.wait_time)
            
            # Check if login is required
            if "authwall" in self.driver.current_url or "login" in self.driver.current_url:
                self.logger.warning(f"Login required to access {type_names.get(connection_type)}")
                return []
            
            # Scroll to load content
            self.scroll_page()
            
            # Find all connections
            items = self.safe_find_elements(
                By.XPATH,
                "//li[contains(@class, 'org-people-profile-card')] | " +
                "//div[contains(@class, 'entity-result')]",
                timeout=15
            )
            
            for i, item in enumerate(items, 1):
                try:
                    # Get name and URL
                    name_element = self.safe_find_elements(
                        By.XPATH,
                        ".//span[contains(@class, 'entity-result__title-text')]//a | " +
                        ".//a[contains(@class, 'app-aware-link')]",
                        parent=item
                    )
                    
                    if not name_element:
                        continue
                        
                    name = self.safe_get_text(name_element[0])
                    url = self.safe_get_attribute(name_element[0], "href").split('?')[0]
                    
                    # Get headline if available
                    headline = ""
                    headline_element = self.safe_find_elements(
                        By.XPATH,
                        ".//div[contains(@class, 'entity-result__primary-subtitle')]",
                        parent=item
                    )
                    if headline_element:
                        headline = self.safe_get_text(headline_element[0])
                    
                    connections.append({
                        "no": i,
                        "name": name,
                        "url": url,
                        "headline": headline,
                        "type": connection_type,
                        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process connection {i}: {str(e)}")
                    continue
            
            # Save data
            filename = f"{connection_type}.csv"
            self.save_to_csv(connections, filename)
            self.save_to_json(connections, f"{connection_type}.json")
            
            self.logger.info(f"Successfully collected {len(connections)} {type_names.get(connection_type)}")
            return connections
            
        except Exception as e:
            self.logger.error(f"Failed to collect {type_names.get(connection_type)}: {str(e)}")
            return []

    def scrape_interests(self):
        """Scrape all interests (Top Voices, Companies, Groups, etc.)"""
        self.logger.info("Collecting interests...")
        all_interests = {}
        
        interest_types = {
            "top-voices": "Top Voices",
            "companies": "Companies",
            "groups": "Groups",
            "newsletters": "Newsletters",
            "schools": "Schools"
        }
        
        for itype, name in interest_types.items():
            self.logger.info(f"Collecting interest: {name}...")
            try:
                url = f"{self.profile_url}/details/interests/?detail={itype}"
                self.driver.get(url)
                time.sleep(self.wait_time)
                
                # Scroll to load content
                self.scroll_page(max_scrolls=5)
                
                # Find all interest items
                items = self.safe_find_elements(
                    By.XPATH,
                    "//li[contains(@class, 'org-people-profile-card')] | " +
                    "//div[contains(@class, 'entity-result')]",
                    timeout=15
                )
                
                interests = []
                for i, item in enumerate(items, 1):
                    try:
                        # Get name and URL
                        name_element = self.safe_find_elements(
                            By.XPATH,
                            ".//span[contains(@class, 'entity-result__title-text')]//a | " +
                            ".//a[contains(@class, 'app-aware-link')]",
                            parent=item
                        )
                        
                        if not name_element:
                            continue
                            
                        name = self.safe_get_text(name_element[0])
                        url = self.safe_get_attribute(name_element[0], "href").split('?')[0]
                        
                        # Get description if available
                        description = ""
                        desc_element = self.safe_find_elements(
                            By.XPATH,
                            ".//div[contains(@class, 'entity-result__primary-subtitle')]",
                            parent=item
                        )
                        if desc_element:
                            description = self.safe_get_text(desc_element[0])
                        
                        interests.append({
                            "no": i,
                            "name": name,
                            "url": url,
                            "description": description,
                            "type": itype,
                            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to process interest {i}: {str(e)}")
                        continue
                
                all_interests[itype] = interests
                self.save_to_csv(interests, f"{itype}.csv")
                self.save_to_json(interests, f"{itype}.json")
                
            except Exception as e:
                self.logger.error(f"Failed to collect interest {name}: {str(e)}")
                continue
        
        return all_interests

    def download_media(self):
        """Download all uploaded media (images)"""
        self.logger.info("Downloading uploaded media...")
        try:
            media_url = f"{self.profile_url}/details/media/"
            self.driver.get(media_url)
            time.sleep(self.wait_time)
            
            # Scroll to load content
            self.scroll_page()
            
            # Find all images
            images = self.safe_find_elements(
                By.XPATH,
                "//img[contains(@class, 'ivm-view-attr__img--centered')] | " +
                "//img[contains(@class, 'image-item')]",
                timeout=15
            )
            
            media_dir = os.path.join(self.data_dir, "media")
            os.makedirs(media_dir, exist_ok=True)
            
            downloaded = 0
            for i, img in enumerate(images, 1):
                try:
                    img_url = img.get_attribute("src")
                    if not img_url or not img_url.startswith('http'):
                        continue
                        
                    # Download high quality image if possible
                    if '=' in img_url:  # URL with parameters
                        img_url = img_url.split('=')[0] + '=w800-h800'
                    
                    response = requests.get(img_url, timeout=10)
                    if response.status_code == 200:
                        img_path = os.path.join(media_dir, f"media_{i}.jpg")
                        with open(img_path, 'wb') as f:
                            f.write(response.content)
                        downloaded += 1
                except Exception as e:
                    self.logger.warning(f"Failed to download media {i}: {str(e)}")
                    continue
            
            self.logger.info(f"Successfully downloaded {downloaded} media items")
            return downloaded
            
        except Exception as e:
            self.logger.error(f"Failed to download media: {str(e)}")
            return 0

    def save_to_csv(self, data, filename):
        """Save data to CSV file with error handling"""
        if not data:
            self.logger.warning(f"No data to save to {filename}")
            return
        
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            self.logger.info(f"Data saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save data to {filename}: {str(e)}")

    def save_to_json(self, data, filename):
        """Save data to JSON file with error handling"""
        if not data:
            self.logger.warning(f"No data to save to {filename}")
            return
        
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Data saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save data to {filename}: {str(e)}")

    def create_zip_archive(self):
        """Create ZIP archive of all collected data"""
        try:
            self.logger.info("Creating ZIP archive of data...")
            zip_path = os.path.join(os.path.dirname(self.data_dir), "linkedin_data_archive.zip")
            
            with ZipFile(zip_path, 'w') as zipf:
                for root, _, files in os.walk(self.data_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.data_dir)
                        zipf.write(file_path, arcname)
            
            self.logger.info(f"ZIP archive created: {zip_path}")
            return zip_path
        except Exception as e:
            self.logger.error(f"Failed to create ZIP archive: {str(e)}")
            return None

    def create_summary_report(self, scraped_data):
        """Create scraping summary report"""
        try:
            summary = {
                "scraping_summary": {
                    "profile_url": self.profile_url,
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "total_data_points": sum(len(data) for data in scraped_data.values() if isinstance(data, list))
                },
                "data_breakdown": {}
            }
            
            for key, data in scraped_data.items():
                if isinstance(data, list):
                    summary["data_breakdown"][key] = len(data)
                elif isinstance(data, dict):
                    summary["data_breakdown"][key] = 1
            
            self.save_to_json(summary, "scraping_summary.json")
            self.logger.info("Summary report created")
            
        except Exception as e:
            self.logger.error(f"Failed to create summary report: {str(e)}")

    def scrape_all(self):
        """Run all scraping functions"""
        scraped_data = {}
        
        try:
            self.logger.info("Starting LinkedIn scraping process...")
            self.start_driver()
            
            # Login if credentials provided
            login_success = False
            if self.email and self.password:
                login_success = self.linkedin_login()
            
            # 1. Save profile as PDF/HTML
            self.save_profile_as_pdf()
            
            # 2. Scrape basic profile info
            scraped_data['profile_info'] = self.scrape_basic_profile_info()
            
            # 3. Download profile image
            self.download_profile_image()
            
            # 4. Scrape activities
            scraped_data['posts'] = self.scrape_activity("posts")
            scraped_data['comments'] = self.scrape_activity("comments")
            scraped_data['reactions'] = self.scrape_activity("reactions")
            
            # 5. Scrape connections (only if logged in)
            if login_success:
                scraped_data['connections'] = self.scrape_connections("connections")
                scraped_data['followers'] = self.scrape_connections("followers")
                scraped_data['following'] = self.scrape_connections("following")
            else:
                self.logger.warning("Skipping connections scraping (not logged in)")
            
            # 6. Scrape interests
            scraped_data['interests'] = self.scrape_interests()
            
            # 7. Download media
            scraped_data['media_downloaded'] = self.download_media()
            
            # 8. Create summary report
            self.create_summary_report(scraped_data)
            
            # 9. Create ZIP archive
            zip_path = self.create_zip_archive()
            
            self.logger.info(f"\n{'='*50}")
            self.logger.info("SCRAPING COMPLETED!")
            self.logger.info(f"All data saved to: {self.data_dir}")
            if zip_path:
                self.logger.info(f"ZIP archive created: {zip_path}")
            self.logger.info(f"{'='*50}")
            
        except KeyboardInterrupt:
            self.logger.info("Scraping stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error during scraping: {str(e)}")
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    self.logger.info("WebDriver closed")
                except Exception as e:
                    self.logger.error(f"Failed to close WebDriver: {str(e)}")

def main():
    print("=" * 60)
    print("     LINKEDIN PROFILE SCRAPER PRO - COMPLETE SOLUTION")
    print("=" * 60)
    print("IMPORTANT WARNING:")
    print("- LinkedIn scraping may violate their Terms of Service")
    print("- Use only for educational and ethical purposes")
    print("- Respect privacy and rights of others")
    print("- Use responsibly and legally")
    print("=" * 60)
    
    try:
        # Input profile URL
        while True:
            profile_url = input("\nEnter LinkedIn profile URL: ").strip()
            if profile_url:
                break
            print("URL cannot be empty!")
        
        # Ask for login
        use_login = input("Do you want to login to LinkedIn? (y/n): ").lower().strip() == 'y'
        
        email = None
        password = None
        
        if use_login:
            email = input("Enter LinkedIn email: ").strip()
            password = input("Enter LinkedIn password: ").strip()
            
            if not email or not password:
                print("Email and password required for login!")
                use_login = False
        
        # Ask for headless mode
        headless = input("Run in headless mode (no browser window)? (y/n): ").lower().strip() == 'y'
        
        # Confirm before starting
        print(f"\nConfiguration:")
        print(f"- Profile URL: {profile_url}")
        print(f"- Login: {'Yes' if use_login else 'No'}")
        print(f"- Headless Mode: {'Yes' if headless else 'No'}")
        
        confirm = input("\nProceed with scraping? (y/n): ").lower().strip()
        if confirm != 'y':
            print("Scraping cancelled.")
            return
        
        # Start scraping
        scraper = LinkedInScraperPro(profile_url, email, password, headless)
        scraper.scrape_all()
        
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("Please try again or check your configuration.")

if __name__ == "__main__":
    main()
