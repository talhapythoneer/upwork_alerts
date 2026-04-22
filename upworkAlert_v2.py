import scrapy
import json
from scrapy.crawler import CrawlerProcess
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import pyaudio
import wave
import logging
import os
from rich import print
import random
import sys
from datetime import datetime
from config import (
    AVG_SPENT_THRESHOLD,
    CHROMEDRIVER_PATH,
    COVER_LETTER_PATH,
    FIXED_BUDGET_THRESHOLD,
    HOURLY_BUDGET_MAX_THRESHOLD,
    HOURLY_BUDGET_MIN_THRESHOLD,
    NEGATIVE_COUNTRIES,
    NEGATIVE_KEYWORDS,
    NOTIFICATION_SOUND_PATH,
    PROCESSED_JOBS_PATH,
    TOTAL_FEEDBACK_THRESHOLD,
    TOTAL_HIRES_THRESHOLD,
    TOTAL_SPENT_THRESHOLD,
    UPWORK_EMAIL,
    UPWORK_PASSWORD,
    get_api_headers,
)

# seed the random number generator
random.seed(datetime.now())

logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
logger.setLevel(logging.WARNING)  
logger.propagate = False


# CONSTRAINTS / THRESHOLDS
hourly_budget_min_threshold = HOURLY_BUDGET_MIN_THRESHOLD
hourly_budget_max_threshold = HOURLY_BUDGET_MAX_THRESHOLD
fixed_budget_threshold = FIXED_BUDGET_THRESHOLD
total_hires_threshold = TOTAL_HIRES_THRESHOLD
total_spent_threshold = TOTAL_SPENT_THRESHOLD
total_feedback_threshold = TOTAL_FEEDBACK_THRESHOLD
avg_spent_threshold = AVG_SPENT_THRESHOLD


negative_keywords = NEGATIVE_KEYWORDS

neg_countries = NEGATIVE_COUNTRIES

random_sleep = [60, 80, 100, 120, 140, 160, 180]

def botInitialization(isHeaderless=False):
    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    
    # options.add_argument("start-maximized")
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option('useAutomationExtension', False)
    # options.add_argument('--disable-blink-features=AutomationControlled')


    driver = uc.Chrome(driver_executable_path=str(CHROMEDRIVER_PATH), options=options)
    
    # chromedriver_path = 'requiredFiles/chromedriver.exe'
    # driver = webdriver.Chrome(executable_path=chromedriver_path)

    driver.maximize_window()

    return driver


def login(driver):
    user = driver.find_element(By.CSS_SELECTOR, "#login_username")
    user.send_keys(UPWORK_EMAIL)
    user.send_keys(Keys.ENTER)
    sleep(2)
    print("Email Entered...")

    password = driver.find_element(By.CSS_SELECTOR, "#login_password")
    password.send_keys(UPWORK_PASSWORD)
    print("Password Entered...")

    rememberme = driver.find_element(By.CSS_SELECTOR, "#login_rememberme")
    driver.execute_script("arguments[0].click();", rememberme)
    sleep(1)
    print("Remember Me Clicked...")

    password.send_keys(Keys.ENTER)
    sleep(10)
    print("Logged In...")

    return driver




def notifSound():
    for i in range(1):
        # open the wav file
        wav_file = wave.open(str(NOTIFICATION_SOUND_PATH), 'rb')

        # create an instance of PyAudio
        audio = pyaudio.PyAudio()

        # open a stream
        stream = audio.open(format=audio.get_format_from_width(wav_file.getsampwidth()),
                            channels=wav_file.getnchannels(),
                            rate=wav_file.getframerate(),
                            output=True)

        # read the data in chunks and play it
        chunk = 1024
        data = wav_file.readframes(chunk)
        while data:
            stream.write(data)
            data = wav_file.readframes(chunk)

        # close the stream and terminate the PyAudio instance
        stream.close()
        audio.terminate()



def check_title(title):
    for keyword in negative_keywords:
        if keyword in title.lower():
            return False

    return True

def check_description(description):
    for keyword in negative_keywords:
        if keyword in description.lower():
            return False

    return True

def check_attr_list(attr_names_list):
    for keyword in negative_keywords:
        if keyword in attr_names_list.lower():
            return False

    return True


