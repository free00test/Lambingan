import sys
import urllib
import urllib2
import xbmcgui
import xbmcplugin
import uuid
import xbmcaddon
import platform

def load_videos(urls, thumbnail, title):
    msg = "Please wait.  Loading video."
    notify(msg, 500)
    #p_dialog = xbmcgui.DialogProgressBG()
    #p_dialog.create('Getting Multiple Video URL\'s', 'Getting Video URL\'s...')
    #p_dialog.create('', 'Please wait.  Loading Video.')
    vidlinks = []
    cntr = 0
    numentries = len(urls)
    totl = numentries
    #p_d_msg = "Found total of %s playlist items..."%(numentries)
    xbmcPlayer = xbmc.Player()
    playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
    playlist.clear() 
    play_started = 0
    # cycle through each url
    for url in urls:
        #print url
        cntr = cntr + 1
        if (play_started == 0):
            vidlinks1, noofitems = get_vid_link(url, 1)
            # add the first one to playlist and play it immediately
            if (totl == 1):
                totl = noofitems
            else:
                totl = (totl - 1) + noofitems
            #pct = int((cntr / float(totl)) * 100)
            if (len(vidlinks1) == 0):
                #print "videos array length returned for %s is 0"%(url)
                msg = "Video is invalid."
                notify(msg, 500)
                cntr = cntr - 1
            elif (vidlinks1[0] == ""):
                #print "first videos array item found for %s is null"%(url)
                msg = "Video is invalid."
                notify(msg, 500)
                cntr = cntr - 1
            elif (len(vidlinks1) == 1):
                #print "%s resolved!"%(url)
                videoId = vidlinks1[0]
                list_title = title +" ["+ str(cntr) +" of "+ str(totl) +"]"
                listitem = xbmcgui.ListItem(list_title)
                listitem.setThumbnailImage(thumbnail)
                msg = "Playing video."
                notify(msg, 500)
                playlist.add(videoId, listitem)
                #start playing!
                #print "start playing!"
                #p_dialog.update(pct, "", "Playing Video...")
                xbmcPlayer.play(playlist)
                play_started = 1
            else:
                #unexpected. we got more than 1 item.  we expected only one.
                #print "unexpected. we got more than 1 item.  we expected only one."
                #print totl
                #print len(vidlinks)
                print "%s error3"%(url)
                msg = "Video error 3."
                notify(msg, 500)
                cntr = cntr - 1
            # now that the first item is being played....
            # retrieve the rest of the videos if any and add them to the existing playlist.
            if ((play_started == 1) and (noofitems > 1)):
                #p_dialog.update(pct, "", "Loading rest of the videos...")
                msg = "Loading rest of the videos..."
                notify(msg, 500)
                vidlinks2, noofitems = get_vid_link(url, 2)
                for vid in vidlinks2:
                    if (vid == ""):
                        msg = "Video is invalid."
                        notify(msg, 500)
                    else:
                        vidlinks.append(vid)
        else:
            msg = "Loading rest of the videos..."
            notify(msg, 250)
            vidlinks3, noofitems = get_vid_link(url, 3)
            #pct = int((cntr / float(totl)) * 100)
            #p_dialog.update(pct, "", "Loading rest of the videos...")
            for vid in vidlinks3:
                if (vid == ""):
                    msg = "Video is invalid."
                    notify(msg, 500)
                else:
                    vidlinks.append(vid)
        #p_d_msg = "Got URL's of %s / %s items..."%(cntr, numentries)
        #p_dialog.update(int((cntr / float(numentries)) * 100), "Getting Multiple Video URL's", p_d_msg)
    vcntr = 2
    totl = len(vidlinks) + 1
    if (play_started == 1):
        if (len(vidlinks) > 0):
            msg = "Adding to playlist."
            notify(msg, 500)
        for videoId in vidlinks:
            list_title = title +" ["+ str(vcntr) +" of "+ str(totl) +"]"
            listitem = xbmcgui.ListItem(list_title)
            listitem.setThumbnailImage(thumbnail)
            playlist.add(videoId, listitem)
            vcntr = vcntr + 1 
        #p_dialog.close()
        msg = "Loading completed."
        notify(msg, 500)
    return 0

def build_url(query):
    base_url = sys.argv[0]
    return base_url + '?' + urllib.urlencode(query)

def get_page(url, common):
    if common == '':
        common = init_common()
    result = common.fetchPage({"link": url})
    if result["status"] == 200:
        return result["content"]
    else:
        dbox = xbmcgui.Dialog()
        dbox.ok(url, "Can't connect to site!", "Please try again later.")
    return 0

def post_page(url, postdata, common):
    if common == '':
        common = init_common()
    result = common.fetchPage({"link": url, "post_data": postdata})
    if result["status"] == 200:
        return result["content"]
    else:
        dbox = xbmcgui.Dialog()
        dbox.ok(url, "Can't connect to site!", "Please try again later.")
    return 0

