import os
import sys
import json
import datetime
from nbformat import read
import numpy as np
import skimage.draw
import pydicom
import cv2
import time
import pickle
# os.environ['CUDA_VISIBLE_DEVICES'] = '0'
# os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

ROOT_DIR = os.path.abspath("../../")
# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library
from mrcnn.config import Config
from mrcnn import model as modellib, utils
# Path to trained weights file
COCO_WEIGHTS_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")
# Directory to save logs and model checkpoints, if not provided
# through the command line argument --logs
DEFAULT_LOGS_DIR = os.path.join(ROOT_DIR, "logs")

class TumorConfig(Config):
    """Configuration for training on the toy  dataset.
    Derives from the base Config class and overrides some values.
    """
    # Give the configuration a recognizable name
    NAME = "tumor"

    # We use a GPU with 12GB memory, which can fit two images.
    # Adjust down if you use a smaller GPU.
    IMAGES_PER_GPU = 2

    # Number of classes (including background)
    NUM_CLASSES = 1 + 1  # Background + tumor

    # Number of training steps per epoch
    STEPS_PER_EPOCH = 100

    # Skip detections with < 90% confidence
    DETECTION_MIN_CONFIDENCE = 0.9

class TumorDataset(utils.Dataset):

    def load_tumor(self, dataset_dir, subset):
        """Load a subset of the Tumor dataset.
        dataset_dir: Root directory of the dataset.
        subset: Subset to load: train or val
        """
        # Add classes. We have only one class to add.
        self.add_class("tumor", 1, "tumor")

        # Train or validation dataset?
        assert subset in ["train", "val"]
        dataset_dir = os.path.join(dataset_dir, subset)

        if subset=="train":
            annotations = json.load(open("C:/Users/John/Desktop/UCSD/CT lab/maskrcnn/tumordataset2/train/tumor150png.json"))
        else:
            annotations = json.load(open("C:/Users/John/Desktop/UCSD/CT lab/maskrcnn/tumordataset2/val/val50tumor.json"))

        annotations = annotations["_via_img_metadata"]
        annotations = list(annotations.values())  # don't need the dict keys

        # The VIA tool saves images in the JSON even if they don't have any
        # annotations. Skip unannotated images.
        # annotations = [a for a in annotations if a['regions']]

        # Add images
        for a in annotations:
            # Get the x, y coordinaets of points of the polygons that make up
            # the outline of each object instance. These are stores in the
            # shape_attributes (see json format above)
            # The if condition is needed to support VIA versions 1.x and 2.x.
            if type(a['regions']) is dict:
                polygons = [r['shape_attributes'] for r in a['regions'].values()]
            else:
                polygons = [r['shape_attributes'] for r in a['regions']] 

            # load_mask() needs the image size to convert polygons to masks.
            # Unfortunately, VIA doesn't include it in JSON, so we must read
            # the image. This is only managable since the dataset is tiny.
            image_path = os.path.join(dataset_dir, a['filename'])
            image = skimage.io.imread(image_path)
            height, width = image.shape[:2]

            self.add_image(
                "tumor",
                image_id=a['filename'],  # use file name as a unique image id
                path=image_path,
                width=width, height=height,
                polygons=polygons)
    def load_mask(self, image_id):
        """Generate instance masks for an image.
       Returns:
        masks: A bool array of shape [height, width, instance count] with
            one mask per instance.
        class_ids: a 1D array of class IDs of the instance masks.
        """
        # If not a balloon dataset image, delegate to parent class.
        image_info = self.image_info[image_id]
        if image_info["source"] != "tumor":
            return super(self.__class__, self).load_mask(image_id)

        # Convert polygons to a bitmap mask of shape
        # [height, width, instance_count]
        info = self.image_info[image_id]
        mask = np.zeros([info["height"], info["width"], len(info["polygons"])],
                        dtype=np.uint8)
        for i, p in enumerate(info["polygons"]):
            # Get indexes of pixels inside the polygon and set them to 1
            rr, cc = skimage.draw.polygon(p['all_points_y'], p['all_points_x'])
            mask[rr, cc, i] = 1

        # Return mask, and array of class IDs of each instance. Since we have
        # one class ID only, we return an array of 1s
        return mask.astype(np.bool), np.ones([mask.shape[-1]], dtype=np.int32)

    def image_reference(self, image_id):
        """Return the path of the image."""
        info = self.image_info[image_id]
        if info["source"] == "tumor":
            return info["path"]
        else:
            super(self.__class__, self).image_reference(image_id)

def train(model):
    """Train the model."""
    # Training dataset.
    dataset_train = TumorDataset()
    dataset_train.load_tumor(args.dataset, "train")
    dataset_train.prepare()

    # Validation dataset
    dataset_val = TumorDataset()
    dataset_val.load_tumor(args.dataset, "val")
    dataset_val.prepare()

    # *** This training schedule is an example. Update to your needs ***
    # Since we're using a very small dataset, and starting from
    # COCO trained weights, we don't need to train too long. Also,
    # no need to train all layers, just the heads should do it.
    print("Training network heads")
    model.train(dataset_train, dataset_val,
                learning_rate=config.LEARNING_RATE,
                epochs=30,
                layers='heads')


