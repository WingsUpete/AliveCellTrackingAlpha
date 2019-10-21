import numpy as np
from random import randint
import math
import cv2 as cv
import sys

from tkinter import Tk
from tkinter.filedialog import askopenfilename

import matplotlib.pyplot as plt
from pylab import *

from Config import *


class CellTrack:
    """
        Cell Track Class is used to keep track of multiple cells
        at the same time without the processing of fluorescence.
        The algorithm will detect missing cells and prompt for
        new sample cells when necessary
    """
    miss_threshold = math.floor(max_cell_cnt * miss_tolerance)
    miss_judge = MISS_JUDGE

    def __init__(self):
        self.video = None                           # input video
        self.cur_frame = None

        self.bboxes = None                          # bounding boxes of the current frame
        self.colors = []                            # set of colors
        self.tracking_cell_cnt = 0                  # number of tracking cells now

        self.multiTracker = None                    # Multi-tracker

        self.initialPos = None                      # initial position of each cell
        self.positions = []                         # absolute positions of each cell - [[ (cell[i].x, cell[i].y) ]]
        self.dataset = []                           # relative positions of each cell (output) - [[ (cell[i].x, cell[i].y) ]]

        self.dawdle_cnt = []                        # how many frames each cell dawdles
        self.continuous_valid_cnt = []              # how many frames each cell travel with validity confirmed
        self.miss_cnt = 0                           # number of cells missing

        self.miss_boom = False                      # flag indicating a missing cell occurs
        self.del_list = []                          # list of index in which the data should be deleted

        self.data_res = []                          # final output data result
        self.data_res_colors = []                   # final output with colors assigned


    def readVideo(self, filename = None):
        """
            read a video
        """
        # Read video
        if filename != None:
            filename = "src/chanel3-p1.avi" # default file
        else:
            tkwd = Tk().withdraw() # Avoid using a full GUI
            filename = askopenfilename()    # file chooser
        # Create a video capture object to read videos
        video = cv.VideoCapture(filename)
        self.video = video
        # Exit if video is not opened.
        if not video.isOpened():
            print("Could not open video")
            return False
        # Read first frame
        ok, frame = video.read()
        # quit if unable to read the video file
        if not ok:
            print("Cannot read video file")
            return False
        self.cur_frame = frame
        return True


    def selectCells(self, cur_frame):
        """
            OpenCV's selectROIs function does not work for selecting
            multiple objects in Python, so we will call this function
            in a loop till we are done selecting all objects
            1. Select an object and press ENTER
            2. Press ESC to quit selecting boxes and start tracking
        """
        cv.namedWindow('MultiTracker', cv.WINDOW_NORMAL)
        print('{} / {} cells active now'.format(self.tracking_cell_cnt, max_cell_cnt))
        print('---------------------------- selecting regions... -----------------------------')
        bboxes = cv.selectROIs('MultiTracker', cur_frame, showCrosshair, fromCenter)
        print('----------------------------- regions selected... -----------------------------')
        newlen = len(bboxes)
        if (type(self.bboxes) == type(None)):
            self.bboxes = bboxes
        else:
            self.bboxes = np.append(self.bboxes, bboxes, axis=0)
        newPts = (bboxes[:,:2] + bboxes[:,2:] * 0.5)
        if (type(self.initialPos) == type(None)):
            self.initialPos = newPts
        else:
            self.initialPos = np.append(self.initialPos, newPts, axis=0)
        self.positions += newPts.reshape(-1,1,2).tolist()
        self.dataset += (newPts-newPts).reshape(-1,1,2).tolist()
        zeros = np.zeros([newlen]).astype(int).tolist()
        self.dawdle_cnt += zeros
        self.continuous_valid_cnt += zeros
        if len(self.bboxes) > max_cell_cnt: # if select more than set, truncate
            self.bboxes = self.bboxes[0:max_cell_cnt]
            self.initialPos = self.initialPos[0:max_cell_cnt]
            self.positions = self.positions[0:max_cell_cnt]
            self.dataset = self.dataset[0:max_cell_cnt]
        self.tracking_cell_cnt = len(self.bboxes)   # update tracking_cell_cnt
        if self.tracking_cell_cnt < CellTrack.miss_threshold:     # not enough cells selected...
            print('only {} cells being tracked and < {}, which is not enough...'.format(self.tracking_cell_cnt, CellTrack.miss_threshold))
            self.selectCells(cur_frame)


    def fillRandomColors(self):
        """
            This method fills colors[] with colors generated randomly
            The colors[] will have a length of newlen after generations
        """
        curlen = len(self.colors)
        newlen = self.tracking_cell_cnt
        fill_cnt = newlen - curlen
        print("Fill up {} colors to new length = {}".format(fill_cnt, newlen))
        cnt = 0
        while cnt < fill_cnt:
            self.colors.append((randint(0,255), randint(0,255), randint(0,255)))
            cnt += 1


    def initMultiTracker(self, cur_frame):
        """
            Initialize a multi-tracker with initial positions
        """
        # Create a MultiTracker object
        multiTracker = cv.MultiTracker_create()
        # Initialize MultiTracker
        for bbox in self.bboxes:
            added = multiTracker.add(self.createTrackerByName(tracker_type), cur_frame, tuple(bbox)) # Convert bbox to a tuple, then everything is just fine
        self.multiTracker = multiTracker


    def createTrackerByName(self, trackerType):
        """
            This function creates a single object tracker by name
        """
        # Create a tracker based on tracker name
        if tracker_type == tracker_types[0]:
            tracker = cv.TrackerBoosting_create()
        elif tracker_type == tracker_types[1]:
            tracker = cv.TrackerMIL_create()
        elif tracker_type == tracker_types[2]:
            tracker = cv.TrackerKCF_create()
        elif tracker_type == tracker_types[3]:
            tracker = cv.TrackerTLD_create()
        elif tracker_type == tracker_types[4]:
            tracker = cv.TrackerMedianFlow_create()
        elif tracker_type == tracker_types[5]:
            tracker = cv.TrackerGOTURN_create()
        elif tracker_type == tracker_types[6]:
            tracker = cv.TrackerMOSSE_create()
        elif tracker_type == tracker_types[7]:
            # We mainly use CSRT
            tracker = cv.TrackerCSRT_create()
        else:
            tracker = None
            print('Incorrect tracker name')
            print('Available trackers are:')
            for t in tracker_types:
                print(t)
        # returns the created tracker
        return tracker

    
    def trackTillMiss(self):
        """
            Keep tracking cells until one of them is missing
        """
        # Process video and track objects
        while self.video.isOpened():
            # Read a new frame
            ok, self.cur_frame = self.video.read()
            if not ok:
                print('video finished')
                # the video ends, before returning, check all validities
                for i in range(len(self.continuous_valid_cnt)):
                    if i not in self.del_list and self.continuous_valid_cnt[i] < valid_threshold:  # not enough valid records, sorry...
                        # self.deleteCellRecord(i)
                        self.del_list.append(i)
                # delete now will be save, and in reverse order
                self.del_list.sort()
                self.del_list = self.del_list[::-1]
                for ind in self.del_list:
                    self.deleteCellRecord(ind)
                self.del_list = []  # clear
                # Finish tracking
                cv.destroyAllWindows()
                return False    # no need to loop back here
            # Start timer
            timer = cv.getTickCount()

            # Update multi-tracker: get updated location of objects
            # in subsequent frames
            ok, self.bboxes = self.multiTracker.update(self.cur_frame)

            # Calculate FPS
            fps = cv.getTickFrequency() / (cv.getTickCount() - timer)

            # Draw bounding box
            if ok:
                # Tracking success
                # draw tracked objects proceedingly
                p1s = self.bboxes[:,:2]
                stretch = self.bboxes[:,2:]
                p2s = p1s + stretch
                curPos = p1s + stretch * 0.5
                curRelPos = curPos - self.initialPos
                self.miss_boom = False
                for i in range(len(self.bboxes)):
                    if i in self.del_list:
                        continue
                    self.positions[i].append(list(curPos[i]))
                    self.dataset[i].append(list(curRelPos[i]))
                    p1 = tuple(p1s[i].astype(int))
                    p2 = tuple(p2s[i].astype(int))
                    rect = cv.rectangle(self.cur_frame, p1, p2, self.colors[i], 2, 1)
                    # judge dawdle
                    x = curRelPos[i][0]
                    y = curRelPos[i][1]
                    rel_dist = math.sqrt(x*x + y*y)
                    if rel_dist <= dawdle_dist_def:     # dawdling
                        self.dawdle_cnt[i] += 1
                        # further judge whether it exceeds threshold
                        if self.dawdle_cnt[i] > dawdle_threshold:
                            # say goodbye to this cell cause it is probably missing
                            # self.deleteCellRecord(i)  # if delete now, list will change
                            self.del_list.append(i)
                            self.tracking_cell_cnt -= 1
                            self.miss_cnt += 1
                            print('miss due to dawdling, {} missed'.format(self.miss_cnt))
                            # if this cell has enough valid records, the data can stay...
                            if self.continuous_valid_cnt[i] >= valid_threshold:
                                self.data_res.append(self.dataset[i][0:self.continuous_valid_cnt[i]])
                                self.data_res_colors.append(self.colors[i])
                            # there are still video frames left, so check how many cells we have missed
                            if self.miss_cnt >= CellTrack.miss_threshold:
                                self.miss_boom = True     # loop back to this method
                                print('missing too many cells, reinitialization required')
                    else:                               # well-moved
                        # add former dawdle guess count, and add current frame count
                        self.continuous_valid_cnt[i] += self.dawdle_cnt[i] + 1
                        self.dawdle_cnt[i] = 0  # reset dawdle guess count

                if self.miss_boom == True:
                    # delete now will be save, and in reverse order
                    self.del_list.sort()
                    self.del_list = self.del_list[::-1]
                    for ind in self.del_list:
                        self.deleteCellRecord(ind)
                    self.del_list = []  # clear
                    self.miss_cnt = 0   # reset before return
                    # Finish tracking
                    cv.destroyAllWindows()
                    continue_or_not = input('Continue? (y/n): ')
                    return continue_or_not.upper() == 'Y'

                # Display tracker type on frame
                txtImg = cv.putText(self.cur_frame, tracker_type + " Tracker", (100,20), cv.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2)
                # Display FPS on frame
                txtImg = cv.putText(self.cur_frame, "FPS : " + str(int(fps)), (100,50), cv.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2)

                # Display result (show frame)
                cv.imshow("MultiTracker", self.cur_frame)

                # Exit if ESC pressed
                k = cv.waitKey(1) & 0xFF
                if k == 27:
                    # the tracking ends, before returning, check all validities
                    for i in range(len(self.continuous_valid_cnt)):
                        if i not in self.del_list and self.continuous_valid_cnt[i] < valid_threshold:  # not enough valid records, sorry...
                            # self.deleteCellRecord(i)
                            self.del_list.append(i)
                    # delete now will be save, and in reverse order
                    print('manually terminated')
                    self.del_list.sort()
                    self.del_list = self.del_list[::-1]
                    for ind in self.del_list:
                        self.deleteCellRecord(ind)
                    self.del_list = []  # clear
                    # Finish tracking
                    cv.destroyAllWindows()
                    return False    # the user is tired of tracking, stop then
            else:
                # Tracking failure
                # txtImg = cv.putText(self.cur_frame, "Tracking failure detected", (100,80), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255), 2)
                print('tracking failed on some cells')
                # find them, they have relative distance moved as 0, or a very small value
                p1s = self.bboxes[:,:2]
                stretch = self.bboxes[:,2:]
                curPos = p1s + stretch * 0.5
                curRelPos = curPos - self.initialPos
                for i in range(len(self.bboxes)):
                    if i in self.del_list:
                        continue
                    # still append if data is valid
                    self.positions[i].append(list(curPos[i]))
                    self.dataset[i].append(list(curRelPos[i]))
                    # judge dawdle
                    last_ind = len(self.positions[i])-2
                    x = self.positions[i][last_ind+1][0] - self.positions[i][last_ind][0]
                    y = self.positions[i][last_ind+1][1] - self.positions[i][last_ind][1]
                    rel_dist = math.sqrt(x*x + y*y)
                    if rel_dist < CellTrack.miss_judge:     # really missing
                        # say goodbye to this cell
                        # self.deleteCellRecord(i)  # if delete now, list will change
                        self.del_list.append(i)
                        self.tracking_cell_cnt -= 1
                        self.miss_cnt += 1
                        print('directly missing cell detected')
                        # if this cell has enough valid records, the data can stay
                        if self.continuous_valid_cnt[i] >= valid_threshold:
                            self.data_res.append(self.dataset[i][0:self.continuous_valid_cnt[i]])
                            self.data_res_colors.append(self.colors[i])
                    else:
                        # not missing
                        # add former dawdle guess count, and add current frame count
                        self.continuous_valid_cnt[i] += self.dawdle_cnt[i] + 1
                        self.dawdle_cnt[i] = 0  # reset dawdle guess count

                # delete records now in reverse order
                self.del_list.sort()
                self.del_list = self.del_list[::-1]
                for ind in self.del_list:
                    self.deleteCellRecord(ind)
                self.del_list = []  # clear
                self.miss_cnt = 0   # reset
                # Finish tracking
                cv.destroyAllWindows()
                continue_or_not = input('Continue? (y/n): ')
                return continue_or_not.upper() == 'Y'


    def deleteCellRecord(self, index):
        """
            delete specific cell record from all attributes according to the index given
        """
        try:
            self.bboxes = np.delete(self.bboxes, index, axis=0)
            del_color = self.colors.pop(index)
            self.initialPos = np.delete(self.initialPos, index, axis=0)
            del_pos = self.positions.pop(index)
            del_data = self.dataset.pop(index)
            del_dawdle_cnt = self.dawdle_cnt.pop(index)
            del_cvcnt = self.continuous_valid_cnt.pop(index)
        except IndexError:
            print('An index error occurred, here we just skip it for now...')
            print(self.del_list)
            print(index)
            pass


    def plotResults(self):
        # draw board showing
        xlab = plt.xlabel('distance_x')
        ylab = plt.ylabel('distance_y')
        plot_title = plt.title('Motion')
        plot_axis = plt.axis('equal')
        plt.grid(True)
        dataset = np.array(self.data_res + self.dataset)    # add everything left
        self.data_res_colors += self.colors
        for i in range(len(dataset)):
            try:
                data = dataset[i]
                xs = data[:,:1]
                ys = data[:,1:] * -1    # on image for y: lower larger; however when plotting, higher larger.
                plot_line = plt.plot(xs, ys, color=(float(self.data_res_colors[i][2])/255,float(self.data_res_colors[i][1])/255,float(self.data_res_colors[i][0])/255))
            except:
                print('An error occurred when plotting results... Here we just pass it')
        # hl = plt.hlines(0,-20,20)
        # vl = plt.vlines(0,-20,20)
        plt.show()
        plt.close('all')


    def saveToFile(self, filename):
        # np.savetxt('out/out_txt.txt', dataset)     # save as txt to existing file
        dataset = np.array(self.data_res + self.dataset)    # add everything left
        try:
            np.save("out/" + filename, dataset)    # save in format of numpy array config
            print('data saved to out/{}'.format(filename))
        except:
            print('sth went wrong on saving the data to file... Here we just pass it')