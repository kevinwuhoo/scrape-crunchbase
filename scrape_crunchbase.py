import string
import requests
from bs4 import BeautifulSoup
import json
import glob
from multiprocessing import Pool
import sys

API_KEY = None  # your api key here
CRUNCHBASE_COMPANY_API = "http://api.crunchbase.com/v/1/company/%s.js?api_key=%s" 


company_urls = []

# iterate through all crunchbase companies by going a-z and "other"
for letter in list(string.lowercase) + ["other"]:
  r = requests.get("http://www.crunchbase.com/companies?c=%s" % (letter))
  soup = BeautifulSoup(r.text)

  # get all the companies that are listed by checking for 
  # "/company/" at the beginning of the url
  # however, only save the name of the company by taking 
  # substring after /company/ (9 characters long)
  # output error message if company name too long, skips for now
  for link in soup.select("li > a"):
    if "/company/" == link['href'][:9]:
      company_name = link['href'][9:]

      # max filename len is 255, .json = 5
      if len(company_name) < 255 - 5:  
        company_urls.append(company_name)
      else:
        print "%s too long, skipping." % (company_name)

# write this list of companies to file 
open("list_of_companies.txt", 'w').write("\n".join(company_urls))

def download(company_url):
  r = requests.get(CRUNCHBASE_COMPANY_API % (company_url, API_KEY))
  open("crunchbase_companies/%s.json" % (company_url), 'w').write(r.text.encode("utf-8"))

# get all the already scraped companies so we don't rescrape them
# if force flag is used, rescrape all companies
if "--force" in sys.argv or "-f" in sys.argv:
  scraped_companies = []
else:
  # remove json extension
  scraped_companies = [x[:-5] for x in glob.glob("crunchbase_companies/*.json")]

p = Pool(10)
r = p.map_async(download, set(company_urls) - set(scraped_companies))
r.get()
