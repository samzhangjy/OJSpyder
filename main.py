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

    def submit(self, pid='', ans=''):
        """Submit a problem to the OJ

        This function auto submits the problem to the OJ system. You need to give
        the problem id and answer.

        Args:
            pid (str, optional): The problem id. Defaults to ''.
            ans (str, optional): The problem answer source code. Defaults to ''.

        Returns:
            dict: The status of submitting the problem. For example:
                When succeeded:
                {
                    'status': 'success',
                    'msg': 'success'
                }
                When failed:
                {
                    'status': 'error',
                    'msg': '<error message>'
                }
        """
        self.driver.get('http://oj.noi.cn/oj/#main/submit/%s' % pid)
        try:
            toggle = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'toggle_editor'))
            )
            toggle.click()
            editor = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'submit-editor'))
            )
            editor.send_keys(ans)
            submit = self.driver.find_element_by_id('submit_button')
            dropdown = self.driver.find_element_by_xpath(
                '//select[@name=\'language[SRC]\']/option[text()=\'c++\']')
            dropdown.click()
            submit.click()
            return {
                'status': 'success',
                'msg': 'success'
            }
        except Exception as error:
            return {
                'status': 'error',
                'msg': error
            }

    def get_status(self, pid=''):
        """Get problem status

        This function gets the given problem's status through OJ. It returns a list
        of all problems submitted by the current user and is the given pid.

        Args:
            pid (str, optional): The problem id. Defaults to ''.

        Returns:
            dict: The status of getting problem status. E.g:
                When succeeded:
                {
                    'status': 'success',
                    'msg': 'success',
                    'problems': [
                        {
                            'index': '<problem submit index>',
                            'pid': '<problem id>',
                            'user': '<problem submitter username>',
                            'status': '<problem status>',
                            'res': <problem result, max to 100, an integer>,
                            'time-cost': '<the time cost to run the program, in milseconds>',
                            'space-cost': '<the space cost to run the program, in kb>',
                            'language': '<the language of the program>',
                            'code-length': '<the program code length>',
                            'submit-time': '<the problem submit time>'
                        },
                        ...
                    ]
                }
                When failed:
                {
                    'status': 'error',
                    'msg': '<error message>'
                }
        """
        self.driver.get(
            'http://oj.noi.cn/oj/index.php/main/status?users%5B%5D={username}&problems%5B%5D={pid}'.format(username=self.username, pid=pid))
        try:
            table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'table')))
            source = htmlmin.minify(table.get_attribute(
                'innerHTML'), remove_empty_space=True)
            bs = BeautifulSoup(source, 'html.parser')
            trs = bs.find('tbody').findAll('tr')
            results = []
            for tr in trs:
                result = {}
                tds = tr.findAll('td')
                index = tds[0].text
                result['index'] = index
                pid = tds[1].find('a').text
                result['pid'] = pid
                user = tds[2].find('span').find('a').text
                result['user'] = user
                status = tds[3].find('a').find('span').text
                result['status'] = status
                try:
                    res = int(tds[3].find('a').findAll('span')[1].text)
                except IndexError:
                    res = 0
                result['res'] = res
                time_cost = tds[4].text
                result['time-cost'] = time_cost
                space_cost = tds[5].text
                result['space-cost'] = space_cost
                language = tds[6].find('a').text
                result['language'] = language
                code_length = tds[7].text
                result['code-length'] = code_length
                submit_time = tds[8].text
                result['submit-time'] = submit_time
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
    time.sleep(1)
    print('Getting problem...')
    ans = open('./1014-test.cpp', 'r').read()
    pprint(spyder.submit('1014', ans.replace('\t', '')))
    print('Getting problem status...')
    status = spyder.get_status('1014')
    pprint(status)
    spyder.quit()
