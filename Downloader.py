import requests
import json
import sys
import os

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}


class download_manager():
    def __check_url(self, url):
        if not url.startswith('http'):
            self.url = 'https://www.pornhub.com/view_video.php?viewkey=' + url
            self.key = url
        else:
            self.url = url
            self.key = url.split('=')[-1]

    def __find_media_definition(self, body):
        index = body.index('mediaDefinitions')
        begin = 0
        end = 0
        for i in range(len(body)):
            tempStr = body[index + i: index + i + 1]
            if tempStr is '[':
                begin = index + i

            if tempStr is ']':
                end = index + i
                break
        return begin, end

    def __find_highest_quality_url(self, json):
        best_quality_info = None
        current_quality = -1
        for info in json:
            if info['videoUrl'] is not '' and current_quality < int(info['quality']):
                best_quality_info = info
                current_quality = int(info['quality'])
        return best_quality_info

    def __parse_download_body(self, body):
        begin, end = self.__find_media_definition(body)
        if begin >= 0 and end >= 0:
            json_response = json.loads(body[begin: end + 1])
            return self.__find_highest_quality_url(json_response)

    def find_download_info(self, url):
        self.__check_url(url)
        response = requests.get(self.url, headers=headers)
        return self.__parse_download_body(response.text), self.key

    def download_video(self, video_info, key):
        filename = str(key) + '_' + str(video_info['quality']) + '_.mp4'
        print('downloading file: ' + filename + " to " + os.getcwd())
        with open(filename, 'wb') as f:
            url = video_info['videoUrl']
            response = requests.get(url, stream=True)
            total = response.headers.get('content-length')
            if total is None:
                f.write(response.content)
            else:
                downloaded = 0
                total = int(total)
                for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                    downloaded += len(data)
                    f.write(data)
                    done = int(50*downloaded/total)
                    sys.stdout.write('{} MB/{} MB'.format(int(downloaded/(1024*1024)), int(total/(1024*1024))))
                    sys.stdout.write('\r[{}{}]  '.format(
                        '█' * done, '.' * (50-done)))
        sys.stdout.flush()

if __name__ == "__main__":
    download_manager = download_manager()
    while True:
        input_url = input("Enter URL (ctrl+c to exit): ")
        video_info, key = download_manager.find_download_info(input_url)
        download_manager.download_video(video_info, key)
        print('\n')
