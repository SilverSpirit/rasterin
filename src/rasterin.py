from PIL import Image

import base64
import os
import inkex
from lxml import etree
import io


class Rasterin(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.arg_parser.add_argument('-i', '--rasterpath', action='store',
                                     type=str,
                                     default='None', help='Path to raster '
                                                          'file.')
        self.arg_parser.add_argument('-f', '--firstpage', action='store',
                                     type=str,
                                     default='1', help='Page number to '
                                                       'start from for '
                                                       'multi page tiffs.')
        self.arg_parser.add_argument('-l', '--lastpage', action='store',
                                     type=str,
                                     default='1', help='Page number to '
                                                       'stop at for '
                                                       'multipage tiffs.'
                                                       'Use "last" to '
                                                       'convert all pages.')

    def effect(self):
        raster_path = self.arg_parser.parse_args().rasterpath
        if not os.path.exists(raster_path):
            # raise FileNotFoundError('{} not found!'.format(raster_path)
            raise inkex.AbortExtension('Image not found!')
            # inkex.errormsg('{} not found!'.format(raster_path))
        svg = self.document.getroot()

        filename = os.path.basename(raster_path)
        basename, ext = os.path.splitext(filename)
        image = Image.open(raster_path)

        if ext in ['.tif', '.tiff']:
            if ext == '.tif':
                with open('temp.tiff', 'wb') as f:
                    with open(raster_path) as f1:
                        f.write(f1.read())
            # image.load()
            first_page = self.cast_to_int(
                self.arg_parser.parse_args().firstpage)
            if first_page < 1:
                raise inkex.AbortExtension('Invalid first page!')
            last_page_param = self.arg_parser.parse_args().firstpage
            if last_page_param == 'last':
                last_page = image.n_frames
            else:
                last_page = self.cast_to_int(
                    last_page_param)  # why do I need self?

            if first_page > last_page:
                raise inkex.AbortExtension('Invalid page numbers!')

            for i in range(first_page - 1, last_page):
                image.seek(i)
                # copied from here
                layer = etree.SubElement(svg, 'g')
                layer.set(inkex.addNS('label', 'inkscape'), '{}_{}'.format(
                    basename, i + 1))
                layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')

                width, height = image.size

                output = io.BytesIO()
                image.save(output, format='.tiff')
                node = self._create_image_node(
                    base64.b64encode(output.getvalue()), self.px_to_mm(width),
                    self.px_to_mm(height))

                layer.append(node)

        else:
            if ext == '.jpg':
                ext = '.jpeg'
            layer = etree.SubElement(svg, 'g')
            layer.set(inkex.addNS('label', 'inkscape'), '{}'.format(
                filename))
            layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')

            width, height = image.size
            # image_format = os.path.splitext(raster_path)[1]
            # with open(raster_path, 'rb') as f:
            #     image_string = base64.b64encode(f.read()) # get this from image
            output = io.BytesIO()
            image.save(output, format=ext[1:])
            node = self._create_image_node(base64.b64encode(output.getvalue()),
                                           self.px_to_mm(width),
                                           self.px_to_mm(height))

            layer.append(node)
        image.close()
        if os.path.exists('temp.tiff'):
            os.remove('temp.tiff')

    @staticmethod
    def cast_to_int(num_str):
        try:
            return int(num_str)
        except ValueError:
            raise inkex.AbortExtension('Invalid value {}'.format(num_str))

    @staticmethod
    def px_to_mm(px):
        # 1 inch = 25.4 mm
        # 1 inch  = 96 px (i.e. dots)
        # => 1 px = 25.4/96 mm
        return (px * 25.4) / 96

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


if __name__ == '__main__':
    # with open(r'C:\Users\adity\Desktop\original_TIFF_document_1_before_scan'
    #           r'.jpg', 'rb') as f:
    #     image_string = base64.b64encode(f.read())
    placeholder = Rasterin()
    placeholder.run()
