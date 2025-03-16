import pandas as pd
import numpy as np
import requests
from datetime import datetime
 
# 1. API'den Veri Çekme
url = "http://localhost:3000/sales"
response = requests.get(url)
data = response.json() if response.status_code == 200 else exit("API isteği başarısız!")

# Veriyi Pandas DataFrame'e dönüştürüyoruz.
df = pd.DataFrame(data)

# 2. Veri Manipülasyonu
# Eksik verileri dolduruyoruz veya varsayılan değerler atıyoruz.
if "Category" not in df.columns:
    df["Category"] = "Unknown"
df.fillna({"Price": 0, "Quantity_purchased": 0, "Customer_satisfaction_score": 0}, inplace=True)

# Tarih formatını düzeltiyoruz.
df["Purchase_date"] = pd.to_datetime(df["Purchase_date"], errors="coerce")

# Sayısal sütunları düzeltiyoruz.
df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0)
df["Quantity_purchased"] = pd.to_numeric(df["Quantity_purchased"], errors="coerce").fillna(0)

# 3. Veri Analizi
# En çok satın alınan ürünleri belirliyoruz.
def most_purchased_products(df, n=10):
    return df.groupby("Product_name")["Quantity_purchased"].sum().sort_values(ascending=False).head(n)

most_purchased_products = most_purchased_products(df)

# Fiyat ve satış miktarı arasındaki korelasyonu hesaplıyoruz.
def price_sales_correlation(df):
    return df[["Price", "Quantity_purchased"]].corr()

df_correlation = price_sales_correlation(df)

# Kategorilere göre ortalama fiyat hesaplıyoruz.
def average_price_by_category(df):
    return df.groupby("Category")["Price"].mean()

average_price_per_category = average_price_by_category(df)

# Belirli bir zaman diliminde en çok satılan ürünleri buluyoruz.

def top_selling_products_in_period(df, start_date, end_date, n=10):
    df_filtered = df[(df["Purchase_date"] >= start_date) & (df["Purchase_date"] <= end_date)]
    return df_filtered.groupby("Product_name")["Quantity_purchased"].sum().sort_values(ascending=False).head(n)

start_period, end_period = datetime(2024, 6, 1), datetime(2024, 6, 15)
most_sold_in_period = top_selling_products_in_period(df, start_period, end_period)

# Müşteri harcama seviyelerine göre gruplama yapıyoruz.
def customer_spending_levels(df, bins, labels):
    df["Total Spending"] = df["Price"] * df["Quantity_purchased"]
    df["Spending Level"] = pd.cut(df["Total Spending"], bins=bins, labels=labels)
    return df

bins, labels = [0, 500, 1500, 3000, float("inf")], ["Düşük", "Orta", "Yüksek", "Premium"]
df = customer_spending_levels(df, bins, labels)


# 4. Dinamik Fiyatlandırma
# Aşırı ucuz ürünlerin fiyatlarını belirli bir oranda artırıyoruz.
def dynamic_pricing(df, price_increase_rate=1.10):
    average_price = np.mean(df["Price"])
    std_dev = np.std(df["Price"])
    cheap_threshold = average_price - 1.5 * std_dev
    df["Price"] = np.where(df["Price"] < cheap_threshold, df["Price"] * price_increase_rate, df["Price"])
    return df

df = dynamic_pricing(df)

print("\nGüncellenen Fiyatlar:")
print(df[["Product_name", "Price"]])

# 5. Ürün Öneri Sistemi
# Müşterilere, satın aldıkları ürünlere benzer en popüler ürünleri öneriyoruz.
def recommend_products(customer_id, df, category=None):
    customer_purchases = df[df["Customer_id"] == customer_id]

    if category:
        category_purchases = customer_purchases[customer_purchases["Category"] == category]
    else:
        category_purchases = customer_purchases

    if category_purchases.empty and category:
        recommended_products = df[df["Category"] == category].groupby("Product_name")["Quantity_purchased"].sum().sort_values(ascending=False).head(5)
    elif not category_purchases.empty:
        recommended_products = df[df["Product_name"].isin(category_purchases["Product_name"].unique())].groupby("Product_name")["Quantity_purchased"].sum().sort_values(ascending=False).head(5)
    else:
        recommended_products = pd.Series()

    return recommended_products

