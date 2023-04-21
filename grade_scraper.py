
# Operational imports: 'os' and 'dotenv' used for username and password security (thanks Mike!)
#   'time' is used loggin completion time.
import os
from dotenv import load_dotenv
from time import time

# May not need these two, used for debugging with 'traceback.print_exc(file=sys.stdout)'
import traceback
import sys

# Selenium imports are fun!
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait # WebDriverWait is the MVP of this script!
from selenium.webdriver.support import expected_conditions as EC # So is this guy!


options = Options() # All our selenium options will go into this built-in function.
options.add_argument("--no-sandbox") # Ensures stability
options.add_argument("start-maximized") # Looks nice
options.add_experimental_option("detach", True) # Can't remember why I added this but I know it was useful
options.add_experimental_option("excludeSwitches", ["enable-logging"]) # Removes annoying warnings from output
path = Service("/usr/lib/chromium-browser/chromedriver") # Path to our chrome webdriver tool. This works for me on Windows somehow.
driver = webdriver.Chrome(service=path, options=options) # Creating the webdriver with the proper driver tool and options.
driver.get("https://blackboard.gwu.edu/webapps/login/") # Our very favorite webscraping site! (not)

load_dotenv() # Loading environment variables

# Login page is honestly the easiest part.
def loginPage():
    # Secure username and passowrd env vars.
    username = os.getenv("BB_USERNAME")
    password = os.getenv("BB_PASSWORD")
    # Getting the username and password fields, and login button.
    # Full xpaths may not seem very pythonic, but it has saved me a lot of headaches. If you want to try to do it
    #   with abbreviated xpaths, good luck.
    user_field = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/form/div[3]/ul/li[1]/input")
    pass_field = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/form/div[3]/ul/li[2]/input")
    login_btn = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/form/div[3]/ul/li[3]/input")

    # Entering info and clicking login
    user_field.send_keys(username)
    pass_field.send_keys(password)
    login_btn.click()
    print("Login: success.")

# Dealing with the cookies. Note that you will not see this in your normal browser, but since selenium opens
#   a new window that is not signed in, you will still get the cookie message, which we have to accept.
def cookieAgree():
    # THIS IS CRITICAL! We have to wait for the popup to appear, since it is js driven and not instant.
    wait = WebDriverWait(driver, 10) # Setting up the webdriver. Probably could have done this globally.
    # EC is super helpful here as it essentially waits until the element is useful before we try to access it, so we
    #   don't get an error because we were trying to get it before it was loaded.
    ok_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[7]/div/div/div/div/div/div/div[2]/button")))

    ok_btn.click()
    print("Cookie agree: success.")
    print("-----------------------------------------------\nGRADES: \n") # Output formatting. Don't ask questions.

# The function that opens each course, so we can get a grade from each, which will actually be handled by a separate function.
def openCourse():
    wait = WebDriverWait(driver, 10)

    # Here we don't need the full xpath because there's only one element with this id on the home page. Also note the use
    #   of 'find_elements()', plural, as opposed to 'find_element()'.
    course_row = driver.find_elements(By.XPATH, '//*[@id="_388_1termCourses_noterm"]/ul/li')

    # Nice easy for loop. Here's were the 'find_elements()' makes a difference; it returns a list of the courses instead of
    #   just the first one it finds.
    for course in range(len(course_row)):
        next_course = wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="_388_1termCourses_noterm"]/ul/li[{course + 1}]/a'))) # 0-indexing for the win!
        name = driver.find_element(By.XPATH, f'//*[@id="_388_1termCourses_noterm"]/ul/li[{course + 1}]/a') # Raw course name which we will format later
        formatted_name = formatName(name.text) # See the function definition below
        next_course.click()
        course_grade = getCourseGrade() # See the function definition below
#         print(course_grade)
        # Scientists have recently discovered the only thing that has a 0% chance of happening in an infinite universe: all your professors properly inputing
        #   a total grade on blackboard. Either because they are smart enough to put them in a better format (like a certain R professor...), or because they
        #   are too smart and making the grading scheme and blackboard page overly comlicated so you can't find anything and there are six other third-party
        #   sites each with their own grading schema.
        # Sooooo, we need to know if the grade we're getting back is actually a total
        if course_grade[1] != "Total": # Note here we are talking about 'Total', and not 'Weighted Total', which is often the first criteria on blackboard.
            print(f"'{formatted_name}' grade: TOTAL NOT AVAILABLE")
        else:
            print(f"'{formatted_name}' grade:", course_grade[0].replace('\n', '')) # Since all professors have their own scheme (see rant above), we should return points/total available.
        courses_btn = driver.find_element(By.XPATH, '//*[@id="Courses.label"]/a') # Navigate back to the 'Courses' home page. I'm pretty sure I had to do it like this due to some BB stupidity.
        courses_btn.click()

# Here is where we actually scrape the grade from the grading page. Maybe I didn't have to make it a whole different function.
def getCourseGrade():
    wait = WebDriverWait(driver, 3) # Shorter wait to justify not creating the wait globaly.
    try:
        show_grades = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'My Grades'))) # DIFFERENT METHOD ALERT! For some reason, xpaths were just not working for this.
        show_grades.click()
        grade_type = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div[3]/div/div/div/div/div[2]/div[3]/div[2]/div[2]/div[1]/span')))
        tot_grade = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div[3]/div/div/div/div/div[2]/div[3]/div[2]/div[2]/div[3]')))
        # Please note the '.text' function here. This is a WebElement attribute that returns the string of what it was applied to. Otherwise you'll get a WebElement id, which is useless.
        return [tot_grade.text, grade_type.text]
    except TimeoutException: # This exception is thrown by the WebDriverWait function if it exceeds its wait time (in this case 3, in the 'openCourse()' function it's 10)
#         traceback.print_exc(file=sys.stdout)
        return "Not found"

# Wanted to keep the name formatting separate for some reason so I put it in a function
def formatName(name):
    split_name = name.split("_") # My own moment of original genius: splitting the course names on the underscores to get nice-looking output names.
    formatted_name = split_name[2]
    return(formatted_name)

# Main function yay!
def main():
    loginPage()
    cookieAgree()
    openCourse()
    driver.close() # MAKE SURE YOU CLOSE YOUR DRIVER!!!!! Even though the script may exit, the WebDriver instance remains open and can cause crippling memory issues,
                   #   especially with weaker or lighter systems such as RaspberryPi.


if __name__ == '__main__':
    start = float(time()) # Timing script because why not.
    main()
    end = float(time())
    print('-----------------------------------------------\ncompleted in:', (end-start)) # More formatting. Same drill.

