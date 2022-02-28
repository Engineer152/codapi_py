import httpx
import urllib
import json
import random
import string

userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
baseCookie = {"new_SiteId":"cod","ACT_SSO_LOCALE":"en_US","country":"US"}
ssoCookie = ""
loggedIn = False
debug = 0

headers={
    "content-type": "application/json",
    "Referer": "https://my.callofduty.com/home",
    "x-requested-with": userAgent,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Connection": "keep-alive"
}
cookies=baseCookie

httpxclient = httpx.Client(http2=True,headers=headers,cookies=cookies)

defaultBaseURL = "https://my.callofduty.com/api/papi-client/"
defaultProfileURL = "https://profile.callofduty.com/"

def uniqid():
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(16))
    return result_str

class _helpers():

    def __init__(self, headers, cookies, proxies):
        self.headers = headers
        self.cookies = cookies
        self.proxies = _helpers.genproxy(proxies)

    def genproxy(self,proxies):
        if (proxies==[]): return None
        ip=random.choice(proxies)
        return {"https://": f"http://{ip}"}

    def buildUri(self, str):
        return f'{defaultBaseURL}+{str}'

    def buildProfileUri(self, str):
        return '{defaultProfileURL}+{str}'

    def cleanClientName(self, gamertag):
        return urllib.parse.quote(gamertag)

    def sendRequestUserInfoOnly(self, url):
        if (not loggedIn): return ("Not Logged In.")
        r=httpxclient.get(url, headers = self.headers, cookies = self.cookies, proxies = self.proxies)
        if (r.status == 403): return ("Forbidden. You may be IP banned.")
        else: return r.json()

    def sendRequest(self, url):
        if (not loggedIn): return ("Not Logged In.")
        r=httpxclient.get(url, headers = self.headers, cookies = self.cookies, proxies = self.proxies)
        if (r.data.status != None and r.data.status == 'success'):
            return r.data.data
        else:
            return _helpers.apiErrorHandling(r)

    def sendPostRequest(self, url, data):
        if (not loggedIn): return ("Not Logged In.")
        r=httpxclient.post(url, data=json.dumps(data), headers = self.headers, cookies = self.cookies, proxies = self.proxies)
        if (r.data.status != None and r.data.status == 'success'):
            return r.data.data
        else:
            return _helpers.apiErrorHandling(r)

    def postReq(self, url, data, headers = None):
        r=httpxclient.post(url, data, headers = self.headers, cookies = self.cookies, proxies = self.proxies)
        if (r.data.status != None and r.data.status == 'success'):
            return r
        else:
            return _helpers.apiErrorHandling(r)

    def sendRawRequest(self, url, **kwargs):
        r=httpxclient.post(url, headers = self.headers, cookies = self.cookies, proxies = self.proxies)
        if (r.status != None and r.status == 200):
            return (r.data)
        else:
            return _helpers.apiErrorHandling(r)

    def platformcheck(self, platform):
        platforms = {
            "battle": "battle",
            "steam": "steam",
            "psn": "psn",
            "xbl": "xbl",
            "acti": "acti",
            "uno": "uno"}
        if platform in platforms.keys():
            return True
        else:
            return f"{platform} is not a correct platform, please try: battle, psn, xbl, steam, acti, or uno."

    def apiErrorHandling(self, r):
        status=r.status_code
        if status==200:
            try: resp=r.json()
            except: pass
            try: msg=resp['data']['message']
            except: pass
            if msg=='Not permitted: user not found':
                return '404 - Not found. Incorrect username or platform? Misconfigured privacy settings?'
            elif msg=='Not permitted: rate limit exceeded':
                return '429 - Too many requests. Try again in a few minutes.'
            elif msg=='Error from datastore':
                return '500 - Internal server error. Request failed, try again.'
            else: return r
        elif status==401:
            return '401 - Unauthorized. Incorrect username or password.'
        elif status==403:
            return '403 - Forbidden. You may have been IP banned. Try again in a few minutes.'
        elif status==500:
            return '500 - Internal server error. Request failed, try again.'
        elif status==502:
            return '502 - Bad gateway. Request failed, try again.'
        return f'We Could not get a valid reason for a failure. Status: {status}'

