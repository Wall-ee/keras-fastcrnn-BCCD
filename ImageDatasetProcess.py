import os
import shutil
import xml.etree.ElementTree as ET
from glob import glob
import pandas as pd

"""
put this file to BCCD  directory and run script.  
BCCD dataset 
https://github.com/Shenggan/BCCD_Dataset

it will generate 
train_images：用于训练模型的图像，包含每个图像的类别和实际边界框；
test_images：用于模型预测的图像，该集合缺少对应的标签；
train.csv：包含每个图像的名称、类别和边界框坐标。一张图像可以有多行数据，因为单张图像可能包含多个对象；
"""


trainList = []
testList = []
file = open('./BCCD/ImageSets/Main/train.txt','r')
for line in file.readlines():
    trainList.append(line.strip())
file.close()

file = open('./BCCD/ImageSets/Main/test.txt','r')
for line in file.readlines():
    testList.append(line.strip())
file.close()

try:
    os.mkdir('./train_images')
    os.mkdir('./test_images')
except Exception:
    pass
trainPath = './train_images'
testPath = './test_images'

for trainFile in trainList:
    shutil.copy('./BCCD/JPEGImages/'+trainFile+'.jpg',trainPath+'/'+trainFile+'.jpg')

for testFile in testList:
    shutil.copy('./BCCD/JPEGImages/'+testFile+'.jpg',testPath+'/'+testFile+'.jpg')


"""
export to train.csv
"""

# annotations = glob('BCCD/Annotations/*.xml')
annotations = []

for trainFile in trainList:
    annotations.append('BCCD/Annotations\\'+trainFile+'.xml')


df = []
cnt = 0
for file in annotations:
    #filename = file.split('/')[-1].split('.')[0] + '.jpg'
    #filename = str(cnt) + '.jpg'
    filename = file.split('\\')[-1]
    filename =filename.split('.')[0] + '.jpg'
    row = []
    parsedXML = ET.parse(file)
    for node in parsedXML.getroot().iter('object'):
        blood_cells = node.find('name').text
        xmin = int(node.find('bndbox/xmin').text)
        xmax = int(node.find('bndbox/xmax').text)
        ymin = int(node.find('bndbox/ymin').text)
        ymax = int(node.find('bndbox/ymax').text)

        row = [filename, blood_cells, xmin, xmax, ymin, ymax]
        df.append(row)
        cnt += 1

train = pd.DataFrame(df, columns=['image_names', 'cell_type', 'xmin', 'xmax', 'ymin', 'ymax'])

train[['image_names', 'cell_type', 'xmin', 'xmax', 'ymin', 'ymax']].to_csv('train.csv', index=False)


data = pd.DataFrame()
data['format'] = train['image_names']

# as the images are in train_images folder, add train_images before the image name
for i in range(data.shape[0]):
    data['format'][i] = 'train_images/' + data['format'][i]

# add xmin, ymin, xmax, ymax and class as per the format required
for i in range(data.shape[0]):
    data['format'][i] = data['format'][i] + ',' + str(train['xmin'][i]) + ',' + str(train['ymin'][i]) + ',' + str(train['xmax'][i]) + ',' + str(train['ymax'][i]) + ',' + train['cell_type'][i]

data.to_csv('annotate.txt', header=None, index=None, sep=' ')
