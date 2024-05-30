import requests
import json
from bs4 import BeautifulSoup


class MetaContent:
    def __init__(self, original=None, author=None, nickname=None, wechat_id=None, introduction=None, publish_time=None,
                 location=None, content=None):
        self.original = original
        self.author = author
        self.nickname = nickname
        self.wechat_id = wechat_id
        self.introduction = introduction
        self.publish_time = publish_time
        self.location = location
        self.content = content

    def __hash__(self):
        return hash((self.original, self.author, self.nickname, self.wechat_id, self.introduction, self.publish_time,
                     self.location, self.content))

    def __eq__(self, other):
        if not isinstance(other, MetaContent):
            return NotImplemented
        return (self.original, self.author, self.nickname, self.wechat_id, self.introduction, self.publish_time,
                self.location, self.content) == (
            other.original, other.author, other.nickname, other.wechat_id, other.introduction, other.publish_time,
            other.location, self.content)

    def __repr__(self):
        return f"MetaContent(original={self.original}, author={self.author}, nickname={self.nickname}, wechat_id={self.wechat_id}, introduction={self.introduction}, publish_time={self.publish_time}, location={self.location}, content={self.content})"


def get_wechat_info(query):
    # 用户动态输入query参数
    url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?action=search_biz&begin=0&count=5&query=' + query + '&token=923054189&lang=zh_CN&f=json&ajax=1'

    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cookie': 'appmsglist_action_3262368579=card; appmsglist_action_3919708237=card; _qimei_uuid42=1850711052a10029a89869fde1d080a0cc53b30785; pac_uid=0_f4541366cb935; iip=0; _qimei_fingerprint=8c54daec95be2ae7c4a60f75b93d0266; _qimei_h38=9c1ed6c1a89869fde1d080a00300000b618507; _qimei_q36=; rewardsn=; wxtokenkey=777; ua_id=t0h5UtJBkfTZIvS8AAAAAAcKifvUeelKOwHj0IWk_Q8=; _clck=1ybvnnh|1|fm6|0; wxuin=16967431689331; mm_lang=zh_CN; media_ticket=92980cebec9d1e3f967ddf8177fb79ebc8f194a7; media_ticket_id=gh_b363d2a30240; cert=ugvZxt3BhBtk_D6OmSt224XnGHdQbNhd; xid=a8da546cb512f65513183bc04630440a; use_waban_ticket=1; uuid=034da4d3a35af71ed8e5087458d49f6a; sig=h01449bd2ab9030898c6dbdd5fe17fd9a7d72b2e558faba95bbfcef63361818c2d240a2eb14bf89a4d2; data_bizuin=3919708237; bizuin=3919708237; master_user=gh_d244cdefd7a0; master_sid=REd3eWJFUnhoU1BHb3pZQTF0QWx3bkhpVHJteEFpVTlxbXpaU2dJUERqZ0ZCMDR1VUxEZ2VyOXE4cTJvWjhOa1dYcGpPS2JvaThxVUdGNFdBWTdINVZYOUdMTWxQWlo1MlMxSDgxYzBCc3hyTXQ3clFJU2NpWVFvbW9NVElhWG00eDdzVnJFalhTOFFTYmtq; master_ticket=4b48f18861f33411684f8df1c4485450; data_ticket=oE8hYrXPf2UO+iy2EkQkGjP3Wlkt55v5cFEhz+jnIuGcas4c8DFyXYuxnM4s+33g; rand_info=CAESIH2JXMmtAyon+OHPi/Y0d7jY8ITwJP60zwhlCXCx5ZBt; slave_bizuin=3919708237; slave_user=gh_d244cdefd7a0; slave_sid=N3JWcTh1aGYyMDZMU05jUHJqTGI2NjV1eG44bnJHbHJMbHNFZDFVMDNxT015dXhmektnOVd6NUJ5NHZBV3dYckxuSEFhZVBDMDVWYm1xUHhXX0NhUkpZakpYTGZnYW41T2tuZ0lRNXZIR0pOcW94VmF2MTBJc0tHcVE4STdGTHJhZFpieVNQcHd2TlFxaGtn; _clsk=1hsrg37|1716976397716|33|1|mp.weixin.qq.com/weheat-agent/payload/record',
        'priority': 'u=1, i',
        'referer': 'https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&token=923054189&lang=zh_CN&timestamp=1716976355950',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    # 请求微信API
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
    except requests.RequestException as e:
        print(f"Failed to retrieve data from {url}: {e}")
        data = {}

    fakeid = ''

    # 确保列表不为空
    if data.get('list'):
        # 获取list中第一个元素
        first_element = data['list'][0]
        # 获取fakeid字段
        fakeid = first_element.get('fakeid', '')
    else:
        print("The list is empty.")

    link_set = set()

    if fakeid:
        detailUrl = f'https://mp.weixin.qq.com/cgi-bin/appmsgpublish?sub=list&search_field=null&begin=0&count=5&query=&fakeid={fakeid}&type=101_1&free_publish_type=1&sub_action=list_ex&token=923054189&lang=zh_CN&f=json&ajax=1'

        # 请求详细信息API
        try:
            detailResponse = requests.get(detailUrl, headers=headers)
            detailResponse.raise_for_status()  # 检查请求是否成功
            detailData = detailResponse.json()
        except requests.RequestException as e:
            print(f"Failed to retrieve data from {detailUrl}: {e}")
            detailData = {}

        if detailData.get('base_resp', {}).get('ret') == 0:
            # 获取 publish_list
            publish_page = json.loads(detailData.get("publish_page", '{}'))
            publish_list = publish_page.get('publish_list', [])
            # 遍历 publish_list
            for publish_item in publish_list:
                # 获取 appmsgex 列表
                appmsgex_list = json.loads(publish_item.get('publish_info', '{}')).get('appmsgex', [])
                for appmsgex in appmsgex_list:
                    # 获取文章链接
                    link = appmsgex.get('link')
                    if link:
                        link_set.add(link)
        else:
            print("Failed to retrieve detailed data:", detailData.get('base_resp', {}).get('err_msg'))
    else:
        print("Invalid fakeid, unable to retrieve detailed data.")

    print(link_set)

    info_list = get_all_meta_content(link_set)

    return info_list