def check_country(client_country):
    if client_country.lower() in neg_countries:
        return False

    return True

def check_payment_verification(payment_verification_status):
    if payment_verification_status == 1:
        return True

    return False

def check_budget(jobType, amount, hourly_budget_min, hourly_budget_max):
    if jobType == 2:
        # last condition i.e (hourly_budget_min == 0 and hourly_budget_max == 0) is for the jobs that have no budget specified by client
        if hourly_budget_min >= hourly_budget_min_threshold or hourly_budget_max >= hourly_budget_max_threshold or (hourly_budget_min == 0 and hourly_budget_max == 0): 
            return True
    else:
        if amount >= fixed_budget_threshold or amount == 0: # amount 0 means no budget specified by client
            return True

    return False

def check_client_history(total_hires, total_spent):
    if total_hires >= total_hires_threshold and total_spent >= total_spent_threshold:
        return True

    return False


def check_client_rating(total_reviews, total_feedback):
    if total_reviews >= 1:
      if total_feedback >= total_feedback_threshold:
          return True
    else:
        return True
    
    return False

def check_avg_spent(total_spent, total_hires):
    if not total_spent:
        total_spent = 0
    if not total_hires:
        total_hires = 0

    if total_hires == 0 or total_spent == 0:
        return True

    avg_spent = total_spent / total_hires

    if avg_spent >= avg_spent_threshold:
        return True

    return False


# read the cover letter text
with open(COVER_LETTER_PATH, "r", encoding='utf-8-sig') as f:
    coverLetterText = f.read()

    
# to keep record of the jobs that are processed
with open(PROCESSED_JOBS_PATH, "r") as f:
    processedJobs = f.readlines()
processedJobs = [job.strip() for job in processedJobs]



payload = {
    "query": """
      query bestMatches ($fromTime: String!, $toTime: String!) {
          bestMatchJobsFeed(fromTime: $fromTime, toTime: $toTime) {
            results {
              uid:id
              title
              ciphertext
              description
              type
              recno
              freelancersToHire
              duration
              durationLabel
              engagement
              amount {
                amount
                currencyCode
              }
              createdOn:createdDateTime
              publishedOn:publishedDateTime
              renewedOn:renewedDateTime
              prefFreelancerLocation
              prefFreelancerLocationMandatory
              connectPrice
              client {
                totalHires
                totalSpent
                paymentVerificationStatus
                location {
                  country
                  city
                  state
                  countryTimezone
                  worldRegion
                }
                totalReviews
                totalFeedback
                hasFinancialPrivacy
              }
              enterpriseJob
              premium
              jobTime
              skills {
                id
                prefLabel
              }
              tierText
              tier
              tierLabel
              proposalsTier
              isApplied
              hourlyBudget {
                type
                min
                max
              }
              weeklyBudget {
                amount
              }
              clientRelation {
                companyName
                lastContractRid
                lastContractTitle
              }
              relevanceEncoded
              attrs {
                uid:id
                prettyName
                freeText
                skillType
              }
            }
            paging {
              total
              count
              minTime
              maxTime
            }
          }
        }""",
    "variables": {"limit": 10}
}



headers = get_api_headers("https://www.upwork.com/nx/find-work/most-recent")


