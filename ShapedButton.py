#!/bin/env python

import wx

from Utils import *

# --------------------------------------------------------------------------------------------------
# ShapedButton class
# --------------------------------------------------------------------------------------------------
class ShapedButton(wx.PyControl):
	def __init__(self, parent, normal, pressed = ''):
		super(ShapedButton, self).__init__(parent, wx.ID_ANY, style = wx.BORDER_NONE | wx.TRANSPARENT_WINDOW)
		self.InheritAttributes()

		self.normal = None if len(normal) == 0 else shapedBitmap(normal)
		self.pressed = None if len(pressed) == 0 else shapedBitmap(pressed)
		self.region = wx.RegionFromBitmap(self.normal)
		self._clicked = False
		self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

		w, h = self.normal.GetWidth(), self.normal.GetHeight()
		self.SetClientSize((w, h))

		self.Bind(wx.EVT_PAINT,        self.onPaint)
		self.Bind(wx.EVT_LEFT_DOWN,    self.onLeftDown)
		self.Bind(wx.EVT_LEFT_DCLICK,  self.onLeftDClick)
		self.Bind(wx.EVT_LEFT_UP,      self.onLeftUp)
		self.Bind(wx.EVT_MOTION,       self.OnMouseMove)
		self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

	def DoGetBestSize(self):
		return self.normal.GetSize()

	def postEvent(self):
		event = wx.CommandEvent()
		event.SetEventObject(self)
		event.SetEventType(wx.EVT_BUTTON.typeId)
		wx.PostEvent(self, event)

	def onPaint(self, event):
		bitmap = self.normal
		if self.clicked:
			bitmap = self.pressed or bitmap

		# TODO: If the bitmaps of the button have different shapes, it is necessary to clear
		# the background before draw concrete bitmap
		# clearDc(dc, bitmap)

		dc = wx.PaintDC(self)
		dc.DrawBitmap(bitmap, 0, 0, True)

	def setClicked(self, clicked):
		if clicked != self._clicked:
			self._clicked = clicked
			self.Refresh()

	def getClicked(self):
		return self._clicked

	clicked = property(getClicked, setClicked)

	def onLeftDown(self, event):
		x, y = event.GetPosition()
		if self.region.Contains(x, y):
			self.clicked = True

	def onLeftDClick(self, event):
		self.onLeftDown(event)

	def onLeftUp(self, event):
		if self.clicked:
			x, y = event.GetPosition()
			if self.region.Contains(x, y):
				self.postEvent()
		self.clicked = False

	def OnMouseMove(self, event):
		if self.clicked:
			x, y = event.GetPosition()
			if not self.region.Contains(x, y):
				self.clicked = False

	def OnLeaveWindow(self, event):
		self.clicked = False
