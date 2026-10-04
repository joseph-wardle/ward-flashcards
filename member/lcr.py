from urllib.parse import urljoin

import bs4
from playwright.sync_api import sync_playwright

from member.core import Member


def get_member_lcr(member_url: str) -> Member:
    soup = bs4.BeautifulSoup(member_url, features="html.parser")
    name = ""
    image_url = ""
    name_element = soup.find(class_="name")
    if name_element is not None:
        name = name_element.get_text(strip=True)
    name_label = soup.find(
        lambda tag: tag.name == "dt" and "Preferred Name" in tag.text
    )
    if name_label is not None:
        name_element = name_label.find_next_sibling("dd")
        if name_element is not None:
            name_text = name_element.get_text(strip=True)
            if name_text != "":
                name = name_text

    image_url: str | None = None
    image_element = soup.find("img", class_="individual-thumbnail")
    if image_element is not None:
        url = image_element.get("src")
        if url is not None:
            image_url = str(url)

    gender = None
    gender_label = soup.find(lambda tag: tag.name == "dt" and "Gender" in tag.text)
    if gender_label is not None:
        gender_element = gender_label.find_next_sibling("dd")
        if gender_element is not None:
            gender = gender_element.get_text(strip=True)

    return Member(name=name, image_url=image_url, gender=gender)


def get_member_links_lcr(directory_html: str) -> list[str]:
    soup = bs4.BeautifulSoup(directory_html, features="html.parser")
    table = soup.find("table", class_="member-list")
    if table is None:
        return []
    member_rows = table.find_all("tr")
    member_links: list[str] = []
    for member_row in member_rows:
        name_data = member_row.find("td", class_="n")
        if name_data is None:
            continue
        name = name_data.find("member-card")
        if name is None:
            continue
        link_element = name.find("a", href=True)
        if link_element is None:
            continue
        link_url = link_element["href"]
        member_links.append(str(link_url))
    return member_links


def get_directory_lcr(
    username: str, password: str, start_index: int = 0, end_index: int = -1
):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://lcr.churchofjesuschrist.org/?lang=eng")

        page.fill('input[name="username"]', username)
        page.locator("#button-primary").click()
        page.fill('input[name="password"]', password)
        page.locator("#button-primary").click()

        page.wait_for_selector("#signInMenu")
        # now authenticated

        member_list_url = "https://lcr.churchofjesuschrist.org/records/member-list"
        page.goto(member_list_url)

        previous_height = 0

        while True:
            # Scroll to the bottom
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            # Wait for new content to load
            page.wait_for_timeout(1000)  # adjust if necessary

            # Check if we've reached the bottom
            current_height = page.evaluate("document.body.scrollHeight")
            if current_height == previous_height:
                break
            previous_height = current_height

        html = page.content()
        members: list[Member] = []
        for member_link in get_member_links_lcr(html)[start_index:end_index]:
            page.goto(urljoin(member_list_url, member_link))
            members.append(get_member_lcr(page.content()))
        return members
