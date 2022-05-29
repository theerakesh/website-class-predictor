# from turtle import ht
from bs4 import BeautifulSoup
from bs4.element import Comment
import csv
import aiohttp
import asyncio
import nest_asyncio
nest_asyncio.apply()

# prepare urls
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


medical = 'hhs.gov drugs.com epocrates.com everydayhealth.com healthline.com mayoclinic.org medicinenet.com medlineplus.gov medpagetoday.com medscape.com merckmanuals.com nih.gov openmd.com rxlist.com cdc.gov uptodate.com webmd.com biomedcentral.com freemedicaljournals.com jamanetwork.com nejm.org ncbi.nlm.nih.gov 1mg.com pharmeasy.in'
education = 'coursera.org udemy.com udacity.com edx.org linkedin.com skillshare.com alison.com khanacademy.org ocw.mit.edu openculture.com connectionsacademy.com academicearth.org open.edu online.stanford.edu online-learning.harvard.edu oyc.yale.edu code.org uopeople.edu vedantu.com unacademy unacademy.com byjus.com ed.ted.com lessonpaths.com codehs.com thegymnasium.com canvas.net uw.is oli.cmu.edu open.edu'
construction = 'connect-homes.com mikeschaapbuilders.com luxurysimplified.com dittodc.com maman-corp.com hutchinsonbuilders.com.au hueyarchitect.com tollbrothers.com rebath.com segalebros.com gfipartners.com brymor.co.uk adcengineering.com scapeconstruct.com buildcover.com schumacherhomes.com canyondesignbuild.com level10gc.com pcl.com reborncabinets.com farrellbuilding.com weitz.com henselphelps.com probuild.com.au bandk.co.uk fletcherconstruction.co.nz snydercg.com'
service = 'medallia.com hortonworks.com achievers.com arcurve.com hootsuite.com domo.com ivision.com marketingcloud.com waveoc.com shopping-cart-migration.com interamark.com'
medical_urls = medical.split(' ')
education_urls = education.split(' ')
construction_urls = construction.split(' ')
service_urls = service.split(' ')
urls = [*medical_urls, *education_urls, *construction_urls, *service_urls]
urltype = {}
for url in medical_urls:
    urltype[url] = "medical"
for url in education_urls:
    urltype[url] = "education"
for url in construction_urls:
    urltype[url] = "construction"
for url in service_urls:
    urltype[url] = "service"
# print(urls) #ctl00_ContentPlaceHolder1_DataList1_ctl00_StudentNameLabel


async def fetch(session, url):
    try:
        async with session.get(url) as response:
            text = await response.text()
            return text, url
    except Exception as e:
        print(str(e))


ldict = []


async def main():
    tasks = []

    async with aiohttp.ClientSession(headers=hdr, trust_env=True) as session:
        for url in urls:
            tasks.append(fetch(session=session, url=f'https://{url}'))
        htmls = await asyncio.gather(*tasks)
        for html in htmls:
            if html is not None:
                url = html[1]
                mdict = {}
                try:
                    mdict["url"] = url
                    mdict["type"] = urltype[url[8:]]
                    mdict["text"] = "\"" + text_from_html(html[0]) + "\""
                    ldict.append(mdict)
                except Exception as e:
                    continue
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
with open('data.csv', 'w', encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["url", "type", "text"])
    writer.writeheader()
    writer.writerows(ldict)
