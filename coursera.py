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

    script_content = page_content.find('script', attrs={'type': 'application/ld+json'})
    date_start = None
    if script_content:
        date_start = json.loads(script_content.text)['@graph'][1]['hasCourseInstance']['startDate']

    rating = page_content.select_one('div.CourseRating span')
    return {
        'title': page_content.select_one('div.Banner .BannerTitle h1').text,
        'rating': rating.text if rating else '-',
        'language': page_content.select('div.ProductGlance div h4')[-1].text,
        'date_start': date_start if date_start else '-',
        'count_week': len(page_content.select('div.leftColumn_1rt24er')),
    }


def output_courses_info_to_xlsx(filepath, courses):
    work_book = Workbook()
    work_sheet = work_book.active

    for course in courses:
        work_sheet.append(list(course.values()))

    save_workbook(work_book, filepath)


def save_workbook(work_book, filepath):
    work_book.save(filepath)


if __name__ == '__main__':
    main()
