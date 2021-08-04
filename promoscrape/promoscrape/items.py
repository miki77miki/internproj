# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PromoscrapeItem(scrapy.Item):
    # define the fields for your item here like:
    product_name = scrapy.Field()
    VPC_Dollar=scrapy.Field()
    VPC_Percent=scrapy.Field()
    price = scrapy.Field()
    Lightning_Dollar = scrapy.Field()
    Lightning_Percent = scrapy.Field()
    DOTD_Dollar= scrapy.Field()
    DOTD_Percent= scrapy.Field()
    Displayed_Discount_Dollar= scrapy.Field()
    Displayed_Discount_Percent= scrapy.Field()
    SNS_min= scrapy.Field()
    SNS_max= scrapy.Field()
    Fresh_Availability= scrapy.Field()
    DateScraped=scrapy.Field()
    AMZ_Choice=scrapy.Field()
    Best_Seller=scrapy.Field()
    Out_of_Stock=scrapy.Field()
    ASIN=scrapy.Field()
    Competes_With=scrapy.Field()
    Brand=scrapy.Field()
    SNS_Coupon_Dollar=scrapy.Field()
    SNS_Coupon_Percent= scrapy.Field()

    pass
