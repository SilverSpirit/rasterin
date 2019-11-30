from PIL import Image

import base64
import os
import inkex
from lxml import etree


class Rasterin(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.arg_parser.add_argument('-i', '--rasterpath', action='store',
                                     type=str,
                                     default='None', help='Path to raster')
        self.arg_parser.add_argument('-p', '--pagenumber', action='store',
                                     type=str,
                                     default='all', help='Page number for '
                                                         'multipage tiffs. '
                                                         'Default is all.')

    def effect(self):
        raster_path = self.arg_parser.parse_args().rasterpath
        if not os.path.exists(raster_path):
            # raise FileNotFoundError('{} not found!'.format(raster_path))
            raise inkex.AbortExtension('Image not found!')
            # inkex.errormsg('{} not found!'.format(raster_path))

        svg = self.document.getroot()

        layer = etree.SubElement(svg, 'g')
        layer.set(inkex.addNS('label', 'inkscape'), '{}'.format(
            os.path.basename(raster_path)))
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')

        image = Image.open(raster_path)
        width, height = image.size
        # image_format = os.path.splitext(raster_path)[1]
        with open(raster_path, 'rb') as f:
            image_string = base64.b64encode(f.read())
        node = self._create_image_node(image_string, self.px_to_mm(width),
                                       self.px_to_mm(height))

        layer.append(node)

    def px_to_mm(self, px):
        # 1 inch = 25.4 mm
        # 1 mm  = 1/25.4 inch
        # 1 inch  = 96 dpi (px)
        # 1 dpi = 1/96 inch
        return (px*25.4)/96

    def _create_image_node(self, image_string, width, height):
        attribs = {
            'height': str(height),
            'width': str(width),
            'x': '0',
            'y': '0',
            'preserveAspectRatio': 'None',
            inkex.addNS('href', 'xlink'): u'data:image;base64,'
                                          u'' + image_string.decode()
        }
        node = etree.Element(inkex.addNS('image', 'svg'), attribs)
        return node

    # def image_to_byte_array(self, image: Image):
    #     img_byte_array = io.BytesIO()
    #     image.save(img_byte_array, format=image.format)
    #     imgByteArr = img_byte_array.getvalue()
    #     return imgByteArr


if __name__ == '__main__':
    with open(r'C:\Users\adity\Desktop\original_TIFF_document_1_before_scan'
              r'.jpg', 'rb') as f:
        image_string = base64.b64encode(f.read())
    placeholder = Rasterin()
    placeholder.run()
