# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline
from urllib.parse import urlparse
from os.path import basename, dirname, join


# 实现FilesPipeline,覆写file_path方法
class MyFilePipeline(FilesPipeline):

    def file_path(self, request, response=None, info=None):
        # http://matplotlib.org/mpl_examples/axes_grid/demo_floating_axes.py
        # path = axes_grid/demo_floating_axes.py
        path = urlparse(request.url).path
        # basename(dirname(path)) = axes_grid   basename(path) =demo_floating_axes.py
        return join(basename(dirname(path)), basename(path))


class MatplotlibExamplesPipeline:
    def process_item(self, item, spider):
        return item