def send_ga(dt):
    __addon__ = xbmcaddon.Addon()
    addon_name = __addon__.getAddonInfo('name')
    addon_version = __addon__.getAddonInfo('version')
    gauid, gaappid = get_ga_details()
    p_system = platform.system()
    p_release = platform.release()
    p_machine = platform.machine()
    xbmc_version = xbmc.getInfoLabel( "System.BuildVersion" )
    dt = urllib.quote_plus(dt)
    url = "http://www.google-analytics.com/collect?v=1&tid=%s&cid=%s&t=pageview&dp=%s&dt=%s"%(gaappid, gauid, dt, dt)
    url = url.encode("UTF-8")
    useragent = "%s/%s (%s; %s; %s) XBMC/%s"%(addon_name, addon_version, p_system, p_release, p_machine, xbmc_version)
    useragent = useragent.encode("UTF-8")
    headers = { 'User-Agent' : useragent }
    try:
        req = urllib2.Request(url, None, headers)
        try:
            response = urllib2.urlopen(req)
            #print url
            #print headers
        except:
            return 0
    except:
        return 0
    return 0

def get_mirror_name(msrclink):
    mname = msrclink.split(".")
    mnamet1 = mname[1]
    if (mnamet1.find("/") > -1):
        mnamet1 = mname[0].replace("http://", "")
    return mnamet1

def notify(msg, duration):
    __addon__ = xbmcaddon.Addon()
    __addonname__ = __addon__.getAddonInfo('name')
    __icon__ = __addon__.getAddonInfo('icon')
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, msg, duration, __icon__))
    return 0

def get_vid_link(url, mode):
    #print url
    # returns (array of urls, no of playlist items)
    # mode can be:
    # 1 - get first item of the playlist
    # 2 - get rest of the items starting with the second one
    # 3 - get all playlist items
    # if not a playlist then mode is irrelevant;   
    # only pass mode when it's to get_vidlink_youtube
    vidlink = []
    noofitems = 1
    if (url.find("dailymotion") > -1):
        vidlink = get_vidlink_dailymotion(url)
    elif (url.find("cloudy") > -1):
        vidlink = get_vidlink_cloudy(url)
    elif ((url.find("youtube") > -1) or (url.find("youtu.be") > -1)):
        vidlink, noofitems = get_vidlink_youtube(url, mode)
    elif (url.find("nowvideo") > -1):
        vidlink = get_vidlink_nowvideo(url)
    elif (url.find("allmyvideos") > -1):
        vidlink = get_vidlink_allmyvideos(url)
    elif (url.find("dmcdn.net") > -1):
        vidlink.append(url)
    elif (url.find("videomega") > -1):
        vidlink = get_vidlink_videomega(url)
    return vidlink, noofitems

def get_vidlink_dailymotion(url):
    import re
    videolink = []
    vidlink = ""
    match=re.compile('http://www.dailymotion.com/embed/video/(.+?)\?').findall(url)
    if(len(match) == 0):
        match=re.compile('http://www.dailymotion.com/video/(.+?)').findall(url)
    if(len(match) == 0):
        match=re.compile('http://www.dailymotion.com/swf/(.+?)\?').findall(url)
    if(len(match) == 0):
        match=re.compile('http://www.dailymotion.com/embed/video/(.+?)$').findall(url)
    link = 'http://www.dailymotion.com/embed/video/'+str(match[0])
    req = get_page(link, "")
    req = req.encode("UTF-8")
    matchFullHD = re.compile('"stream_h264_hd1080_url":"(.+?)"', re.DOTALL).findall(req)
    matchHD = re.compile('"stream_h264_hd_url":"(.+?)"', re.DOTALL).findall(req)
    matchHQ = re.compile('"stream_h264_hq_url":"(.+?)"', re.DOTALL).findall(req)
    matchSD = re.compile('"stream_h264_url":"(.+?)"', re.DOTALL).findall(req)
    matchLD = re.compile('"stream_h264_ld_url":"(.+?)"', re.DOTALL).findall(req)
    maxVideoQuality = "1080p"
    if matchFullHD and maxVideoQuality == "1080p":
        vidlink = urllib.unquote_plus(matchFullHD[0]).replace("\\", "")
    elif matchHD and (maxVideoQuality == "720p" or maxVideoQuality == "1080p"):
        vidlink = urllib.unquote_plus(matchHD[0]).replace("\\", "")
    elif matchHQ:
        vidlink = urllib.unquote_plus(matchHQ[0]).replace("\\", "")
    elif matchSD:
        vidlink = urllib.unquote_plus(matchSD[0]).replace("\\", "")
    elif matchLD:
        vidlink = urllib.unquote_plus(matchLD[0]).replace("\\", "")
    videolink.append(vidlink)
    return videolink

