#!/usr/bin/env python
# In[ ]:
#  coding: utf-8

###### Searching and Downloading Google Images to the local disk ######

# Import Libraries
import argparse
import codecs
import datetime
import http.client
import json
import os
import re
import ssl
import sys
import time  # Importing the time library to check the time of code execution
import urllib.request
from http.client import BadStatusLine
from urllib.parse import quote
from urllib.request import HTTPError, Request, URLError, urlopen

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

http.client._MAXHEADERS = 1000
args_list = [
    "keywords",
    "keywords_from_file",
    "prefix_keywords",
    "suffix_keywords",
    "limit",
    "format",
    "color",
    "color_type",
    "usage_rights",
    "size",
    "exact_size",
    "aspect_ratio",
    "type",
    "time",
    "time_range",
    "delay",
    "url",
    "single_image",
    "output_directory",
    "image_directory",
    "no_directory",
    "proxy",
    "similar_images",
    "specific_site",
    "print_urls",
    "print_size",
    "print_paths",
    "metadata",
    "extract_metadata",
    "socket_timeout",
    "thumbnail",
    "thumbnail_only",
    "language",
    "prefix",
    "chromedriver",
    "related_images",
    "safe_search",
    "no_numbering",
    "offset",
    "no_download",
    "save_source",
    "silent_mode",
    "ignore_urls",
]


