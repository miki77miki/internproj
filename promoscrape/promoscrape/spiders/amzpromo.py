import scrapy
from ..items import PromoscrapeItem
from datetime import datetime
from shareplum import Site, Office365
from shareplum.site import Version
from scraper_api import ScraperAPIClient
import json
import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = '/'.join([ROOT_DIR, 'config.json'])

# read json config file
with open(config_path) as config_file:
    config = json.load(config_file)
    config = config['share_point']

USERNAME = config['user']
PASSWORD = config['password']
SHAREPOINT_URL = config['url']
SHAREPOINT_SITE = config['site']
# if os.path.exists('promodata_1.csv'):
#     os.remove('promodata_1.csv')
# if os.path.exists('promodata_2.csv'):
#         os.remove('promodata_2.csv')

class SharePoint:
    def auth(self):
        self.authcookie = Office365(
            SHAREPOINT_URL,
            username=USERNAME,
            password=PASSWORD,
        ).GetCookies()
        self.site = Site(
            SHAREPOINT_SITE,
            version=Version.v365,
            authcookie=self.authcookie,
        )
        return self.site

    def connect_to_list(self, ls_name):
        self.auth_site = self.auth()

        list_data = self.auth_site.List(list_name=ls_name).GetListItems()

        return list_data


clients = SharePoint().connect_to_list(ls_name='ASIN_list')

urls=[]
ASINs=[]
ASIN_List=[]
Competitor_List=[]
for idx, client in enumerate(clients, 1):
    ASINs.append(client['ASIN'])
    check='https://www.amazon.com/dp/'+client['ASIN']
    check_fresh='https://www.amazon.com/dp/'+client['ASIN']+'/ref=pd_alm_fs_merch_1_4_fs_dsk_dl_mw_img?fpw=alm'
    ASIN_List.append(client['ASIN'])
    Competitor_List.append(client['Competes_With'])
    urls.append(check)
    urls.append(check_fresh)

Competitor_Dict={}

for n in range(len(ASIN_List)):
    Competitor_Dict[ASIN_List[n]]=Competitor_List[n]

