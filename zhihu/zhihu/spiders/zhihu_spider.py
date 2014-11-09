import re
import json
from urlparse import urlparse


from scrapy.selector import Selector
try:
    from scrapy.spider import Spider
except:
    from scrapy.spider import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor as sle


from zhihu.items import *
from misc.log import *

'''
XXX：理论上，可以把所有的css rules都用dict表示（有深度）：

all_css_rules = {
    '.zm-profile-header': {
        '.zm-profile-header-main': {
            # 这一层就要dump出数据了，以__use标签为准
            ‘__use’:'dump',
            'name':'.title-section .name::text',
            'sign':'.title-section .bio::text',
            'location':'.location.item::text',
            'business':'.business.item::text',
            'employment':'.employment.item::text',
            'position':'.position.item::text',
            'education':'.education.item::text',
            'education_extra':'.education-extra.item::text',
        },
        '.zm-profile-header-operation': {

        },
    }
}
'''

class ZhihuCrawlerContext(object):

    def __init__(self, sel=None, css_rules=None):
        self.sel = sel
        self.css_rules = css_rules


class ZhihuSpider(CrawlSpider):
    name = "zhihu"
    allowed_domains = ["zhihu.com"]
    start_urls = [
        "http://www.zhihu.com/",
        "http://www.zhihu.com/people/jia-yang-qing-74",
    ]
    rules = [
        Rule(sle(allow=("/people/[^/]+/followees$")), callback='parse_followees'),
        Rule(sle(allow=("/people/[^/]+/followers$", )), callback='parse_followers'),
        Rule(sle(allow=("/people/[^/]+$", )), callback='parse_people', follow=True),
    ]

    def parse_followers(self, response):
        return parse_people(response)

    def parse_followees(self, response):
        return parse_people(response)

    def parse_people(self, response):
        info('parsed ' + str(response))
        items = []
        sel = Selector(response)

        profile_header = sel.css('.zm-profile-header')[0]

        profile_header_main = profile_header.css('.zm-profile-header-main')[0]
        profile_header_operation = profile_header.css('.zm-profile-header-operation')[0]
        profile_header_navbar = profile_header.css('.profile-navbar')[0]

        profile_side_following = sel.css('.zm-profile-side-following')[0]

        item = ZhihuPeopleItem()
        item['id'] = urlparse(response.url).path.split('/')[-1]

        zhihu_profile_header_main_dict = {
            'name':'.title-section .name::text',
            'sign':'.title-section .bio::text',
            'location':'.location.item::text',
            'business':'.business.item::text',
            'employment':'.employment.item::text',
            'position':'.position.item::text',
            'education':'.education.item::text',
            'education_extra':'.education-extra.item::text',
        }
        zhihu_profile_header_operation_dict = {
            'agree':'.zm-profile-header-user-agree strong::text',
            'thanks':'.zm-profile-header-user-thanks strong::text',
        }
        zhihu_profile_header_navbar = {
            'asks':'a[href*=asks] .num::text',
            'answers':'a[href*=answers] .num::text',
            'posts':'a[href*=posts] .num::text',
            'collections':'a[href*=collections] .num::text',
            'logs':'a[href*=logs] .num::text',
        }
        zhihu_profile_side_following = {
            'followees':'a.item[href*=followees] strong::text',
            'followers':'a.item[href*=followers] strong::text',
        }


        for key, value in zhihu_profile_header_main_dict.items():
            item[key] = [i.extract() for i in profile_header_main.css(value)]

        for key, value in zhihu_profile_header_operation_dict.items():
            item[key] = [i.extract() for i in profile_header_operation.css(value)]

        for key, value in zhihu_profile_header_navbar.items():
            item[key] = [i.extract() for i in profile_header_navbar.css(value)]

        for key, value in zhihu_profile_side_following.items():
            item[key] = [i.extract() for i in profile_side_following.css(value)]

        items.append(item)
        # import pdb; pdb.set_trace()

        return items

    def _process_request(self, request):
        info('process ' + str(request))
        return request
