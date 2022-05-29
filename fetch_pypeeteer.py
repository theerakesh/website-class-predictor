import asyncio
import re
import csv
from operator import itemgetter
from bs4 import BeautifulSoup, Comment
from matplotlib.pyplot import close
from pyppeteer import launch
import nest_asyncio
nest_asyncio.apply()

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


async def fetch(page, url):
    try:
        await page.setRequestInterception(True)

        async def intercept(request):
            if any(request.resourceType == _ for _ in ('stylesheet', 'image', 'font')):
                await request.abort()
            else:
                await request.continue_()
        page.on('request', lambda req: asyncio.ensure_future(intercept(req)))
        await page.goto(f'http://{url}', {'waitUntil': 'domcontentloaded'})
        content = await page.content()
        await page.close()
        print('fetched ' + url)
        return content
    except Exception as e:
        print(str(e))

ldict = []


async def main():
    browser = await launch()
    tasks = []
    try:
        for url in urls:
            page = await browser.newPage()
            tasks.append(fetch(page, url))
        htmls = await asyncio.gather(*tasks)
        for content in htmls:
            mdict = {}
            mdict["url"] = url
            mdict["type"] = urltype[url]
            content = re.sub(r'\n+', r' ', content)
            mdict["text"] = text_from_html(content)
            ldict.append(mdict)
    except Exception as e:
        print(e)
        pass
    await browser.close()

asyncio.run(main())
with open('data2.csv', 'w', encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["url", "type", "text"])
    writer.writeheader()
    writer.writerows(ldict)
