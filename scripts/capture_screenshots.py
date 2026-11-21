"""Capture pages from the seeded local demo site for the release ZIP."""
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "screenshots"
BASE_URL = "http://127.0.0.1:8000"


def wait_for_server(process):
    for _ in range(40):
        if process.poll() is not None:
            raise RuntimeError("Django development server stopped before becoming ready.")
        try:
            with urllib.request.urlopen(BASE_URL, timeout=2):
                return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.5)
    raise TimeoutError("Django development server did not become ready.")


def capture(page, filename, path):
    page.goto(f"{BASE_URL}{path}", wait_until="networkidle")
    page.screenshot(path=str(SCREENSHOTS / filename), full_page=True)
    print(f"Captured {filename}")


def login(page, username, password, expected_path):
    page.goto(f"{BASE_URL}/login/", wait_until="networkidle")
    page.locator('input[name="username"]').fill(username)
    page.locator('input[name="password"]').fill(password)
    page.locator('button[type="submit"]').click()
    page.wait_for_url(f"**{expected_path}", timeout=10000)


def main():
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["DJANGO_DEBUG"] = "True"
    env["ALLOWED_HOSTS"] = "127.0.0.1,localhost"

    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "127.0.0.1:8000", "--noreload"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    try:
        wait_for_server(server)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            public = browser.new_page(viewport={"width": 1440, "height": 1000})
            capture(public, "01-homepage.png", "/")
            capture(public, "02-registration.png", "/register/")
            capture(public, "03-login.png", "/login/")
            capture(public, "04-active-notices.png", "/notices/")

            student = browser.new_page(viewport={"width": 1440, "height": 1000})
            login(student, "demo.student", "DemoStudent@123", "/student-dashboard/")
            capture(student, "05-student-dashboard.png", "/student-dashboard/")
            capture(student, "06-student-leave.png", "/student/leave/")
            capture(student, "07-student-complaints.png", "/student/complaints/")

            rector = browser.new_page(viewport={"width": 1440, "height": 1000})
            login(rector, "demo.rector", "DemoRector@123", "/rector/registrations/")
            capture(rector, "08-rector-registrations.png", "/rector/registrations/")
            capture(rector, "09-room-management.png", "/rector/rooms/")
            capture(rector, "10-rector-leave.png", "/rector/leave/")
            capture(rector, "11-rector-complaints.png", "/rector/complaints/")
            capture(rector, "12-notice-management.png", "/staff/notices/")

            assistant = browser.new_page(viewport={"width": 1440, "height": 1000})
            login(assistant, "demo.assistant", "DemoAssistant@123", "/staff/notices/")
            capture(assistant, "13-assistant-rector-notices.png", "/staff/notices/")
            browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()

    print(f"Captured UI screenshots in {SCREENSHOTS}")


if __name__ == "__main__":
    main()
