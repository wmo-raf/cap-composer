import textwrap
from io import BytesIO

import cartopy.feature as cf
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont, ImageColor
from cartopy import crs as ccrs
from django.contrib.staticfiles import finders
from django.core.files.base import ContentFile
from django.template.defaultfilters import truncatechars

from capeditor.utils import rasterize_svg_to_png

matplotlib.use('Agg')

fonts = {
    "Roboto-Regular": finders.find("capeditor/fonts/Roboto/Roboto-Regular.ttf"),
    "Roboto-Bold": finders.find("capeditor/fonts/Roboto/Roboto-Bold.ttf")
}

severity_icons = {
    "Extreme": finders.find("capeditor/images/extreme.png"),
    "Severe": finders.find("capeditor/images/severe.png"),
    "Moderate": finders.find("capeditor/images/moderate.png"),
    "Minor": finders.find("capeditor/images/minor.png"),
}
meta_icons = {
    "urgency": finders.find("capeditor/images/urgency.png"),
    "certainty": finders.find("capeditor/images/certainty.png")
}

warning_icon = finders.find("capeditor/images/alert.png")
area_icon = finders.find("capeditor/images/area.png")


def cap_geojson_to_image(geojson_feature_collection, extents=None):
    gdf = gpd.GeoDataFrame.from_features(geojson_feature_collection)

    width = 2
    height = 2

    fig = plt.figure(figsize=(width, height,))
    ax = plt.axes([0, 0, 1, 1], projection=ccrs.PlateCarree())

    # set line width
    [x.set_linewidth(0) for x in ax.spines.values()]

    # set extent
    if extents:
        ax.set_extent(extents, crs=ccrs.PlateCarree())

    # add country borders
    ax.add_feature(cf.LAND)
    ax.add_feature(cf.OCEAN)
    ax.add_feature(cf.BORDERS, linewidth=0.1, linestyle='-', alpha=1)

    # Plot the GeoDataFrame using the plot() method
    gdf.plot(ax=ax, color=gdf["severity_color"], edgecolor='#333', linewidth=0.3, legend=True)
    # label areas
    gdf.apply(lambda x: ax.annotate(text=truncatechars(x["areaDesc"], 20),
                                    xy=x.geometry.centroid.coords[0], ha='center',
                                    fontsize=5, ), axis=1)

    # create plot
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches="tight", dpi=200)

    # close plot
    plt.close()

    return buffer


