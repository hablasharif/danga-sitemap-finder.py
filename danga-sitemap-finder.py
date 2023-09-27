import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pyperclip
import csv
import datetime

# Define a user agent to simulate a web browser
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

@st.cache_data
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

@st.cache_data
def extract_all_urls_from_sitemap(sitemap_url):
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

        except requests.exceptions.RequestException as e:
            pass

    extract_recursive(sitemap_url)
    return url_list

def filter_urls(url_list):
    filtered_urls = []
    removed_urls = []

    # Patterns to filter out
    filter_patterns = [
        "/casts/",
        "/cast/",
        "/directors/",
        "/director/",
        "/artist/",
        "/artists/",
        "/actors/",
        "/actor/",
        "/tag/",
        "/tags/",
        "/country/",
        "/genre/",
        "/stars/",
        "/release-year/",
        "/quality/",
        "/episode-date/",
        "/category/",
        "/lang/",
        "/year/",
        "/index/",
        "/network/",
        "/blog-tag/",
        "/blog-category/",
        "/archive/",
        "/sitemap-",
        "/author/",
        "/writer/",
        "/director_tv/",
        "/cast_tv/",
        ".xml",
        ".jpg"
    ]

    # Extensions to filter out
    filter_extensions = [".jpg", ".png", ".webp", ".xml"]

    for url in url_list:
        # Check if the URL contains any filter patterns
        if any(pattern in url for pattern in filter_patterns):
            removed_urls.append(url)
        else:
            # Check if the URL has a valid extension
            parsed_url = urlparse(url)
            url_path = parsed_url.path
            file_extension = url_path.split(".")[-1].lower()
            if file_extension not in filter_extensions:
                filtered_urls.append(url)

    return filtered_urls, removed_urls

def main():
    st.title("Sitemap URL Extractor")

    domain_input = st.text_area("Enter multiple domains (one per line):")
    domains = [domain.strip() for domain in domain_input.split("\n") if domain.strip()]  # Split input by lines

    all_url_list = []  # Initialize the list to store URLs

    if st.button("Extract URLs"):
        if domains:
            for domain in domains:
                # Ensure the domain is properly formatted
                if not domain.startswith("http://") and not domain.startswith("https://"):
                    domain = "https://" + domain  # Add HTTPS if missing

                sitemap_url = extract_sitemap_url(domain)
                
                if sitemap_url:
                    url_list = extract_all_urls_from_sitemap(sitemap_url)
                    total_urls = len(url_list)  # Count total URLs

                    if url_list:
                        st.success(f"Found {total_urls} URLs in the sitemap of {domain}:")
                        st.text_area(f"URLs from {domain}", "\n".join(url_list))  # Display URLs in a text area
                        all_url_list.extend(url_list)
                    else:
                        st.error(f"Failed to retrieve or extract URLs from {domain}.")

    # Button to copy all URLs to clipboard
    if st.button("Copy All URLs"):
        if all_url_list:
            # Join all URLs into a single string with line breaks
            all_urls_text = "\n".join(all_url_list)
            # Copy all the URLs to the clipboard
            pyperclip.copy(all_urls_text)
            st.success("All URLs copied to clipboard.")

    # Button to download URLs as a CSV file
    if domains:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %A %I-%M-%p")
        # Create a formatted file name with inputted domains and timestamp
        formatted_domains = " ".join(domain.replace("https://", "").replace("http://", "") for domain in domains)
        unfiltered_filename = f"Unfiltered URLs {formatted_domains} {timestamp}.csv"

        # Create a download button for unfiltered URLs
        download_button_unfiltered = st.download_button(
            label="Download Unfiltered URLs as CSV",
            data="\n".join(all_url_list),
            key="download_button_unfiltered",
            file_name=unfiltered_filename,
        )

        # Filter the URLs
        filtered_urls, removed_urls = filter_urls(all_url_list)

        # Create a formatted file name for removed URLs
        removed_filename = f"Removed URLs {formatted_domains} {timestamp}.csv"

        # Create a download button for removed URLs
        download_button_removed = st.download_button(
            label="Download Removed URLs as CSV",
            data="\n".join(removed_urls),
            key="download_button_removed",
            file_name=removed_filename,
        )

        # Create a formatted file name for filtered URLs
        filtered_filename = f"Filtered URLs {formatted_domains} {len(filtered_urls)} {timestamp}.csv"

        # Create a download button for filtered URLs
        download_button_filtered = st.download_button(
            label=f"Download Filtered URLs as CSV ({len(filtered_urls)} URLs)",
            data="\n".join(filtered_urls),
            key="download_button_filtered",
            file_name=filtered_filename,
        )

if __name__ == "__main__":
    main()

# Create a link to the external URL
url = "https://website-titles-and-h1-tag-checke.streamlit.app/"
link_text = "VISIT THIS IF YOU WANT TO PULL WEBSITE ALL TITLES AND H1 TAG TITLE THEN VISIT THIS"

# Display the link
st.markdown(f"[{link_text}]({url})")