def get_vidlink_cloudy(url):
    import re
    videolink = []
    vidlink = ""
    common = init_common()
    pcontent = get_page(url, common)
    pcontent = ''.join(pcontent.splitlines()).replace('\'','"')
    if (len(pcontent) > 0):
        filecode = re.compile('flashvars.file="(.+?)";').findall(pcontent)[0]
        filekey = re.compile('flashvars.filekey="(.+?)";').findall(pcontent)[0]
        if (filecode is not None and filekey is not None):
            vidcontent = "https://www.cloudy.ec/api/player.api.php?file=%s&key=%s"%(filecode,urllib.quote_plus(filekey))
            pcontent = get_page(vidcontent, common)
            pcontent = ''.join(pcontent.splitlines()).replace('\'','"')
            if (len(pcontent) > 0):
                try:
                    urlcode = re.compile('url=(.+?)&').findall(pcontent)[0]
                except:
                    urlcode = ""
                if (urlcode is not None):
                    vidlink = urllib.unquote_plus(urlcode)
                    videolink.append(vidlink)
    return videolink

def get_vidlink_nowvideo(url):
    import re
    videolink = []
    vidlink = ""
    common = init_common()
    link = get_page(url, common)
    link = ''.join(link.splitlines()).replace('\'','"')
    fileid = re.compile('flashvars.file="(.+?)";').findall(link)[0]
    codeid = re.compile('flashvars.cid="(.+?)";').findall(link)
    if(len(codeid) > 0):
        codeid = codeid[0]
    else:
        codeid=""
    keycode = re.compile('flashvars.filekey=(.+?);').findall(link)[0]
    keycode = re.compile('var\s*'+keycode+'="(.+?)";').findall(link)[0]
    vidcontent = get_page("http://www.nowvideo.sx/api/player.api.php?codes="+urllib.quote_plus(codeid) + "&key="+urllib.quote_plus(keycode) + "&file=" + urllib.quote_plus(fileid), common)
    vidlink = re.compile('url=(.+?)\&').findall(vidcontent)[0]
    videolink.append(vidlink)
    return videolink

def get_vidlink_videomega(url):
    import re
    videolink = []
    vidlink = ""
    valid_url = ''
    vhurl = re.compile('validatehash').findall(url)
    if (len(vhurl)>0):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.65 Safari/537.36')
        req.add_header('Referer', 'http://www.lambingan.ru')
        vhpage = urllib2.urlopen(req)
        vhid = vhpage.read()
        #print vhid
        vhids = re.compile('var ref="(.+?)";').findall(vhid)
        #print vhids
        valid_url = "http://videomega.tv/cdn.php?ref=" + vhids[0] + "&#038;width=650&#038;height=400"
    else:
        valid_url = url
    req = urllib2.Request(valid_url.replace("#038;",""))
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.65 Safari/537.36')
    req.add_header('Referer', 'http://www.lambingan.ru')
    page = urllib2.urlopen(req)
    link = page.read()
    link2 = ''.join(link.splitlines()).replace('\'','"')
    urlcode = re.compile('>document.write\(unescape\("(.+?)"\)').findall(link2)
    #print urlcode
    vidcontent = urllib.unquote_plus(urlcode[0])
    #print vidcontent
    vidlinks = re.compile('file:\s*"(.+?)"\s*').findall(vidcontent)
    vidlink = vidlinks[0]
    #print vidlink
    useragent = 'User-Agent=' + urllib.quote_plus('Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.65 Safari/537.36')
    referer = 'Referer=' + urllib.quote_plus(valid_url.replace("#038;",""))
    addheaders = referer + '&' + useragent
    vidlink = vidlink + "|" + addheaders
    videolink.append(vidlink)
    return videolink

def get_vidlink_allmyvideos(url):
    import re
    videolink = []
    vidlink = ""
    common = init_common()
    videoid = re.compile('http://allmyvideos.net/embed-(.+?).html').findall(url)
    if (len(videoid)>0):
        newlink = "http://allmyvideos.net/"+videoid[0]
    link = get_page(newlink, common)
    idkey = re.compile('<input type="hidden" name="id" value="(.+?)">').findall(link)[0]
    op = re.compile('<input type="hidden" name="op" value="(.+?)">').findall(link)[0]
    fname = re.compile('<input type="hidden" name="fname" value="(.+?)">').findall(link)[0]
    mfree = re.compile('<input type="hidden" name="method_free" value="(.+?)">').findall(link)[0]
    posdata = {"op":op,"usr_login":"","id":idkey,"fname":fname,"referer":url,"method_free":mfree}
    pcontent = post_page(newlink, posdata, common)
    vidlink = re.compile('"file" : "(.+?)",').findall(pcontent)[0]
    videolink.append(vidlink)
    return videolink

