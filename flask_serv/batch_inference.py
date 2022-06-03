# import pydicom
import glob
import cv2
import os
from subprocess import call

# run_command=r'''python "C:/Users/John/Desktop/UCSD/CT lab/maskrcnn/Mask_RCNN/samples/tumor/tumor.py" splash --weights="C:/Users/John/Desktop/UCSD/CT lab/maskrcnn/Mask_RCNN/logs/tumor20211231T1726/mask_rcnn_tumor_0030.h5" --image='''

# inputdir = "C:/Users/John/Desktop/UCSD/CT lab/new_workspace/run_one_full_slice/biopsy 1 png/"
inputdir = "C:/Users/John/Desktop/UCSD/CT lab/CTMR_robot_lab/data/export_reslice/biopsy 7"
# inputdir = "C:/Users/John/Desktop/UCSD/CT lab/CTMR_robot_lab/data/from_webserver/1.2.840.113619.6.416.44185176469075267428178798667582221770/DICOM/5A96F838/35D15DC9"


# image
# for f in os.listdir(inputdir):
#     #image
#     call(["python", "C:/Users/John/Desktop/UCSD/CT lab/maskrcnn/Mask_RCNN/samples/tumor/tumor.py", "splash", "--weights=C:/Users/John/Desktop/UCSD/CT lab/maskrcnn/Mask_RCNN/logs/tumor20211231T1726/mask_rcnn_tumor_0030.h5", "--image="+inputdir+f])

# Folder
# call(["python", "C:/Users/John/Desktop/UCSD/CT lab/maskrcnn/Mask_RCNN/samples/tumor/tumor.py", "splash", "--weights=C:/Users/John/Desktop/UCSD/CT lab/maskrcnn/Mask_RCNN/logs/tumor20211231T1726/mask_rcnn_tumor_0030.h5", "--folder="+inputdir])
# call(["python", "C:/Users/John/Desktop/UCSD/CT lab/flask_serv/samples/tumor/tumor.py", "splash", "--weights=C:/Users/John/Desktop/UCSD/CT lab/maskrcnn/Mask_RCNN/logs/tumor20211231T1726/mask_rcnn_tumor_0030.h5", "--folder="+inputdir])
call(["python", "C:/Users/John/Desktop/UCSD/CT lab/flask_serv/test.py", "splash", "--weights=C:/Users/John/Desktop/UCSD/CT lab/maskrcnn/Mask_RCNN/logs/tumor20211231T1726/mask_rcnn_tumor_0030.h5", "--folder="+inputdir])



# python test.py, "splash", "--weights=C:/Users/John/Desktop/UCSD/CT lab/maskrcnn/Mask_RCNN/logs/tumor20211231T1726/mask_rcnn_tumor_0030.h5", "--folder=C:/Users/John/Desktop/UCSD/CT lab/CTMR_robot_lab/data/export_reslice/biopsy 7"