def user_input():
    config = argparse.ArgumentParser()
    config.add_argument(
        "-cf",
        "--config_file",
        help="config file name",
        default="",
        type=str,
        required=False,
    )
    config_file_check = config.parse_known_args()
    object_check = vars(config_file_check[0])

    records = []
    if object_check["config_file"] != "":
        json_file = json.load(open(config_file_check[0].config_file))
        for record in range(len(json_file["Records"])):
            arguments = {i: None for i in args_list}
            for key, value in json_file["Records"][record].items():
                arguments[key] = value
            records.append(arguments)
        len(records)
    else:
        # Taking command line arguments from users
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-k",
            "--keywords",
            help="delimited list input",
            type=str,
            required=False)
        parser.add_argument(
            "-kf",
            "--keywords_from_file",
            help="extract list of keywords from a text file",
            type=str,
            required=False,
        )
        parser.add_argument(
            "-sk",
            "--suffix_keywords",
            help="comma separated additional words added after to main keyword",
            type=str,
            required=False,
        )
        parser.add_argument(
            "-pk",
            "--prefix_keywords",
            help="comma separated additional words added before main keyword",
            type=str,
            required=False,
        )
        parser.add_argument(
            "-l",
            "--limit",
            help="delimited list input",
            type=str,
            required=False)
        parser.add_argument(
            "-f",
            "--format",
            help="download images with specific format",
            type=str,
            required=False,
            choices=["jpg", "gif", "png", "bmp", "svg", "webp", "ico"],
        )
        parser.add_argument(
            "-u",
            "--url",
            help="search with google image URL",
            type=str,
            required=False)
        parser.add_argument(
            "-x",
            "--single_image",
            help="downloading a single image from URL",
            type=str,
            required=False,
        )
        parser.add_argument(
            "-o",
            "--output_directory",
            help="download images in a specific main directory",
            type=str,
            required=False,
        )
        parser.add_argument(
            "-i",
            "--image_directory",
            help="download images in a specific sub-directory",
            type=str,
            required=False,
        )
        parser.add_argument(
            "-n",
            "--no_directory",
            default=False,
            help="download images in the main directory but no sub-directory",
            action="store_true",
        )
        parser.add_argument(
            "-d",
            "--delay",
            help="delay in seconds to wait between downloading two images",
            type=int,
            required=False,
        )
        parser.add_argument(
            "-co",
            "--color",
            help="filter on color",
            type=str,
            required=False,
            choices=[
                "red",
                "orange",
                "yellow",
                "green",
                "teal",
                "blue",
                "purple",
                "pink",
                "white",
                "gray",
                "black",
                "brown",
            ],
        )
        parser.add_argument(
            "-ct",
            "--color_type",
            help="filter on color",
            type=str,
            required=False,
            choices=["full-color", "black-and-white", "transparent"],
        )
        parser.add_argument(
            "-r",
            "--usage_rights",
            help="usage rights",
            type=str,
            required=False,
            choices=[
                "labeled-for-reuse-with-modifications",
                "labeled-for-reuse",
                "labeled-for-noncommercial-reuse-with-modification",
                "labeled-for-nocommercial-reuse",
            ],
        )
        parser.add_argument(
            "-s",
            "--size",
            help="image size",
            type=str,
            required=False,
            choices=[
                "large",
                "medium",
                "icon",
                ">400*300",
                ">640*480",
                ">800*600",
                ">1024*768",
                ">2MP",
                ">4MP",
                ">6MP",
                ">8MP",
                ">10MP",
                ">12MP",
                ">15MP",
                ">20MP",
                ">40MP",
                ">70MP",
            ],
        )
        parser.add_argument(
            "-es",
            "--exact_size",
            help='exact image resolution "WIDTH,HEIGHT"',
            type=str,
            required=False,
        )
        parser.add_argument(
            "-t",
            "--type",
            help="image type",
            type=str,
            required=False,
            choices=["face", "photo", "clipart", "line-drawing", "animated"],
        )
        parser.add_argument(
            "-w",
            "--time",
            help="image age",
            type=str,
            required=False,
            choices=[
                "past-24-hours",
                "past-7-days",
                "past-month",
                "past-year"],
        )
        parser.add_argument(
            "-wr",
            "--time_range",
            help='time range for the age of the image. should be in the format {"time_min":"YYYY-MM-DD","time_max":"YYYY-MM-DD"}',
            type=str,
            required=False,
        )
        parser.add_argument(
            "-a",
            "--aspect_ratio",
            help="comma separated additional words added to keywords",
            type=str,
            required=False,
            choices=["tall", "square", "wide", "panoramic"],
        )
        parser.add_argument(
            "-si",
            "--similar_images",
            help="downloads images very similar to the image URL you provide",
            type=str,
            required=False,
        )
        parser.add_argument(
            "-ss",
            "--specific_site",
            help="downloads images that are indexed from a specific website",
            type=str,
            required=False,
        )
        parser.add_argument(
            "-p",
            "--print_urls",
            default=False,
            help="Print the URLs of the images",
            action="store_true",
        )
        parser.add_argument(
            "-ps",
            "--print_size",
            default=False,
            help="Print the size of the images on disk",
            action="store_true",
        )
        parser.add_argument(
            "-pp",
            "--print_paths",
            default=False,
            help="Prints the list of absolute paths of the images",
            action="store_true",
        )
        parser.add_argument(
            "-m",
            "--metadata",
            default=False,
            help="Print the metadata of the image",
            action="store_true",
        )
        parser.add_argument(
            "-e",
            "--extract_metadata",
            default=False,
            help="Dumps all the logs into a text file",
            action="store_true",
        )
        parser.add_argument(
            "-st",
            "--socket_timeout",
            default=False,
            help="Connection timeout waiting for the image to download",
            type=float,
        )
        parser.add_argument(
            "-th",
            "--thumbnail",
            default=False,
            help="Downloads image thumbnail along with the actual image",
            action="store_true",
        )
        parser.add_argument(
            "-tho",
            "--thumbnail_only",
            default=False,
            help="Downloads only thumbnail without downloading actual images",
            action="store_true",
        )
        parser.add_argument(
            "-la",
            "--language",
            default=False,
            help="Defines the language filter. The search results are authomatically returned in that language",
            type=str,
            required=False,
            choices=[
                "Arabic",
                "Chinese (Simplified)",
                "Chinese (Traditional)",
                "Czech",
                "Danish",
                "Dutch",
                "English",
                "Estonian",
                "Finnish",
                "French",
                "German",
                "Greek",
                "Hebrew",
                "Hungarian",
                "Icelandic",
                "Italian",
                "Japanese",
                "Korean",
                "Latvian",
                "Lithuanian",
                "Norwegian",
                "Portuguese",
                "Polish",
                "Romanian",
                "Russian",
                "Spanish",
                "Swedish",
                "Turkish",
            ],
        )
        parser.add_argument(
            "-pr",
            "--prefix",
            default=False,
            help="A word that you would want to prefix in front of each image name",
            type=str,
            required=False,
        )
        parser.add_argument(
            "-px",
            "--proxy",
            help="specify a proxy address and port",
            type=str,
            required=False,
        )
        parser.add_argument(
            "-cd",
            "--chromedriver",
            help="specify the path to chromedriver executable in your local machine",
            type=str,
            required=False,
        )
        parser.add_argument(
            "-ri",
            "--related_images",
            default=False,
            help="Downloads images that are similar to the keyword provided",
            action="store_true",
        )
        parser.add_argument(
            "-sa",
            "--safe_search",
            default=False,
            help="Turns on the safe search filter while searching for images",
            action="store_true",
        )
        parser.add_argument(
            "-nn",
            "--no_numbering",
            default=False,
            help="Allows you to exclude the default numbering of images",
            action="store_true",
        )
        parser.add_argument(
            "-of",
            "--offset",
            help="Where to start in the fetched links",
            type=str,
            required=False,
        )
        parser.add_argument(
            "-nd",
            "--no_download",
            default=False,
            help="Prints the URLs of the images and/or thumbnails without downloading them",
            action="store_true",
        )
        parser.add_argument(
            "-iu",
            "--ignore_urls",
            default=False,
            help="delimited list input of image urls/keywords to ignore",
            type=str,
        )
        parser.add_argument(
            "-sil",
            "--silent_mode",
            default=False,
            help="Remains silent. Does not print notification messages on the terminal",
            action="store_true",
        )
        parser.add_argument(
            "-is",
            "--save_source",
            help="creates a text file containing a list of downloaded images along with source page url",
            type=str,
            required=False,
        )

        args = parser.parse_args()
        arguments = vars(args)
        records.append(arguments)
    return records


