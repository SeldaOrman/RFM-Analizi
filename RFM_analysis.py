import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_ = pd.read_excel("03_hafta/Ders Öncesi Notlar/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()

#Veriyi anlamak
df.head()
df.shape
df.describe().T
df.isnull().sum()
df["Description"].nunique()
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()

#recency ve frequency hesaplamasıyla rfm segmentleri oluşturma
def create_rfm(dataframe):

    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[(dataframe['Quantity'] > 0)]
    dataframe = dataframe[(dataframe['Price'] > 0)]
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]

    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                                'Invoice': lambda num: num.nunique(),
                                                "TotalPrice": lambda price: price.sum()})
    rfm.columns = ['recency', 'frequency', "monetary"]
    rfm = rfm[(rfm['monetary'] > 0)]


    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])


    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))


    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "recency_score","frequency_score","RFM_SCORE","segment"]]
    return rfm


rfm_new = create_rfm(df)
rfm_new.head()

"""import matplotlib.pyplot as plt

rfm_new['segment'].value_counts().plot(kind='bar')

plt.title("Segmentlerdeki Kişi Sayıları")
plt.xlabel("Segmentler")
plt.ylabel("Kişi Sayıları")

plt.show()"""
