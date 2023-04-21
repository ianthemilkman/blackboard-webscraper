
import os
from dotenv import load_dotenv
from time import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


options = Options()
options.add_argument("--no-sandbox")
options.add_argument("start-maximized")
options.add_experimental_option("detach", True)
options.add_experimental_option("excludeSwitches", ["enable-logging"])
path = Service("/usr/lib/chromium-browser/chromedriver")
driver = webdriver.Chrome(service=path, options=options)
driver.get("https://blackboard.gwu.edu/webapps/login/")

load_dotenv()

def loginPage():
    username = os.getenv("BB_USERNAME")
    password = os.getenv("BB_PASSWORD")
    user_field = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/form/div[3]/ul/li[1]/input")
    pass_field = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/form/div[3]/ul/li[2]/input")
    login_btn = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/form/div[3]/ul/li[3]/input")

    user_field.send_keys(username)
    pass_field.send_keys(password)
    login_btn.click()
    print("success.")

def cookieAgree():
    wait = WebDriverWait(driver, 10)
    ok_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[7]/div/div/div/div/div/div/div[2]/button")))

    ok_btn.click()
    print("success.")

def openCourse():
    wait = WebDriverWait(driver, 10)
    course_row = driver.find_elements(By.XPATH, '//*[@id="_388_1termCourses_noterm"]/ul/li')
    for course in range(len(course_row)):
        next_course = wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="_388_1termCourses_noterm"]/ul/li[{course + 1}]/a')))
        name = driver.find_element(By.XPATH, f'//*[@id="_388_1termCourses_noterm"]/ul/li[{course + 1}]/a')
        formatted_name = formatName(name.text)
        next_course.click()
        course_grade = getCourseGrade()
        print(f"'{formatted_name}' grade:", course_grade)
        courses_btn = driver.find_element(By.XPATH, '//*[@id="Courses.label"]/a')
        courses_btn.click()
    print("success.")

def getCourseGrade():
    wait = WebDriverWait(driver, 3)
    try:
        show_grades = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'My Grades')))
        show_grades.click()
        grade = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div[3]/div/div/div/div/div[2]/div[3]/div[2]/div[1]/div[3]/span')))
        print("success.")
        return grade.text
    except Exception:
        return "Not found"

def formatName(name):
    new_name = name[21:]
    new_name = new_name[:-13]
    return(new_name)

def main():
    loginPage()
    cookieAgree()
    openCourse()
    driver.close()


if __name__ == '__main__':
    start = float(time())
    main()
    end = float(time())
    print('completed in:', (end-start))

