$FSLDIR/fslmaths  $FSLPATH/JHU-WhiteMatter-labels-1mm.nii.gz -thr $1 -uthr $2 -mas $MASKPATH/mean_FA_skeleton_mask  mask_SLF
