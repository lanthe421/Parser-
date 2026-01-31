import re
import requests
import logging
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from typing import List, Set, Dict, Optional
from collections import deque

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class SiteParser:
    def __init__(self, start_url: str, max_pages: int = 50, timeout: int = 10):
        self.start_url = start_url
        self.parsed_start_url = urlparse(start_url)
        self.base_domain = self.parsed_start_url.netloc
        
        self.max_pages = max_pages
        self.timeout = timeout
        
        self.emails: Set[str] = set()
        self.phones: Set[str] = set()
        
        self.queue: deque = deque([start_url])
        self.visited: Set[str] = set()
        
        self.email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        
        self.phone_regex = re.compile(r'(?:\+?\d{1,3})?[-.\s]?\(?\d{2,5}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}(?:[-.\s]?\d{2,4})?')

    def _is_internal_link(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.netloc == '' or parsed.netloc == self.base_domain

    def _clean_phone(self, phone_raw: str) -> Optional[str]:
        clean = re.sub(r'[^\d+]', '', phone_raw)
        if len(clean) >= 7:
            return phone_raw.strip()
        return None

    def _extract_from_html(self, html_content: str):
        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = soup.get_text(separator=' ')

        found_emails = self.email_regex.findall(text_content)
        self.emails.update(found_emails)
        
        for a in soup.select('a[href^="mailto:"]'):
            email = a['href'].replace('mailto:', '').split('?')[0]
            if self.email_regex.match(email):
                self.emails.add(email)

        for a in soup.select('a[href^="tel:"]'):
            self.phones.add(a.get_text(strip=True) or a['href'].replace('tel:', ''))

        potential_phones = self.phone_regex.findall(text_content)
        for p in potential_phones:
            cleaned = self._clean_phone(p)
            if cleaned:
                if len(re.sub(r'\D', '', cleaned)) <= 15:
                    self.phones.add(cleaned)

        return soup

    def _get_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            
            absolute_url = urljoin(current_url, href)
            
            parsed_abs = urlparse(absolute_url)
            clean_url = parsed_abs.scheme + "://" + parsed_abs.netloc + parsed_abs.path
            
            if self._is_internal_link(absolute_url) and clean_url not in self.visited:
                links.append(clean_url)
        return links

    def run(self) -> Dict:
        pages_processed = 0

        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; ContactParser/1.0; +http://example.com)'
        }

        while self.queue and pages_processed < self.max_pages:
            url = self.queue.popleft()
            
            if url in self.visited:
                continue
            
            try:
                logging.info(f"Processing: {url}")
                response = requests.get(url, headers=headers, timeout=self.timeout)
                
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' not in content_type:
                    continue

                if response.status_code == 200:
                    self.visited.add(url)
                    pages_processed += 1
                    
                    soup = self._extract_from_html(response.text)
                    
                    new_links = self._get_links(soup, url)
                    self.queue.extend(new_links)
                else:
                    logging.warning(f"Status {response.status_code} for {url}")

            except requests.RequestException as e:
                logging.error(f"Error fetching {url}: {e}")
                self.visited.add(url) 

        return {
            "url": self.start_url,
            "emails": list(self.emails),
            "phones": list(self.phones)
        }

def parse_site(start_url: str) -> dict:
    parser = SiteParser(start_url)
    return parser.run()

if __name__ == "__main__":
    test_url = "https://github.com/" # Сайт для тестов
    result = parse_site(test_url)
    
    import json
    print(json.dumps(result, indent=4, ensure_ascii=False))