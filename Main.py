#!/bin/env python

import os, wx

try:
	from agw import flatmenu as FM
except ImportError: # if it's not there locally, try the wxPython lib.
	import wx.lib.agw.flatmenu as FM

from Utils import *
from FlatMenu import FlatMenu
from ShapedButton import ShapedButton
from AlarmsListBox import *

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

# Keys
NONE_SELECTED    = 10
ALARMS_SELECTED  = 11
SETTING_SELECTED = 12
ABOUT_SELECTED   = 13
BG_BITMAP = 20
ALARMS    = 21
SETTING   = 22
ABOUT     = 23

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
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

		icon = wx.IconFromBitmap(shapedBitmap('app.png'))
		self.SetIcon(icon)

		if setTaskBarIcon:
			try:
				self.tbicon = TaskBarIcon(self)
			except:
				self.tbicon = None

		self._bginfo = {
			ALARMS_SELECTED : {
				BG_BITMAP: shapedBitmap('main_frame_bg_alarms_selected.png'),
				ALARMS: wx.RegionFromPoints([wx.Point(0, 80), wx.Point(80, 0), wx.Point(226, 0), wx.Point(244, 18), wx.Point(244, 80), wx.Point(0, 80)]),
				SETTING: wx.RegionFromPoints([wx.Point(244, 80), wx.Point(244, 45), wx.Point(283, 5), wx.Point(430, 5), wx.Point(447, 23), wx.Point(447, 80), wx.Point(244, 80)]),
				ABOUT: wx.RegionFromPoints([wx.Point(447, 80), wx.Point(447, 49), wx.Point(491, 5), wx.Point(638, 5), wx.Point(655, 23), wx.Point(655, 80), wx.Point(447, 80)]),
			},
			SETTING_SELECTED : {
				BG_BITMAP: shapedBitmap('main_frame_bg_setting_selected.png'),
				ALARMS: wx.RegionFromPoints([wx.Point(0, 80), wx.Point(75, 5), wx.Point(222, 5), wx.Point(239, 23), wx.Point(239, 49), wx.Point(208, 80), wx.Point(0, 80)]),
				SETTING: wx.RegionFromPoints([wx.Point(208, 80), wx.Point(288, 0), wx.Point(434, 0), wx.Point(452, 18), wx.Point(452, 80), wx.Point(208, 80)]),
				ABOUT: wx.RegionFromPoints([wx.Point(452, 80), wx.Point(452, 45), wx.Point(491, 5), wx.Point(638, 5), wx.Point(655, 23), wx.Point(655, 80), wx.Point(452, 80)]),
			},
			ABOUT_SELECTED : {
				BG_BITMAP: shapedBitmap('main_frame_bg_about_selected.png'),
				ALARMS: wx.RegionFromPoints([wx.Point(0, 80), wx.Point(75, 5), wx.Point(222, 5), wx.Point(239, 23), wx.Point(239, 49), wx.Point(208, 80), wx.Point(0, 80)]),
				SETTING: wx.RegionFromPoints([wx.Point(208, 80), wx.Point(283, 5), wx.Point(430, 5), wx.Point(447, 23), wx.Point(447, 49), wx.Point(416, 80), wx.Point(208, 80)]),
				ABOUT: wx.RegionFromPoints([wx.Point(416, 80), wx.Point(496, 0), wx.Point(642, 0), wx.Point(660, 18), wx.Point(660, 80), wx.Point(416, 80)]),
			},
		}
		self._tab_selected = ALARMS_SELECTED

		self.SetClientSize((800, 600))
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
		dc.DrawBitmap(self._bginfo[self._tab_selected][BG_BITMAP], 0, 0, True)

		self.AddTitleBarButton('minimize_btn', self.onMinimizeBtnPressed, wx.Point(670, 17))
		self.AddTitleBarButton('close_btn', self.onCloseBtnPressed, wx.Point(735, 17))

		self._alarmsList = AlarmsListBox(self, wx.Point(10, 90), wx.Size(780, 500))
		for i in range(20):
			self._alarmsList.AddAlarm('20131015 10:%02d:01' % (i), 'Tet Test %d' % (i))

	def AddTitleBarButton(self, basePicName, cmdFun, pos):
		btn = ShapedButton(self, basePicName + '.png', basePicName + '_pressed.png')
		btn.Bind(wx.EVT_BUTTON, cmdFun)
		btn.SetPosition(pos)
		return btn

	def SetWindowShape(self, *evt):
		# Use the bitmap's mask to determine the region
		r = wx.RegionFromBitmap(self._bginfo[self._tab_selected][BG_BITMAP])
		self.hasShape = self.SetShape(r)

	def OnPaint(self, evt):
		dc = wx.PaintDC(self)
		dc.DrawBitmap(self._bginfo[self._tab_selected][BG_BITMAP], 0, 0, True)
#		self._alarmsList.Refresh()

	def OnEraseBackground(self, evt):
		"""
		This method is intentionally empty to reduce flicker.
		"""
		pass

	def OnLeftDown(self, evt):
		self.CaptureMouse()
		x, y = self.ClientToScreen(evt.GetPosition())
		originx, originy = self.GetPosition()
		dx = x - originx
		dy = y - originy
		self.delta = ((dx, dy))
		self._needHitTest = True

	def OnLeftUp(self, evt):
		if self.HasCapture():
			self.ReleaseMouse()

			if self._needHitTest:
				hitZone = self.HitTest(evt.GetPosition())
				if hitZone != self._tab_selected and hitZone != NONE_SELECTED:
					self._tab_selected = hitZone
					self.SetWindowShape()
					self.Refresh()

	def OnMouseMove(self, evt):
		if evt.Dragging() and evt.LeftIsDown() and self.HasCapture():
			x, y = self.ClientToScreen(evt.GetPosition())
			fp = (x - self.delta[0], y - self.delta[1])
			self.Move(fp)
			self._needHitTest = False

	def onMinimizeBtnPressed(self, evt):
		self.Iconize()

	def onCloseBtnPressed(self, evt):
		self.Close(True)

	def HitTest(self, pos):
		if self._bginfo[self._tab_selected][ALARMS].Contains(pos.x, pos.y):
			return ALARMS_SELECTED
		elif self._bginfo[self._tab_selected][SETTING].Contains(pos.x, pos.y):
			return SETTING_SELECTED
		elif self._bginfo[self._tab_selected][ABOUT].Contains(pos.x, pos.y):
			return ABOUT_SELECTED
		return NONE_SELECTED

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
