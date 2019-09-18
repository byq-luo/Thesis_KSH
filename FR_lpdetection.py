from label_processing import predicted_label_to_origin_image_WPOD, predicted_label_to_origin_image_Vernex_lp
from img_utility import read_img_from_dir
from os.path import join, basename, isdir
from os import mkdir
from drawing_utility import draw_LP_by_vertices
from config import Configs
from model_define import model_and_loss
import numpy as np
import cv2


# for testing SINGLE image
# return a list of possible license plates, in each label -> [prob, cor_after_affine]
def single_img_predict(img, input_dim=(0, 0), input_norm=True, model_code=''):
    if model_code in ['WPOD+WPOD', 'Hourglass+WPOD']:
        label_to_origin = predicted_label_to_origin_image_WPOD
    elif model_code == 'Hourglass+Vernex_lp':
        label_to_origin = predicted_label_to_origin_image_Vernex_lp
    elif model_code == 'Hourglass+Vernex_lpfr':
        pass

    img_shape = img.shape
    if input_norm:
        div = 255.
    else:
        div = 1.
    img_feed = cv2.resize(img, input_dim) / div
    img_feed = np.expand_dims(img_feed, 0)
    output_labels = model.predict(img_feed)
    final_labels = label_to_origin(img_shape, output_labels[0], stride=c.stride,
                                   prob_threshold=c.prob_threshold, use_nms=True, side=c.side)

    return final_labels


if __name__ == '__main__':

    c = Configs()

    model = model_and_loss()[0]

    model.load_weights(c.weight)

    if not isdir(c.output_dir):
        mkdir(c.output_dir)
    imgs_paths = read_img_from_dir(c.input_dir)

    for img_path in imgs_paths:

        print 'processing', img_path
        final_labels = single_img_predict(cv2.imread(img_path), input_dim=c.test_input_dim,
                                          input_norm=c.input_norm, model_code=c.model_code)

        if len(final_labels) == 0:
            print 'fail to detect'
            continue

        print '%d LPs found' % len(final_labels)

        img = cv2.imread(img_path)

        for i, final_label in enumerate(final_labels[:c.LPs_to_find]):
            prob, vertices = final_label
            try:
                img = draw_LP_by_vertices(img, vertices)
            except:
                print '%d LP area cutting failed' % i
                continue

        cv2.imwrite(join(c.output_dir, basename(img_path)), img)
        print 'write', join(c.output_dir, basename(img_path))




