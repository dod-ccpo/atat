#! .venv/bin/python

import os
import sys

script_directory = os.path.dirname(__file__)
project_directory = os.path.join(script_directory, "../")
parent_dir = os.path.abspath(project_directory)
sys.path.append(parent_dir)

from atat.app import make_app, make_config
import base64
import re
from urllib.parse import urlparse
import argparse
from bs4 import BeautifulSoup
import subprocess


# how large the html file can be before showing a warning message
HTML_FILE_SIZE_LIMIT = 1024 * 1024

# refer to https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
# for additional mime types
mime_types = {
    ".woff2": "font/woff2",
    ".woff": "font/woff",
    ".svg": "image/svg+xml",
    ".ico": "image/vnd.microsoft.icon",
    ".eot": "application/vnd.ms-fontobject",
    ".ttf": "font/ttf",
}

# These are the font files required to load this page.  IE 11 increases this list
# by about 2/3rds.
css_asset_whitelist = {
    # woff2
    "sourcesanspro-bold-webfont.*woff2",
    "sourcesanspro-regular-webfont.*woff2",
    "sourcesanspro-light-webfont.*woff2",
    "sourcesanspro-italic-webfont.*woff2",
    # woff
    "sourcesanspro-light-webfont.*woff",
    "sourcesanspro-bold-webfont.*woff",
    "sourcesanspro-italic-webfont.*woff",
    # eot
    "merriweather-light-webfont.*eot",
    "merriweather-italic-webfont.*eot",
    "merriweather-bold-webfont.*eot",
    "merriweather-regular-webfont.*eot",
    "sourcesanspro-regular-webfont.*eot",
    "sourcesanspro-light-webfont.*eot",
    "sourcesanspro-italic-webfont.*eot",
    "sourcesanspro-bold-webfont.*eot",
    # ttf
    "sourcesanspro-light-webfont.*ttf",
    "sourcesanspro-bold-webfont.*ttf",
    "sourcesanspro-italic-webfont.*ttf",
}


def relative_path(file_path):
    return urlparse(file_path.strip()).path[1:]


def file_ext(file_path):
    return os.path.splitext(file_path)[1]


def make_base64(file_path):
    file_path = relative_path(file_path)
    mime_type = mime_types[file_ext(file_path)]

    print(f"  {file_path}")

    with open(file_path, "rb") as fh:
        data = fh.read()

    if mime_types[".svg"] == mime_type:
        encoding = "utf-8"
    else:
        data = base64.b64encode(data)
        encoding = "base64"

    return f"data:{mime_type};{encoding},{data.decode('utf-8')}"


def render_template():
    config = make_config()
    app = make_app(config)
    with app.app_context():
        template = app.jinja_env.get_template("under_maintenance.html")
        return BeautifulSoup(template.render(), "html.parser")


def encode_images(soup):
    print("Encoding img assets...")
    for img in soup.find_all("img"):
        img["src"] = make_base64(img["src"])


def encode_css(soup):
    print("Encoding css assets...")
    css_whitelist_pattern = "|".join(css_asset_whitelist)
    url_pattern = re.compile(r"url\(\"*([a-z0-9/.\-#?]+)\"*\)")
    css_link_elements = (
        l for l in soup.find_all("link") if file_ext(l["href"]) == ".css"
    )

    for link in css_link_elements:
        with open(relative_path(link["href"])) as fh:
            # remove all comments, including reference to css map file
            css_str = re.sub(r"/\*.*?\*/", "", fh.read().strip(), flags=re.S)

        # encode all css assets that have been whitelisted
        for url_match in url_pattern.finditer(css_str):
            if re.search(css_whitelist_pattern, url_match.group(1)):
                css_str = css_str.replace(
                    url_match.group(0), f"url({make_base64(url_match.group(1))})"
                )

        # inject css into head of html
        style = soup.new_tag("style")
        style.string = css_str
        soup.head.append(style)

        # remove css element from html
        link.decompose()


def encode_other_link_elements(soup):
    # this is usually the ico file...
    print("Encoding other link assets...")
    non_css_link_elements = (
        l for l in soup.find_all("link") if file_ext(l["href"]) != ".css"
    )
    for link in non_css_link_elements:
        link["href"] = make_base64(link["href"])


def remove_javascript(soup):
    for script in soup.find_all("script"):
        script.decompose()


def file_is_too_large(html_file):
    return os.stat(html_file).st_size > HTML_FILE_SIZE_LIMIT


def yarn_build():
    process = subprocess.Popen(["yarn", "build"])
    process.communicate()
    if process.returncode:
        exit(1)


def main(output):
    yarn_build()

    soup = render_template()

    encode_images(soup)
    encode_css(soup)
    encode_other_link_elements(soup)
    remove_javascript(soup)

    # write html to file
    html_file = os.path.join(output, "index.html")
    with open(html_file, "w") as fh:
        fh.write(str(soup))

    # print warning if html file is too large
    if file_is_too_large(html_file):
        print(
            f"Warning: Under Maintenance HTML file is larger then {HTML_FILE_SIZE_LIMIT} Bytes.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Under Maintenance Page")
    default_output = "./"
    parser.add_argument(
        "--output",
        help=f"Directory where file will be written. (default: {default_output})",
        default=default_output,
    )
    args = parser.parse_args()
    main(args.output)
