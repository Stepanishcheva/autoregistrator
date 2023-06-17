import cv2
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import re


class TextExtractor:
    def __init__(self, image_path):
        self.image = cv2.imread(image_path)
        self.gray = None
        self.blur = None
        self.thresh = None
        self.dilate = None
        self.cnts = None
        self.ROIS = []
        self.parts = []
        self.ROI_number = 0

    def preprocess_image(self):
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.blur = cv2.GaussianBlur(self.gray, (9, 9), 0)
        self.thresh = cv2.adaptiveThreshold(self.blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11,
                                            30)

    def dilate_image(self):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (12, 12))
        self.dilate = cv2.dilate(self.thresh, kernel, iterations=8)

    def find_text_contours(self):
        cnts = cv2.findContours(self.dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    def extract_ROIs(self):
        for c in self.cnts:
            area = cv2.contourArea(c)
            if area > 10000:
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(self.image, (x, y), (x + w, y + h), (36, 255, 12), 3)
                self.ROIS.append([x, y, w, h, self.ROI_number])
                self.parts = self.image[y:y + h, x:x + w]
                # ROI = self.image[y:y + h, x:x + w]
                # cv2.imwrite('ROI_{}.png'.format(self.ROI_number), ROI)
                self.ROI_number += 1

    def extract_text(self, ROI_index):
        first_segment = [(x, y, x + w, y + h) for (x, y, w, h) in self.ROIS][ROI_index - 1]
        x_min, y_min, x_max, y_max = first_segment
        cv2.rectangle(self.image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        cropped_image = self.image[y_min:y_max, x_min:x_max]
        gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        custom_config = r'--oem 3 --psm 6 -l rus'
        text = pytesseract.image_to_string(gray_image, config=custom_config)
        phrase = "№"
        phrase_coords = []
        lines = text.split('\n')
        for y, line in enumerate(lines):
            if phrase in line:
                x = line.index(phrase)
                phrase_coords.append((x, y))
        return  phrase_coords

    def add_text_to_image(self, date, number, phrase_coord):
        pil_image = Image.fromarray(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)
        font = ImageFont.truetype('arial.ttf', 16)
        text_width, text_height = draw.textsize(date, font=font)
        string = date+" № "+number
        draw.text(phrase_coord, string, font=font, fill=(255, 0, 0))
        image_with_text = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        cv2.imwrite('imageres.jpg', image_with_text)

    def save_image(self, output_path):
        cv2.imwrite(output_path, self.image)

    def find_label_coordinates(self, label_image):
        sift = cv2.SIFT_create()
        keypoints1, descriptors1 = sift.detectAndCompute(label_image, None)
        keypoints2, descriptors2 = sift.detectAndCompute(self.image, None)

        bf = cv2.BFMatcher()
        matches = bf.knnMatch(descriptors1, descriptors2, k=2)
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

        label_coords = []
        for match in good_matches:
            x, y = keypoints2[match.trainIdx].pt
            label_coords.append((int(x), int(y)))

        return label_coords

    def overlay_image(self, overlay_image_p, x, y):
        overlay_image = cv2.imread(overlay_image_p)

        overlay_height, overlay_width = overlay_image.shape[:2]
        x_min = x
        y_min = y
        x_max = x + overlay_width
        y_max = y + overlay_height

        self.image[y_min:y_max, x_min:x_max] = overlay_image

    def put_eds(self, filepath):
        if filepath == '':
            filepath = 'defaultEds.jpg'

        fio_regions = self.find_fio_regions()
        overlay_image = cv2.imread(filepath)

        overlay_x, overlay_y, overlay_width, overlay_height = self.find_free_area(fio_regions, overlay_image.shape[1],
                                                                                  overlay_image.shape[0])
        result_image = self.overlay_eds_image(overlay_image, overlay_x, overlay_y)
        self.image = result_image

    def find_fio_regions(self):
        ROIs = self.parts
        fio_regions = []
        for (x, y, w, h, roi) in ROIs:
            text = self.recognize_text(roi)
            if self.is_fio_text(text):
                fio_regions.append((x, y, w, h))
        return fio_regions

    @staticmethod
    def is_fio_text(text):
        pattern = r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+(\s[А-ЯЁ]\.[А-ЯЁ]\.)?$'
        match = re.match(pattern, text)

        if match:
            return True
        else:
            return False

    def find_free_area(self, fio_regions, width, height):
        for (x, y, w, h) in fio_regions:
            free_x, free_y, free_width, free_height = (x, y, w, h)
            while self.is_area_clean(x, y, width, height):
                free_x = x - 10
                free_y = y
                free_width = width
                free_height = height
            return (free_x, free_y, free_width, free_height)
        return None

    def overlay_eds_image(self, overlay_image, x, y):
        overlay_height, overlay_width, _ = overlay_image.shape
        self.image[y:y+overlay_height, x:x+overlay_width] = overlay_image
        return self.image

    @staticmethod
    def recognize_text(part):
        custom_config = r'--oem 3 --psm 6 -l rus'
        text = pytesseract.image_to_string(part, config=custom_config)
        return text

    def is_area_clean(self, x, y, width, height, threshold=10):
        area = self.image[y:y + height, x:x + width]
        gray = cv2.cvtColor(area, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        pixels_count = cv2.countNonZero(binary)

        if pixels_count < threshold:
            return True
        else:
            return False
