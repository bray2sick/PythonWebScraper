# main.py

import os  # For file and directory operations
import requests  # For making HTTP requests
import uuid  # For generating unique filenames

from urllib.parse import urlparse, urlunparse, urljoin  # For URL manipulation
from bs4 import BeautifulSoup  # For processing HTML content

def find_website(url):
    try:
        process_url = urlparse(url)
        if not process_url.scheme:  # Check if the scheme (http/https) is missing
            url = urlunparse(('https',) + process_url[1:])  # Add 'https' as the default scheme if missing
        
        response = requests.get(url)
        response.raise_for_status()
        
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        css_links = soup.find_all('link', rel='stylesheet')  # Find all <link> tags with rel="stylesheet"
        css_content = {
            urljoin(url, css_link['href']): requests.get(urljoin(url, css_link['href'])).text
            for css_link in css_links
        }
        
        return soup, css_content
    except requests.exceptions.RequestException as e:
        print(f"Error finding {url}: {e}") 
        return None, None

def save_content(soup, css_content, output_folder, filename):
    html_folder = os.path.join(output_folder, "html")
    css_folder = os.path.join(output_folder, "css")
    os.makedirs(html_folder, exist_ok=True)  # Ensure the HTML folder exists
    os.makedirs(css_folder, exist_ok=True)  # Ensure the CSS folder exists
    
    html_filepath = os.path.join(html_folder, filename)
    if os.path.exists(html_filepath):
        filename = str(uuid.uuid4()) + ".html"  # Generate a unique filename
        html_filepath = os.path.join(html_folder, filename)
    
    with open(html_filepath, 'w', encoding='utf-8') as f:  # Open the file in write mode
        f.write(str(soup))
    print(f"\nHTML content saved to {html_filepath}")
    
    for css_url, css_text in css_content.items():  # Loop through each CSS content
        css_filename = os.path.basename(urlparse(css_url).path)
        css_filepath = os.path.join(css_folder, css_filename)
        with open(css_filepath, 'w', encoding='utf-8') as f:
            f.write(css_text)
        print(f"CSS content saved to {css_filepath}")
    print("")

def main():
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
                url_input = 'https://' + url_input  # Add 'https://' prefix if the URL doesn't start with 'http'
                
            filename_input = input("Enter the filename to save (without extension): ").strip() + ".html"
            output_folder = os.getcwd()
            
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
