#coding: utf-8

import os
from io import BytesIO
import requests
import traceback
import logging
#logger = logging.getLogger(__name__)
logger = logging.getLogger("m38u")

class D():

    def __init__(self, cookie=None, proxies=None,headers=None,ignore_local=False,retry_times=9999999999, session = None) -> None:
        self.cookie = cookie
        self.proxies = proxies
        self.headers=headers
        self.ignore_local =ignore_local
        self.retry_times = retry_times
        self.current_retry_times = 0
        self.session = session
        super().__init__()

    def download(self, url, destFile, isAppend=True):
        try:
            if not os.path.isdir(os.path.dirname(destFile)):
                    os.mkdir(os.path.dirname(destFile))
            

            if os.path.exists(destFile):
                logger.error("File already exists")
                return True

            webSize = self.getWebFileSize(url)
            if webSize == 0:
                logger.error("something went wrong, webSize is 0")
                return False

            localSize = 0
            if self.cookie:
                self.headers['cookie']=self.cookie

            if isAppend:
                self.headers['Range']='bytes=%d-' % localSize
            else:
                os.remove(destFile)
                localSize=0

            #resp = requests.request("GET", url,timeout=10, headers=self.headers, stream=True, proxies=self.proxies, allow_redirects=True, verify=False)
            resp = self.session.get(url,timeout=10, headers=self.headers, stream=True, proxies=self.proxies, allow_redirects=True, verify=False)
            # if 300>resp.status_code >= 200:
            if resp.status_code>=200:
                # logger.debug(f"stauts_code:{resp.status_code},destfile:{destFile}")

                with open(destFile+".tmp", "ab") as f:
                    block_size = 1024
                    wrote = localSize
                    # for data in tqdm(resp.iter_content(block_size), initial=wrote / block_size, total=webSize / block_size,unit='Mb', unit_scale=True):
                    for data in resp.iter_content(block_size):
                        if data:
                            wrote = wrote + len(data)
                            f.write(data)
                    if wrote != webSize:
                        logger.error(f"ERROR, something went wrong wroteSize{wrote} != webSize{webSize}")
                        return False

                    os.rename(destFile+".tmp",destFile)
                    logger.error("Success!")
                    return True

            logger.error(f"stauts_code:{resp.status_code},url:{resp.url}") 
            raise Exception("status_code is not 200.") 

        except Exception as e:
            logger.exception(e)
            return False

    def getWebFileSize(self, url):
        if self.cookie:
            self.headers['cookie']=self.cookie

        rr = requests.get(url, headers=self.headers, stream=True, proxies=self.proxies, verify=False)
        file_size = int(rr.headers['Content-Length'])

        if 300>rr.status_code>=200:
            return file_size
        else:
            return 0
