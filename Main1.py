#!/bin/env python

import os, wx

try:
	from agw import flatmenu as FM
except ImportError: # if it's not there locally, try the wxPython lib.
	import wx.lib.agw.flatmenu as FM

from Utils import *
from FlatNoteBook import FlatNotebook
from FlatMenu import FlatMenu
from ShapedButton import ShapedButton

import inspect
from pprint import pprint
from wx.lib.eventwatcher import EventWatcher

# Editor bgcolor(RGBA): c3ff8eff
# Editor border(RGBA): 21361cff, 1px

# --------------------------------------------------------------------------------------------------
# Global Variables
# --------------------------------------------------------------------------------------------------

APP_TITLE = 'Flat Alarm'

CLIENT_BGCOLOR = wx.Colour(177, 247, 177, 255)
TEXT_COLOR = wx.BLACK
BORDER_COLOR = wx.Colour(65, 107, 56, 255)
TAB_SEL_BGCOLOR = CLIENT_BGCOLOR
TAB_NOSEL_BGCOLOR = wx.Colour(107, 255, 107, 255)
PRESSED_BGCOLOR = wx.Colour(0, 202, 0, 255)

# --------------------------------------------------------------------------------------------------
# TaskBarIcon class
# --------------------------------------------------------------------------------------------------
class TaskBarIcon(wx.TaskBarIcon):
	TBMENU_RESTORE = wx.NewId()
	TBMENU_CLOSE   = wx.NewId()

	def __init__(self, frame):
		wx.TaskBarIcon.__init__(self)
		self.frame = frame

		self._popUpMenu = None
		self.popUpX = 0
		self.popUpY = 0

		# Set the image
		icon = self.MakeIcon()
		self.SetIcon(icon, APP_TITLE)

		# bind some events
		self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarActivate)
		self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnTaskBarActivate, id = self.TBMENU_RESTORE)
		self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnTaskBarClose, id = self.TBMENU_CLOSE)

	def CreatePopupMenu(self):
		"""
		This method is called by the base class when it needs to popup
		the menu for the default EVT_RIGHT_DOWN event.  Just create
		the menu how you want it and return it from this function,
		the base class takes care of the rest.
		"""
		if not self._popUpMenu:
			self._popUpMenu = FlatMenu()
			self._popUpMenu.Append(self.TBMENU_RESTORE, 'Restore ' + APP_TITLE)
			self._popUpMenu.Append(self.TBMENU_CLOSE,   'Exit ' + APP_TITLE)

		self._popUpMenu.Popup(wx.GetMousePosition(), self)
		return None

	def MakeIcon(self):
		"""
		The various platforms have different requirements for the
		icon size...
		"""
		img = shapedImage('app.png')
		if 'wxMSW' in wx.PlatformInfo:
			img = img.Scale(16, 16)
		elif 'wxGTK' in wx.PlatformInfo:
			img = img.Scale(22, 22)
		# wxMac can be any size upto 128x128, so leave the source img alone....
		icon = wx.IconFromBitmap(wx.BitmapFromImage(img))
		return icon

	def GetEventHandler(self):
		"""
		This method is called by the FlatMenu class when it needs to
		send FM.EVT_FLAT_MENU_SELECTED event.
		"""
		return self

	def OnTaskBarActivate(self, evt):
		if self.frame:
			if self.frame.IsIconized():
				self.frame.Iconize(False)
			if not self.frame.IsShown():
				self.frame.Show(True)
			self.frame.Raise()
		else:
			self.frame = MainFrame(False)
			self.frame.Show()

	def OnTaskBarClose(self, evt):
		if self.frame and self.frame.IsShown():
			wx.CallAfter(self.frame.Destroy)
		self.Destroy()

