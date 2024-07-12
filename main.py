import os
import requests
from urllib.parse import urlparse, urlunparse, urljoin
from bs4 import BeautifulSoup
import uuid

def fetch_website(url):
    # Function to retrieve HTML content and CSS links from a specified URL.
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            # URL is missing scheme, add 'https' as default
            url = urlunparse(('https',) + parsed_url[1:])
        
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad response status
        
        # Parse HTML content
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all CSS links
        css_links = soup.find_all('link', rel='stylesheet')
        css_content = {}
        
        for css_link in css_links:
            css_url = urljoin(url, css_link['href'])
            css_response = requests.get(css_url)
            css_response.raise_for_status()
            css_content[css_url] = css_response.text
        
        return html_content, css_content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None, None
    
def process_html(html):
    # Function to process HTML content for further operations.
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def save_html_and_css(soup, css_content, output_folder, filename):
    # Function to save processed HTML and CSS content to specified folders.
    html_folder = os.path.join(output_folder, "html")
    css_folder = os.path.join(output_folder, "css")
    os.makedirs(html_folder, exist_ok=True)  # Create html folder
    os.makedirs(css_folder, exist_ok=True)  # Create css folder
    
    # Save HTML file
    html_filepath = os.path.join(html_folder, filename)
    if os.path.exists(html_filepath):
        filename = str(uuid.uuid4()) + ".html"
        html_filepath = os.path.join(html_folder, filename)
    
    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"HTML content saved to {html_filepath}")
    
    # Save CSS files
    for css_url, css_text in css_content.items():
        css_filename = os.path.basename(urlparse(css_url).path)
        css_filepath = os.path.join(css_folder, css_filename)
        
        with open(css_filepath, 'w', encoding='utf-8') as f:
            f.write(css_text)
        print(f"CSS content saved to {css_filepath}")

if __name__ == "__main__":
    # Prompt user for URL input
    url_input = input("Enter the URL: ").strip()  # Strip to remove any extra spaces
    
    # Check if 'https://' prefix is missing, add it if necessary
    if not url_input.startswith('http'):
        url_input = 'https://' + url_input
    
    # Prompt user for filename input
    filename_input = input("Enter the filename to save (without extension): ").strip() + ".html"
    
    # Define output folder (root directory)
    output_folder = os.getcwd()  # Current working directory
    
    # Fetch HTML content and CSS from the specified URL.
    html_content, css_content = fetch_website(url_input)
    
    # If HTML content is fetched successfully, prepare it for processing and save
    if html_content:
        processed_html = process_html(html_content)
        save_html_and_css(processed_html, css_content, output_folder, filename_input)
