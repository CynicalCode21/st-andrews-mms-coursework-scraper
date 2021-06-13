from getpass import getpass
from selenium import webdriver
import re
import pprint

def main():

    
    options = webdriver.ChromeOptions();
    options.add_argument('headless');
    options.add_argument('window-size=1200x600')

    driver = webdriver.Chrome(options=options)
    #driver = webdriver.Chrome('chromedriver')
    print("Logging into mms...")
    login(driver)
    print("Scraping years to collect grades from...")
    dates = scrape_years(driver)
    print("Scraping grades for each CS module...")
    grades = scrape_coursework_grades(driver, dates)

    pprint.pprint(grades)

    driver.close()


def login(driver):
    # login 
    # get username and password (also black out password)
    username = input("Enter username: ")
    password = getpass("Enter password: ")

    driver.get("https://login.st-andrews.ac.uk/cas/login?service=https%3A%2F%2Fmms.st-andrews.ac.uk%2Fmms%2Fuser%2Fme%2FModules")

    driver.find_element_by_id('username').send_keys(username)
    driver.find_element_by_id('password').send_keys(password)
    driver.find_element_by_name('submit').click()

def scrape_years(driver):
    # open menu
    #dropdown = driver.find_element_by_id('select2-chosen-2')
    dropdown = driver.find_element_by_class_name('select2-arrow')
    dropdown.click()

    # collect the years of page to scrape
    dates = []
    for date in driver.find_elements_by_class_name("select2-result-label"):
        if (date.text == "Current"):
            continue
        else:
            dates.append(date.text)

    # close menu
    driver.find_element_by_class_name("select2-result-label").click()

    return dates


# for each year, click and goto, then scrape page
def scrape_coursework_grades(driver, dates):
    modules = {}
    for date in dates:
        driver.find_element_by_id('select2-chosen-2').click()
        for x in driver.find_elements_by_class_name("select2-result-label"):
            if (x.text == date):
                x.click()
                # click button and go to modules for that year
                driver.find_element_by_name("command").click()
                # scrape modules on the page
                current_url = driver.current_url
                modules_for_year = scrape_page(driver)
                modules_for_year = {date: modules_for_year}
                modules.update(modules_for_year)
                driver.get(current_url)
                break

    return modules

# go through entire page, clicking on
# with driver and the element to click
def scrape_page(driver):
    link_elements = driver.find_elements_by_class_name("coursework")
    links = []
    for link in link_elements:
        # if a cs module then go to page and scrape it
        if (re.search(r"CS\d{4} Coursework$", link.text) or
            re.search(r"CS\d{4} Coursework Practicals", link.text)):
            links.append(link.get_attribute("href"))

    modules = {}
    for link in links:
        modules.update(scrape_module_page(driver, link))
    return modules


# returns the coursework grade and module name
def scrape_module_page(driver, url):
    driver.get(url)
    text = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div/div/div/div/p[3]")
    module = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/nav/ul/li[3]/a")
    # manipulate modules into {module: {coursework: N}}
    out = {module.text[0:6]: re.search(r"\d{1,2}\.\d{1}", text.text)[0]}
    return out

if __name__ == "__main__":
    main()
