# ROI Check
# Egor Ananyev
# 2016-09-03

# The objective is to check the validity of the results obtained by FSL and roiExtraction.py, as they currently
# diverge.

#============#============#============#============#============#============#============#============#============
import nibabel as nib
import pandas as pd
import numpy as np
import os

# System-specific paths:
#atlDir = '/Applications/fsl/data/atlases/'
atlDir = '/usr/share/fsl/5.0/data/atlases/'
projDir = os.path.expanduser('~') + '/Dropbox/Projects/md/dti/'

# Loading the data:
dtiType = 'FA'
allComps = [12, 13, 23]
curComp = 0 # 0=12, 1=13, 2=23
dataDir12 = projDir + 'results_roi_2016-08-27/tbss12-roi/'
img12 = nib.load(dataDir12 + 'all_' + dtiType + '_skeletonised.nii.gz')
imgData12 = img12.get_data()
dataDir13 = projDir + 'results_roi_2016-08-27/tbss13-roi/'
img13 = nib.load(dataDir13 + 'all_' + dtiType + '_skeletonised.nii.gz')
imgData13 = img13.get_data()

#============#============#============#============#============#============#============#============#============
# Extracting the voxels to test
voxDs = pd.read_excel(projDir + 'sign_clusters_v2.xlsx', 't123_roi')
# Retaining only the appropriate DTI marker:
voxDs = voxDs.ix[voxDs['index']==dtiType,:]
voxDs = voxDs.reset_index()
#voxDs['Label'] = 'vox_' + str(voxDs['x']) + '_' + str(voxDs['y']) + '_' + str(voxDs['z'])
nVox = voxDs.shape[0]

## Structure labels and their indices in the atlas:
#wmLabels = nib.load(atlDir + 'JHU/JHU-ICBM-labels-1mm.nii.gz')
#wmLabelsData = wmLabels.get_data()
#allLabels = pd.read_excel(projDir + 'analyses/wmLabels.xlsx')

#============#============#============#============#============#============#============#============#============
# Loading the subject data set:
subjDF = pd.read_excel(projDir + 'MAPRCT_Consolidated_v2.xlsx', 'tabbed')
#list(subjDF.columns.values) # list column names
subjDF['group'] = 'MAP'
subjDF.ix[subjDF['Program'] == 'Health Education Program', 'group'] = 'HEP'
# Filtering out bad subjects and subjects without all three visits
subjSS = subjDF.ix[subjDF['runSum']==3,:]
subjSS = subjSS.ix[subjSS['bad']==0,:] # not really applicable, as all subjs are 'good'
subjSS = subjSS.reset_index()
nSubjs = subjSS.shape[0]

#============#============#============#============#============#============#============#============#============
# Extracting the data from all three runs into a long df:
runData = np.zeros((img12.shape[0], img12.shape[1], img12.shape[2], nSubjs, 3), dtype='float32')
runData[:,:,:,:,0] = imgData12[:,:,:,0:nSubjs]
runData[:,:,:,:,1] = imgData12[:,:,:,nSubjs:nSubjs*2]
runData[:,:,:,:,2] = imgData13[:,:,:,nSubjs:nSubjs*2]
del imgData12, imgData13

#============#============#============#============#============#============#============#============#============
# For every voxel, every run, and every participant, compute average voxel value:

# Initialization:
ds = pd.DataFrame()
curSubjN = 0 #temp
#curLabelId = labelIds[0] #temp, 23
#curVoxId = range(np.ptp(wmLabelsData))[0]+1 # ranges from 1 to 48
curVox = 1
runN = 0

# subject data set:
for curSubjN in range(nSubjs):
    curSubjID = subjSS.ix[curSubjN, 'subjID'] # e.g., MCI001
    print 'current subjects is ' + curSubjID
    for curVox in np.add(range(nVox),1):
        #print 'curVox=' + str(curVox)
        curX = voxDs.ix[curVox-1,'x']
        curY = voxDs.ix[curVox-1,'y']
        curZ = voxDs.ix[curVox-1,'z']
        curXvx = voxDs.ix[curVox-1,'xVx']
        curYvx = voxDs.ix[curVox-1,'yVx']
        curZvx = voxDs.ix[curVox-1,'zVx']
        for runN in range(3):
            voxVal = runData[curXvx, curYvx, curZvx, curSubjN, runN]
            sds = pd.DataFrame({'subjN': curSubjN,
                                'subjID': curSubjID,
                                'run': runN+1,
                                'curVox': curVox,
                                'x': curX,
                                'y': curY,
                                'z': curZ,
                                'xVx': curXvx,
                                'yVx': curYvx,
                                'zVx': curZvx,
                                'dtiType': dtiType,
                                'voxVal': [voxVal]})
            ds = ds.append(sds)
del runData

#============#============#============#============#============#============#============#============#============
# Completing and exporting the data set

# Add Label information to the (all) data set:
#ads = pd.merge(ds, voxDs, on='labelID')
# Merge the ds with the subject data:
ads = pd.merge(ds, subjSS, on='subjID')
# Exporting the data set:
ads.to_csv(projDir + 'analyses/voxDS_' + dtiType + '_fixed.csv', index=False)

#============#============#============#============#============#============#============#============#============