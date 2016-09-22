#============#============#============#============#============#============#============#============#============
import nibabel as nib
import pandas as pd
import numpy as np

# System-specific paths:
homeDir = '/Users/Egor/' # MacOS
atlDir = '/Applications/fsl/data/atlases/'
#homeDir = '/home/egor/' # Linux
#atlDir = '/usr/share/fsl/5.0/data/atlases/'
projDir = homeDir + 'Dropbox/Projects/md/dti/'

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
# Masks and labels

## Structure labels and their indices in the atlas:
wmLabels = nib.load(atlDir + 'JHU/JHU-ICBM-labels-1mm.nii.gz')
wmLabelsData = wmLabels.get_data()
allLabels = pd.read_excel(projDir + 'analyses/wmLabels.xlsx')

## Create two masks: one with the labels intact, the other binary:

### First, creating the mask with the labels
#maskLabels = np.zeros(wmLabels.shape) # creating an empty array with the MNI dimensions
#for curLabelId in labelIds:
#    maskLabels[wmLabelsData == curLabelId] = curLabelId
#np.ptp(maskLabels) # the range of values in the new mask; should be 28

### The binary mask is simply the maskLabels with all values > 0 equal to 1
#maskBin = np.zeros(wmLabels.shape)
#maskBin[maskLabels > 0] = 1
#np.ptp(maskBin) # the range of values in the new mask; should be 1

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
runData = np.zeros((wmLabels.shape[0], wmLabels.shape[1], wmLabels.shape[2], nSubjs, 3), dtype='float32')
runData[:,:,:,:,0] = imgData12[:,:,:,0:nSubjs]
runData[:,:,:,:,1] = imgData12[:,:,:,nSubjs:nSubjs*2]
runData[:,:,:,:,2] = imgData13[:,:,:,nSubjs:nSubjs*2]
del imgData12, imgData13

#============#============#============#============#============#============#============#============#============
# For every label in wmLabels, every run, and every participant, compute average voxel value:

# Initialization:
ds = pd.DataFrame()
nLabels = np.ptp(wmLabelsData)
curSubjN = 0 #temp
#curLabelId = labelIds[0] #temp, 23
curLabelId = range(np.ptp(wmLabelsData))[0]+1 # ranges from 1 to 48
runN = 0

# curSubjN group run labelID label dtiType value

# subject data set:
for curSubjN in range(nSubjs):
    curSubjID = subjSS.ix[curSubjN, 'subjID'] # e.g., MCI001
    print 'current subjects is ' + curSubjID
    for curLabelId in np.add(range(nLabels),1):
        #print 'curLabelId=' + str(curLabelId)
        for runN in range(3):
            strMean = np.mean(runData[wmLabelsData == curLabelId, curSubjN, runN])
            sds = pd.DataFrame({'subjN': curSubjN,
                                'subjID': curSubjID,
                                'run': runN+1,
                                'labelID': curLabelId,
                                'dtiType': dtiType,
                                'value': [strMean]})
            ds = ds.append(sds)
del runData

#============#============#============#============#============#============#============#============#============
# Completing and exporting the data set

# Add Label information to the (all) data set:
ads = pd.merge(ds, allLabels, on='labelID')
# Merge the ds with the subject data:
ads = pd.merge(ads, subjSS, on='subjID')
# Exporting the data set:
ads.to_csv(projDir + 'analyses/roiDS_' + dtiType + '.csv', index=False)

#============#============#============#============#============#============#============#============#============