class googleimagesdownload:
    def __init__(self):
        pass

    @staticmethod
    def _extract_data_pack(page):
        start_line = page.find("AF_initDataCallback({key: \\'ds:1\\'") - 10
        start_object = page.find("[", start_line + 1)
        end_object = page.rfind(
            "]", 0, page.find(
                "</script>", start_object + 1)) + 1
        object_raw = str(page[start_object:end_object])
        return bytes(object_raw, "utf-8").decode("unicode_escape")

    @staticmethod
    def _extract_data_pack_extended(page):
        start_line = page.find("AF_initDataCallback({key: 'ds:1'") - 10
        start_object = page.find("[", start_line + 1)
        end_object = page.rfind(
            "]", 0, page.find(
                "</script>", start_object + 1)) + 1
        return str(page[start_object:end_object])

    @staticmethod
    def _extract_data_pack_ajax(data):
        lines = data.split("\n")
        return json.loads(lines[3])[0][2]

    @staticmethod
    def _image_objects_from_pack(data):
        image_objects = json.loads(data)[31][-1][12][2]
        image_objects = [x for x in image_objects if x[0] == 1]
        return image_objects

    # Downloading entire Web Document (Raw Page Content)
    def download_page(self, url):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
            }
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req)
            respData = str(resp.read())
        except BaseException:
            print(
                "Could not open URL. Please check your internet connection and/or ssl settings \n"
                "If you are using proxy, make sure your proxy settings is configured correctly")
            sys.exit()
        try:
            return (
                self._image_objects_from_pack(
                    self._extract_data_pack(respData)),
                self.get_all_tabs(respData),
            )
        except Exception as e:
            print(e)
            sys.exit()

    # Download Page for more than 100 images
    def download_extended_page(self, url, chromedriver):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")

        try:
            browser = webdriver.Chrome(chromedriver, chrome_options=options)
        except Exception as e:
            print(
                "Looks like we cannot locate the path the 'chromedriver' (use the '--chromedriver' "
                "argument to specify the path to the executable.) or google chrome browser is not "
                "installed on your machine (exception: %s)" %
                e)
            sys.exit()
        browser.set_window_size(1024, 768)

        # Open the link
        browser.get(url)
        browser.execute_script(
            """
            (function(XHR){
                "use strict";
                var open = XHR.prototype.open;
                var send = XHR.prototype.send;
                var data = [];
                XHR.prototype.open = function(method, url, async, user, pass) {
                    this._url = url;
                    open.call(this, method, url, async, user, pass);
                }
                XHR.prototype.send = function(data) {
                    var self = this;
                    var url = this._url;
                    function stateChanged() {
                        if (self.readyState == 4) {
                            console.log("data available for: " + url)
                            XHR.prototype._data.push(self.response);
                        }
                    }
                    if (url.includes("/batchexecute?")) {
                        this.addEventListener("readystatechange", stateChanged, false);
                    }
                    send.call(this, data);
                };
                XHR.prototype._data = [];
            })(XMLHttpRequest);
        """
        )

        time.sleep(1)
        print("Getting you a lot of images. This may take a few moments...")

        element = browser.find_element_by_tag_name("body")
        # Scroll down
        for i in range(50):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)

        try:
            browser.find_element_by_xpath(
                '//input[@value="Show more results"]').click()
            for _ in range(50):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)  # bot id protection
        except BaseException:
            for _ in range(10):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)  # bot id protection

        print("Reached end of Page.")
        time.sleep(0.5)

        source = browser.page_source  # page source
        images = self._image_objects_from_pack(
            self._extract_data_pack_extended(source))

        ajax_data = browser.execute_script(
            "return XMLHttpRequest.prototype._data")
        for chunk in ajax_data:
            images += self._image_objects_from_pack(
                self._extract_data_pack_ajax(chunk))

        # close the browser
        browser.close()

        return images, self.get_all_tabs(source)

    # Correcting the escape characters for python2
    @staticmethod
    def replace_with_byte(match):
        return chr(int(match.group(0)[1:], 8))

    def repair(self, brokenjson):
        invalid_escape = re.compile(
            r"\\[0-7]{1,3}"
        )  # up to 3 digits for byte values up to FF
        return invalid_escape.sub(self.replace_with_byte, brokenjson)

    # Finding 'Next Image' from the given raw page
    @staticmethod
    def get_next_tab(s):
        start_line = s.find('class="dtviD"')
        if start_line == -1:  # If no links are found then give an error!
            return "no_tabs", "", 0
        start_line = s.find('class="dtviD"')
        start_content = s.find('href="', start_line + 1)
        end_content = s.find('">', start_content + 1)
        url_item = "https://www.google.com" + \
            str(s[start_content + 6: end_content])
        url_item = url_item.replace("&amp;", "&")

        start_line_2 = s.find('class="dtviD"')
        s = s.replace("&amp;", "&")
        start_content_2 = s.find(":", start_line_2 + 1)
        end_content_2 = s.find("&usg=", star
