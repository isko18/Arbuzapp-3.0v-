from urllib.parse import urlparse, parse_qs

def parse_url_hash(url):
    # Parse the URL
    parsed_url = urlparse(url)
    # Extract the hash (fragment)
    hash_fragment = parsed_url.fragment
    # Parse the hash fragment into a dictionary
    hash_params = parse_qs(hash_fragment)
    return hash_params