def get_vidlink_youtube(url, mode):
    # returns (array of urls, no of playlist items)
    # mode can be:
    # 1 - get first item of the playlist
    # 2 - get rest of the items starting with the second one
    # 3 - get all playlist items
    # if not a playlist then mode is irrelevant;
    import re
    try:
        import simplejson as json
    except ImportError:
        import json
    from urlparse import parse_qs
    common = init_common()
    videolinks = []
    numentries = 1
    # if item is a playlist
    if (url.find("youtube") > -1) and ((url.find("list=") > -1) or (url.find("playlists") > -1) or (url.find("/p/") > -1)):
        #p_dialog = xbmcgui.DialogProgressBG()
        #p_dialog.create('Getting Youtube Playlist Video URL\'s', 'Getting Video URL\'s...')
        #print "YT playlist"
        playlistid = []
        playlistid = re.compile('videoseries\?list=(.+?)&').findall(url+"&")
        if (len(playlistid) == 0):
            playlistid = re.compile('list=(.+?)$').findall(url)
        if (len(playlistid) == 0):
            playlistid = re.compile('playlists/(.+?)\?v').findall(url)
        if (len(playlistid) == 0):
            playlistid = re.compile('/p/(.+?)\?').findall(url)
        plid = ''
        if (len(playlistid) > 0):
            plid = playlistid[0]
        else:
            #p_dialog.close()
            return "", 0
        # get information about the playlist
        ytapiurl = "http://gdata.youtube.com/feeds/api/playlists/" + plid
        pcontent = get_page(ytapiurl, common)
        entries = common.parseDOM(pcontent, "entry")
        vidlinks = []
        cntr = 0
        numentries = len(entries)
        #p_d_msg = "Found total of %s playlist items..."%(numentries)
        #p_dialog.update(1, "Getting Youtube Playlist Video URL's", p_d_msg)
        items_found = 0
        for entry in entries:
            cntr = cntr + 1
            # get the media:player url data
            murl = common.parseDOM(entry, "media:player", ret = "url")
            if (len(murl) == 0):
                # there's no url information about this playlist item; most likely the video has been deleted.  loop to the next item.
                continue
            cleanmurl = common.replaceHTMLCodes(murl[0])
            #mtnail = common.parseDOM(entry, "media:thumbnail", ret = "url")
            #cleanmtnail = common.replaceHTMLCodes(mtnail[0])
            #mtitle = common.parseDOM(entry, "media:title")
            #cleanmtitle = common.replaceHTMLCodes(mtitle[0])
            # get the videoid of this playlist item from the media:player url info
            match = re.compile('http://www.youtube.com/watch\?v=(.+?)&').findall(cleanmurl)
            #print match
            if(len(match) > 0):
                # now get the video file url
                vidlink = get_youtube_video_url(match[0], common, re, json, parse_qs)
                if (vidlink != ""):
                    items_found = items_found + 1
                    if (mode == 1):
                        videolinks.append(vidlink)
                        #return the first item immediately
                        break
                    elif (mode == 2):
                        if (items_found > 1):
                            #skip 1st item; then from 2nd item onwards, append them to the videolinks array.
                            videolinks.append(vidlink)
                    elif (mode == 3):
                        #append all to the videolinks array
                        videolinks.append(vidlink)
                #p_d_msg = "Got URL's of %s / %s playlist items..."%(cntr, numentries)
                #p_dialog.update(int((cntr / float(numentries)) * 100), "Getting Youtube Playlist Video URL's", p_d_msg)
    # if item is a single video
    elif (url.find("youtube") > -1) and (url.find("/embed/") > -1):
        #print "YT single video"
        videoid = re.compile('/embed/(.+?)\?').findall(url+"?")
        if (len(videoid) > 0):
            vidlink = get_youtube_video_url(videoid[0], common, re, json, parse_qs)
            videolinks.append(vidlink)
    # else item is not captured as playlist or single video
    else:
        #print "YT all the rest"
        match = re.compile('youtu\.be/(.+?)$').findall(url)
        #print match
        if (len(match) == 0):
            match = re.compile('(youtu\.be\/|youtube-nocookie\.com\/|youtube\.com\/(watch\?(.*&)?v=|(embed|v|user)\/))([^\?&"\'>]+)').findall(url)
        if (len(match) == 0):
            match = re.compile('http://www.youtube.com/watch\?v=(.+?)').findall(url)
        if (len(match) > 0):
            #lastmatch = match[0][len(match[0])-1].replace('v/','')
            lastmatch = match[0]
            #print lastmatch
        if (len(lastmatch) > 0):
            vidlink = get_youtube_video_url(lastmatch, common, re, json, parse_qs)
            videolinks.append(vidlink)
    return videolinks, numentries
 
