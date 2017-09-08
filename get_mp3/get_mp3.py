from bs4 import BeautifulSoup
import requests
import os
import sys
import argparse
import subprocess
import time

# todo: make this multithreaded

def download_mp3(valid_link, movie_name, folder_path):
    for link in valid_link:
        print "Sleeping for 60 seconds before downloading next songs"
        time.sleep(60)
        print "Downloading song with Id using subprocess : ", link
        status = subprocess.call(['wget', link])
        if status == 0:
            print "Download successful for id  ", str(link)
            prelink = link.split("/")
            print prelink[-1]
            if os.rename(prelink[-1], movie_name + "_" + str(prelink[-1]) + ".mp3"):
                print "file renamed to : ", movie_name + "_" + str(prelink[-1] + ".mp3")

    print "All songs downloaded "


def prepare_url(url, movie_name, folder_path):
    urldata = requests.get(url)
    web_data = urldata.text
    soup = BeautifulSoup(web_data, "html.parser")

    valid_link = []

    # sample = "http://www.mymp3song.com/files/download/id/12860"

    for link in soup.find_all('a', attrs={'class': 'fileName'}):
        prelink = link['href'].split("/")
        website_url = "http://www.mymp3song.com/files/download/id/"
        created_newlink = website_url + str(prelink[2])
        valid_link.append(created_newlink)

    download_mp3(valid_link, movie_name, folder_path)


def main():
    parser = argparse.ArgumentParser(
        description="Downloading Videos from the given link and saving in local machine")
    parser.add_argument(
        '-u', '--url', help="Enter the URL path you want to traverse for downloading mp4 files ", required=True)
    parser.add_argument(
        '-f', '--folder', help="Enter the folder location ", required=True)
    parser.add_argument(
        '-m', '--moviename', help="Enter the movie to make filename at the end")
    args = parser.parse_args()

    if args.url:
        url = args.url
        print url

    if not args.folder:
        print "Please Enter folder location "
        sys.ext()

    if args.moviename:
        movie_name = args.moviename

    folder_path = args.folder

    if os.chdir(folder_path):
        print "Directory successfully changed to location - ", folder_path

    # url = "http://www.songspk.link/dastak1996.html"
    # url = "http://www.mymp3song.com/filelist/747/navrang_(1959)_%3A_mp3_songs/new2old/1"

    prepare_url(url, movie_name, folder_path)

if __name__ == "__main__":
    main()

