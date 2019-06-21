import selenium
import time
import sys
import csv
import getpass

from selenium import webdriver

#------------------------------------------------
default_target = "https://canvas.sydney.edu.au/courses/14200/groups"
#------------------------------------------------
# Useage: 
# python canvas_group_scraper.py <target groups page>
# Requires gecko driver
#------------------------------------------------


def scrape(target):

    driver = webdriver.Firefox()
    
    print("Canvas login creds:")

    print("Loading login portal")
    driver.get("https://canvas.sydney.edu.au/")

    username = input("Enter your canvas username: ")
    password = getpass.getpass(prompt="Enter your canvas password: ")

    print("Logging in")

    # Enter username
    username_field = driver.find_element_by_name("UserName")
    username_field.clear()
    username_field.send_keys(username)

    # Enter password
    password_field = driver.find_element_by_name("Password")
    password_field.clear()
    password_field.send_keys(password)

    # Hit the button
    login_button = driver.find_element_by_id("submitButton")
    login_button.click()

    time.sleep(2)

    print("Logged in!")
    driver.get(target)

    category_selectors = driver.find_elements_by_class_name("group-category-tab-link")

    # Skip the 'everyone' tab
    for category_selector in category_selectors:
        print("Scraping Group Category...")
        category_selector.click()
        time.sleep(2)
        groups = extract_groups(driver)
        csv_groups(groups, category_selector.text)

    print("Scraping finished, closing web driver.")
    driver.close()


def extract_groups(driver):

    # Click to expand group header

    groups = {}

    group_selectors = driver.find_elements_by_class_name('group-name')
    tabbed_group_selectors = [i for i in group_selectors if i.text != ''] 

    group_names = [i.text for i in group_selectors if i.text != ''] 


    # Need to click each of the groups
    for i in tabbed_group_selectors:

        group_member_cursor = len(driver.find_elements_by_class_name('group-user-name'))
        print(group_member_cursor)

        i.click()
        # Waiting for the response
        time.sleep(0.3)

        group_name = i.text
        groups[group_name] = []

        group_members = driver.find_elements_by_class_name('group-user-name')
        for j in group_members[group_member_cursor:]:

            groups[group_name].append(j.text)               

        print("Group: {} contains {}".format(group_name, groups[group_name].__repr__()))

    return groups





#------------------------------------------------

def csv_groups(groups, group_file):
    with open('elec5616_groups_{}.csv'.format(group_file), 'w') as groups_file:
        csv_writer = csv.writer(groups_file) 
        for count, group in enumerate(groups):
            if len(groups[group]) > 0:
                for member in groups[group]:
                    group_line = ['group_{}'.format(count ), member]
                    csv_writer.writerow(group_line)
    print("CSV written")
    return

#------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) == 1:
        target_url = default_target
    else:
        target_url = sys.argv[1]

    scrape(target_url)

print("Finished!")


