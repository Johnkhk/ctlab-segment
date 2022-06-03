import sys
sys.path.insert(1, 'C:/Users/John/Desktop/UCSD/CT lab/flask_serv/samples/tumor')
# from tumor import hello, dicom_folder_splash, main, read_dicom_to_np
# from tumor import *
import tumor.tumor as tumor
import tumor

# import itk
# import pydicom

testpic = "C:/Users/John/Desktop/UCSD/CT lab/CTMR_robot_lab/data/export_reslice/biopsy 7/IMG-0015-00001.dcm"
a = tumor.read_dicom_to_np(testpic)
# print(dir(a))

# image = itk.GetImageFromArray(a)
# itk.imwrite(image, 'nrrd_files/image.nrrd')

# pydicom.readfile()



# from flask import Flask, request
# from flask_sqlalchemy import SQLAlchemy

# hello()
# dicom_folder_splash
# inputdir = "C:/Users/John/Desktop/UCSD/CT lab/CTMR_robot_lab/data/export_reslice/biopsy 7"
# uh=["splash", "--weights=C:/Users/John/Desktop/UCSD/CT lab/maskrcnn/Mask_RCNN/logs/tumor20211231T1726/mask_rcnn_tumor_0030.h5", "--folder="+inputdir]
tumor.main()

# app = Flask(__name__)
# # app.config['SQLALCHEMY_DATABASE_URI']= ''
# # cb = SQLAlchemy(app)

# # Focus on visualization first
# # optimze inference time

# tmp = {'arr': a.tolist()}
# # Todo fields, low dimension coords, high, quick access: visualization

# @app.route('/')
# def hello_world():
#     return tmp
#     # return 'Hello, World!'
# # @app.route('/pushdicom', methods=['GET', 'POST'])
# # def push():
#     # if request.method == 'POST':


# if __name__ == '__main__':
#     app.run(debug=True)