def color_splash(image, mask):
    """Apply color splash effect.
    image: RGB image [height, width, 3]
    mask: instance segmentation mask [height, width, instance count]

    Returns result image.
    """
    # Make a grayscale copy of the image. The grayscale copy still
    # has 3 RGB channels, though.
    # gray = skimage.color.gray2rgb(skimag.color.rgb2gray(image)) * 255
    print(image.shape)
    w,h,_= image.shape

    red = np.full((w,h,_), [0,254,0])
    # Copy color pixels from the original color image where mask is set
    if mask.shape[-1] > 0:
        # We're treating all instances as one, so collapse the mask into one layer
        mask = (np.sum(mask, -1, keepdims=True) >= 1)
        # splash = np.where(mask, image, gray).astype(np.uint8)
        # splash = np.where(mask, image, red).astype(np.uint8)
        splash = np.where(mask, red, image).astype(np.uint8)

    else:
        # splash = gray.astype(np.uint8)
        # splash = red.astype(np.uint8)
        splash = image
    # return mask
    return splash

def hello():
    print("hello")
def dicom_folder_splash(model, folder_path=None):
    assert folder_path
    if folder_path:
        resmask= [] 
        # todo change to sort based on series
        for im in sorted(os.listdir(folder_path)):
            print("OOOOO"*40,im)
            ### Time inference and just loading data, and dataprep

            # original staright up dicom
            # image = pydicom.read_file(folder_path+"/"+im)
            # image = image.pixel_array
            # image = skimage.io.imread(folder_path+"/"+im)

            # gotta turn to png then read, omit if no save png
            start = time. time()
            image = pydicom.read_file(folder_path+"/"+im)
            image = image.pixel_array #raw pixel data

            # reads it as it woulda been saved (compression)
            image = cv2.imencode('.png', image)[1].tobytes()
            image = np.frombuffer(image, np.byte)
            image = cv2.imdecode(image, cv2.IMREAD_ANYCOLOR)
            end = time. time()
            print("&"*200,"\n",end - start, '\n')

            


            if image.ndim != 3:
                image = skimage.color.gray2rgb(image)


            start = time. time()
            r = model.detect([image], verbose=1)[0]
            end = time. time()
            print("@"*200,"\n",end - start, '\n')
            # print("r['masks']", r['masks'])
            # print("r['masks'] type", type(r['masks']))
            # print("r['masks'] shape", r['masks'].shape)

            mask = (np.sum(r['masks'], -1, keepdims=True) >= 1)
            resmask.append(mask)
            # print("mask", mask)
            # print("mask type", type(mask))
            # print("mask shape", mask.shape)



            ### make a golder and put in ###
            # splash = color_splash(image, r['masks'])
            # output_folder = "/".join(folder_path.split("/")[:-1])+"/"+folder_path.split("/")[-1]+"_splash/"
            # if not os.path.exists(output_folder):
                # os.makedirs(output_folder)
            # output = output_folder + im +"_splash_{:%Y%m%dT%H%M%S}.png".format(datetime.datetime.now())
            # skimage.io.imsave(output, splash)
    ### pickle the mask ###
    with open("mask.bin","wb") as f:
        pickle.dump(resmask, f)

