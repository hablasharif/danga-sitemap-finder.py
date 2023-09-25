import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pyperclip

# Define a user agent to simulate a web browser
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

def extract_sitemap_url(domain):
    sitemap_urls = [
        urljoin(domain, "sitemap.xml"),
        urljoin(domain, "sitemap_index.xml"),
        urljoin(domain, "sitemap_gn.xml")
    ]
    
    for sitemap_url in sitemap_urls:
        try:
            # Send an HTTP GET request with the user agent
            headers = {"User-Agent": user_agent}
            response = requests.get(sitemap_url, headers=headers)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                return sitemap_url  # Return the first found sitemap URL
        except requests.exceptions.RequestException as e:
            pass

    return None  # Return None if none of the sitemap URLs were found

def extract_robots_txt(domain):
    robots_txt_url = urljoin(domain, "robots.txt")
    try:
        # Send an HTTP GET request with the user agent
        headers = {"User-Agent": user_agent}
        response = requests.get(robots_txt_url, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return response.text
    except requests.exceptions.RequestException as e:
        pass

    return None  # Return None if robots.txt was not found

def extract_all_urls_from_sitemap(sitemap_url, progress_callback=None):
    url_list = []

    def extract_recursive(sitemap_url):
        try:
            # Send an HTTP GET request with the user agent
            headers = {"User-Agent": user_agent}
            response = requests.get(sitemap_url, headers=headers)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the XML content of the sitemap
                soup = BeautifulSoup(response.text, "xml")

                # Find all URL elements within the sitemap
                url_elements = soup.find_all("loc")

                # Extract and add the URLs to the list
                urls = [url.text for url in url_elements]
                url_list.extend(urls)

                # Look for sub-sitemap references (sitemapindex)
                sitemapindex_elements = soup.find_all("sitemap")
                for sitemapindex_element in sitemapindex_elements:
                    sub_sitemap_url = sitemapindex_element.find("loc").text
                    extract_recursive(sub_sitemap_url)

                # Update progress
                if progress_callback:
                    progress_callback(len(url_list))
        except requests.exceptions.RequestException as e:
            pass

    extract_recursive(sitemap_url)
    return url_list

def main():
    st.title("Sitemap URL Extractor")

    domain_input = st.text_area("Enter multiple domains (one per line):")
    domains = [domain.strip() for domain in domain_input.split("\n") if domain.strip()]  # Split input by lines

    if st.button("Extract URLs"):
        if domains:
            all_url_list = []  # Store URLs from all domains

            for domain in domains:
                # Ensure the domain is properly formatted
                if not domain.startswith("http://") and not domain.startswith("https://"):
                    domain = "https://" + domain  # Add HTTPS if missing

                sitemap_url = extract_sitemap_url(domain)
                
                if sitemap_url:
                    url_list = extract_all_urls_from_sitemap(sitemap_url)
                    total_urls = len(url_list)  # Count total URLs

                    progress_text = st.empty()  # Create an empty element for progress text

                    def update_progress(progress):
                        percentage = (progress / total_urls) * 100
                        progress_text.text(f"{progress} out of {total_urls} URLs ({percentage:.2f}% completed)...")

                    with st.spinner(f"Extracting URLs from {domain}..."):
                        url_list = extract_all_urls_from_sitemap(sitemap_url, progress_callback=update_progress)

                    if url_list:
                        st.success(f"Found {total_urls} URLs in the sitemap of {domain}:")
                        st.text_area(f"URLs from {domain}", "\n".join(url_list))  # Display URLs in a text area
                        all_url_list.extend(url_list)
                    else:
                        st.error(f"Failed to retrieve or extract URLs from {domain}'s sitemap.")
                        progress_text.empty()  # Clear the progress text if extraction fails
                else:
                    st.error(f"No sitemap found for {domain}.")
                
                # Check for robots.txt
                robots_txt_content = extract_robots_txt(domain)
                if robots_txt_content:
                    st.success(f"robots.txt for {domain}:")
                    st.text_area(f"robots.txt from {domain}", robots_txt_content)  # Display robots.txt
                else:
                    st.warning(f"No robots.txt found for {domain}.")

            if all_url_list:
                # Add a "Copy All URLs" button
                if st.button("Copy All URLs"):
                    # Join all URLs into a single string with line breaks
                    all_urls_text = "\n".join(all_url_list)
                    # Copy all the URLs to the clipboard
                    pyperclip.copy(all_urls_text)
                    st.success("All URLs copied to clipboard.")

if __name__ == "__main__":
    main()


# Create a link to the external URL
url = "https://website-titles-and-h1-tag-checke.streamlit.app/"
link_text = "VISIT THIS IF YOU WANT TO PULL WEBSITE  ALL  TITLES AND H1 TAG TITLE THEN VISIT THIS"

# Display the link
st.markdown(f"[{link_text}]({url})")
