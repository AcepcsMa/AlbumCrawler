import hashlib
import AlbumCrawler.settings
import pymysql
import base64
import requests

class Utils(object):

    @staticmethod
    def md5(data):
        return hashlib.md5(data.encode()).hexdigest()

    @staticmethod
    def getStartUrlsFromDb(name):
        host = AlbumCrawler.settings.MYSQL_HOST
        port = AlbumCrawler.settings.MYSQL_PORT
        dbName = AlbumCrawler.settings.MYSQL_DBNAME
        user = AlbumCrawler.settings.MYSQL_USER
        pwd = AlbumCrawler.settings.MYSQL_PWD

        connect = pymysql.connect(host=host, port=port,
                                  db=dbName, user=user,
                                  passwd=pwd, charset="utf8")

        cursor = connect.cursor()
        cursor.callproc("get_crawler_source", [name.lower()])
        urls = cursor.fetchall()
        urls = [each[0] for each in urls]
        cursor.close()
        connect.close()
        return urls

    @staticmethod
    def fetchImage(imgUrl, auth, bucket, newImgName):
        '''Fetch image using qiniu's public API

            Args:
                imgUrl: image url
                auth: qiniu Auth object
                bucket: qiniu bucket name
                newImgName: new image name on qiniu
            Returns:
                True when fetch is successful, otherwise False

        '''
        encoded_url = base64.urlsafe_b64encode(imgUrl.encode()).decode()
        dest_entry = '%s:%s' % (bucket, newImgName)
        encoded_entry = base64.urlsafe_b64encode(dest_entry.encode()).decode()

        api_host = "http://iovip.qbox.me"
        api_path = "/fetch/%s/to/%s" % (encoded_url, encoded_entry)

        token = auth.token_of_request(api_host + api_path)
        headers = {
            'Authorization': "QBox %s" % token
        }
        response = requests.post(url=api_host + api_path, headers=headers)
        return response.status_code == 200
