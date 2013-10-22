#!/bin/env python

import wx
from Utils import *

class AlarmsListBox(wx.VScrolledWindow):
	def __init__(self, parent, pos, size):
		wx.SimpleHtmlListBox.__init__(self, parent, wx.ID_ANY, pos, size, style = wx.NO_BORDER,  name = 'AlarmsListBox')

#class AlarmsListBox(wx.SimpleHtmlListBox):
#	def __init__(self, parent, pos, size):
#		wx.SimpleHtmlListBox.__init__(self, parent, wx.ID_ANY, pos, size, style = wx.NO_BORDER,  name = 'AlarmsListBox')
#
#		self._itemPressed = -1
#
#		self._itemBorderPen = wx.Pen(wx.Colour(204, 225, 198, 255))
#		self._itemBrush = wx.Brush(wx.Colour(188, 249, 188, 255))
#		self._itemPressedBrush = wx.Brush(wx.Colour(207, 251, 207, 255))
#		self._itemPressedBgColor = wx.Colour(147, 245, 147, 255)
#
#		self.SetBackgroundColour(self._itemPressedBgColor)
#		self.SetSelectionBackground(self._itemPressedBgColor)
#
# Missed:
# wxVListBox::Clear
# wxVListBox::Create
# wxVListBox::GetItemCount
#
#	def GetFirstSelected(self):
#		return wx.NOT_FOUND
#
#	def GetNextSelected(self, cookie):
#		return wx.NOT_FOUND
#
#	def GetMargins(self):
#		return wx.Point(5, 5)
#
#	def HasMultipleSelection(self):
#		return False
#
#	def GetSelection(self):
#		return wx.NOT_FOUND
#
#	def GetSelectedCount(self):
#		return 0
#
#	def GetSelectionBackground(self):
#		return self._itemPressedBgColor
#
#	def IsCurrent(self, itemIndex):
#		return self.IsSelected(itemIndex)
#
#	def IsSelected(self, itemIndex):
#		return itemIndex == self._itemPressed
#
#	def SetItemCount(self, count):
#		pass
#
#	def SetSelection(self, itemIndex):
#		super(AlarmsListBox, self).SetSelection(-1)
#
#	def Select(self, itemIndex, select):
#		return False
#
#	def SelectRange(self, fromItemIdx, toItemIdx):
#		return False
#
#	def SelectAll(self):
#		return False
#
#	def DeselectAll(self):
#		return True
#
#	def SetMargins(self, margin):
#		pass
#
#	def SetMarginsXY(self, x, y):
#		pass
#
#	def SetSelectionBackground(self, color):
#		pass
#
#	def Toggle(self, itemIndex):
#		pass
#
#	def OnDrawBackground(self, dc, rect, itemIndex):
#		print 'OnDrawBackground(', dc, rect, itemIndex, ')'
#		if itemIndex == self._itemPressed:
#			dc.SetBrush(self._itemPressedBrush)
#		else:
#			dc.SetBrush(self._itemBrush)
#		dc.SetPen(self._itemBorderPen)
#		dc.DrawRoundedRectangleRect(rect, 5)
#
#	def OnDrawItem(self, dc, rect, itemIndex):
#		print 'OnDrawItem(', dc, rect, itemIndex, ')'
#		# TODO: draw the item
#		dc.SetFont(self.GetFont())
#		dc.SetTextForeground(wx.BLACK)
#		deadline, msg = self.GetAlarm(itemIndex)
#		dc.DrawLabel(msg, rect, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
#
#	def OnDrawSeparator(self, dc, rect, itemIndex):
#		print 'OnDrawSeparator(', dc, rect, itemIndex, ')'
#
#	def OnMeasureItem(self, itemIndex):
#		print 'OnMeasureItem(', itemIndex, ')'
#		# TODO: measure the item's height in pixels
#		return 50
#
#	def AddAlarm(self, deadline, msg):
#		self.Append('<FONT SIZE=4 FACE=Verdana>%s</FONT><BR><FONT SIZE=7 FACE=Verdana>%s</FONT>' % (deadline, msg))
#
#	def DeleteAlarm(self, itemIndex):
#		if itemIndex >= 0 and itemIndex < len(self._items):
#			self.Delete(itemIndex)
#
#	def EditAlarm(self, itemIndex, deadline, msg):
#		if itemIndex >= 0 and itemIndex < len(self._items):
#			self._items[itemIndex] = (deadline, msg)
#
#	def GetAlarm(self, itemIndex):
#		if itemIndex >= 0 and itemIndex < len(self._items):
#			return self.GetString(itemIndex).split('|')
#		return None