class CODAPI():
    config = {"platform":"uno"}

    def __init__(self,sso_token=None,cookies=cookies,headers=headers,proxies=[]):
        self.sso = sso_token
        self.platform = "uno"
        self.timeout = 5
        self.cookies = cookies
        self.headers = headers
        self.proxies = proxies
        self.loggedIn = loggedIn
        login = self.login()
        self.helpers = _helpers(self.headers,self.cookies,self.proxies)

    def login (self):
        if (type(self.sso) == None or len(self.sso)<=0): return ("SSO token is invalid.")
        loginURL = "https://profile.callofduty.com/cod/mapp/"
        deviceId = uniqid()
        r=_helpers.postReq(f'{loginURL}registerDevice', {'deviceId': deviceId})
        authHeader = r.data.authHeader
        fakeXSRF = "68e8b62e-1d9d-4ce1-b93f-cbe5ff31a041"
        self.headers['Authorization'] = f'bearer {authHeader}'
        self.headers['x_cod_device_id'] = f'{deviceId}'
        self.headers["X-XSRF-TOKEN"] = fakeXSRF
        self.headers["X-CSRF-TOKEN"] = fakeXSRF
        self.headers["Atvi-Auth"] = f'Bearer {self.sso}'
        self.headers["ACT_SSO_COOKIE"] = f'{self.sso}'
        self.headers["atkn"] = f'{self.sso}'
        ssoCookie = self.sso;
        new_cookies = {"ACT_SSO_COOKIE": self.sso,"XSRF-TOKEN": fakeXSRF,"API_CSRF_TOKEN":fakeXSRF,"ACT_SSO_EVENT":"LOGIN_SUCCESS:1644346543228","ACT_SSO_COOKIE_EXPIRY":1645556143194,"comid":"cod","ssoDevId":"63025d09c69f47dfa2b8d5520b5b73e4","tfa_enrollment_seen":"true","gtm.custom.bot.flag":"human"}
        self.cookies.update(new_cookies)
        self.loggedIn = True
        return ("200 - Logged in with SSO.")

    ## BLACK OPS 4 ##
    def BO4Stats(self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            if (platform == "battle"): 
                gamertag = _helpers.cleanClientName(gamertag)
                urlInput = _helpers.buildUri(f"crm/cod/v2/title/bo4/platform/{platform}/gamer/{gamertag}/profile/type/mp")
            return self.helpers.sendRequest(urlInput)
        return platform

    def BO4zm (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            if (platform == "battle"):
                gamertag = _helpers.cleanClientName(gamertag)
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/bo4/platform/{platform}/gamer/{gamertag}/profile/type/zm')
            return self.helpers.sendRequest(urlInput)
        return platform

    def BO4mp (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            if (platform == "battle"):
                gamertag = _helpers.cleanClientName(gamertag)
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/bo4/platform/{platform}/gamer/{gamertag}/profile/type/mp')
            return self.helpers.sendRequest(urlInput)
        return platform

    def BO4blackout (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            if (platform == "battle"):
                gamertag = _helpers.cleanClientName(gamertag)
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/bo4/platform/{platform}/gamer/{gamertag}/profile/type/wz')
            return self.helpers.sendRequest(urlInput)
        return platform

    def BO4friends (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            if (platform == "battle"):
                return ("Battlenet does not support Friends.")
            urlInput = _helpers.buildUri(f'leaderboards/v2/title/bo4/platform/{platform}/time/alltime/type/core/mode/career/gamer/{gamertag}/friends')
            return self.helpers.sendRequest(urlInput)
        return platform

    def BO4combatmp (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            if (platform == "battle"):
                gamertag = _helpers.cleanClientName(gamertag)
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/bo4/platform/{platform}/gamer/{gamertag}/matches/mp/start/0/end/0/details')
            return self.helpers.sendRequest(urlInput)
        return platform

    def BO4combatmpdate (self, gamertag, start = 0, end = 0, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            if (platform == "battle"):
                gamertag = _helpers.cleanClientName(gamertag)
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/bo4/platform/{platform}/gamer/{gamertag}/matches/mp/start/{start}/end/{end}/details')
            return self.helpers.sendRequest(urlInput)
        return platform

    def BO4combatzm (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            if (platform == "battle"):
                gamertag = _helpers.cleanClientName(gamertag)
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/bo4/platform/{platform}/gamer/{gamertag}/matches/zombies/start/0/end/0/details')
            return self.helpers.sendRequest(urlInput)
        return platform

    def BO4combatzmdate (self, gamertag, start = 0, end = 0, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            if (platform == "battle"):
                gamertag = _helpers.cleanClientName(gamertag)
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/bo4/platform/{platform}/gamer/{gamertag}/matches/zombies/start/{start}/end/{end}/details')
            return self.helpers.sendRequest(urlInput)
        return platform

    def BO4combatbo (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            if (platform == "battle"):
                gamertag = _helpers.cleanClientName(gamertag)
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/bo4/platform/{platform}/gamer/{gamertag}/matches/warzone/start/0/end/0/details')
            return self.helpers.sendRequest(urlInput)
        return platform

    def BO4combatbodate (self, gamertag, start = 0, end = 0, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            if (platform == "battle"):
                gamertag = _helpers.cleanClientName(gamertag)
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/bo4/platform/{platform}/gamer/{gamertag}/matches/warzone/start/{start}/end/{end}/details')
            return self.helpers.sendRequest(urlInput)
        return platform

    def BO4leaderboard (self, page, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            urlInput = _helpers.buildUri(f'leaderboards/v2/title/bo4/platform/{platform}/time/alltime/type/core/mode/career/page/{page}')
            return self.helpers.sendRequest(urlInput)
        return platform

    ## MODERN WARFARE / WARZONE ##
    def MWleaderboard (self, page, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            urlInput = _helpers.buildUri(f'leaderboards/v2/title/mw/platform/{platform}/time/alltime/type/core/mode/career/page/{page}')
            return self.helpers.sendRequest(urlInput)
        return platform

    def MWcombatmp (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for MW. Try `battle` instead.")
            gamertag = _helpers.cleanClientName(gamertag)
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/mw/platform/{platform}/{lookupType}/{gamertag}/matches/mp/start/0/end/0/details')
            return self.helpers.sendRequest(urlInput)
        return platform

    def MWcombatmpdate (self, gamertag, platform, start = 0, end = 0):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            gamertag = _helpers.cleanClientName(gamertag);
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/mw/platform/{platform}/{lookupType}/{gamertag}/matches/mp/start/{start}/end/{end}/details')
            return self.helpers.sendRequest(urlInput)
        return platform

    def MWcombatwz (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for WZ. Try `battle` instead.")
            gamertag = _helpers.cleanClientName(gamertag)
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/mw/platform/{platform}/{lookupType}/{gamertag}/matches/wz/start/0/end/0/details')
            return self.helpers.sendRequest(urlInput)
        return platform

    def MWcombatwzdate (self, gamertag, platform, start = 0, end = 0):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            gamertag = _helpers.cleanClientName(gamertag);
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/mw/platform/{platform}/{lookupType}/{gamertag}/matches/wz/start/{start}/end/{end}/details')
            return self.helpers.sendRequest(urlInput)
        return platform


    def MWfullcombatmp (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for MW. Try `battle` instead.")
            gamertag = _helpers.cleanClientName(gamertag)
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/mw/platform/{platform}/{lookupType}/{gamertag}/matches/mp/start/0/end/0')
            return self.helpers.sendRequest(urlInput)
        return platform

    def MWfullcombatmpdate (self, gamertag, start = 0, end = 0, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            gamertag = _helpers.cleanClientName(gamertag);
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/mw/platform/{platform}/{lookupType}/{gamertag}/matches/mp/start/{start}/end/{end}')
            return self.helpers.sendRequest(urlInput)
        return platform

    def MWfullcombatwz (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for WZ. Try `battle` instead.")
            gamertag = _helpers.cleanClientName(gamertag)
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/mw/platform/{platform}/{lookupType}/{gamertag}/matches/wz/start/0/end/0')
            return self.helpers.sendRequest(urlInput)
        return platform

    def MWfullcombatwzdate (self, gamertag, start = 0, end = 0, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for BO4. Try `battle` instead.")
            gamertag = _helpers.cleanClientName(gamertag);
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/mw/platform/{platform}/{lookupType}/{gamertag}/matches/wz/start/{start}/end/{end}')
            return self.helpers.sendRequest(urlInput)
        return platform

    def MWmp (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for MW. Try `battle` instead.")
            gamertag = _helpers.cleanClientName(gamertag)
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'stats/cod/v1/title/mw/platform/{platform}/{lookupType}/{gamertag}/profile/type/mp')
            return self.helpers.sendRequest(urlInput)
        return platform

    def MWwz (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for WZ. Try `battle` instead.")
            gamertag = _helpers.cleanClientName(gamertag)
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'stats/cod/v1/title/mw/platform/{platform}/{lookupType}/{gamertag}/profile/type/wz')
            return self.helpers.sendRequest(urlInput)
        return platform

    ## PARSE BATTLE DATA ##
    # def MWBattleData (gamertag, platform):
    #     platform = _helpers.platformcheck()
    #     if platform:
    #         brDetails = {};
    #         data=COD_API.MWwz(gamertag, platform)
    #         try: lifetime = data['lifetime']
    #         except: lifetime="undefined"
    #         if (lifetime != "undefined"):
    #             filtered = Object.keys(lifetime.mode).filter(x => x.startsWith("br")).reduce((obj, key) => {
    #                 obj[key] = lifetime.mode[key];
    #                 return obj;
    #             }, {});
    #             if (typeof filtered.br !== "undefined") {
    #                 filtered.br.properties.title = "br";
    #                 brDetails.br = filtered.br.properties;
    #             }
    #             if (typeof filtered.br_dmz !== "undefined") {
    #                 filtered.br_dmz.properties.title = "br_dmz";
    #                 brDetails.br_dmz = filtered.br_dmz.properties;
    #             }
    #             if (typeof filtered.br_all !== "undefined") {
    #                 filtered.br_all.properties.title = "br_all";
    #                 brDetails.br_all = filtered.br_all.properties;
    #             }
    #         }
    #             resolve(brDetails);
    #         }).catch(e => reject(e));
    #     });
    # };

    def MWfriends (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for MW. Try `battle` instead.")
            if (platform == "battle"):
                return ("Battlenet friends are not supported. Try a different platform.")
            if (platform == "uno"):
                gamertag = _helpers.cleanClientName(gamertag);
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'stats/cod/v1/title/mw/platform/{platform}/{lookupType}/{gamertag}/profile/friends/type/mp')
            return self.helpers.sendRequest(urlInput)
        return platform

    def MWWzfriends (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for WZ. Try `battle` instead.")
            if (platform == "battle"):
                return ("Battlenet friends are not supported. Try a different platform.")
            if (platform == "uno"):
                gamertag = _helpers.cleanClientName(gamertag);
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'stats/cod/v1/title/mw/platform/{platform}/{lookupType}/{gamertag}/profile/friends/type/wz')
            return self.helpers.sendRequest(urlInput)
        return platform

    def MWstats (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for MW. Try `battle` instead.")
            if (platform == "uno"):
                gamertag = _helpers.cleanClientName(gamertag);
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'stats/cod/v1/title/mw/platform/{platform}/{lookupType}/{gamertag}/profile/type/mp')
            return self.helpers.sendRequest(urlInput)
        return platform


    def MWwzstats (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for WZ. Try `battle` instead.")
            if (platform == "uno"):
                gamertag = _helpers.cleanClientName(gamertag);
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'stats/cod/v1/title/mw/platform/{platform}/{lookupType}/{gamertag}/profile/type/wz')
            return self.helpers.sendRequest(urlInput)
        return platform

    ## PARSE WEEKLY STATS ##
    # module.MWweeklystats = function (gamertag, platform = config.platform) {
    #     return new Promise((resolve, reject) => {
    #         weeklyStats = {};
    #         this.MWstats(gamertag, platform).then((data) => {
    #             if (typeof data.weekly !== "undefined") weeklyStats.mp = data.weekly;
    #             this.MWwzstats(gamertag, platform).then((data) => {
    #                 if (typeof data.weekly !== "undefined") weeklyStats.wz = data.weekly;
    #                 resolve(weeklyStats);
    #             }).catch(e => reject(e));
    #         }).catch(e => reject(e));
    #     });
    # };

    def MWloot (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for MW. Try `battle` instead.")
            if (platform == "uno"):
                gamertag = _helpers.cleanClientName(gamertag)
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'loot/title/mw/platform/{platform}/{lookupType}/{gamertag}/status/en')
            return self.helpers.sendRequest(urlInput)
        return platform

    def MWAnalysis (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for MW. Try `battle` instead.")
            if (platform == "uno"):
                gamertag = _helpers.cleanClientName(gamertag)
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'ce/v2/title/mw/platform/{platform}/gametype/all/gamer/{gamertag}/summary/match_analysis/contentType/full/end/0/matchAnalysis/mobile/en')
            return self.helpers.sendRequest(urlInput)
        return platform

    def MWMapList (self, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'ce/v1/title/mw/platform/{platform}/gameType/mp/communityMapData/availability')
            return self.helpers.sendRequest(urlInput)
        return platform

    def MWFullMatchInfomp (self, matchId, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/mw/platform/{platform}/fullMatch/mp/{matchId}/en')
            return self.helpers.sendRequest(urlInput)
        return platform

    def MWFullMatchInfowz (self, matchId, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/mw/platform/{platform}/fullMatch/wz/{matchId}/en')
            return self.helpers.sendRequest(urlInput)
        return platform

    ## COLD WAR ##
    def CWmp (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for CW. Try `battle` instead.")
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno"):
                gamertag = _helpers.cleanClientName(gamertag)
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'stats/cod/v1/title/cw/platform/{platform}/{lookupType}/{gamertag}/profile/type/mp')
            return self.helpers.sendRequest(urlInput)
        return platform

    def CWloot (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for CW. Try `battle` instead.")
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno"):
                gamertag = _helpers.cleanClientName(gamertag)
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'loot/title/cw/platform/{platform}/{lookupType}/{gamertag}/status/en')
            return self.helpers.sendRequest(urlInput)
        return platform

    def CWAnalysis (self, gamertag, platform = config.platform): # Could be v1
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for CW. Try `battle` instead.")
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno"):
                gamertag = _helpers.cleanClientName(gamertag)
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'ce/v2/title/cw/platform/{platform}/gametype/all/gamer/{gamertag}/summary/match_analysis/contentType/full/end/0/matchAnalysis/mobile/en')
            return self.helpers.sendRequest(urlInput)
        return platform

    def CWMapList (self, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'ce/v1/title/cw/platform/{platform}/gameType/mp/communityMapData/availability')
            return _helpers.sendRequest(urlInput)
        return platform

    def CWcombatmp (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for CW. Try `battle` instead.")
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno"):
                gamertag = _helpers.cleanClientName(gamertag)
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/cw/platform/{platform}/{lookupType}/{gamertag}/matches/mp/start/0/end/0/details')
            return self.helpers.sendRequest(urlInput)
        return platform

    def CWcombatdate (self, gamertag, start = 0, end = 0, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for CW. Try `battle` instead.")
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno"):
                gamertag = _helpers.cleanClientName(gamertag)
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/cw/platform/{platform}/{lookupType}/{gamertag}/matches/mp/start/{start}/end/{end}/details')
            return self.helpers.sendRequest(urlInput)
        return platform

    def CWFullMatchInfo (self, matchId, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/cw/platform/{platform}/fullMatch/mp/{matchId}/en')
            return self.helpers.sendRequest(urlInput)
        return platform

    ## VANGUARD ##
    def VGmp (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for VG. Try `battle` instead.")
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno"):
                gamertag = _helpers.cleanClientName(gamertag)
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'stats/cod/v1/title/vg/platform/{platform}/{lookupType}/{gamertag}/profile/type/mp')
            return self.helpers.sendRequest(urlInput)
        return platform

    def VGloot (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for VG. Try `battle` instead.")
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno"):
                gamertag = _helpers.cleanClientName(gamertag)
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'loot/title/vg/platform/{platform}/{lookupType}/{gamertag}/status/en')
            return self.helpers.sendRequest(urlInput)
        return platform

    def VGAnalysis (self, gamertag, platform = config.platform): # Could be v1
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for VG. Try `battle` instead.")
            gamertag = _helpers.cleanClientName(gamertag)
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'ce/v2/title/vg/platform/{platform}/gametype/all/gamer/{gamertag}/summary/match_analysis/contentType/full/end/0/matchAnalysis/mobile/en')
            return self.helpers.sendRequest(urlInput)
        return platform

    def VGMapList (self, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'ce/v1/title/vg/platform/{platform}/gameType/mp/communityMapData/availability')
            return self.helpers.sendRequest(urlInput)
        return platform

    def VGcombatmp (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for VG. Try `battle` instead.")
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno"):
                gamertag = _helpers.cleanClientName(gamertag)
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/vg/platform/{platform}/{lookupType}/{gamertag}/matches/mp/start/0/end/0/details')
            return self.helpers.sendRequest(urlInput)
        return platform

    def VGcombatdate (self, gamertag, start = 0, end = 0, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "steam"):
                return ("Steam Doesn't exist for VG. Try `battle` instead.")
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno"):
                gamertag = _helpers.cleanClientName(gamertag)
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/vg/platform/{platform}/{lookupType}/{gamertag}/matches/mp/start/{start}/end/{end}/details')
            return self.helpers.sendRequest(urlInput)
        return platform

    def VGFullMatchInfo (self, matchId, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/title/vg/platform/{platform}/fullMatch/mp/{matchId}/en')
            return self.helpers.sendRequest(urlInput)
        return platform

    ## https://my.callofduty.com/api/papi-client/inventory/v1/title/cw/platform/psn/purchasable/public/en
    def GetPurchasablePublic (self):
        urlInput = _helpers.buildUri('inventory/v1/title/cw/platform/psn/purchasable/public/en')
        return self.helpers.sendRequest(urlInput)

    ## https://my.callofduty.com/api/papi-client/inventory/v1/title/cw/bundle/22497100/en
    def getBundleInformation (self, title, bundleId):
        urlInput = _helpers.buildUri(f'inventory/v1/title/{title}/bundle/{bundleId}/en')
        return self.helpers.sendRequest(urlInput)

    def friendFeed (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            gamertag = _helpers.cleanClientName(gamertag);
            urlInput = _helpers.buildUri(f'userfeed/v1/friendFeed/platform/{platform}/gamer/{gamertag}/friendFeedEvents/en')
            return self.helpers.sendRequest(urlInput)
        return platform

    def getEventFeed (self):
        urlInput = _helpers.buildUri(f'userfeed/v1/friendFeed/rendered/en/{ssoCookie}')
        self.helpers.sendRequestUserInfoOnly(urlInput)

    def getLoggedInIdentities (self):
        urlInput = _helpers.buildUri(f'crm/cod/v2/identities/{ssoCookie}')
        self.helpers.sendRequestUserInfoOnly(urlInput)

    def getLoggedInUserInfo (self):
        urlInput = _helpers.buildProfileUri(f'cod/userInfo/{ssoCookie}')
        self.helpers.sendRequestUserInfoOnly(urlInput)

    def FuzzySearch (self, query, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "battle" or platform == "uno" or platform == "all"):
                query = _helpers.cleanClientName(query)
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/platform/{platform}/username/{query}/search')
            return self.helpers.sendRequest(urlInput)
        return platform

    def getBattlePassInfo (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "battle" or platform == "uno" or platform == "acti"):
                gamertag = _helpers.cleanClientName(gamertag)
            lookupType = "gamer"
            if (platform == "uno"):
                lookupType = "id"
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'loot/title/mw/platform/{platform}/{lookupType}/{gamertag}/status/en')
            return self.helpers.sendRequest(urlInput)
        return platform

    def getCodPoints (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            gamertag = _helpers.cleanClientName(gamertag);
            urlInput = _helpers.buildUri(f'inventory/v1/title/mw/platform/{platform}/gamer/{gamertag}/currency')
            return self.helpers.sendRequest(urlInput)
        return platform

    def getBattlePassLoot (self, season, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'loot/title/mw/platform/{platform}/list/loot_season_{season}/en')
            return self.helpers.sendRequest(urlInput)
        return platform

    def getPurchasable (self, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'inventory/v1/title/mw/platform/{platform}/purchasable')
            return self.helpers.sendRequest(urlInput)
        return platform

    def purchaseItem (self, gamertag, platform = config.platform, item = "battle_pass_upgrade_bundle_4"):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            gamertag = _helpers.cleanClientName(gamertag);
            urlInput = _helpers.buildUri(f'inventory/v1/title/mw/platform/{platform}/gamer/{gamertag}/item/{item}/purchaseWith/CODPoints')
            return self.helpers.sendRequest(urlInput)
        return platform

    def getGiftableFriends (self, unoId, itemSku = "432000"):
        urlInput = _helpers.buildUri(f'gifting/v1/title/mw/platform/uno/{unoId}/sku/{itemSku}/giftableFriends')
        return self.helpers.sendRequest(urlInput)

    def sendGift (self, gamertag, recipientUnoId, senderUnoId, sendingPlatform, platform = config.platform, itemSku = "432000"):
        platform = _helpers.platformcheck()
        if platform:
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            data = {
                recipientUnoId: recipientUnoId,
                senderUnoId: senderUnoId,
                sendingPlatform: sendingPlatform,
                "sku": int(itemSku)
            };
            gamertag = _helpers.cleanClientName(gamertag);
            urlInput = _helpers.buildUri(f'gifting/v1/title/mw/platform/{platform}/gamer/{gamertag}')
            return self.helpers.sendPostRequest(urlInput, data)
        return platform

    def ConnectedAccounts (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            gamertag = _helpers.cleanClientName(gamertag);
            lookupType = "gamer";
            if (platform == "uno"):
                lookupType = "id";
            if (platform == "uno" or platform == "acti"):
                platform = "uno"
            urlInput = _helpers.buildUri(f'crm/cod/v2/accounts/platform/{platform}/{lookupType}/{gamertag}')
            return self.helpers.sendRequest(urlInput)
        return platform

    def Presence (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            gamertag = _helpers.cleanClientName(gamertag)
            urlInput = _helpers.buildUri(f'crm/cod/v2/friends/platform/{platform}/gamer/{gamertag}/presence/1/{ssoCookie}')
            return self.helpers.sendRequest(urlInput)
        return platform

    def Settings (self, gamertag, platform = config.platform):
        platform = _helpers.platformcheck()
        if platform:
            gamertag = _helpers.cleanClientName(gamertag);
            urlInput = _helpers.buildUri(f'preferences/v1/platform/{platform}/gamer/{gamertag}/list')
            return self.helpers.sendRequest(urlInput)
        return platform

    def isLoggedIn (self):
        return loggedIn

    def getLookupValues (self):
        urlInput = "https://my.callofduty.com/content/atvi/callofduty/mycod/web/en/data/json/iq-content-xweb.js"
        return self.helpers.sendRawRequest(urlInput)