def detect_and_color_splash(model, image_path=None, video_path=None):
    assert image_path or video_path
    # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%", "\n")
    # print(args.image)
    # return
    # Image or video?
    if image_path:
        # convert dicom to ndarray
        # image = pydicom.read_file(args.image)
        # image = image.pixel_array

        # Run model detection and generate the color splash effect
        print("Running on {}".format(args.image))
        # Read image png to ndarray
        image = skimage.io.imread(args.image)

        if image.ndim != 3:
            image = skimage.color.gray2rgb(image)

        # Detect objects
        r = model.detect([image], verbose=1)[0]
        # Color splash
        splash = color_splash(image, r['masks'])
        # Save output
        # file_name = "splash_{:%Y%m%dT%H%M%S}.png".format(datetime.datetime.now())
        
        # file_name = "/".join(args.image.split("/")[:-2])
        file_name="C:/Users/John/Desktop/UCSD/CT lab/CTMR_robot_lab/inference_outputs/"
        file_name += "_".join(args.image.split("/")[9:-1])
        if not os.path.exists(file_name):
            os.makedirs(file_name)
        file_name += "/" + args.image.split("/")[-1] +"_splash_{:%Y%m%dT%H%M%S}.png".format(datetime.datetime.now())
        # file_name = "C:/Users/John/Desktop/UCSD/CT lab/new_workspace/run_one_full_slice/biopsy 1 splash/"+"splash_{:%Y%m%dT%H%M%S}.png".format(datetime.datetime.now())
    
        skimage.io.imsave(file_name, splash)
    elif video_path:
        import cv2
        # Video capture
        vcapture = cv2.VideoCapture(video_path)
        width = int(vcapture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vcapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = vcapture.get(cv2.CAP_PROP_FPS)

        # Define codec and create video writer
        file_name = "splash_{:%Y%m%dT%H%M%S}.avi".format(datetime.datetime.now())
        vwriter = cv2.VideoWriter(file_name,
                                  cv2.VideoWriter_fourcc(*'MJPG'),
                                  fps, (width, height))

        count = 0
        success = True
        while success:
            print("frame: ", count)
            # Read next image
            success, image = vcapture.read()
            if success:
                # OpenCV returns images as BGR, convert to RGB
                image = image[..., ::-1]
                # Detect objects
                r = model.detect([image], verbose=0)[0]
                # Color splash
                splash = color_splash(image, r['masks'])
                # RGB -> BGR to save image to video
                splash = splash[..., ::-1]
                # Add image to video writer
                vwriter.write(splash)
                count += 1
        vwriter.release()
    print("Saved to ", file_name)

def read_dicom_to_np(dicom_path, resolution=False): 
    #resulution true means better res, not good with inference
    image = pydicom.read_file(dicom_path)
    image = image.pixel_array #raw pixel data
    if resolution == True:
        # return image
        pass
    else:
        image = cv2.imencode('.png', image)[1].tobytes()
        image = np.frombuffer(image, np.byte)
        image = cv2.imdecode(image, cv2.IMREAD_ANYCOLOR)
    return image


############################################################
#  Training
############################################################

# if __name__ == '__main__':
# def main(args):
def main():
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Train Mask R-CNN to detect balloons.')
    parser.add_argument("command",
                        metavar="<command>",
                        help="'train' or 'splash'")
    parser.add_argument('--dataset', required=False,
                        metavar="/path/to/balloon/dataset/",
                        help='Directory of the Balloon dataset')
    parser.add_argument('--weights', required=True,
                        metavar="/path/to/weights.h5",
                        help="Path to weights .h5 file or 'coco'")
    parser.add_argument('--logs', required=False,
                        default=DEFAULT_LOGS_DIR,
                        metavar="/path/to/logs/",
                        help='Logs and checkpoints directory (default=logs/)')
    parser.add_argument('--image', required=False,
                        metavar="path or URL to image",
                        help='Image to apply the color splash effect on')
    parser.add_argument('--folder', required=False,
                        metavar="path or URL to dicom_folder",
                        help='Folder of images to apply the color splash effect on')
    parser.add_argument('--video', required=False,
                        metavar="path or URL to video",
                        help='Video to apply the color splash effect on')
    args = parser.parse_args()

    # Validate arguments
    if args.command == "train":
        assert args.dataset, "Argument --dataset is required for training"
    elif args.command == "splash":
        assert args.image or args.video or args.folder,\
               "Provide --image or --video to apply color splash"

    print("Weights: ", args.weights)
    print("Dataset: ", args.dataset)
    print("Logs: ", args.logs)

    # Configurations
    if args.command == "train":
        config = TumorConfig()
    else:
        class InferenceConfig(TumorConfig):
            # Set batch size to 1 since we'll be running inference on
            # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
            GPU_COUNT = 1
            IMAGES_PER_GPU = 1
        config = InferenceConfig()
    config.display()

    # Create model
    if args.command == "train":
        model = modellib.MaskRCNN(mode="training", config=config,
                                  model_dir=args.logs)
    else:
        model = modellib.MaskRCNN(mode="inference", config=config,
                                  model_dir=args.logs)

    # Select weights file to load
    if args.weights.lower() == "coco":
        weights_path = COCO_WEIGHTS_PATH
        # Download weights file
        if not os.path.exists(weights_path):
            utils.download_trained_weights(weights_path)
    elif args.weights.lower() == "last":
        # Find last trained weights
        weights_path = model.find_last()
    elif args.weights.lower() == "imagenet":
        # Start from ImageNet trained weights
        weights_path = model.get_imagenet_weights()
    else:
        weights_path = args.weights

    # Load weights
    print("Loading weights ", weights_path)
    if args.weights.lower() == "coco":
        # Exclude the last layers because they require a matching
        # number of classes
        model.load_weights(weights_path, by_name=True, exclude=[
            "mrcnn_class_logits", "mrcnn_bbox_fc",
            "mrcnn_bbox", "mrcnn_mask"])
    else:
        model.load_weights(weights_path, by_name=True)

    # Train or evaluate
    if args.command == "train":
        train(model)
    # elif args.command == "read":
    #     read_dicom_to_np
        pass
    elif args.command == "splash":
        # detect_and_color_splash(model, image_path=args.image,
        #                         video_path=args.video)
        dicom_folder_splash(model, folder_path = args.folder)
    else:
        print("'{}' is not recognized. "
              "Use 'train' or 'splash'".format(args.command))

if __name__ == '__main__':
    # main(sys.argv[1:])
    main()