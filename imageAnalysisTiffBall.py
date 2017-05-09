"""
Joshua Arribere May 7, 2017

Script to go through pixels of a tif file. For each pixel, will calculate an
    average pixel intensity for some radius around that pixel. If that avg
    is above some threshold (in red, green channels), it will call that pixel
    a signal-containing pixel. Otherwise the pixel is bg. Will output the avg
    of all signal-containing pixels, with the average of all bg-pixels
    subtracted.

Input: in.tif - 12-bit tif file in three channels: r,g,b

Output: image with location of all signal and bg pixels as white/black
    print-to-screen of signal, bg, signal-bg

This script will assume the tif values are on a 0-4095 scale, and will
    scale as a fraction of 255*x/4095 for output pngs

run as python imageAnalysisTiffBall.py in.tif outPrefix
EDIT: Feb 10, 2017 - JOSH edited from tifToPNG.py to filter pixels
EDIT: Apr 7, 2017 - JOSH edited from imageAnalysisTiff.py to draw a circle around
    each pixel and only include it if the average intensity is above some background
EDIT: May 7, 2017 - JOSH clened up and modified, adding bg subtraction and removing
    extraneous comments and historical items
"""
import sys, numpy, math, copy
import tifffile as tiff
from logJosh import Tee
from PIL import Image
from pyx import *

def getCircle(aa,radius,gCutoff,rCutoff):
    """aa is an image, as read in via tiff.imread. radius is the radius of the circle.
    For each point in the image, will draw a circle around it and calculate the avg
    pixel intensity within that circle. If the pixel intensities are at least
    gCutoff and rCutoff, it'll keep the pixel. Otherwise toss it."""
    bb=copy.copy(aa)
    bgG=[]
    for ii in range(len(aa)):
        if ii%200==0:
            pass#print 'working on row %s of %s ...'%(ii,len(aa))
        col=aa[ii]
        for jj in range(len(col)):
            row=col[jj]
            r,g,b=row
            rTotal=[r]
            gTotal=[g]
            for x in range(jj-radius,jj+radius+1):
                for y in range(ii-radius,ii+radius+1):
                    if ((x-jj)**2+(y-ii)**2)**0.5<=radius:
                        if (0<=y<len(aa) and 0<=x<len(col)):
                            rTotal.append(aa[y][x][0])
                            gTotal.append(aa[y][x][1])
            if (numpy.average(gTotal)>gCutoff and numpy.average(rTotal>rCutoff)):
                bb[ii][jj]=[r,g,b]
            else:
                bgG.append(gTotal[0])
                bb[ii][jj]=[0,0,0]
    return bb, numpy.average(bgG)

def main(args):
    inFile,outPrefix=args[0:]
    #input the file
    aa=tiff.imread(inFile)
    #
    theMin,theMax=0.,4095.
    im=Image.new("RGB",(aa.shape[0:2]))#im is now a blank image of same dimensions as aa
    imFiltered=Image.new("RGB",(aa.shape[0:2]))#ditto wih imFiltered
    filteredG=[]#will keep track of signal values
    bgG=[]#will keep track of bg values
    #circle parameters: radius, gCut,rCut
    bb,bg=getCircle(aa,5,370,350)###this works well for exp1.2 sec
    bg=255*(bg-theMin)/theMax
    #
    ii=0
    for col in bb:
        jj=0
        for row in col:
            r,g,b=row
            r,g,b=255.*(r-theMin)/theMax,255.*(g-theMin)/theMax,255.*(b-theMin)/theMax
            if g>0:
                im.putpixel((ii,jj),(0,int(g),0))
                imFiltered.putpixel((ii,jj),(255,255,255))
                filteredG.append(g)
            else:
                r2,g2,b2=aa[ii][jj]
                g2=255.*(g2-theMin)/theMax
                im.putpixel((ii,jj),(0,int(g2),0))
                bgG.append(g2)
                imFiltered.putpixel((ii,jj),(0,0,0))
            jj+=1
        ii+=1
    im.save(outPrefix+'.png')
    imFiltered.save(outPrefix+'.filtered.png')
    im.save(outPrefix+'.png')
    mu=numpy.average(filteredG)
    bg=numpy.average(bgG)
    print inFile,mu,bg,mu-bg

if __name__=='__main__':
    Tee()
    main(sys.argv[1:])
