# Author: Gaurav Gupta (keybase: gdgupta11)
"""
    The script aims to provide easy way to query and check report of IP address and URL's from virustotal.com. They provide API but the repsonse in JSON. 
    Here I have taken out important part and made that as a script which can combine both IP address check and URL together in one script. 
    Lot of things to improve here. 
"""

# API call to Virustotal.com for checking a URL and its status whether its clean or infected .
import sys
import requests
import time
import re

# check IP address report


def validateIpAddress(ipaddress):
    """
        Function to check if given string is in IP Address format or not. 
        Parameters: 
            ipaddress
        Return:
            validation: boolean (True/False)
    """
    validation = False
    match = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ipaddress)
    if match:
        validation = True

    return validation


def getIpAddressReport(ipaddress, apikey, ipAddressUrl):
    """
        API Call: /ip-address/report
        Paramters: 
            IP address: String
            apiKey: String
        Return:
            IpAddressResult: dict {51.68.201.117: {positiveCount:3, country: GB, EU}}
    """
    IpAddressResult = {}
    # check if the IP address is given properly or not.
    if validateIpAddress(ipaddress):
        payload = {"apikey": apikey, "ip": ipaddress}
        reportResponse = requests.get(ipAddressUrl, params=payload)
        if reportResponse.status_code == 200:
            data = reportResponse.json()
            positiveCount = data['detected_urls'][0]['positives']
            country = data['country'] + "," + data['continent']
            if positiveCount > 0:
                IpAddressResult[ipaddress] = {
                    'positiveCount': positiveCount, "country": country}
    else:
        print("Not a valid IP address, please check")
        sys.exit(1)

    return IpAddressResult


def submitUrl(virusTotalUrl, apikey, urlToCheck):
    """
        API: /vtapi/v2/url/scan
        Parameters: 
            VirusTotalUrl: String - Url for the API to call
            apikey: String - API key 
            urlToCheck: String - Target URL to check

        Return:
            scanId: String - Hash report ID for getting further results
    """
    scanId = 0
    params = {'apikey': apikey, "url": urlToCheck}
    response = requests.post(virusTotalUrl, params)
    if response.status_code == 200:
        data = response.json()
        scanId = data['scan_id']

    return scanId


def getUrlReport(reportCheckUrl, apikey, scanId):
    """
        API: vtapi/v2/url/report
        Paramters:
            reportCheckUrl: String - URL for checking the report after intial submitting it
            apikey: String - Api Key
            scanId: String - scanId returned by submitting URL which will used to fetch the report
    """
    payload = {"apikey": apikey, "resource": scanId}
    reportResponse = requests.get(reportCheckUrl, params=payload)
    finalResult = {}
    if reportResponse.status_code == 200:
        print("Got the report reponse from the virusTotal server for scanId - {} ".format(scanId))
        reportData = reportResponse.json()
        for website, value in reportData['scans'].items():
            cleanStatus = value['result']
            if cleanStatus not in ["clean site", "unrated site"]:
                finalResult[website] = cleanStatus
                print("Website - {} - Result - {} ".format(website, value))


def main():
    # todo: Creating Config file to put all the variables at one place and import config
    virusTotalUrl = "https://www.virustotal.com/vtapi/v2/url/scan"
    apikey = "<Enter your API KEY>" # Get you API KEY from here https://developers.virustotal.com/reference#getting-started"
    reportCheckUrl = "https://www.virustotal.com/vtapi/v2/url/report"
    ipAddressUrl = "https://www.virustotal.com/vtapi/v2/ip-address/report"

    if len(sys.argv) < 3:
        print("Usage: filename.py ipaddress/urlcheck <ipaddress>/<urltocheck> ")
        sys.exit(1)
    # todo: Argparse for better parsing of arguments and CLI messges.
    action = sys.argv[1]
    target = sys.argv[2]

    if action == "ipaddress":
        ipAddressResult = getIpAddressReport(target, apikey, ipAddressUrl)
        print("Result for IPAddress -  {} ".format(target))
        print(ipAddressResult)
    elif action == "urlcheck":
        print("URL to check is {}".format(target))

        scanId = submitUrl(virusTotalUrl, apikey, target)
        if scanId != 0:            
            # calling the report API to check the report for the request URL
            print(
                "Sleeping for 30 seconds before making another call because of restrictions of API call limits")
            time.sleep(30)
            getUrlReport(reportCheckUrl, apikey, scanId)
    else:
        print("Usage: filename.py ipaddress/urlcheck <ipaddress>/<urltocheck> ")


if __name__ == "__main__":
    main()

"""
Output on command line: 

url to check is http://0797fdc.com.cn
The Scan ID is -- b5467950f7ca621336cec8d615d1d22d94f832e8ab730e9c9e229ac8ebc675c6-1589827807
Sleeping for 45 seconds before sending out another query
Got the report reponse from the virusTotal server for scanId - b5467950f7ca621336cec8d615d1d22d94f832e8ab730e9c9e229ac8ebc675c6-1589827807
Website - Kaspersky - Result - {'detected': True, 'result': 'phishing site'}
Website - AutoShun - Result - {'detected': True, 'result': 'malicious site'}

"""
