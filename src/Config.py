import cv2 as cv

# General Info
(major_ver, minor_ver, subminor_ver) = (cv.__version__).split('.')
tracker_types = ['BOOSTING','MIL','KCF','TLD','MEDIANFLOW','GOTURN','MOSSE','CSRT']

# Specify the tracker type
tracker_type = "CSRT"

# selectROI Prop
showCrosshair = False
fromCenter = False

# Tracking Param
max_cell_cnt = 15        # Track how many cells at most
miss_tolerance = 0.5    # percentage of cells missing which the program can stand at most

dawdle_dist_def = 100    # the maximum distance considered as dawdling
dawdle_threshold = 100  # maximum time cells can stay almost still at one place - 100
valid_threshold = 150   # minimum number of continuous valid frames tracked - 150

MISS_JUDGE = 0.0001     # how do you specify the difference on directly missing cells?