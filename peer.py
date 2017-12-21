# #############################################################################
# PEER testing for fMRI data

# Screen size: 1680 x 1050 - from follow_the_dot_lastrun.py in ~/Desktop/HBN_Peer

import os
import sys
import numpy as np
import pandas as pd
import nibabel as nib
from nilearn import image
from sklearn.svm import SVR
from nilearn import plotting
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV

# DON'T FORGET MOTION CORRECTION BEFORE IMPORTING DATA

monitor_width = 1680
monitor_height = 1050

# Import data
img = nib.load('peer2_processed.nii.gz')
data = img.get_data()
testing = nib.load('peer1_processed.nii.gz')
testing_data = testing.get_data()
print(img.shape)

# Vectorize data into single np array

listed = []
listed_testing = []

for tr in range(int(data.shape[3])):

    tr_data = data[::2, ::2, 18:25, tr]
    # tr_data = data[:, :, 15:30, tr]
    te_data = testing_data[::2, ::2, 18:25, tr]
    # te_data = testing_data[:, :, 15:30, tr]
    vectorized = np.array(tr_data.ravel())
    vectorized_testing = np.array(te_data.ravel())
    listed.append(vectorized)
    listed_testing.append(vectorized_testing)

df = np.asarray(listed)
df_testing = np.asarray(listed_testing)

# Create np array that contains all fixation locations, separated by x and y coordinates

fixations = pd.read_csv('stim_vals.csv')
x_targets = np.repeat(np.array(fixations['pos_x']), 5)*monitor_width/2
y_targets = np.repeat(np.array(fixations['pos_y']), 5)*monitor_height/2

# # For visualization
# for num in [0, 50]:
#     visual = image.index_img(testing, num)
#     slice_data = visual.get_data()[:, :, 15:30]
#     plotting.plot_stat_map(visual)
#     plotting.show()

# Testing
train_vectors = df
test_vectors = df_testing

# Build classifiers with variable hyperparameters

classifier = SVR(kernel='rbf', C=100, epsilon=.001)
# Validation
validation_x = classifier.fit(train_vectors, x_targets).predict(train_vectors)
validation_y = classifier.fit(train_vectors, y_targets).predict(train_vectors)
# Testing
predicted_x = classifier.fit(train_vectors, x_targets).predict(test_vectors)
predicted_y = classifier.fit(train_vectors, y_targets).predict(test_vectors)

parameters = {'kernel': ('linear', 'rbf', 'poly', 'sigmoid'), 'C': [100, 200, 300, 400, 500, 1000, 2500, 5000, 10000],
              'epsilon': [.01, .001]}
clfx = GridSearchCV(classifier, parameters)
clfx.fit(train_vectors, x_targets)
clfy = GridSearchCV(classifier, parameters)
clfy.fit(train_vectors, y_targets)

predicted_x = clfx.predict(test_vectors)
predicted_y = clfy.predict(test_vectors)

# Plot SVR predictions against targets
plt.figure()
plt.scatter(predicted_x[:5], predicted_y[:5], color='r', alpha=.25)
plt.scatter(predicted_x[5:10], predicted_y[5:10], color='b', alpha=.25)
plt.scatter(predicted_x[10:15], predicted_y[10:15], color='g', alpha=.25)
plt.scatter(predicted_x[15:20], predicted_y[15:20], color='m', alpha=.25)
plt.scatter(predicted_x[20:25], predicted_y[20:25], color='y', alpha=.25)
plt.scatter(predicted_x[25:30], predicted_y[25:30], color='c', alpha=.25)
plt.scatter(x_targets, y_targets, color='k', alpha=.1)
plt.xlabel('x-position')
plt.ylabel('y-position')
plt.title('Support Vector Regression - PEER')
plt.legend()
plt.show()


