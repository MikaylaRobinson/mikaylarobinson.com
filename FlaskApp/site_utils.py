import string

def make_url_slug(title):
    """Convert the title into url slug format"""
    url_slug = title.lower().strip()
    exclude = set(string.punctuation)
    url_slug = "".join(ch for ch in url_slug if ch not in exclude)
    url_slug = url_slug.replace(" ", "-")
    return url_slug