client = ScraperAPIClient('7e956f6602ae81bbf32384f231ccd327')
class AmzpromoSpider(scrapy.Spider):
    name = 'amzpromo'


    def start_requests(self):
        urls_proxy=urls
        #urls_proxy=['https://www.amazon.com/dp/B004S6C0I2','https://www.amazon.com/dp/B07KFH3YZF','https://www.amazon.com/dp/B01NHBZAVM']

        items=PromoscrapeItem()
        country_code=['us']
        for url in urls_proxy:
            #result = client.get(url=url, country_code=True).text
            yield scrapy.Request(client.scrapyGet(url=url, render=False,country_code='us'), callback=self.parse)
    def parse(self, response):


        price=response.css('span#priceblock_ourprice::text').get()
        if price is None or 0:
            try:
                price=response.css('span.a-size-medium.a-color-price.priceBlockBuyingPriceString').get()
            except:
                price=0
        if price is None or 0:
            try:
                price=response.css('span#priceblock_saleprice::text').get()
            except:
                price=0
        if price is None or 0:
            try:
                price=response.css('span#priceblock_dealprice::text').get()
            except:
                price=0

        ASIN=response.request.url

        ASIN=ASIN.replace('https://api.scraperapi.com/?url=https%3A%2F%2Fwww.amazon.com%2Fdp%2F','').replace('&api_key=7e956f6602ae81bbf32384f231ccd327&country_code=us&scraper_sdk=python','')
        ASIN=ASIN.replace('%2Fref%3Dpd_alm_fs_merch_1_4_fs_dsk_dl_mw_img%3Ffpw%3Dalm','')
        DOTD_Dollar=0
        Displayed_Discount_Dollar=0
        Displayed_Discount_Percent=0
        Lightning_Percent=0
        items=PromoscrapeItem()
        Competes_With=Competitor_Dict[ASIN]

        if '%2Fref%3Dpd_alm_fs_merch_1_4_fs_dsk_dl_mw_img%3Ffpw%3Dalm' in response.request.url:

            try:
                Fresh_Availability = response.css('span.a-size-base-plus.a-text-bold::text').get()

                if 'Unavailable' in Fresh_Availability:
                    Fresh_Availability=('Fresh Unavailable')
                if 'Currently' in Fresh_Availability:
                    Fresh_Availability=('Fresh Unavailable')
                if 'Prime' in Fresh_Availability:
                    Fresh_Availability=('Fresh Available')
                Fresh_Availability_check = response.css('div#fresh-merchant-info::text').get()
                if Fresh_Availability_check != None:
                    if 'AmazonFresh.' in Fresh_Availability_check:
                        Fresh_Availability = ('Fresh Available')
            except:
                Fresh_Availability=('Fresh Unavailable')
        else:
            Fresh_Availability=('N/A')



        try:
            product_name=response.css('span#productTitle::text').get().replace('\n','')
        except:
            product_name='N/A'

        try:
            product_VPC=response.xpath('//*[@id="vpcButton"]/span[2]/text()').get()
            product_VPC_Alt=response.xpath('//*[@id="vpcButton"]/span[2]/text()').get()
        except:
            product_VPC='0'
            product_VPC_Alt='0'

        SNS_Coupon_Bool=False
        try:
            SNS_Coupon_Check=response.xpath('//*[@id="vpcButtonSns"]/span[2]/text()').get()
        except:
            SNS_Coupon_Check='0'
        try:
            if 'Subscribe & Save' in SNS_Coupon_Check:
                SNS_Coupon_Bool=True
        except:
            SNS_Coupon_Bool=False


        try:

            if 'coupon' in product_VPC and product_VPC_Alt:
                product_VPC_Alt=product_VPC.replace('\nSave an extra ','').replace(' when you apply this coupon.\n','')
                product_VPC=product_VPC.replace('\nSave an extra ','').replace(' when you apply this coupon.\n','')


        except:
            product_VPC_Alt='0'
            product_VPC='0'



        try:

            product_Lightning_test=response.css('span.a-size-base.gb-accordion-active::text').get().replace('\n','')
        except:
            product_Lightning_test='0'
            Lightning_Percent='0'
            Lightning_Dollar='0'
        try:
            if 'Lightning' in product_Lightning_test:
                product_Lightning = response.xpath('//*[@id="dealprice_savings"]/td[2]/text()').get()
                if product_Lightning is not None:
                    Lightning_Dollar,Lightning_Percent=product_Lightning.split()
                    Lightning_Percent=Lightning_Percent.replace('(','').replace(')','')
        except:
            Lightning_Percent='0'
            Lightning_Dollar='0'
        try:
            product_DOTD=response.xpath('//*[@id="priceblock_dealprice_lbl"]/text()').get()
        except:
            product_DOTD='0'
        try:
            if 'Day' in product_DOTD:
                product_DOTD=response.xpath('//*[@id="dealprice_savings"]/td[2]/text()').get().replace('\n','')
                DOTD_Dollar, DOTD_Percent= product_DOTD.split()
                DOTD_Percent=DOTD_Percent.replace('(','').replace(')','')
            else:
                DOTD_Dollar='0'
                DOTD_Percent='0'

        except:
            DOTD_Dollar='0'
            DOTD_Percent='0'

        try:
            Displayed_Discount_Dollar =response.css('span.a-size-base.a-color-price.priceBlockSavingsString::text').get().split()[0]
            Displayed_Discount_Percent =response.css('span.a-size-base.a-color-price.priceBlockSavingsString::text').get().split()[1].replace('(','').replace(')','')
        except Exception as e:
            print(e)
            print('Block1')
            Displayed_Discount_Dollar = 0
            Displayed_Discount_Percent = 0
        if Displayed_Discount_Percent==0 or None or '0':
            try:
                Displayed_Discount_Dollar=response.xpath('//*[@id="dealprice_savings"]/td[2]/text()').get().replace('\n','').split()[0]
                Displayed_Discount_Percent=response.xpath('//*[@id="dealprice_savings"]/td[2]/text()').get().replace('\n','').split()[1].replace('(','').replace(')','')
            except Exception as e:
                print(e)
                print('Block2')
                Displayed_Discount_Dollar = 0
                Displayed_Discount_Percent = 0

        if Displayed_Discount_Percent==0 or None or '0':
            try:
                Displayed_Discount_Dollar =response.xpath('//*[@id="regularprice_savings"]/td[2]/text()').get().split()[0]
                Displayed_Discount_Percent =response.xpath('//*[@id="regularprice_savings"]/td[2]/text()').get().split()[1].replace('(','').replace(')','')
            except Exception as e:
                print(e)
                print('Block3')
                Displayed_Discount_Dollar=0
                Displayed_Discount_Percent=0
            print(Displayed_Discount_Percent)
        # if Displayed_Discount_Percent==0 or None or '0':
        #     try:
        #         Displayed_Discount_Dollar =response.xpath('td.a-span12.a-color-price.a-size-base.priceBlockSavingsString').get().split()[0]
        #         Displayed_Discount_Percent =response.css('td.a-span12.a-color-price.a-size-base.priceBlockSavingsString').get().split()[1].replace('(','').replace(')','')
        #
        #     except Exception as e:
        #         print(e)
        #         print('Block4')
        #         Displayed_Discount_Dollar = 0
        #         Displayed_Discount_Percent = 0
        # if Displayed_Discount_Percent == 0 or None or '0':
        #
        #     try:
        #         Displayed_Discount_Dollar=response.xpath('//*[@id="dealprice_savings"]/td[2]/text()').get().replace('\n','').split()[0]
        #         Displayed_Discount_Percent=response.xpath('//*[@id="dealprice_savings"]/td[2]/text()').get().replace('\n','').split()[1].replace('(','').replace(')','')
        #     except:
        #         Displayed_Discount_Dollar = 0
        #         Displayed_Discount_Percent = 0
        # if Displayed_Discount_Percent == 0:
        #     try:
        #         Displayed_Discount_Dollar =response.xpath('//*[@id="regularprice_savings"]/td[2]/text()').get().split()[0]
        #         Displayed_Discount_Percent =response.xpath('//*[@id="regularprice_savings"]/td[2]/text()').get().split()[1].replace('(','').replace(')','')
        #     except:
        #         Displayed_Discount_Dollar = 0
        #         Displayed_Discount_Percent = 0




        try:
            SNS_min=response.xpath('//*[@id="snsDiscountPill"]/span[1]/span/text()').get()
            SNS_max=response.xpath('//*[@id="snsDiscountPill"]/span[2]/span/text()').get()
        except:
            SNS_min='N/A'
            SNS_max='N/A'
        if SNS_max is 'N/A' or None or 0:
            try:
                SNS_max=response.css('span.discountTextRight::text').get()
                SNS_min=response.css('span.discountTextLeft::text').get()
            except:
                SNS_min = 'N/A'
                SNS_max = 'N/A'
        try:
            SNS_Coupon=response.xpath('//*[@id="unclippedCoupon"]/span[1]/text()').get()
            SNS_Coupon_Alt=response.xpath('//*[@id="unclippedCoupon"]/span[1]/text()').get()

            if 'Subscribe' in SNS_Coupon:
                try:

                    SNS_Coupon=response.xpath('//*[@id="unclippedCoupon"]/div/span/text()').get().split()[0]
                    SNS_Coupon_Alt=response.xpath('//*[@id="unclippedCoupon"]/div/span/text()').get().split()[0]

                except:
                    SNS_Coupon=response.xpath('//*[@id="vpcButtonSns"]/span[2]/text()').get().replace('\nSave an extra ','').replace(' on your first Subscribe & Save order.\n','')
                    SNS_Coupon_Alt=response.xpath('//*[@id="vpcButtonSns"]/span[2]/text()').get().replace('\nSave an extra ','').replace(' on your first Subscribe & Save order.\n','')

        except:
            SNS_Coupon='0'
            SNS_Coupon_Alt='0'


        if '%' in SNS_Coupon:
            SNS_Coupon_Percent=SNS_Coupon
            SNS_Coupon_Dollar = ('.' + SNS_Coupon_Alt.replace('%', ''))
            SNS_Coupon_Dollar=round((float(price.replace('$','')) * float(SNS_Coupon_Dollar)),4)
            SNS_Coupon_Dollar=('$'+str(SNS_Coupon_Dollar))
        if '$' in SNS_Coupon:
            SNS_Coupon_Dollar=SNS_Coupon
            SNS_Coupon_Percent=SNS_Coupon_Alt.replace('$','')
            SNS_Coupon_Percent=round((float(SNS_Coupon_Percent)/float(price.replace('$',''))),4)
            SNS_Coupon_Percent=SNS_Coupon_Percent*100
            SNS_Coupon_Percent=(str(SNS_Coupon_Percent)+'%')

        # if '%' in product_VPC:
        #     VPC_Percent=product_VPC
        #     VPC_Dollar= ('.'+product_VPC_Alt.replace('%',''))
        #     VPC_Dollar=round((float(price.replace('$','')) * float(VPC_Dollar)),4)
        #     VPC_Dollar=('$'+str(VPC_Dollar))
        # if '$' in product_VPC:
        #     VPC_Dollar=product_VPC
        #     VPC_Percent=product_VPC_Alt.replace('$','')
        #     VPC_Percent=round((float(VPC_Percent)/float(price.replace('$',''))),4)
        #     VPC_Percent=VPC_Percent*100
        #     VPC_Percent=(str(VPC_Percent)+'%')

        #     if price is None:
        #         price=response.css('span#priceblock_dealprice::text').get()
        #     if price is None:
        #         price=response.css('span.a-size-medium.a-color-price.priceBlockSalePriceString::text').get()
        #     if price is None:
        #         price=response.xpath('//*[@id="priceblock_ourprice"]/text()').get()
        #     if price is None:
        #         price=response.css('//*[@id="priceblock_ourprice"]/text()').get()
        # except:
        #     price='N/A'

        try:
            AMZ_Choice=response.css('span.ac-badge-text-secondary.ac-orange::text').get()
            if 'Choice' in AMZ_Choice:
                AMZ_Choice='Yes'
            else:
                AMZ_Choice='No'
        except:
            AMZ_Choice='No'

        try:
            Best_Seller=response.css('i.a-icon.a-icon-addon.p13n-best-seller-badge::text').get()
            if '#1' in Best_Seller:
                Best_Seller='Yes'
            else:
                Best_Seller='No'
        except:
            Best_Seller='No'


        try:
            Out_of_Stock=response.css('span.a-size-medium.a-color-state::text').get()
            if 'soon.' in Out_of_Stock:
                Out_of_Stock='Yes'
            elif 'Usually' in Out_of_Stock:
                Out_of_Stock='Yes'
            elif 'out' in Out_of_Stock:
                Out_of_Stock='Yes'
            else:
                Out_of_Stock='No'
        except:
            Out_of_Stock='No'
        # if price==None:
        #     Out_of_Stock='Yes'
        if Out_of_Stock is 'No':
            try:
                Out_of_Stock=response.css('span.a-color-price.a-text-bold::text').get()
                if 'out' in Out_of_Stock:
                    Out_of_Stock='Yes'
                else:
                    Out_of_Stock='No'
            except:
                Out_of_Stock='No'
        try:
            Brand=response.css('a#bylineInfo::text').get().replace('Visit the ','').replace(' Store','')

        except:
            Brand='N/A'
        try:
            if Brand == 'N/A':
                Brand=response.xpath('//*[@id="bylineInfoUS_feature_div"]/div/text()').get()
                Brand=Brand.replace('\n\n\n\n\n\n\n\n\n\n\nBrand: ','').replace('\n\n\n\n\n\n\n','')
        except:
            Brand='N/A'

        VPC_Dollar=0
        VPC_Percent=0
        if '%' in product_VPC:
            VPC_Percent=product_VPC
            VPC_Dollar= ('.'+product_VPC_Alt.replace('%',''))
            VPC_Dollar=round((float(price.replace('$','')) * float(VPC_Dollar)),2)
            VPC_Dollar=('$'+str(VPC_Dollar))
        if '$' in product_VPC:
            VPC_Dollar=product_VPC
            VPC_Percent=product_VPC_Alt.replace('$','')
            VPC_Percent=round((float(VPC_Percent)/float(price.replace('$',''))),4)
            VPC_Percent=round(VPC_Percent*100)
            VPC_Percent=(str(VPC_Percent)+'%')

        SNS_Coupon_Dollar=0
        SNS_Coupon_Percent=0
        if SNS_Coupon_Bool is True:
            SNS_Coupon_Percent=VPC_Percent
            SNS_Coupon_Dollar=VPC_Dollar
            VPC_Dollar=0
            VPC_Percent=0



        dt=datetime.now()
        DateScraped=(dt.strftime("%m/%d/%y"))



        items['product_name']=product_name
        items['price']=price
        items['Lightning_Percent'] = Lightning_Percent
        items['Lightning_Dollar'] = Lightning_Dollar
        items['DOTD_Dollar'] = DOTD_Dollar
        items['DOTD_Percent'] = DOTD_Percent
        items['Displayed_Discount_Dollar'] = Displayed_Discount_Dollar
        items['Displayed_Discount_Percent'] = Displayed_Discount_Percent
        items['SNS_min'] = SNS_min
        items['SNS_max'] = SNS_max
        items['SNS_Coupon_Percent'] = SNS_Coupon_Percent
        items['SNS_Coupon_Dollar']=SNS_Coupon_Dollar
        items['VPC_Dollar']=VPC_Dollar
        items['VPC_Percent']=VPC_Percent
        items['Fresh_Availability']=Fresh_Availability
        items['DateScraped']=DateScraped
        items['AMZ_Choice']=AMZ_Choice
        items['Best_Seller']=Best_Seller
        items['Out_of_Stock']=Out_of_Stock
        items['ASIN']=ASIN
        items['Competes_With']=Competes_With
        items['Brand']=Brand

        yield items