def get_youtube_video_url(videoid, common, re, json, parse_qs):
    #print "get_youtube_video_url called"
    vapiurl = 'http://www.youtube.com/get_video_info?&video_id=' + videoid
    pcontent = get_page(vapiurl, common)
    pcontent = pcontent.encode("UTF-8")
    token = ""
    try:
        token = parse_qs(pcontent)['token'][0]
    except:
        return ""
    vurl = "http://www.youtube.com/watch?v=%s&t=%s&fmt=18"%(videoid, token)
    pcontent = get_page(vurl, common)
    pcontent = pcontent.encode("UTF-8")
    ytargs = ""
    scripts = common.parseDOM(pcontent, "script")
    for script in scripts:
        if (script.find("var ytplayer = ytplayer") != -1):
            match = re.compile("ytplayer.config = (.+?);ytplayer.load =").findall(script)
            if(len(match)>0):
                data1 = json.loads(match[0])
                #yurl = parse_qs(urllib.unquote(data1["args"]["url_encoded_fmt_stream_map"].decode('utf-8')))['url'][0]
                if not data1.has_key(u"args"):
                    return ""
                ytargs = data1["args"]
    if len(ytargs) == 0:
        return ""
    if not ytargs.has_key(u"url_encoded_fmt_stream_map"):
        return ""
    links = {}
    for url_desc in ytargs[u"url_encoded_fmt_stream_map"].split(u","):
        #print "URL_DESC: "
        #print url_desc
        url_desc_map = parse_qs(url_desc)
        #print "URL_DESC_MAP: " 
        #print url_desc_map
        if not (url_desc_map.has_key(u"url") or url_desc_map.has_key(u"stream")):
            print "has no key url or stream"
            continue
        key = int(url_desc_map[u"itag"][0])
        #print "KEY:"
        #print key
        url = u""
        if url_desc_map.has_key(u"url"):
            url = urllib.unquote(url_desc_map[u"url"][0])
            #print "has key url"
            #print url
        elif url_desc_map.has_key(u"stream"):
            url = urllib.unquote(url_desc_map[u"stream"][0])
            #print "has key stream"
            #print url
        if url_desc_map.has_key(u"sig"):
            url = url + u"&signature=" + url_desc_map[u"sig"][0]
            #print "has key sig"
            #print url
        links[key] = url
    video_url = ""
    link = links.get
    itags = [ 121, 120, 102, 101, 100, 85, 84, 83, 82, 78, 59, 46, 45, 44, 43, 38, 37, 35, 34, 33, 26, 22, 18, 5 ]
    #5: "240p h263 flv container",
    #18: "360p h264 mp4 container | 270 for rtmpe?",
    #22: "720p h264 mp4 container",
    #26: "???",
    #33: "???",
    #34: "360p h264 flv container",
    #35: "480p h264 flv container",
    #37: "1080p h264 mp4 container",
    #38: "720p vp8 webm container",
    #43: "360p h264 flv container",
    #44: "480p vp8 webm container",
    #45: "720p vp8 webm container",
    #46: "520p vp8 webm stereo",
    #59: "480 for rtmpe",
    #78: "seems to be around 400 for rtmpe",
    #82: "360p h264 stereo",
    #83: "240p h264 stereo",
    #84: "720p h264 stereo",
    #85: "520p h264 stereo",
    #100: "360p vp8 webm stereo",
    #101: "480p vp8 webm stereo",
    #102: "720p vp8 webm stereo",
    #120: "hd720",
    #121: "hd1080"
    #useragent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36'
    useragent = 'User-Agent=Mozilla%2F5.0+%28Windows+NT+6.2%3B+Win64%3B+x64%3B+rv%3A16.0.1%29+Gecko%2F20121011+Firefox%2F16.0.1'
    for itag in itags:
        if (link(itag)):
            video_url = link(itag)
            break
    video_url += "|" + useragent
    return video_url

def get_streamph_sources(url):
    import re
    try:
        import simplejson as json
    except ImportError:
        import json
    videolink = []
    common = init_common()
    pcontent = get_page(url, common)
    sconfig = re.compile('<script>var config =(.+?);</script>').findall(pcontent)[0]
    hsdata = json.loads(sconfig)
    purl = hsdata["log"]
    posdata = hsdata["param"]
    pcontent2 = post_page(purl, posdata, common)
    pdata = json.loads(pcontent2)
    if (pdata["embed"] == "0"):
        if (len(pdata["conf"]["playlist"]) == 1):
            pvidlink = pdata["conf"]["playlist"][0]["sources"][0]["file"]
            videolink.append(pvidlink)
        else:
            # multiple source files in the playlist; get all urls and feed to load_all_videos
            for murldata in pdata["conf"]["playlist"]:
                murl = murldata["sources"][0]["file"]
                videolink.append(murl)
    else:
        # video is embedded in iframe
        ifsdata = pdata["code"]
        ifslink = common.parseDOM(ifsdata, "iframe", ret = "src")
        ifs = ""
        if (len(ifslink) > 0):
            ifs = ifslink[0]
        else:
            return ""
        # check if URL starts with just // and not the usual http: or https:; add it accordingly
        dblslshpat = re.compile("//")
        if (dblslshpat.match(ifs, 0) > -1):
            ifs = "http:"+ifs
        videolink.append(ifs)        
    return videolink

