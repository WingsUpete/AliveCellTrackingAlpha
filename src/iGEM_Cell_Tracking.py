import sys

from Config import *
from CellTrack import *

if __name__ == '__main__':
    cell_track = CellTrack()
    resp = cell_track.readVideo()
    if resp == False:
        sys.exit(0)
    # loop judge
    while True:
        cell_track.selectCells(cell_track.cur_frame)
        cell_track.fillRandomColors()
        cell_track.initMultiTracker(cell_track.cur_frame)
        loop_back = cell_track.trackTillMiss()
        if not loop_back:
            break

    cell_track.saveToFile('out_numpy')
    cell_track.plotResults()
    sys.exit(1)
