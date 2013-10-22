#!/bin/env python

import wx

try:
	from agw import flatmenu as FM
	from agw.artmanager import DCSaver
except ImportError: # if it's not there locally, try the wxPython lib.
	import wx.lib.agw.flatmenu as FM
	from wx.lib.agw.artmanager import DCSaver

# --------------------------------------------------------------------------------------------------
# FlatMenu class
# --------------------------------------------------------------------------------------------------
class FlatMenu(FM.FlatMenu):
	def __init__(self):
		super(FlatMenu, self).__init__()

	# TODO:
	# 1. Make the left margin to round rectangle
	# 2. Make the FlatMenu to round rectangle. FYI: FlatMenu extends wx.Window
	def DrawLeftMargin(self, dc, menuRect):
		"""
		Draws the menu left margin.

		:param `dc`: an instance of `wx.DC`;
		:param `menuRect`: the menu client rectangle.
		"""

		# Construct the margin rectangle
		w = super(FlatMenu, self).GetLeftMarginWidth()
		marginRect = wx.Rect(menuRect.x + 1, menuRect.y, w - 1, menuRect.height)

		dcsaver = DCSaver(dc)
		marginColour = (195, 255, 142)
		dc.SetPen(wx.Pen(marginColour))
		dc.SetBrush(wx.Brush(marginColour))
		dc.DrawRectangleRect(marginRect)
