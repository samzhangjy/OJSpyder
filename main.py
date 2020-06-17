"""OJ spyder

This is a web spyder for http://oj.noi.cn/. Currently supporting login,
get problems and get problem by id.

Author: samzhangjy
GitHub: https://github.com/samzhangjy
GitLab: https://gitlab.com/samzhangjy
Email: samzhang951@outlook.com
Licence: MIT
Documentation: See README.md for details
"""


import time
from pprint import pprint

import htmlmin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Spyder(object):
    def __init__(self, username='', password='', headless=True):
        """Initialize the OJ spyder.

        This function will be ran when creating a new instance of the `Spyder`
        class. The two args `username` and `password` will be used in subfunctions
        like login.

        Args:
            username (str, optional): The oj username. Defaults to ''.
            password (str, optional): The oj password. Defaults to ''.
            headless (bool, optional): Weather to use headless version of web driver or not. Defaults to True.
        """
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(
            './chromedriver', options=self.chrome_options)
        self.username = username
        self.password = password

    def login(self):
        """Login to OJ.

        This function uses selenium web driver to login into the OJ account.
        Requires the username and password to be setted in the __init__ function.

        Returns:
            dict: The login status. For example, when succeeded:
                {
                    'status': 'success',
                    'msg': 'success'
                }
                When failed:
                {
                    'status': 'error',
                    'msg': '<error message here>'
                }
        """
        try:
            self.driver.get('http://oj.noi.cn/')
            time.sleep(1)
            username = self.driver.find_element_by_id('username')
            username.send_keys(self.username)
            password = self.driver.find_element_by_id('ori_passwd')
            password.send_keys(self.password)
            remember = self.driver.find_element_by_name('remember')
            remember.click()
            login = self.driver.find_element_by_class_name('pull-right')
            login.click()
            time.sleep(0.5)
            errs = self.driver.find_elements_by_css_selector(
                'span.alert-error')
            if errs:
                try:
                    err = errs[1]
                except IndexError:
                    return {
                        'status': 'success',
                        'msg': 'success'
                    }
                return {
                    'status': 'error',
                    'msg': err.text
                }
            return {
                'status': 'success',
                'msg': 'success'
            }
        except Exception as error:
            return {
                'status': 'error',
                'msg': error
            }

    def _format_string(self, s=''):
        """Format the given string

        This function removes starting and trailing spaces and extra line breaks
        from the string.

        Args:
            s (str, optional): The string to format. Defaults to ''.

        Returns:
            str: The formatted string.
        """
        return s.strip().replace('\n', '')

    def get_problems(self, page=1):
        """Get the problem set from OJ

        This function uses selenium and Chrome webdriver to get data from the OJ
        website.

        Args:
            page (int, optional): The current page number. Defaults to 1.

        Returns:
            dict: The problems status. E.g.:
                When succeeded:
                {
                    'status': 'success',
                    'msg': 'success',
                    'problems': [
                        { problem data here },
                        { problem data here },
                        { problem data here },
                        ...
                    ]
                }

                When failed:
                {
                    'status': 'error',
                    'msg': '<error message here>'
                }
        """
        if page > 25:
            return {
                'status': 'error',
                'msg': 'page number too big'
            }
        elif page < 1:
            return {
                'status': 'error',
                'msg': 'page number too small'
            }
        self.driver.get(
            'http://oj.noi.cn/oj/index.php/main/problemset/%d' % page)
        try:
            table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'table'))
            )
            source = htmlmin.minify(table.get_attribute(
                'innerHTML'), remove_empty_space=True)
            bs = BeautifulSoup(source, 'html.parser')
            problems = bs.findAll('tr', attrs={'style': 'height:0px'})
            results = []
            for problem in problems:
                result = {}
                try:
                    status = problem.find('td', class_='status').find(
                        'span', class_='label-success').text
                except AttributeError:
                    status = ''
                result['status'] = status
                pid = problem.find('td', class_='pid').find('a').text
                result['pid'] = pid
                title = problem.find('td', class_='title').find('a').text
                result['title'] = title
                try:
                    labels = self._format_string(problem.find(
                        'td', class_='title').find('span', class_='label').text)
                except AttributeError:
                    labels = ''
                result['labels'] = labels
                source = problem.find('td', class_='source').text
                result['source'] = source
                solved = problem.find('td', class_='solvedCount').find(
                    'a').find('span', class_='badge-info').text
                result['solved'] = solved
                submitted = problem.find('td', class_='submitCount').find(
                    'a').find('span', class_='badge-info').text
                result['submitted'] = submitted
                avg = str(problem.find('td', class_='avg').find(
                    'span', class_='badge-info').text).replace(' pts', '')
                result['avg'] = avg
                results.append(result)
            if results == []:
                return {
                    'status': 'error',
                    'msg': 'no results'
                }
            return {
                'status': 'success',
                'msg': 'success',
                'problems': results
            }
        except TimeoutException:
            return {
                'status': 'error',
                'msg': 'request timed out'
            }

    def get_problem(self, pid='1001'):
        """Get the problem by the given id

        This function gathers information about the problem, such as content,
        input, output, sample input, sample output and limits.

        Args:
            pid (str, optional): The problem id. Defaults to '1001'.

        Returns:
            dict: The problem status. For example:
                When succeeded:
                {
                    'status': 'success',
                    'msg': 'success',
                    'problem': {
                        'content': '<problem content>',
                        'input': '<problem input>',
                        'output': '<problem output>',
                        'sample_input': '<problem sample input>',
                        'sample_output': '<problem sample output>',
                        'limits': '<problem limits>'
                    }
                }
                When failed:
                {
                    'status': 'error',
                    'msg': '<error message>'
                }
        """
        self.driver.get('http://oj.noi.cn/oj/index.php/main/show/%s' % pid)
        try:
            mainbar = self.driver.find_element_by_class_name('problem')
            source = htmlmin.minify(mainbar.get_attribute(
                'innerHTML'), remove_empty_space=True)
            bs = BeautifulSoup(source, 'html.parser')
            contents = bs.findAll('div', class_='content')
            content = contents[0].text
            input_ = contents[1].text
            output = contents[2].text
            sample_input = contents[3].text
            sample_output = contents[4].text
            limits = contents[5].text
            return {
                'status': 'success',
                'msg': 'success',
                'problem': {
                    'content': content,
                    'input': input_,
                    'output': output,
                    'sample_input': sample_input,
                    'sample_output': sample_output,
                    'limits': limits
                }
            }
        except Exception as error:
            return {
                'status': 'error',
                'msg': error
            }

    def quit(self):
        """Quit the webdriver."""
        self.driver.quit()


if __name__ == '__main__':
    username = input('Username: ')
    password = input('Password: ')
    spyder = Spyder(username, password)
    print('Logging in...')
    login = spyder.login()
    print('Login status:')
    pprint(login)
    print('Getting problem...')
    pprint(spyder.get_problem('1001'))
    spyder.quit()
