import httpx
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import subprocess

client = httpx.Client(http2=True)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Dnt': '1',
    'Sec-Gpc': '1',
    'Te': 'trailers'
}
client.headers = headers

playerHeaders = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    #'Referer': '', #fill this
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-User': '?1'
}

print('#####iframe.mediadelivery.net video downloader#####')
URI = input('Enter URI in the following form [https://iframe.mediadelivery.net/embed/{video_library_id}/{video_id}]\n: ')
title = input('Enter a title (without extension)\n: ')

###to get player HTML.
player = client.get(URI, headers=playerHeaders).text
###
print('Wait a second. Getting ts files list...')
######################################################################################################
client.headers['Accept'] = '*/*'
client.headers['Sec-Fetch-Dest'] = 'empty'
client.headers['Sec-Fetch-Mode'] = 'cors'

pingHeaders = {
    'Origin': 'https://iframe.mediadelivery.net',
    'Referer': 'https://iframe.mediadelivery.net/',
    'Sec-Fetch-Site': 'same-site'
}

mid_idx = player.find('/.drm')
start_idx = player.rfind('"', 0, mid_idx) + 1
end_idx = player.find('/ping', mid_idx)
mediadelivery = player[start_idx:end_idx]

#Hash value doesn't matter
ping = mediadelivery + '/ping?hash=13892ac0903f805449a8dcbe781f896e&time=300&paused=false&resolution=720'

###ping and activate is needed to download full video
client.get(ping, headers=pingHeaders)
###

activate = mediadelivery + '/activate'

###
client.get(activate, headers=pingHeaders)
###
######################################################################################################
playlistHeaders = {
    'Referer': URI,
    'Sec-Fetch-Site': 'same-origin'
}

mid_idx = player.find('playlist.drm')
start_idx = player.rfind('"', 0, mid_idx) + 1
end_idx = player.find('"', mid_idx)
playlistURI = player[start_idx:end_idx]

###
playlist = client.get(playlistURI, headers=playlistHeaders).text
###

resolution = playlist.split('\n')[-1]
tsListURI = playlistURI[:playlistURI.find('playlist')] + (resolution if resolution != '' else playlist.split('\n')[-2])

###
tsList = client.get(tsListURI, headers=playlistHeaders).text #video.drm
###
######################################################################################################
client.headers['Origin'] = 'https://iframe.mediadelivery.net'
client.headers['Referer'] = 'https://iframe.mediadelivery.net/'
sameSiteHeader = {
    'Sec-Fetch-Site': 'same-site'
}
crossSiteHeader = {
    'Sec-Fetch-Site': 'cross-site'
}

print('Done\nDownloading ts file...', end='')

tsCNT = 0
pingCNT = 0
start_idx = tsList.rfind('video') + 5
end_idx = tsList.find('.', start_idx)
totalTs = int(tsList[start_idx:end_idx]) #Total number of ts files. (last ts file number)

tsFile = f'./{title}.ts'
with open(tsFile, 'wb') as file:
    for uri in tsList.split('\n'):
        if uri[:10] == '#EXT-X-KEY':
            start_idx = uri.find('URI="') + 5
            end_idx = uri.find('"', start_idx)
            keyURI = uri[start_idx:end_idx]

            ###to get a key
            key = client.get(keyURI, headers=sameSiteHeader).content
            ###

            start_idx = uri.find('IV=0x') + 5
            iv = bytes.fromhex(uri[start_idx:])

        elif uri[:5] == 'https':
            ###to get a encrypted ts file
            encryptedTs = client.get(uri, headers=crossSiteHeader).content
            ###

            cipher = AES.new(key, AES.MODE_CBC, iv)
            decryptedTs = unpad(cipher.decrypt(encryptedTs), AES.block_size)

            file.write(decryptedTs)

            #Show progress
            print('\rDownloading ts file... ' + str(round(tsCNT / totalTs * 100, 2)) + '%  ', end='')
            tsCNT += 1
            pingCNT += 1
        
        if pingCNT == 10:
            ###Ping is required periodically
            client.get(ping, headers=sameSiteHeader)
            ###
            pingCNT = 0

######################################################################################################
#convert ts to mp4 and remove ts file.
print('\nAlmost done!\nConverting ts to mp4...')
mp4File = f'./{title}.mp4'
command = ['ffmpeg', '-i', tsFile, '-c', 'copy', '-bsf:a', 'aac_adtstoasc', mp4File]
subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
command = ['rm', tsFile]
subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

print('Complete!')