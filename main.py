# Roblox Limiteds Sniper
import configparser, time, warnings, os, requests, lxml.html, threading, bs4, datetime, json, multiprocessing
from multiprocessing.context import Process
from run import item
from bs4 import BeautifulSoup
from contextlib import nullcontext
from urllib import parse
from configparser import ConfigParser
from threading import *
from colorama import Fore

# Read config file and grab username/password
config = ConfigParser()
config.read('config.ini')
cookie = config.get('data','cookie')
shop = config.get('data','shop')
robuxLimit = float(config.get('data','robuxLimit'))
purchaseLimit = float(config.get('data','purchaseLimit'))
snipeAt = float(config.get('data','singleSnipe'))
# item = config.get('data', 'item')
threads = int(config.get('data', 'threads'))
purchases = 0

# Set Login Cookies
token_headers = {
    'Cookie': cookie
}

# Log/Snipe Files
log = open("log.txt", "a")
snipes = open("snipes.txt", "a")

# Disable python logging to console
warnings.filterwarnings("ignore")
clear = lambda: os.system('cls')
clear()

# TODO

class User:
    # Get Recent Average Price of item
    def itemRap(self):
        page = requests.get("https://www.rolimons.com/item/"+str(item)+"")
        tree = lxml.html.fromstring(page.content)
        strRAP = tree.xpath('//*[@id="page_content_body"]/div[6]/div[2]/div[2]/div[2]/text()')[0]
        RAP = float(strRAP.replace(',',''))
        print("[+] Current RAP for " + item + " is " + strRAP)
        return RAP
    
    # Fetch X-CSRF token
    def getToken(self):
        cookies = {
        ".ROBLOSECURITY": cookie
        }
        page = requests.get('https://www.roblox.com/catalog/'+str(item)+'', cookies=cookies)
        tree = lxml.html.fromstring(page.content)
        tok = tree.xpath('//*[@id="rbx-body"]/script[34]/text()')[0]
        token = tok.replace("Roblox.XsrfToken.setToken('", '').replace("');",'').replace(' ','').replace('\n','').replace('\r','')
        return token

    # Fetch Current Balance
    def getBalance(self):
        cookies = {
        ".ROBLOSECURITY": cookie
        }
        page = requests.get('https://www.roblox.com/catalog/'+str(item)+'', cookies=cookies)
        soup = BeautifulSoup(page.content, 'html.parser')
        balance = soup.find("div", {"id":"ItemPurchaseAjaxData"})["data-user-balance-robux"]
        print("[+] Current balance is: " + balance)
        return balance

    # Fetch ID of Item
    def getID(self):
        productID_request = requests.get(url='https://api.roblox.com/Marketplace/ProductInfo?assetId='+str(item)+'', headers=token_headers)
        productID_page = lxml.html.fromstring(productID_request.content).text
        productID_split = productID_page.split(',')
        productID = int(productID_split[3].replace('"ProductId":',''))
        # print("productID: " + str(productID))
        return productID

    # Fetch Seller ID
    def getSellerId(self):
        cookies = {
        ".ROBLOSECURITY": cookie
        }
        page = requests.get('https://www.roblox.com/catalog/'+str(item)+'', cookies=cookies)
        soup = BeautifulSoup(page.content, 'html.parser')
        sellerID = soup.find("div", {"id":"item-container"})["data-expected-seller-id"]
        # print("sellerID: " + sellerID)
        return sellerID

    # Fetch User Asset ID
    def getUserAssetId(self):
        cookies = {
        ".ROBLOSECURITY": cookie
        }
        page = requests.get('https://www.roblox.com/catalog/'+str(item)+'', cookies=cookies)
        soup = BeautifulSoup(page.content, 'html.parser')
        userAssetId = soup.find("div", {"id":"item-container"})["data-lowest-private-sale-userasset-id"]
        # print("userAssetId: " + userAssetId)
        return userAssetId

    # Enable Threading
    def threading(self, RAP, purchases, productID):
        thread = []
        for i in range(0, threads):
            thread.append("thread["+str(i)+"]")
            thread[i] = threading.Thread(target=roblox.priceScan, args=(RAP, purchases, productID))
            thread[i].start()
    
    # Enable Processes
    def processing(self, RAP, purchases, productID):
        process = []
        for i in range(0, threads):
            process.append("process["+str(i)+"]")
            process[i] = Process(target=roblox.priceScan, args=(RAP, purchases, productID))
            process[i].start()
    
    # Scan the market for prices until an item is worth buying
    def priceScan(self, RAP, purchases, productID):
        while True:
            page = requests.get("https://www.roblox.com/catalog/"+str(item)+"")
            tree = lxml.html.fromstring(page.content)
            strCurrentPrice = "10,000"
            try:
                strCurrentPrice = tree.xpath('//*[@id="item-details"]/div[1]/div[1]/div[2]/div/span[2]/text()')[0]
            except:
                roblox.priceScan(RAP, purchases, productID)
            print("Current Price for " + item + " is " + strCurrentPrice)
            currentPrice = int(strCurrentPrice.replace(',',''))
            if currentPrice <= 200:
                roblox.buyItem(cookie, currentPrice, productID, purchases)
                break

    # Pushes a request to purchase an item at the suggested discount price
    def buyItem(self, cookie, currentPrice, productID, purchases):
        print("Attempting to buy: " + item + " at the price: " + str(currentPrice))
        sellerID = roblox.getSellerId()
        userAssetId = roblox.getUserAssetId()
        try:
            token = roblox.getToken()
            data = {
                "expectedCurrency": 1,
                "userAssetID": userAssetId,
                "isLimited": True,
                "expectedPrice": currentPrice,
                "productId": productID,
                "expectedSellerId": sellerID
            }
            cookies = {
                ".ROBLOSECURITY": cookie
            }
            headers = {
            "X-CSRF-TOKEN": token
            }
            request = requests.post(url="https://economy.roblox.com/v1/purchases/products/"+str(productID)+"", json=data, cookies=cookies, headers=headers)
            # print(request.status_code, request.text)
            soup = BeautifulSoup(request.content, 'html.parser').text
            soupSplit = soup.split(',')
            if soupSplit[0] == '{"purchased":true':
                print("[+] Successfully purchased " + item + "for the price " + currentPrice)
                purchases += 1
                snipes.write(f"[{(datetime.datetime.now().replace(microsecond=0))}] Successfully sniped " + item + " for the price of + " + currentPrice + "!\n")
                print("If purchase limit / balance limit has not been reached, this bot will continue to snipe this item in 5 seconds!")
                roblox.priceScan(RAP, purchases, productID)
            elif soupSplit[0] == '{"purchased":false':
                reason = soupSplit[1].replace("reason",'').replace('"','').replace(':',"")
                print("Failed to purchase " + item + "! Reason: " + reason)
                log.write(f"[{(datetime.datetime.now().replace(microsecond=0))}] Failed to purchase " + item + ". Reasoning: " + reason + "!\n")
                if reason == 'InsufficientFunds':
                    print("[-] You're too broke, running it back in 5 seconds...")
                    time.sleep(5)
                    roblox.priceScan(RAP, purchases, productID)
                elif reason == 'PriceChanged':
                    print("[-] Too slow, running it back in 5 seconds...")
                    time.sleep(5)
                    roblox.priceScan(RAP, purchases, productID)
                elif reason == 'InvalidTransaction':
                    print("[-] This wasn't supposed to happen, running it back in 5 seconds...")
                    time.sleep(5)
                    roblox.priceScan(RAP, purchases, productID)
                else:
                    roblox.priceScan(RAP, purchases, productID)
        except:
            print("There was an error. Oops, restarting sniper.")
            roblox.priceScan(RAP, purchases, productID) 
            pass
    
# Driver Function
roblox = User()
balance = roblox.getBalance()
productID = roblox.getID()
RAP = roblox.itemRap()
roblox.threading(RAP, purchases, productID)