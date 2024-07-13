# Importing necessary standard libraries
import os  # For file and directory operations
import requests  # For making HTTP requests
import uuid  # For generating unique filenames

# Importing third-party libraries
from urllib.parse import urlparse, urlunparse, urljoin  # For URL manipulation
from bs4 import BeautifulSoup  # For processing HTML content

def find_website(url):
    try:
        process_url = urlparse(url)
        if not process_url.scheme:  # Check if the scheme (http/https) is missing
            url = urlunparse(('https',) + process_url[1:])  # Add 'https' as the default scheme if missing
        
        response = requests.get(url)  # Find the content from the URL
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        html_content = response.text  # Get the HTML content as text
        soup = BeautifulSoup(html_content, 'html.parser')  # Create a BeautifulSoup object to process the HTML
        
        css_links = soup.find_all('link', rel='stylesheet')  # Find all <link> tags with rel="stylesheet"
        css_content = {
            urljoin(url, css_link['href']): requests.get(urljoin(url, css_link['href'])).text
            for css_link in css_links  # Find and store CSS content for each link
        }
        
        return soup, css_content  # Return the processed HTML content and the found CSS content
    except requests.exceptions.RequestException as e:
        print(f"Error finding {url}: {e}")  # Print an error message if the request fails
        return None, None  # Return None for both HTML and CSS content on error

def save_content(soup, css_content, output_folder, filename):
    html_folder = os.path.join(output_folder, "html")  # Path for HTML folder
    css_folder = os.path.join(output_folder, "css")  # Path for CSS folder
    os.makedirs(html_folder, exist_ok=True)  # Ensure the HTML folder exists
    os.makedirs(css_folder, exist_ok=True)  # Ensure the CSS folder exists
    
    html_filepath = os.path.join(html_folder, filename)  # Path for the HTML file
    if os.path.exists(html_filepath):  # Check if the file already exists
        filename = str(uuid.uuid4()) + ".html"  # Generate a unique filename
        html_filepath = os.path.join(html_folder, filename)  # Update the file path
    
    with open(html_filepath, 'w', encoding='utf-8') as f:  # Open the file in write mode
        f.write(str(soup))  # Write the HTML content
    print(f"\nHTML content saved to {html_filepath}")  # Print a confirmation message
    
    for css_url, css_text in css_content.items():  # Loop through each CSS content
        css_filename = os.path.basename(urlparse(css_url).path)  # Extract the filename from the URL
        css_filepath = os.path.join(css_folder, css_filename)  # Path for the CSS file
        with open(css_filepath, 'w', encoding='utf-8') as f:  # Open the CSS file in write mode with UTF-8 encoding
            f.write(css_text)  # Write the CSS content
        print(f"CSS content saved to {css_filepath}")# Print a confirmation message with the path to the saved CSS file    

def main():
    while True:
        # Display menu options
        print("=" * 28)
        print("Python Web Scraper".center(28))
        print("=" * 28)
        print("1. Scrape")
        print("2. Exit")
        print("=" * 28)
        
        choice = input("Enter your choice: ").strip()  # Get user choice
        
        if choice == '1':
            url_input = input("Enter the URL: ").strip()  # Get the URL from the user
            if not url_input.startswith('http'):  # Check if the URL starts with 'http'
                url_input = 'https://' + url_input  # Add 'https://' prefix if the URL doesn't start with 'http'
                
            filename_input = input("Enter the filename to save (without extension): ").strip() + ".html"  # Get the filename from the user
            output_folder = os.getcwd()# Use the current working directory as the output folder
            
            soup, css_content = find_website(url_input)  # Find website's HTML and CSS content
            
            if soup:
                save_content(soup, css_content, output_folder, filename_input)  # Save the HTML and CSS content to files
        elif choice == '2':
            print("\nExiting...\n")  # Exit the program
            break
        else:
            print("\nInvalid option. Please enter 1 or 2.\n")  # Print an error message for invalid options
            
if __name__ == "__main__":
    main()  # Call the main function
