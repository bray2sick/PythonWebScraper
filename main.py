# Standard Python libraries
import os
import requests
import uuid

# Third-party libraries
from urllib.parse import urlparse, urlunparse, urljoin
from bs4 import BeautifulSoup

def fetch_website(url):
    try:
        # Process the URL to ensure it includes a scheme
        process_url = urlparse(url)
        if not process_url.scheme:
            # Add 'https' as the default scheme if missing
            url = urlunparse(('https',) + process_url[1:])
        
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Process the HTML content using BeautifulSoup
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all CSS link elements
        css_links = soup.find_all('link', rel='stylesheet')
        # Fetch CSS content for each link
        css_content = {
            urljoin(url, css_link['href']): requests.get(urljoin(url, css_link['href'])).text
            for css_link in css_links
        }
        
        return soup, css_content
    except requests.exceptions.RequestException as e:
        # Print an error message if the request fails
        print(f"Error fetching {url}: {e}")
        return None, None

def save_content(soup, css_content, output_folder, filename):
    # Define the folders for HTML and CSS
    html_folder = os.path.join(output_folder, "html")
    css_folder = os.path.join(output_folder, "css")
    # Create the html folder if it doesn't exist
    os.makedirs(html_folder, exist_ok=True)
    # Create the css folder if it doesn't exist
    os.makedirs(css_folder, exist_ok=True)
    
    # Define the path to save the HTML file
    html_filepath = os.path.join(html_folder, filename)
    if os.path.exists(html_filepath):
        # Ensure unique filenames to avoid overwriting
        filename = str(uuid.uuid4()) + ".html"
        html_filepath = os.path.join(html_folder, filename)
    
    # Save the HTML content to the file
    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"\nHTML content saved to {html_filepath}")
    
    # Save each CSS content to its respective file
    for css_url, css_text in css_content.items():
        css_filename = os.path.basename(urlparse(css_url).path)
        css_filepath = os.path.join(css_folder, css_filename)
        # Open the CSS file in write mode with UTF-8 encoding
        with open(css_filepath, 'w', encoding='utf-8') as f:
            f.write(css_text)
        # Print a confirmation message with the path to the saved CSS file    
        print(f"CSS content saved to {css_filepath}")

def main():
    while True:
        # Display menu options
        print("=" * 28)
        print("Python Web Scraper".center(28))
        print("=" * 28)
        print("1. Scrape")
        print("2. Exit")
        print("=" * 28)
        
        # Get user choice
        choice = input("Enter your choice: ").strip()
        
        if choice == '1':
            # Get URL input from the user
            url_input = input("Enter the URL: ").strip()
            if not url_input.startswith('http'):
                # Add 'https://' prefix if the URL doesn't start with 'http'
                url_input = 'https://' + url_input
                
            # Get filename input from the user
            filename_input = input("Enter the filename to save (without extension): ").strip() + ".html"
            # Use the current working directory as the output folder
            output_folder = os.getcwd()
            
            # Fetch website's HTML and CSS content
            soup, css_content = fetch_website(url_input)
            
            if soup:
                # Save the HTML and CSS content to files
                save_content(soup, css_content, output_folder, filename_input)
        elif choice == '2':
            # Exit the program
            print("\nExiting...\n")
            break
        else:
            # Print an error message for invalid options
            print("\nInvalid option. Please enter 1 or 2.\n")

if __name__ == "__main__":
    # Run the main function if the script is executed directly
    main()
