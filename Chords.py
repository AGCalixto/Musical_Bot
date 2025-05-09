from bs4 import BeautifulSoup
from selenium import webdriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

temp_dir = tempfile.mkdtemp()
options.add_argument(f'--user-data-dir={temp_dir}')


def search_chords_link(song):
    driver = uc.Chrome(options=options)
    href = []
    song = song.lower()
    if ' ' in song:
        song = song.replace(' ', '%20')

    search_url = f'https://www.ultimate-guitar.com/search.php?search_type=title&value={song}'
    driver.get(search_url)
    WebDriverWait(driver, 5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    for link in soup.find_all('a', href=True):
        if 'tabs.ultimate-guitar.com' in link['href']:
            href.append(link['href'])

    return href if href else []


def fetch_chords(chords_link, iterations: int):
    if not chords_link:
        state = False
        return 'No chords found :(', state

    chords_link = chords_link[iterations] if chords_link else None
    driver = uc.Chrome(options=options)
    driver.get(chords_link)
    state = False

    try:
        chord_block = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'pre'))
        )

        state = True
        return (f'Chords found: \n Note: The Chords were obtained from Ultimate Guitar Website...'
                f'\n\n{chord_block.text}'), state
    except Exception as e:
        return f'❌ Could not find chords: {e}', state
    finally:
        driver.quit()


# --------------------TESTING PURPOSES------------------------------
if __name__ == '__main__':
    choice = input('Choose the song: \n')
    url = search_chords_link(choice)
    print(url)

    print(fetch_chords(url, 0))
