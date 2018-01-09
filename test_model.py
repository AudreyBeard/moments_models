# the test script
# load the trained model then forward pass on a given image


import torch
from torch.autograd import Variable as V
import torchvision.models as models
from torchvision import transforms as trn
from torch.nn import functional as F
import os
import numpy as np
from scipy.misc import imresize as imresize
import cv2
from PIL import Image

def load_model(modelID, categories):
    if modelID == 1:
        model_name = 'resnet50_imagenetpretrained_moments'
        weight_file = 'moments_RGB_resnet50_imagenetpretrained.pth.tar'
        if not os.access(weight_file, os.W_OK):
            weight_url = 'http://moments.csail.mit.edu/moments_models/' + weight_file
            os.system('wget ' + weight_url)

        model = models.__dict__['resnet50'](num_classes=len(categories))

        useGPU = 0
        if useGPU == 1:
            checkpoint = torch.load(weight_file)
        else:
            checkpoint = torch.load(weight_file, map_location=lambda storage, loc: storage) # allow cpu

        state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}
        model.load_state_dict(state_dict)

    model.eval()
    return model

def returnTF():
# load the image transformer
    tf = trn.Compose([
        trn.Resize((224,224)),
        trn.ToTensor(),
        trn.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    return tf

dataset = 'moments'
modelID = 1

# load category
with open('category_momentsv1.txt') as f:
    categories = [line.rstrip() for line in f.readlines()]



# load the labels
model = load_model(modelID, categories)


# load the transformer
tf = returnTF() # image transformer


# load the test image
if os.path.exists('test.jpg'):
    os.remove('test.jpg')
img_url = 'http://places2.csail.mit.edu/imgs/demo/IMG_5970.JPG'
os.system('wget %s -q -O test.jpg' % img_url)
img = Image.open('test.jpg')
input_img = V(tf(img).unsqueeze(0), volatile=True)

# forward pass
logit = model.forward(input_img)
h_x = F.softmax(logit, 1).data.squeeze()
probs, idx = h_x.sort(0, True)

print('RESULT ON ' + img_url)


# output the prediction of action category
print('--Top Actions:')
for i in range(0, 5):
    print('{:.3f} -> {}'.format(probs[i], categories[idx[i]]))
