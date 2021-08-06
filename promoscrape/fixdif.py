import pandas as pd
import numpy as np
from openpyxl import Workbook
import os
df1=pd.read_csv('promoscrape/spiders/promodata_1.csv')
df2=pd.read_csv('promoscrape/spiders/promodata_2.csv')
df3=pd.DataFrame(columns=['DateScraped','product_name', 'price', 'Fresh_Availability','Displayed_Discount_Dollar','Displayed_Discount_Percent','VPC_Dollar','VPC_Percent','Lightning_Dollar','Lightning_Percent','DOTD_Dollar','DOTD_Percent','SNS_min','SNS_max','SNS_Coupon','AMZ_Choice','Best_Seller','Out_of_Stock','ASIN','Competes_With','Brand'])

list1=df1['Fresh_Availability'].tolist()
list2=df2['Fresh_Availability'].tolist()
pricelist1=df1['price'].tolist()
pricelist2=df2['price'].tolist()

# print(list1)
# print(list2)
finallist=[]
finallistprice=[]
try:
    for i in range(len(list1)):
        if list1[i] == list2[i]:
            # print('lol')
            finallist.append(df1.iloc[i])
        elif list1[i]== 'Fresh Unavailable' and list2[i]!= 'Fresh Unavailable':
            # print('list1 got it')
            finallist.append(df1.iloc[i])
        elif list1[i]!= 'Fresh Unavailable' and list2[i]=='Fresh Unavailable':
            # print('list2 got it')
            finallist.append(df2.iloc[i])
        elif list1[i] == 'Fresh Available' and list2[i] != 'Fresh Available':
            # print('list1 got it')
            finallist.append(df1.iloc[i])
        elif list1[i] != 'Fresh Available' and list2[i] == 'Fresh Available':
            # print('list2 got it')
            finallist.append(df2.iloc[i])
        elif list1[i] == 'Currently Unavailable' and list2[i] != 'Currently Unavailable':
            # print('list1 got it')
            finallist.append(df1.iloc[i])
        elif list1[i] != 'Currently Unavailable' and list2[i] == 'Currently Unavailable':
            # print('list2 got it')
            finallist.append(df2.iloc[i])
        else:
            finallist.append(df2.iloc[i])
    df4 = pd.DataFrame(finallist)
    betweenlist=[]
    listprice=df4['price'].tolist()
    for i in range(len(list1)):
        if listprice[i] is None and pricelist1[i] is not None:
            finallistprice.append(df1.iloc[i])
        elif listprice[i] is None and pricelist2[i] is not None:
            finallistprice.append(df2.iloc[i])
        else:
            finallistprice.append(df4.iloc[i])





    # print(finallist)
    finallistprice=pd.DataFrame(finallist)
    df4.to_csv('ScrapedOutput.csv', index=False, mode='a', header=None)
except:
    df1.to_csv('ScrapedOutput.csv', index=False, mode='a', header=None)

if os.path.exists('promoscrape/spiders/promodata_1.csv'):
    os.remove('promoscrape/spiders/promodata_1.csv')
if os.path.exists('promoscrape/spiders/promodata_2.csv'):
        os.remove('promoscrape/spiders/promodata_1.csv')