# Yüksek müşteri memnuniyeti olan ürünleri buluyoruz.
def high_satisfaction_products(df, score=4, n=10):
    return df[df["Customer_satisfaction_score"].astype(int) > score].groupby("Product_name")["Quantity_purchased"].sum().sort_values(ascending=False).head(n)

# Fonksiyonu çağırarak sonucu bir değişkene atıyoruz.
high_satisfaction_products = high_satisfaction_products(df)

# Örnek kullanım
customer_id = "107"
recommendations = recommend_products(customer_id, df, category="Ev Aletleri")


print("\nKategorilere Göre Ortalama Fiyat:")
print(average_price_per_category.to_frame())

print("\nYüksek Müşteri Memnuniyeti Olan Ürünler:")
print(high_satisfaction_products.to_frame())

print("\nMüşteri {} için önerilen ürünler (Elektronik kategorisi):".format(customer_id))
if recommendations.empty:
    print("Önerilen ürün bulunamadı.")
else:
    print(recommendations.to_frame())


print("\nEn Çok Satın Alınan Ürünler:")
print(most_purchased_products.to_frame())

print("\nFiyat ve Satış Miktarı Korelasyonu:")
print(df_correlation)

print("\nBelirli Zaman Aralığında En Çok Satılan Ürünler (2024-6-1 - 2024-6-15):")
print(most_sold_in_period.to_frame())

print(df[["Customer_id", "Total Spending", "Spending Level"]].head())  # İlk 5 satırı göster
print("\nSpending Level Distribution:")
print(df["Spending Level"].value_counts())

import seaborn as sns
import matplotlib.pyplot as plt

# 6. Görselleştirmeler
# Görselleştirme ayarları
sns.set(style="whitegrid")
plt.figure(figsize=(12, 6))

# En çok satın alınan ürünler
plt.subplot(2, 2, 1)
most_purchased_products.plot(kind="bar", color="skyblue")
plt.title("En Çok Satın Alınan Ürünler")
plt.xlabel("Ürün Adı")
plt.ylabel("Satın Alınan Miktar")

# Kategorilere göre ortalama fiyat
plt.subplot(2, 2, 2)
average_price_per_category.plot(kind="bar", color="lightgreen")
plt.title("Kategorilere Göre Ortalama Fiyat")
plt.xlabel("Kategori")
plt.ylabel("Ortalama Fiyat")

# Fiyat ve satış miktarı korelasyonu
plt.subplot(2, 2, 3)
sns.heatmap(df_correlation, annot=True, cmap="coolwarm", center=0)
plt.title("Fiyat ve Satış Miktarı Korelasyonu")

# Müşteri harcama seviyeleri
plt.subplot(2, 2, 4)
df["Spending Level"].value_counts().plot(kind="pie", autopct="%1.1f%%", colors=["gold", "lightcoral", "lightskyblue", "lightgreen"])
plt.title("Müşteri Harcama Seviyeleri")

# Görselleştirmeleri gösterme
plt.tight_layout()
plt.show()

# 7. Raporlama
print("\nKategorilere Göre Ortalama Fiyat:")
print(average_price_per_category.to_frame())

print("\nYüksek Müşteri Memnuniyeti Olan Ürünler:")
print(high_satisfaction_products.to_frame())

print("\nMüşteri {} için önerilen ürünler (Elektronik kategorisi):".format(customer_id))
if recommendations.empty:
    print("Önerilen ürün bulunamadı.")
else:
    print(recommendations.to_frame())

print("\nEn Çok Satın Alınan Ürünler:")
print(most_purchased_products.to_frame())

print("\nFiyat ve Satış Miktarı Korelasyonu:")
print(df_correlation)

print("\nBelirli Zaman Aralığında En Çok Satılan Ürünler (2024-6-1 - 2024-6-15):")
print(most_sold_in_period.to_frame())

