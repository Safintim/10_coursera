import requests
import argparse
import random
import json
from lxml import etree
from openpyxl import Workbook
from bs4 import BeautifulSoup


def main():
    parser = create_parser()
    namespace = parser.parse_args()
    URL_COURSES = 'https://www.coursera.org/sitemap~www~courses.xml'
    try:
        courses = get_courses(URL_COURSES)
        courses_info = [get_course_info(course) for course in courses]
    except requests.exceptions.RequestException as e:
        exit(e)

    output_courses_info_to_xlsx(namespace.filepath, courses_info)


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file')
    return parser


def get_courses(url, count=20):
    response = requests.get(url)
    response.raise_for_status()
    content = response.content
    urlset = etree.XML(content)
    return [random.choice(urlset).getchildren()[0].text for _ in range(count)]


def get_course_info(url_cource):
    print(url_cource)
    response = requests.get(url_cource)
    response.raise_for_status()
    content = response.text
    page_content = BeautifulSoup(content, 'html.parser')

    title_class = 'H2_1pmnvep-o_O-weightNormal_s9jwp5-o_O-fontHeadline_1uu0gyz max-text-width-xl m-b-1s'
    language_class = 'H4_1k76nzj-o_O-weightBold_uvlhiv-o_O-bold_1byw3y2 m-b-0'
    count_week_class = 'H1Xl_jd0thw-o_O-weightNormal_s9jwp5-o_O-fontHeadline_1uu0gyz text-secondary d-block m-y-1'
    rating_class = 'H4_1k76nzj-o_O-weightBold_uvlhiv-o_O-bold_1byw3y2 m-l-1s m-r-1 m-b-0'

    script_content = page_content.find('script', attrs={'type': 'application/ld+json'})
    date_start = None
    if script_content:
        date_start = json.loads(script_content.text)['@graph'][1]['hasCourseInstance']['startDate']

    rating = page_content.find(class_=rating_class)
    return [
        page_content.find(class_=title_class).text,
        rating.text if rating else '-',
        page_content.find_all(class_=language_class)[-1].text,
        date_start if date_start else '-',
        len(page_content.find_all(class_=count_week_class)),
    ]


def output_courses_info_to_xlsx(filepath, courses):
    work_book = Workbook()
    work_sheet = work_book.active
    header = ['title', 'rating', 'language', 'date_start', 'count_week']
    work_sheet.append(header)

    for course in courses:
        work_sheet.append(course)

    work_book.save(filepath)


if __name__ == '__main__':
    main()