def get_meta_content_info(link):
    try:
        response = requests.get(link)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        meta_content = soup.find('div', id='meta_content')
        if meta_content:
            original = meta_content.find('span', id='copyright_logo').get_text(strip=True) if meta_content.find('span',
                                                                                                                id='copyright_logo') else None
            author = meta_content.find('span', class_='rich_media_meta_text').get_text(strip=True) if meta_content.find(
                'span', class_='rich_media_meta_text') else None
            nickname = meta_content.find('a', id='js_name').get_text(strip=True) if meta_content.find('a',
                                                                                                      id='js_name') else None
            profile_container = meta_content.find('div', id='js_profile_qrcode')
            wechat_id = None
            introduction = None
            if profile_container:
                profile_inner = profile_container.find('div', class_='profile_inner')
                if profile_inner:
                    wx_id_label = profile_inner.find('label', text='微信号')
                    wechat_id = wx_id_label.find_next_sibling('span', class_='profile_meta_value').get_text(
                        strip=True) if wx_id_label else None
                    intro_label = profile_inner.find('label', text='功能介绍')
                    introduction = intro_label.find_next_sibling('span', class_='profile_meta_value').get_text(
                        strip=True) if intro_label else None

            # content = soup.find('div', class_='autoTypeSetting24psection')
            # clean_content = None
            # if content:
            #     text = content.get_text(separator=' ', strip=True)
            #     clean_content = ' '.join(text.split())
            clean_content = soup.get_text(separator=' ', strip=True)
            return MetaContent(original, author, nickname, wechat_id, introduction, None, None, clean_content)
        else:
            print("Meta content div not found.")
            return None
    except requests.RequestException as e:
        print(f"Failed to retrieve {link}: {e}")
        return None


def get_all_meta_content(links):
    info_list = []
    for link in links:
        info = get_meta_content_info(link)
        if info:
            info_list.append(info)
    return info_list


info = get_wechat_info("Datawhale")
print(info)
