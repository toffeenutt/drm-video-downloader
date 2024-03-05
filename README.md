# drm-video-downloader
Download DRM video from iframe.mediadelivery.net

## Version
Ubuntu 22.04.3 (WSL2)  
Python 3.10.12

## Module and Library
pip install httpx  
pip install pycryptodome

sudo apt install ffmpeg

## README
You may need to edit the header.  
**In particular, the referer of playerHeaders must be filled in.**  

Only tested on some videos.  
There is no error handling.  
If it does not work properly, analyze the request and response and modify the code.

The main requests and responses are:
* https://iframe.mediadelivery.net/embed/{video_library_id}/{video_id}
* .../ping?...
* .../activate
* .../playlist.drm?...
* .../video.drm?...
* .../{resolution}.drmkey?...
* .../video{n}.ts?...

Analyze this request and response using your browser's developer tools.  
(In my case, ping and activate worked fine using any values.)