"""
Everything under this comment block is customized for this addon.  All above functions can be used for other addons.
"""

def get_lambingantv_sources(url):
    import re
    videolink = []
    common = init_common()
    pcontent = get_page(url, common)
    ifslink = common.parseDOM(pcontent, "iframe", ret = "src")
    ifs = ""
    if (len(ifslink) > 0):
        ifs = ifslink[0]
    else:
        return ""
    # check if URL starts with just // and not the usual http: or https:; add it accordingly
    dblslshpat = re.compile("//")
    if (dblslshpat.match(ifs, 0) > -1):
        ifs = "http:"+ifs
    videolink.append(ifs)        
    return videolink

def get_ga_details():
    gauid = ''
    gaappid = 'UA-65751650-1'
    xbmcsettings = xbmcaddon.Addon(id='plugin.video.lambingan')
    gauid = xbmcsettings.getSetting("gauid")
    #print "GA UID from settings file"
    #print gauid
    if (gauid == '555') or (len(gauid) == 0):
        uid_gen = uuid.uuid4()
        uid = str(uid_gen)
        #print "Random UID:"
        #print uid
        xbmcsettings.setSetting(id="gauid", value=uid)
        gauid = xbmcsettings.getSetting("gauid")
    return (gauid, gaappid)

def init_common():
    import CommonFunctions
    common = CommonFunctions
    common.plugin = "lambingan"
    common.dbg = True
    common.dbglevel = 3
    return common

def get_latest(url):
    addon_handle = int(sys.argv[1])
    xbmcplugin.setContent(addon_handle, 'movies')
    common = init_common()
    # retrieve url and save it to wpage
    wpage = get_page(url, common)
    wpage = wpage.encode("UTF-8")
    # wpage is the url page, and can be re-used later in this function.
    # now zoom in on a particular section of the page where we could find the video links,
    # save the section contents as vidsec
    rboxcon = common.parseDOM(wpage, "div", attrs = {"class": "review-box-container"})
    for r in rboxcon:
        rbox = common.parseDOM(r, "div", attrs = {"class": "review-box review-box-extended"})
        for rb in rbox:
            vidlink = common.parseDOM(rb, "a", ret = "href")
            vidname = common.parseDOM(rb, "a")
            if (len(vidname) > 1):
                newvidname = common.makeAscii(vidname[1])
            else:
                newvidname = common.makeAscii(vidname[0])
            # get thumbnail
            tnlink = common.parseDOM(rb, "img", ret = "src")
            thumbnail = ''
            if (len(tnlink) > 0):
                thumbnail = tnlink[0]
            durl = build_url({'url': vidlink[0], 'mode': 'folder', 'foldername': newvidname, 'thumbnail': thumbnail})
            li = xbmcgui.ListItem(newvidname, iconImage=thumbnail)
            li.setProperty('fanart_image', thumbnail)
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=durl, listitem=li, isFolder=True)
    # get newer/older posts page links
    bpager = common.parseDOM(wpage, "div", attrs={"class": "wp-pagenavi cat-navi"})
    plinks = common.parseDOM(bpager, "a", ret = "href")
    tgtindx = len(plinks) - 2
    oldlink = ""
    if (len(plinks) > 2):
        oldlink = plinks[tgtindx]
    oldlink = oldlink.replace("?page", "/?page")
    lpagename = "[COLOR blue] Next Page [/COLOR]"
    durl = build_url({'url': oldlink, 'mode': 'getLatest', 'foldername': 'Next Page'})
    li = xbmcgui.ListItem(lpagename, iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=durl, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)
    return 0

