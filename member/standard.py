from urllib.parse import urljoin

from playwright.sync_api import Locator, Page, Response, sync_playwright

from member.core import Member


def thumnbail_response_filter(response: Response) -> bool:
    return (
        "photos/members/" in response.url
        and "?thumbnail=true" in response.url
        and response.status == 200
    )


def quality_response_filter(response: Response) -> bool:
    return (
        "photos/members/" in response.url
        and "?thumbnail=true" not in response.url
        and response.status == 200
    )


def get_member(
    page: Page, member_link: Locator, base_url: str, quality_images: bool = True
) -> Member | None:
    member_link.click()
    page.get_by_text("View Household").wait_for(state="visible")
    name_selector = page.locator("h1.eGmzRN")
    name = name_selector.text_content()
    print(name)
    image_button_selector = page.locator("img[src*='photos/members/']")
    image_data = None
    try:
        response_filter = (
            quality_response_filter if quality_images else thumnbail_response_filter
        )
        with page.expect_response(
            response_filter,
            timeout=2000,
        ) as response_info:
            image_button_selector.click(timeout=1000)
        response = response_info.value
        image_data = response.body()

        image_selector = page.locator("img.bonSxs[src*='photos/members/']")
        image_src = image_selector.get_attribute("src")
        print(image_src)
        image_url = urljoin(base_url, image_src)
        image_close_button = page.locator("button.ghvXqF").last
        image_close_button.click()
    except Exception:
        print("no image")
        image_url = None
    if name is None:
        return None
    close_button = page.locator("button.FLjuw").first
    close_button.click()
    return Member(name=name, image_url=image_url, image_data=image_data)


def get_household(
    page: Page, household_link: Locator, base_url: str, quality_images: bool = True
) -> list[Member]:
    members: list[Member] = []
    household_link.click()
    member_selector = page.locator("a.AOftt[href*='/members/']")
    member_selector.first.wait_for(timeout=1000)
    for i in range(member_selector.count()):
        member_link = member_selector.nth(i)
        member = get_member(
            page, member_link, base_url=base_url, quality_images=quality_images
        )
        if member is not None:
            members.append(member)
    close_button = page.locator("button.FLjuw")
    close_button.click()
    return members


def get_directory_standard(
    username: str,
    password: str,
    start_index: int = 0,
    end_index: int = -1,
    quality_images: bool = True,
) -> list[Member]:
    members: list[Member] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://directory.churchofjesuschrist.org")

        page.fill('input[name="username"]', username)
        page.locator("#button-primary").click()
        page.fill('input[name="password"]', password)
        page.locator("#button-primary").click()

        page.wait_for_selector("#signInMenu")
        # now authenticated
        base_url = page.url
        selector = "a[href*='/households/']"
        page.wait_for_selector(selector)
        household_selector = page.locator(selector)
        link_count = household_selector.count()

        for i in range(link_count):
            if i < start_index or i > end_index:
                continue
            household_link = household_selector.nth(i)
            household_members = get_household(
                page=page, household_link=household_link, base_url=base_url
            )
            members.extend(household_members)

    return members
