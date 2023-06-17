from registrator.TextExtractor import TextExtractor


def process(image_path, eds, label_image, date, number):
    output_path = 'image.jpg'
    extractor = TextExtractor(image_path)
    extractor.preprocess_image()
    extractor.dilate_image()
    extractor.find_text_contours()
    extractor.extract_ROIs()
    if date != '' or number != '':
        extractor.add_text_to_image(date, number, extractor.extract_text(extractor.ROI_number))
    if label_image != '':
        coordinates = extractor.find_label_coordinates(label_image)
        if len(coordinates) != 0:
            extractor.overlay_image(eds, coordinates[0][0], coordinates[0][1])
    else:
        extractor.put_eds(eds)
    extractor.save_image(output_path)
    return output_path