def get_video_links(url,thumbnail,foldername):
    import re
    common = init_common()
    addon_handle = int(sys.argv[1])
    xbmcplugin.setContent(addon_handle, 'movies')
    mirrorcntr = {}
    # Add first item which is the Video Title with no link or action
    title = foldername
    titlename = "[COLOR red][B]"+title+"[/B][/COLOR]"
    durl = build_url({'foldername': foldername})
    li = xbmcgui.ListItem(titlename, iconImage=thumbnail)
    li.setProperty('fanart_image', thumbnail)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=durl, listitem=li)
    # retrieve page and save into wpage
    wpage = get_page(url, common)
    wpage = wpage.encode("UTF-8")
    ret = common.parseDOM(wpage, "div", attrs = {"id": "post-content"})
    linkseen = {}
    for vidsec in ret:
        #scrape tabber videos
        #we expect the group of video links (per mirror) within vidsec.  let's save array into vidlinkgrp.
        vidlinkgrp = common.parseDOM(vidsec, "div", attrs = {"class": "tabber"})
        for vlgrp in vidlinkgrp:
            #get the name of this mirror from the first item!
            iframesrc = common.parseDOM(vlgrp, "iframe", ret = "src")
            mirrornamet1 = get_mirror_name(iframesrc[0])
            #we expect the parts of the video within vlgrp.  let's save array into parts.
            parts = common.parseDOM(vlgrp, "div", attrs = {"class": "tabbertab"})
            partcntr = 1
            ptotal = len(parts)
            links = []
            for part in parts:
                ifslink = common.parseDOM(part, "iframe", ret = "src")
                for ifs in ifslink:
                    # check if URL starts with just // and not the usual http: or https:; add it accordingly
                    dblslshpat = re.compile("//")
                    if (dblslshpat.match(ifs, 0) > -1):
                        ifs = "http:"+ifs
                    linkseen[str(ifs)] = 1
                    ltotal = len(parts)
                    mirrorname = ""
                    if (len(parts) == 1):
                        mirrorname = "["+mirrornamet1+"] Full"
                    else:
                        mirrorname = "["+mirrornamet1+"] part "+str(partcntr)+" of "+str(ltotal)
                    links.append(str(ifs))
                    durl = build_url({'url': ifs, 'mode': 'playVideo', 'foldername': mirrorname, 'thumbnail': thumbnail, 'title': title})
                    li = xbmcgui.ListItem(mirrorname, iconImage=thumbnail)
                    li.setInfo(type="Video",infoLabels={"Title": mirrorname})
                    li.setProperty('fanart_image', thumbnail)
                    xbmcplugin.addDirectoryItem(handle=addon_handle, url=durl, listitem=li)
                    partcntr = partcntr + 1
                #end ifslink loop
            #end parts loop
            #if there is more than 1 part, then add item to play all parts
            if (len(links) > 1):
                durl = build_url({'url': links, 'mode': 'playAllVideos', 'foldername': mirrornamet1, 'thumbnail': thumbnail, 'title': title})
                itemname = '[COLOR green]-->Play All above '+mirrornamet1+' parts[/COLOR]'
                li = xbmcgui.ListItem(itemname, iconImage=thumbnail)
                li.setInfo(type="Video",infoLabels={"Title": mirrornamet1})
                li.setProperty('fanart_image', thumbnail)
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=durl, listitem=li)
        #end vidlinkgrp loop
        #scrape non-tabber videos
        ntmirrors = []
        ntlinks = {}
        ifslink = common.parseDOM(vidsec, "iframe", ret = "src")
        ifslink2 = common.parseDOM(vidsec, "IFRAME", ret = "SRC")
        ifslink = ifslink + ifslink2
        for ifs in ifslink:
            # check if URL starts with just // and not the usual http: or https:; add it accordingly
            dblslshpat = re.compile("//")
            if (dblslshpat.match(ifs, 0) > -1):
                ifs = "http:"+ifs
            if str(ifs) in linkseen:
                continue
            mirrornamet1 = get_mirror_name(ifs)
            if (mirrornamet1 == 'facebook'):
                continue
            if (mirrornamet1 == 'lambingantv'):
                sources = get_lambingantv_sources(ifs)
                for source in sources:
                    #print source
                    mirrornamet1 = get_mirror_name(source)
                    if str(mirrornamet1) in ntlinks:
                        ntlinks[str(mirrornamet1)].append(str(source))
                    else:
                        ntlinks[str(mirrornamet1)] = []
                        ntlinks[str(mirrornamet1)].append(str(source))
                    if str(mirrornamet1) in mirrorcntr:
                        mirrorcntr[str(mirrornamet1)] = mirrorcntr[mirrornamet1] + 1
                    else:
                        mirrorcntr[str(mirrornamet1)] = 1
            else:
                if str(mirrornamet1) in ntlinks:
                    ntlinks[str(mirrornamet1)].append(str(ifs))
                else:
                    ntlinks[str(mirrornamet1)] = []
                    ntlinks[str(mirrornamet1)].append(str(ifs))
                if str(mirrornamet1) in mirrorcntr:
                    mirrorcntr[str(mirrornamet1)] = mirrorcntr[mirrornamet1] + 1
                else:
                    mirrorcntr[str(mirrornamet1)] = 1
        #end ifslink loop
        for mirrornamet1 in ntlinks:
            mlinkscntr = 1
            for mlinks in ntlinks[str(mirrornamet1)]:
                if mirrorcntr[str(mirrornamet1)] == 1:
                    mirrorname = "["+mirrornamet1+"] Full"
                else :
                    mirrorname = "["+mirrornamet1+"] link "+ str(mlinkscntr) +" of "+str(mirrorcntr[str(mirrornamet1)])
                durl = build_url({'url': mlinks, 'mode': 'playVideo', 'foldername': mirrorname, 'thumbnail': thumbnail, 'title': title})
                li = xbmcgui.ListItem(mirrorname, iconImage=thumbnail)
                li.setInfo(type="Video",infoLabels={"Title": mirrorname})
                li.setProperty('fanart_image', thumbnail)
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=durl, listitem=li)
                mlinkscntr = mlinkscntr + 1
            #if there is more than 1 link for this mirror, then add item to play all links
            if (len(ntlinks[str(mirrornamet1)]) > 1):
                durl = build_url({'url': ntlinks[str(mirrornamet1)], 'mode': 'playAllVideos', 'foldername': mirrornamet1, 'thumbnail': thumbnail, 'title': title})
                itemname = '[COLOR green]-->Play All above '+mirrornamet1+' links[/COLOR]'
                li = xbmcgui.ListItem(itemname, iconImage=thumbnail)
                li.setInfo(type="Video",infoLabels={"Title": mirrornamet1})
                li.setProperty('fanart_image', thumbnail)
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=durl, listitem=li)
                
    #end ret loop
    xbmcplugin.endOfDirectory(addon_handle)
    return 0

