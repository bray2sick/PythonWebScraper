# main.py

import os  # For file and directory operations
import requests  # For making HTTP requests
import uuid  # For generating unique filenames

from urllib.parse import urlparse, urlunparse, urljoin  # For URL manipulation
from bs4 import BeautifulSoup  # For processing HTML content

def find_website(url):
    try:
        # Parse the provided URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = urlunparse(('https',) + parsed_url[1:])
            
        # Make an HTTP GET request to fetch the web page content
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the request failed
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        css_links = soup.find_all('link', rel='stylesheet')
        css_content = {
            urljoin(url, link['href']): requests.get(urljoin(url, link['href'])).text
            for link in css_links if 'href' in link.attrs
        }
        
        return soup, css_content
    except requests.RequestException as e:
        print(f"Error finding {url}: {e}")
        return None, None

def save_content(soup, css_content, output_folder, filename):
    html_folder = os.path.join(output_folder, "html")
    css_folder = os.path.join(output_folder, "css")
    os.makedirs(html_folder, exist_ok=True)  # Create the HTML folder if it doesn't exist
    os.makedirs(css_folder, exist_ok=True)  # Create the CSS folder if it doesn't exist
    
    html_filepath = os.path.join(html_folder, filename)
    # If the HTML file already exists, generate a unique filename
    if os.path.exists(html_filepath):
        filename = f"{uuid.uuid4()}.html"
        html_filepath = os.path.join(html_folder, filename)
    
    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"\nHTML content saved to {html_filepath}")
    
    for css_url, css_text in css_content.items():
        css_filename = os.path.basename(urlparse(css_url).path) or f"{uuid.uuid4()}.css"
        css_filepath = os.path.join(css_folder, css_filename)
        with open(css_filepath, 'w', encoding='utf-8') as f:
            f.write(css_text)
        print(f"CSS content saved to {css_filepath}")
    print("")

def main():
    while True:
        # Display the menu
        print("=" * 28)
        print("Python Web Scraper".center(28))
        print("=" * 28)
        print("1. Scrape")
        print("2. Exit")
        print("=" * 28)
        
        # Get user input for menu choice
        choice = input("Enter your choice: ").strip()
        
        if choice == '1':
            url_input = input("Enter the URL: ").strip()
            if not url_input.startswith('http'):
                url_input = 'https://' + url_input    # Add 'https://' prefix if the URL doesn't start with 'http'
            
            filename_input = input("Enter the filename to save (without extension): ").strip() + ".html"
            output_folder = os.getcwd()
            
            # Find and save the website content
            soup, css_content = find_website(url_input)
            
            if soup:
                save_content(soup, css_content, output_folder, filename_input)
        elif choice == '2':
            print("\nExiting...\n")
            break
        else:
            print("\nInvalid option. Please enter 1 or 2.\n")
            
if __name__ == "__main__":
    main()  # Call the main function