class CapAlertCardImage(object):
    def __init__(self, area_map_img_buffer, cap_detail, file_name):

        self.out_img_width = 800
        self.out_img_height = 800

        self.standard_map_height = 300

        self.padding = 28
        self.drawContext = None
        self.out_img = None

        self.file_name = file_name

        self.area_map_img_buffer = area_map_img_buffer
        self.cap_detail = cap_detail

        self.map_image_h = 0
        self.map_image_w = 0

        self._get_font_paths()

    def render(self):
        self.draw_base()

        # draw logo
        logo_lly = self.draw_org_logo()

        # draw title
        title_lly = self.draw_title(y=logo_lly + self.padding)

        # draw issued date
        issued_date_lly = self.draw_issued_date(y=title_lly + self.padding)

        # draw area map
        map_ulx, map_lly = self.draw_area_map(y=issued_date_lly + self.padding)

        # draw severity badge
        severity_badge_lly = self.draw_severity_badge(x=map_ulx + self.padding, y=issued_date_lly + self.padding)

        # draw info items
        info_items_lly = self.draw_info_items(x=map_ulx + self.padding, y=severity_badge_lly + self.padding)

        # draw alert area details
        self.draw_area_info(x=map_ulx + self.padding, y=info_items_lly + self.padding)

        # draw description
        description_title = "Description: "
        description_text = self.cap_detail.get("properties").get("description")
        description_text = truncatechars(description_text, 360)
        desc_lly = self.draw_title_text_block(description_title, description_text, x=self.padding,
                                              y=map_lly + self.padding)

        # draw instruction
        instruction_title = "Instruction: "
        instruction_text = self.cap_detail.get("properties").get("instruction")
        instruction_text = truncatechars(instruction_text, 360)
        instruction_lly = self.draw_title_text_block(instruction_title, instruction_text, x=self.padding,
                                                     y=desc_lly + self.padding)

        return self.save_image()

    def _get_font_paths(self):
        roboto_regular_font_path = fonts.get("Roboto-Regular")
        roboto_bold_font_path = fonts.get("Roboto-Bold")

        if not roboto_regular_font_path:
            raise FileNotFoundError("Roboto-Regular font not found")

        self.roboto_regular_font_path = roboto_regular_font_path

        if not roboto_bold_font_path:
            raise FileNotFoundError("Roboto-Bold font not found")

        self.roboto_bold_font_path = roboto_bold_font_path

    def draw_title(self, y, font_size=20):
        title = self.cap_detail.get("title")
        title = truncatechars(title, 100)
        title_lly = self._draw_centered_text(title, y=y, font_path=self.roboto_bold_font_path, font_size=font_size)
        return title_lly

    def draw_issued_date(self, y, font_size=20):
        sent = self.cap_detail.get("properties", {}).get('sent')
        time_fmt = '%d/%m/%Y %H:%M'
        sent = sent.strftime(time_fmt)
        issued_date_text = f"Issued on: {sent} local time"
        issued_date_lly = self._draw_centered_text(issued_date_text, y=y, font_path=self.roboto_bold_font_path,
                                                   font_size=font_size)
        return issued_date_lly

    def draw_base(self):
        self.map_image_w, self.map_image_h = self._get_image_size(self.area_map_img_buffer)

        if self.map_image_h > self.standard_map_height:
            self.out_img_height = self.out_img_height + (self.map_image_h - self.standard_map_height)

        self.out_img = Image.new(mode="RGBA", size=(self.out_img_width, self.out_img_height), color="WHITE")
        self.drawContext = ImageDraw.Draw(self.out_img)

    def draw_org_logo(self, y_offset=10, max_logo_height=60):
        org_logo_file = self.cap_detail.get("org_logo_file")
        if org_logo_file:
            logo_image = Image.open(org_logo_file)
            logo_w, logo_h = self._get_image_size(org_logo_file)
            if logo_h > max_logo_height:
                ratio = logo_w / logo_h
                new_width = int(ratio * max_logo_height)
                logo_image = logo_image.resize((new_width, max_logo_height))
                logo_w, logo_h = logo_image.size

            offset = ((self.out_img_width - logo_w) // 2, y_offset)
            self.out_img.paste(logo_image, offset, logo_image)

            return y_offset + logo_h

    def _draw_centered_text(self, text, y, font_path, font_size=20):
        text_max_width = int(self.out_img_width * 0.07)
        wrapper = textwrap.TextWrapper(width=text_max_width)
        word_list = wrapper.wrap(text=text)
        title_new = ''
        for ii in word_list:
            title_new = title_new + ii + '\n'

        font = ImageFont.truetype(font_path, font_size)
        _, _, text_w, text_h = self.drawContext.textbbox((0, 0), title_new, font=font)
        text_offset = ((self.out_img_width - text_w) // 2, y)
        self.drawContext.text(text_offset, title_new, font=font, fill="BLACK")

        return y + text_h

    def draw_area_map(self, y):
        map_offset = (self.padding, y)
        map_image = Image.open(self.area_map_img_buffer)
        self.out_img.paste(map_image, map_offset)

        return self.padding + self.map_image_w, y + self.map_image_h

    def draw_severity_badge(self, x, y):
        alert_badge_height = 50
        badge_lrx = self.out_img_width - self.padding  # x1
        badge_lry = y + alert_badge_height  # y1

        severity_background_color = self.cap_detail.get("severity").get("background_color")
        severity_border_color = self.cap_detail.get("severity").get("border_color")
        severity_icon_color = self.cap_detail.get("severity").get("icon_color")
        severity_color = self.cap_detail.get("severity").get("color")

        badge_bg_color = ImageColor.getrgb(severity_background_color)
        badge_border_color = ImageColor.getrgb(severity_border_color)

        self.drawContext.rectangle((x, y, badge_lrx, badge_lry), fill=badge_bg_color,
                                   outline=badge_border_color)

        event_icon = self.cap_detail.get("properties").get("event_icon")
        if not event_icon:
            event_icon = "alert"

        max_icon_height = 30

        try:
            icon_file = rasterize_svg_to_png(icon_name=event_icon, fill_color=severity_icon_color)
        except Exception:
            icon_file = warning_icon

        event_icon_img = Image.open(icon_file, formats=["PNG"])
        icon_w, icon_h = event_icon_img.size
        if icon_h > max_icon_height:
            icon_ratio = icon_w / icon_h
            new_icon_width = int(icon_ratio * max_icon_height)
            event_icon_img = event_icon_img.resize((new_icon_width, max_icon_height))
            icon_w, icon_h = event_icon_img.size

        badge_width = self.out_img_width - x - self.padding
        rec_width = 40
        rec_padding = 5

        icon_ulx = x + rec_padding
        icon_uly = y + rec_padding
        icon_lrx = badge_lrx - (badge_width - (rec_width + rec_padding))
        icon_lry = badge_lry - rec_padding

        icon_rect_fill_color = ImageColor.getrgb(severity_color)
        self.drawContext.rectangle((icon_ulx, icon_uly, icon_lrx, icon_lry), fill=icon_rect_fill_color,
                                   outline=badge_border_color)

        event_icon_offset = (
            x + (rec_padding * 2),
            y + (rec_padding * 2))

        self.out_img.paste(event_icon_img, event_icon_offset, event_icon_img)

        # draw event text
        event_text = self.cap_detail.get("event")
        event_text = truncatechars(event_text, 35)

        font = ImageFont.truetype(self.roboto_bold_font_path, 12)
        self.drawContext.text((icon_lrx + 10, icon_uly + 10), event_text, font=font, fill="black")

        return badge_lry

    def draw_info_items(self, x, y):
        meta_h_padding = 10
        urgency_val = self.cap_detail.get("properties").get("urgency")
        urgency_icon_file = meta_icons.get("urgency")
        urgency_icon_h = self._draw_info_item(self.out_img, "Urgency", urgency_val, urgency_icon_file, x, y,
                                              self.drawContext)

        severity_y_offset = y + meta_h_padding + urgency_icon_h
        severity = self.cap_detail.get("properties").get("severity")
        severity_icon_file = severity_icons.get(severity)
        severity_icon_h = self._draw_info_item(self.out_img, "Severity", severity, severity_icon_file, x,
                                               severity_y_offset, self.drawContext)

        certainty_y_offset = severity_y_offset + meta_h_padding + severity_icon_h
        certainty = self.cap_detail.get("properties").get("certainty")
        certainty_icon_file = meta_icons.get("certainty")
        certainty_icon_h = self._draw_info_item(self.out_img, "Certainty", certainty, certainty_icon_file, x,
                                                certainty_y_offset, self.drawContext)

        return certainty_y_offset + certainty_icon_h

    def draw_area_info(self, x, y):
        area_icon_img = Image.open(area_icon)
        area_icon_w, area_icon_h = area_icon_img.size
        area_title_offset = (x, y)
        self.out_img.paste(area_icon_img, area_title_offset, area_icon_img)

        font = ImageFont.truetype(self.roboto_bold_font_path, 16)
        self.drawContext.text((x + area_icon_w + 5, y), text="Area of concern", font=font, fill="black")

        areaDesc = self.cap_detail.get("properties").get("area_desc")

        # Truncate the area description to 85 characters
        areaDesc = truncatechars(areaDesc, 85)

        area_wrapper = textwrap.TextWrapper(
            width=int((self.out_img_width - (x + area_icon_w + 5 + self.padding)) * 0.14))
        area_word_list = area_wrapper.wrap(text=areaDesc)
        area_desc_new = ''
        for ii in area_word_list:
            area_desc_new = area_desc_new + ii + '\n'

        regular_font = ImageFont.truetype(self.roboto_regular_font_path, size=14)
        self.drawContext.text((x + self.padding, y + area_icon_h + 1), area_desc_new, font=regular_font, fill="black")

    def draw_title_text_block(self, title, text, x, y):
        title_text_spacing = 10
        font = ImageFont.truetype(self.roboto_bold_font_path, 20)
        _, _, title_w, title_h = self.drawContext.textbbox((0, 0), title, font=font)
        self.drawContext.text((x, y), title, font=font, fill="black")

        text_wrapper = textwrap.TextWrapper(width=int(self.out_img_width * 0.16))

        text_word_list = text_wrapper.wrap(text=text)
        text_new = ''
        for ii in text_word_list:
            text_new = text_new + ii + '\n'
        regular_font = ImageFont.truetype(self.roboto_regular_font_path, size=12)

        text_offset_y = y + title_h + title_text_spacing
        _, _, text_w, text_h = self.drawContext.textbbox((0, 0), text_new, font=regular_font)
        self.drawContext.text((x, text_offset_y), text_new, font=regular_font, fill="black")

        return text_offset_y + text_h

    def save_image(self):
        buffer = BytesIO()
        self.out_img.convert("RGB").save(fp=buffer, format='PNG')
        buff_val = buffer.getvalue()

        return ContentFile(buff_val, self.file_name)

    @staticmethod
    def _get_image_size(file):
        image = Image.open(file)
        return image.size

    def _draw_info_item(self, out_img, key, value, icon_file, x_offset, y_offset, draw):
        meta_icon_img = Image.open(icon_file)
        icon_w, icon_h = meta_icon_img.size
        offset = (x_offset, y_offset)

        out_img.paste(meta_icon_img, offset, meta_icon_img)

        meta_font_size = 16
        regular_font = ImageFont.truetype(self.roboto_regular_font_path, meta_font_size)
        bold_font = ImageFont.truetype(self.roboto_bold_font_path, meta_font_size)

        padding = 10

        label_x_offset = x_offset + icon_w + padding
        label_y_offset = y_offset + 7

        label = f"{key}: "
        _, _, label_w, label_h = draw.textbbox((0, 0), label, font=regular_font)
        draw.text((label_x_offset, label_y_offset), text=label, font=regular_font, fill="black")

        _, _, value_w, value_h = draw.textbbox((0, 0), value, font=bold_font)
        draw.text((label_x_offset + label_w + 5, label_y_offset), text=value, font=bold_font, fill="black")

        return icon_h