class UpworkSpider(scrapy.Spider):
    name = 'upwork_spider'
    allowed_domains = ['upwork.com']

    custom_settings = {
        'CONCURRENT_REQUESTS': '1',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        # "RETRY_TIMES": 100,
        # "RETRY_HTTP_CODES": [406, 403],
        # "AUTOTHROTTLE_ENABLED" : True,
        # "AUTOTHROTTLE_START_DELAY" : 0.25,
        # "AUTOTHROTTLE_MAX_DELAY" : 2
        # 'DOWNLOADER_MIDDLEWARES': {
        #     'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 1
        # },
    }

    def __init__(self):
        self.driver = botInitialization()

        self.driver.get('https://www.upwork.com/ab/account-security/login')
        sleep(2)

        self.driver = login(self.driver)


    def start_requests(self):
        while True:
            url = "https://www.upwork.com/api/graphql/v1"

            yield scrapy.Request(
                url,
                method="POST",
                body=json.dumps(payload),
                headers=headers,
                callback=self.parse,
                dont_filter=True
            )


    def parse(self, response):
        # print(response.text)

        # Optionally, you can process the response data here
        data = json.loads(response.text)
        
        # results = data['data']['mostRecentJobsFeed']['results']
        results = data['data']['mostRecentJobsFeed']['results']

        os.system('cls')

        for result in results:
            
            print("\n\n ----------------------------- \n\n")

            # Assigning variables
            job_id = result['id']
            job_uid = result['uid']
            title = result['title'] # Job Title
            ciphertext = result['ciphertext'] # Job URL
            description = result['description'] # Job Description
            job_type = result['type']
            recno = result['recno']
            freelancers_to_hire = result['freelancersToHire']
            duration = result['duration']
            engagement = result['engagement']
            amount = result['amount']['amount']
            created_on = result['createdOn']
            published_on = result['publishedOn']
            pref_freelancer_location_mandatory = result['prefFreelancerLocationMandatory']
            connect_price = result['connectPrice']
            total_hires = result['client']['totalHires']
            total_spent = result['client']['totalSpent']
            payment_verification_status = result['client']['paymentVerificationStatus']
            client_country = result['client']['location']['country']
            total_reviews = result['client']['totalReviews']
            total_feedback = result['client']['totalFeedback']
            has_financial_privacy = result['client']['hasFinancialPrivacy']
            tier_text = result['tierText']
            tier = result['tier']
            tier_label = result['tierLabel']
            proposals_tier = result['proposalsTier']
            enterprise_job = result['enterpriseJob']
            premium = result['premium']
            job_ts = result['jobTs']
            attr_names_list = [attr['prettyName'] for attr in result['attrs']] # Job Tags
            attr_names_list = ', '.join(attr_names_list) # Job Tags
            hourly_budget_type = result['hourlyBudget']['type']
            hourly_budget_min = result['hourlyBudget']['min']
            hourly_budget_max = result['hourlyBudget']['max']
            is_applied = result['isApplied']

            
            print({
                # "Job ID": job_id,
                # "Job UID": job_uid,
                "Title": title,
                # "Ciphertext": ciphertext,
                "Description": description,
                "Type": job_type,
                # "Recno": recno,
                # "Freelancers to Hire": freelancers_to_hire,
                # "Duration": duration,
                # "Engagement": engagement,
                "Amount": amount,
                # "Created On": created_on,
                # "Published On": published_on,
                # "Pref Freelancer Location Mandatory": pref_freelancer_location_mandatory,
                # "Connect Price": connect_price,
                "Total Hires": total_hires,
                "Total Spent": total_spent,
                "Payment Verification Status": payment_verification_status,
                "Client Country": client_country,
                "Total Reviews": total_reviews,
                "Total Feedback": total_feedback,
                # "Has Financial Privacy": has_financial_privacy,
                # "Tier Text": tier_text,
                # "Tier": tier,
                # "Tier Label": tier_label,
                # "Proposals Tier": proposals_tier,
                # "Enterprise Job": enterprise_job,
                # "Premium": premium,
                # "Job TS": job_ts,
                "Pretty Names": attr_names_list,
                "Hourly Budget Type": hourly_budget_type,
                "Hourly Budget Min": hourly_budget_min,
                "Hourly Budget Max": hourly_budget_max,
                # "Is Applied": is_applied
                'URL': "https://www.upwork.com/ab/proposals/job/" + ciphertext + "/apply/"
            })

              
            if ciphertext in processedJobs:
                print("\nAlready Processed: " + title)
                continue

            is_title_OK = check_title(title)
            if not is_title_OK:
                print("\nIRRELEVANT: Negative keyword found in title. Skipping...")
                continue

            is_description_OK = check_description(description)
            if not is_description_OK:
                print("\nIRRELEVANT: Negative keyword found in description. Skipping...")
                continue

            is_attr_list_OK = check_attr_list(attr_names_list)
            if not is_attr_list_OK:
                print("\nIRRELEVANT: Negative keyword found in skills. Skipping...")
                continue
            
            is_country_OK = check_country(client_country)
            if not is_country_OK:
                print("\nIRRELEVANT: Negative country. Skipping...")
                continue

            is_payment_verification_OK = check_payment_verification(payment_verification_status)
            if not is_payment_verification_OK:
                print("\nIRRELEVANT: Payment Unverified. Skipping...")
                continue
            

            is_budget_OK = check_budget(job_type, amount, hourly_budget_min, hourly_budget_max)
            if not is_budget_OK:
                print("\nIRRELEVANT: Budget is LOW. Skipping...")
                continue
            
            is_client_rating_OK = check_client_rating(total_reviews, total_feedback)
            if not is_client_rating_OK:
                print("\nIRRELEVANT: Low Rating. Skipping...")
                continue

            # is_client_history_OK = check_client_history(total_hires, total_spent)
            # if not is_client_history_OK:
            #     print("\nIRRELEVANT: No Hires or Low Spent. Skipping...")
            #     continue
            
            is_averageSpent_OK = check_avg_spent(total_spent, total_hires)
            if not is_averageSpent_OK:
                print("\nIRRELEVANT: Low Average Spent. Skipping...")
                continue

            is_hourly = True if job_type == 2 else False

            budgetToPut = int(amount - (amount * 0.2))
            
            applyURL = "https://www.upwork.com/ab/proposals/job/" + ciphertext + "/apply/"

            # close all tabs except the first one
            for handle in self.driver.window_handles[1:]:
                self.driver.switch_to.window(handle)
                self.driver.close()

            self.driver.switch_to.window(self.driver.window_handles[0])
            
            self.driver.get(applyURL)
            
            # check if it's a login page
            if "Log in" in self.driver.title:
                print("Logging in...")
                self.driver = login(self.driver)

                self.driver.get(applyURL)
    
            sleep(2)


            moreButton = self.driver.find_element(By.CSS_SELECTOR, "button.air3-truncation-btn.air3-btn-link-secondary")
            self.driver.execute_script("arguments[0].click();", moreButton)
            sleep(1)

            view_job_button = self.driver.find_element(By.CSS_SELECTOR, 'a[data-test="open-original-posting"]')
            view_job_button.send_keys(Keys.CONTROL + Keys.RETURN)
            
            # if job is fixed, then put the budget
            if is_hourly:
                pass
            else:
                try:
                    byProjectRadio = self.driver.find_element(By.CSS_SELECTOR, "input[value='default']")
                    self.driver.execute_script("arguments[0].click();", byProjectRadio)
                    sleep(1)
                except:
                    print("Radio Button not found...")
                    pass

                inputAmount = self.driver.find_element(By.CSS_SELECTOR, "#charged-amount-id")
                inputAmount.click()
                # send ctrl + a
                inputAmount.send_keys(Keys.CONTROL + "a")
                # send backspace
                inputAmount.send_keys(Keys.BACKSPACE)
                # inputAmount.clear()
                inputAmount.send_keys(budgetToPut)
                sleep(1)


            
            frequencyDropDown = self.driver.find_elements(By.CSS_SELECTOR, "div.air3-dropdown-icon")[1]
            self.driver.execute_script("arguments[0].click();", frequencyDropDown)
            sleep(1)
            
            number_of_dropdowns = len(self.driver.find_elements(By.CSS_SELECTOR, "div.air3-dropdown-icon"))
            if number_of_dropdowns == 2:
                # it's a duration dropdown
                items = self.driver.find_elements(By.CSS_SELECTOR, "li[role='option']")[-1]
                self.driver.execute_script("arguments[0].click();", items)

            else:
                # it's a frequency dropdown
                items = self.driver.find_elements(By.CSS_SELECTOR, "li[role='option']")[0]
                self.driver.execute_script("arguments[0].click();", items)


            # put the cover letter
            textAreas = self.driver.find_elements(By.CSS_SELECTOR, 'textarea[aria-labelledby="cover_letter_label"]')

            coverLetterArea = textAreas[0]
            coverLetterArea.send_keys(coverLetterText)


            notifSound()

            s = input("\nCheck Proposal... Enter 's' to skip: ")


            print("Processed...")

            processedJobs.append(ciphertext)
            
            with open(PROCESSED_JOBS_PATH, "a") as f:
                f.write(ciphertext + "\n")



        # sleep_time = random.choice(random_sleep)
        sleep_time = 30
        print("Sleeping for " + str(sleep_time) + " seconds...")
        sleep(sleep_time)



process = CrawlerProcess()
process.crawl(UpworkSpider)
process.start()
