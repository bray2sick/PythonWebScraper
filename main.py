import os
import requests
from urllib.parse import urlparse, urlunparse, urljoin
from bs4 import BeautifulSoup
import uuid

def fetch_website(url):
    # Retrieve HTML content and CSS links from the specified URL
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            # URL is missing scheme, add 'https' as default
            url = urlunparse(('https',) + parsed_url[1:])
        
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad response status
        
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract all CSS links
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
    
def convert_html(html):
    # Convert the HTML content into a BeautifulSoup object for further operations.
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def save_html_and_css(soup, css_content, output_folder, filename):
    # Save the processed HTML and CSS content to the specified folders.
    html_folder = os.path.join(output_folder, "html")
    css_folder = os.path.join(output_folder, "css")
    os.makedirs(html_folder, exist_ok=True)  # Create the html folder if it doesn't exist
    os.makedirs(css_folder, exist_ok=True)  # Create the css folder if it doesn't exist
    
    # Save the HTML file
    html_filepath = os.path.join(html_folder, filename)
    if os.path.exists(html_filepath):
        filename = str(uuid.uuid4()) + ".html"
        html_filepath = os.path.join(html_folder, filename)
    
    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"\nHTML content saved to {html_filepath}")
    
    # Save the CSS files
    for css_url, css_text in css_content.items():
        css_filename = os.path.basename(urlparse(css_url).path)
        css_filepath = os.path.join(css_folder, css_filename)
        
        with open(css_filepath, 'w', encoding='utf-8') as f:
            f.write(css_text)
        print(f"CSS content saved to {css_filepath}")
    print("")

def main():
    # Execute the web scraping and saving process.
    
    while True:
        print("=" * 28)
        print("Python Web Scraper".center(28))
        print("=" * 28)
        print("1. Scrape")
        print("2. Exit")
        print("=" * 28)

        choice = input("Enter your choice: ").strip()
        
        if choice == '1':
            url_input = input("Enter the URL: ").strip()
            
            if not url_input.startswith('http'):
                url_input = 'https://' + url_input
            
            filename_input = input("Enter the filename to save (without extension): ").strip() + ".html"
            
            output_folder = os.getcwd()  # Use the current working directory
            
            html_content, css_content = fetch_website(url_input)
            
            if html_content:
                processed_html = convert_html(html_content)
                save_html_and_css(processed_html, css_content, output_folder, filename_input)
        
        elif choice == '2':
            print("\nExiting...\n")
            break
        
        else:
            print("\nInvalid option. Please enter 1 or 2.\n")

if __name__ == "__main__":
    main()