def search():
    keyb = xbmc.Keyboard('', 'Enter search text')
    keyb.doModal()
    searchText = ''
    if (keyb.isConfirmed()):
        searchText = urllib.quote_plus(keyb.getText())
    if (searchText == ''):
        return 0
    else:
        url = 'http://www.lambingan.ru/?s='+ searchText +'&x=0&y=0'
        get_latest(url)
    return 0

def home():
    wurl = "http://www.lambingan.ru"
    addon_handle = int(sys.argv[1])
    xbmcplugin.setContent(addon_handle, 'movies')
    #Search
    #durl = build_url({'mode': 'search', 'foldername': "Search"})
    #li = xbmcgui.ListItem("Search", iconImage='DefaultFile.png')
    #li.setProperty('fanart_image', fanartimg)
    #xbmcplugin.addDirectoryItem(handle=addon_handle, url=durl, listitem=li, isFolder=True)
    #Latest Posts
    durl = build_url({'url': wurl, 'mode': 'getLatest', 'foldername': "Latest Posts"})
    li = xbmcgui.ListItem("Latest Posts", iconImage='DefaultFolder.png')
    #li.setProperty('fanart_image', fanartimg)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=durl, listitem=li, isFolder=True)

    #Pinoy Movies
    #durl = build_url({'url': 'http://www.lambingan.ru/category/pinoy-movies', 'mode': 'getLatest', 'foldername': "Pinoy Movies"})
    #li = xbmcgui.ListItem("Pinoy Movies", iconImage='DefaultFolder.png')
    #li.setProperty('fanart_image', fanartimg)
    #xbmcplugin.addDirectoryItem(handle=addon_handle, url=durl, listitem=li, isFolder=True)

    durl = build_url({'url': 'http://www.lambingan.ru/category/abs-cbn', 'mode': 'getLatest', 'foldername': "Ch 2 Shows"})
    li = xbmcgui.ListItem("Kapamilya Shows", iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=durl, listitem=li, isFolder=True)

    durl = build_url({'url': 'http://www.lambingan.ru/category/Gma7', 'mode': 'getLatest', 'foldername': "Ch 7 Shows"})
    li = xbmcgui.ListItem("Kapuso Shows", iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=durl, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)
    return 0

def main():
    import urlparse
    args = urlparse.parse_qs(sys.argv[2][1:])
    mode = args.get('mode', None)
    if mode is None:
        send_ga_res = send_ga('Home')
        home()
    elif mode[0] == "getLatest":
        foldername = args['foldername'][0]
        #print foldername
        send_ga_res = send_ga(foldername)
        get_latest(args['url'][0])
    elif mode[0] == "search":
        foldername = args['foldername'][0]
        #print foldername
        send_ga_res = send_ga(foldername)
        search()
    elif mode[0] == 'folder':
        foldername = args['foldername'][0]
        #print foldername
        send_ga_res = send_ga(foldername)
        url = args['url'][0]
        try:
            thumbnail = args['thumbnail'][0]
        except:
            thumbnail = ""
        get_video_links(url,thumbnail,foldername)
    elif mode[0] == 'playVideo':
        foldername = args['foldername'][0]
        title = args['title'][0]
        tfname = "%s - %s"%(title, foldername)
        send_ga_res = send_ga(tfname)
        url = args['url'][0]
        aurl = []
        aurl.append(url)
        thumbnail = args['thumbnail'][0]
        load_videos(aurl,thumbnail,title)
    elif mode[0] == 'playAllVideos':
        foldername = args['foldername'][0]
        title = args['title'][0]
        tfname = "%s - %s"%(title, foldername)
        send_ga_res = send_ga(tfname)
        url = args['url'][0]
        thumbnail = args['thumbnail'][0]
        url = url.replace("[","").replace("]","").replace("'","")
        urls = url.split(", ")
        load_videos(urls,thumbnail,title)
    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)
