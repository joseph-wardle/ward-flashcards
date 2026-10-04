"""Scrape member names and photos from directory.churchofjesuschrist.org."""

from collections.abc import Iterator
from contextlib import contextmanager

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, Page, Response, sync_playwright

from members import Member, save_photo

DIRECTORY_URL = "https://directory.churchofjesuschrist.org"

# The directory site uses generated CSS class names, which can change whenever the
# site is redeployed. If scraping stops working, these are the first thing to check.
HOUSEHOLD_LINK = "a[href*='/households/']"
MEMBER_LINK = "a.AOftt[href*='/members/']"
MEMBER_NAME = "h1.eGmzRN"
MEMBER_PHOTO = "img[src*='photos/members/']"
PHOTO_VIEWER_IMAGE = "img.bonSxs[src*='photos/members/']"
PHOTO_VIEWER_CLOSE = "button.ghvXqF"
DIALOG_CLOSE = "button.FLjuw"


@contextmanager
def open_directory() -> Iterator[Page]:
    """Open the directory in a browser window and wait for the user to sign in there."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(DIRECTORY_URL)
        print("Sign in to your church account in the browser window.")
        page.wait_for_selector(HOUSEHOLD_LINK, timeout=0)  # No time limit to sign in.
        yield page


def list_households(page: Page) -> dict[str, Locator]:
    """Return {household id: link} for every household in the directory."""
    links = page.locator(HOUSEHOLD_LINK)
    # The list renders in pieces; wait until it stops growing so none are missed.
    count = -1
    while count != links.count():
        count = links.count()
        page.wait_for_timeout(1000)
    return {str(links.nth(i).get_attribute("href")): links.nth(i) for i in range(count)}


def scrape_household(page: Page, household_link: Locator) -> list[Member]:
    household_link.click()
    member_links = page.locator(MEMBER_LINK)
    member_links.first.wait_for(timeout=1000)

    members: list[Member] = []
    for i in range(member_links.count()):
        member = scrape_member(page, member_links.nth(i))
        if member is not None:
            members.append(member)

    page.locator(DIALOG_CLOSE).click()
    return members


def scrape_member(page: Page, member_link: Locator) -> Member | None:
    member_link.click()
    page.get_by_text("View Household").wait_for(state="visible")
    name = (page.locator(MEMBER_NAME).text_content() or "").strip()
    photo = download_photo(page)
    page.locator(DIALOG_CLOSE).first.click()

    if not name:
        return None
    print(name if photo else f"{name} (no photo)")
    return Member(name, save_photo(name, photo) if photo else None)


def download_photo(page: Page) -> bytes | None:
    """Open the member's photo viewer, capture the full-size photo, and close the viewer."""
    photo = None
    try:
        with page.expect_response(is_full_size_photo, timeout=2000) as response:
            page.locator(MEMBER_PHOTO).click(timeout=1000)
        photo = response.value.body()
        page.locator(PHOTO_VIEWER_IMAGE).wait_for()
        page.locator(PHOTO_VIEWER_CLOSE).last.click()
    except PlaywrightError:
        pass  # No photo (nothing to click), or the viewer misbehaved after we got one.
    return photo


def is_full_size_photo(response: Response) -> bool:
    return (
        "photos/members/" in response.url
        and "?thumbnail=true" not in response.url
        and response.status == 200
    )
