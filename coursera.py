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
    url_xml_courses = 'https://www.coursera.org/sitemap~www~courses.xml'
    try:
        xml_content = download_xml_content(url_xml_courses)
        urls_courses = get_random_urls_courses_from_xml(xml_content)
        courses_info = [get_course_info(download_html_page_course(url_course)) for url_course in urls_courses]
    except requests.exceptions.RequestException as e:
        exit(e)

    output_courses_info_to_xlsx(namespace.filepath, courses_info)


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file')
    return parser


def download_xml_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def get_random_urls_courses_from_xml(xml_content, count=20):
    urlset = etree.XML(xml_content)
    return [random.choice(urlset).getchildren()[0].text for _ in range(count)]


def download_html_page_course(url_course):
    response = requests.get(url_course)
    response.raise_for_status()
    return response.text


def get_course_info(html_content):
    page_content = BeautifulSoup(html_content, 'html.parser')

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

    save_workbook(work_book, filepath)


def save_workbook(work_book, filepath):
    work_book.save(filepath)


if __name__ == '__main__':
    main()