# --------------------------------------------------------------------------------------------------
# MainFrame class
# --------------------------------------------------------------------------------------------------
class MainFrame(wx.Frame):
	def __init__(self, setTaskBarIcon = True):
		wx.Frame.__init__(self, None, wx.ID_ANY, APP_TITLE, style = wx.FRAME_SHAPED | wx.SIMPLE_BORDER)

		self.hasShape = False
		self.delta = (0, 0)

		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		self.Bind(wx.EVT_LEFT_UP,   self.OnLeftUp)
		self.Bind(wx.EVT_MOTION,    self.OnMouseMove)
		self.Bind(wx.EVT_PAINT,     self.OnPaint)

		self.bmp = shapedBitmap('main_frame_bg.png')
		frameW, frameH = self.bmp.GetWidth(), self.bmp.GetHeight()
		self.SetClientSize((frameW, frameH))

		icon = wx.IconFromBitmap(shapedBitmap('app.png'))
		self.SetIcon(icon)

		if setTaskBarIcon:
			try:
				self.tbicon = TaskBarIcon(self)
			except:
				self.tbicon = None

		self.Centre(wx.BOTH)

		if wx.Platform == "__WXGTK__":
			# wxGTK requires that the window be created before you can
			# set its shape, so delay the call to SetWindowShape until
			# this event.
			self.Bind(wx.EVT_WINDOW_CREATE, self.SetWindowShape)
		else:
			# On wxMSW and wxMac the window has already been created, so go for it.
			self.SetWindowShape()

		dc = wx.ClientDC(self)
		dc.DrawBitmap(self.bmp, 0, 0, True)

		book = FlatNotebook(self)
		self.AddPage(book, 'Alarms')
		self.AddPage(book, 'Settings')
		self.AddPage(book, 'About')
		book.SetPosition((10, 10))
		book.SetClientSize((frameW - 20, frameH - 20))

		rect = book.GetHeaderRect()
		rect.x = rect.y = 10
		book.SetHeaderBackground(self.bmp.GetSubBitmap(rect))

		closeBtn = ShapedButton(self, 'close_btn.png', 'close_btn_pressed.png')
		closeBtn.Bind(wx.EVT_BUTTON, self.onCloseBtnPressed)
		btnW, btnH = closeBtn.GetSize()
		closeBtnLeft = frameW - 7.5 - btnW
		closeBtn.SetPosition((closeBtnLeft, 7.5))

		minimizeBtn = ShapedButton(self, 'minimize_btn.png', 'minimize_btn_pressed.png')
		minimizeBtn.Bind(wx.EVT_BUTTON, self.onMinimizeBtnPressed)
		btnW, btnH = minimizeBtn.GetSize()
		minimizeBtn.SetPosition((closeBtnLeft - 5 - btnW, 7.5))

	def AddPage(self, book, caption):
		p = wx.Panel(book, name=caption)
		p.SetBackgroundColour(CLIENT_BGCOLOR)
		wx.StaticText(p, wx.ID_ANY, caption, (20,20))
		wx.TextCtrl(p, wx.ID_ANY, '', (20,40), (150,-1))
		book.AddPage(p, caption)
		return p

	def SetWindowShape(self, *evt):
		# Use the bitmap's mask to determine the region
		r = wx.RegionFromBitmap(self.bmp)
		self.hasShape = self.SetShape(r)

	def OnPaint(self, evt):
		dc = wx.PaintDC(self)
		dc.DrawBitmap(self.bmp, 0, 0, True)

	def OnLeftDown(self, evt):
		self.CaptureMouse()
		x, y = self.ClientToScreen(evt.GetPosition())
		originx, originy = self.GetPosition()
		dx = x - originx
		dy = y - originy
		self.delta = ((dx, dy))

	def OnLeftUp(self, evt):
		if self.HasCapture():
			self.ReleaseMouse()

	def OnMouseMove(self, evt):
		if evt.Dragging() and evt.LeftIsDown() and self.HasCapture():
			x, y = self.ClientToScreen(evt.GetPosition())
			fp = (x - self.delta[0], y - self.delta[1])
			self.Move(fp)

	def onMinimizeBtnPressed(self, evt):
		self.Iconize()

	def onCloseBtnPressed(self, evt):
		self.Close(True)

# --------------------------------------------------------------------------------------------------
# FlatAlarmApp class
# --------------------------------------------------------------------------------------------------
class FlatAlarmApp(wx.App):
	def OnInit(self):

		# Create and show the splash screen.  It will then create and show
		# the main frame when it is time to do so.
		wx.SystemOptions.SetOptionInt("mac.window-plain-transition", 1)
		self.SetAppName("FlatAlarm")

		# For debugging
		#self.SetAssertMode(wx.PYAPP_ASSERT_DIALOG)

		frame = MainFrame()
		frame.Show()

		return True

# --------------------------------------------------------------------------------------------------
# main entry
# --------------------------------------------------------------------------------------------------
def main():
	try:
		appPath = os.path.dirname(__file__)
		os.chdir(appPath)
	except:
		pass
	app = FlatAlarmApp(False)
	app.MainLoop()

if __name__ == '__main__':
	__name__ = 'Main'
	main()
