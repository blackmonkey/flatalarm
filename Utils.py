#!/bin/env python

import os, wx

def opj(path):
	"""Convert paths to the platform-specific separator"""
	st = apply(os.path.join, tuple(path.split('/')))
	# HACK: on Linux, a leading / gets lost...
	if path.startswith('/'):
		st = '/' + st
	return st

def shapedImage(fname):
	img = wx.Image(os.path.join('images', fname))
	img.ConvertAlphaToMask(1)
	return img

def shapedBitmap(fname):
	img = shapedImage(fname)
	return wx.BitmapFromImage(img)

def clearDc(dc, bitmap = None):
	try:
		gcdc = wx.GCDC(dc)
	except:
		gcdc = dc

	dc.SetBrush(wx.TRANSPARENT_BRUSH)
	gcdc.SetBrush(wx.TRANSPARENT_BRUSH)
	gcdc.SetBackgroundMode(wx.TRANSPARENT)

	# The background needs some help to look transparent on Gtk and Windows
	if wx.Platform in ['__WXGTK__', '__WXMSW__']:
		gcdc.SetBackground(wx.TRANSPARENT_BRUSH)
		gcdc.Clear()

	if bitmap:
		gcdc.DrawBitmap(bitmap, 0, 0, True)
