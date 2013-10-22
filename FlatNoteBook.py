"""
FlatNotebook is a full, generic and owner-drawn implementation of `wx.Notebook`.


Description
===========

The FlatNotebook is a full implementation of the `wx.Notebook`, and designed to be
a drop-in replacement for `wx.Notebook`. The API functions are similar so one can
expect the function to behave in the same way.

Some features:

- The scrolling is done for bulks of tabs (so, the scrolling is faster and better);
- The buttons area is never overdrawn by tabs (unlike many other implementations I saw);
- It is a generic control;
- Currently there is only builtin style - VC8;
- Colours for active/inactive tabs, and captions;

And much more.


Window Styles
=============

This class supports the following window styles:

================================ =========== ==================================================
Window Styles                    Hex Value   Description
================================ =========== ==================================================
``FNB_VC8``                            0x100 Use Visual Studio 2005 (VC8) style for tabs.
================================ =========== ==================================================


Events Processing
=================

This class processes the following events:

========================================= ==================================================
Event Name                                Description
========================================= ==================================================
``EVT_FLATNOTEBOOK_PAGE_CHANGED``         Notify client objects when the active page in `FlatNotebook` has changed.
``EVT_FLATNOTEBOOK_PAGE_CHANGING``        Notify client objects when the active page in `FlatNotebook` is about to change.
========================================= ==================================================


Version
===================
Latest Revision: Andrea Gavana @ 21 Apr 2010, 21.00 GMT
"""

__docformat__ = "epytext"


#----------------------------------------------------------------------
# Beginning Of FLATNOTEBOOK wxPython Code
#----------------------------------------------------------------------

import wx
import wx.lib.colourutils as colourutils
import random
import math
import weakref
import cPickle

from Utils import *

# Used on OSX to get access to carbon api constants
if wx.Platform == '__WXMAC__':
	import Carbon.Appearance

# Check for the new method in 2.7 (not present in 2.6.3.3)
if wx.VERSION_STRING < "2.7":
	wx.Rect.Contains = lambda self, point: wx.Rect.Inside(self, point)

FNB_HEIGHT_SPACER = 10

# Use Visual Studio 2005 (VC8) style for tabs
FNB_VC8 = 256
"""Use Visual Studio 2005 (VC8) style for tabs"""

VERTICAL_BORDER_PADDING = 4

# Button status
FNB_BTN_NONE = 0
"""No navigation"""

# Hit Test results
FNB_TAB = 1             # On a tab
"""Indicates mouse coordinates inside a tab"""
FNB_NOWHERE = 0         # Anywhere else
"""Indicates mouse coordinates not on any tab of the notebook"""

# FlatNotebook Events:
# wxEVT_FLATNOTEBOOK_PAGE_CHANGED: Event Fired When You Switch Page;
# wxEVT_FLATNOTEBOOK_PAGE_CHANGING: Event Fired When You Are About To Switch
# Pages, But You Can Still "Veto" The Page Changing By Avoiding To Call
# event.Skip() In Your Event Handler;

wxEVT_FLATNOTEBOOK_PAGE_CHANGED = wx.wxEVT_COMMAND_NOTEBOOK_PAGE_CHANGED
wxEVT_FLATNOTEBOOK_PAGE_CHANGING = wx.wxEVT_COMMAND_NOTEBOOK_PAGE_CHANGING

#-----------------------------------#
#        FlatNotebookEvent
#-----------------------------------#

EVT_FLATNOTEBOOK_PAGE_CHANGED = wx.EVT_NOTEBOOK_PAGE_CHANGED
""" Notify client objects when the active page in `FlatNotebook` has changed."""
EVT_FLATNOTEBOOK_PAGE_CHANGING = wx.EVT_NOTEBOOK_PAGE_CHANGING
""" Notify client objects when the active page in `FlatNotebook` is about to change."""

def LightColour(colour, percent):
	"""
	Brighten the input colour by a percentage.

	:param `colour`: a valid `wx.Colour` instance;
	:param `percent`: the percentage by which the input colour should be brightened.
	"""

	end_colour = wx.WHITE

	rd = end_colour.Red() - colour.Red()
	gd = end_colour.Green() - colour.Green()
	bd = end_colour.Blue() - colour.Blue()

	high = 100

	# We take the percent way of the colour from colour -. white
	i = percent
	r = colour.Red() + ((i*rd*100)/high)/100
	g = colour.Green() + ((i*gd*100)/high)/100
	b = colour.Blue() + ((i*bd*100)/high)/100
	return wx.Colour(r, g, b)

def PaintStraightGradientBox(dc, rect, startColour, endColour, vertical=True):
	"""
	Draws a gradient coloured box from `startColour` to `endColour`.

	:param `dc`: an instance of `wx.DC`;
	:param `rect`: the rectangle to fill with the gradient shading;
	:param `startColour`: the first colour in the gradient shading;
	:param `endColour`: the last colour in the gradient shading;
	:param `vertical`: ``True`` if the gradient shading is north to south, ``False``
	 if it is east to west.
	"""

	rd = endColour.Red() - startColour.Red()
	gd = endColour.Green() - startColour.Green()
	bd = endColour.Blue() - startColour.Blue()

	# Save the current pen and brush
	savedPen = dc.GetPen()
	savedBrush = dc.GetBrush()

	if vertical:
		high = rect.GetHeight()-1
	else:
		high = rect.GetWidth()-1

	if high < 1:
		return

	for i in xrange(high+1):

		r = startColour.Red() + ((i*rd*100)/high)/100
		g = startColour.Green() + ((i*gd*100)/high)/100
		b = startColour.Blue() + ((i*bd*100)/high)/100

		p = wx.Pen(wx.Colour(r, g, b))
		dc.SetPen(p)

		if vertical:
			dc.DrawLine(rect.x, rect.y+i, rect.x+rect.width, rect.y+i)
		else:
			dc.DrawLine(rect.x+i, rect.y, rect.x+i, rect.y+rect.height)

	# Restore the pen and brush
	dc.SetPen(savedPen)
	dc.SetBrush(savedBrush)




# ---------------------------------------------------------------------------- #
# Class PageInfo
# Contains parameters for every FlatNotebook page
# ---------------------------------------------------------------------------- #

class PageInfo(object):
	"""
	This class holds all the information (caption, etc...) belonging to a
	single tab in L{FlatNotebook}.
	"""

	def __init__(self, caption=''):
		"""
		Default Class Constructor.

		:param `caption`: the tab caption;
		:param `tabangle`: the tab angle (only on standard tabs, from 0 to 15
		 degrees);
		"""

		self._strCaption = caption
		self._pos = wx.Point(-1, -1)
		self._size = wx.Size(-1, -1)
		self._region = wx.Region()
		self._colour = None
		self._hasFocus = False
		self._pageTextColour = None

	def SetCaption(self, value):
		"""
		Sets the tab caption.

		:param `value`: the new tab caption string.
		"""

		self._strCaption = value

	def GetCaption(self):
		""" Returns the tab caption. """

		return self._strCaption

	def SetPosition(self, value):
		"""
		Sets the tab position.

		:param `value`: an instance of `wx.Point`.
		"""

		self._pos = value

	def GetPosition(self):
		""" Returns the tab position. """

		return self._pos

	def SetSize(self, value):
		"""
		Sets the tab size.

		:param `value`: an instance of `wx.Size`.
		"""

		self._size = value

	def GetSize(self):
		""" Returns the tab size. """

		return self._size

	def GetPageTextColour(self):
		"""
		Returns the tab text colour if it has been set previously, or ``None``
		otherwise.
		"""

		return self._pageTextColour

	def SetPageTextColour(self, colour):
		"""
		Sets the tab text colour for this tab.

		:param `colour`: an instance of `wx.Colour`. You can pass ``None`` or
		 `wx.NullColour` to return to the default page text colour.
		"""

		if colour is None or not colour.IsOk():
			self._pageTextColour = None
		else:
			self._pageTextColour = colour

	def SetRegion(self, points=[]):
		"""
		Sets the tab region.

		:param `points`: a Python list of `wx.Points`
		"""

		self._region = wx.RegionFromPoints(points)

	def GetRegion(self):
		""" Returns the tab region. """

		return self._region

	def GetColour(self):
		""" Returns the tab colour. """

		return self._colour

	def SetColour(self, colour):
		"""
		Sets the tab colour.

		:param `colour`: a valid `wx.Colour` object.
		"""

		self._colour = colour

# ---------------------------------------------------------------------------- #
# Class FlatNotebookEvent
# ---------------------------------------------------------------------------- #

class FlatNotebookEvent(wx.PyCommandEvent):
	"""
	This events will be sent when a ``EVT_FLATNOTEBOOK_PAGE_CHANGED``,
	``EVT_FLATNOTEBOOK_PAGE_CHANGING`` is mapped in the parent.
	"""

	def __init__(self, eventType, eventId=1, nSel=-1, nOldSel=-1):
		"""
		Default class constructor.

		:param `eventType`: the event type;
		:param `eventId`: the event identifier;
		:param `nSel`: the current selection;
		:param `nOldSel`: the old selection.
		"""

		wx.PyCommandEvent.__init__(self, eventType, eventId)
		self._eventType = eventType

		self.notify = wx.NotifyEvent(eventType, eventId)

	def GetNotifyEvent(self):
		""" Returns the actual `wx.NotifyEvent`. """

		return self.notify

	def IsAllowed(self):
		"""
		Returns ``True`` if the change is allowed (L{Veto} hasn't been called) or
		``False`` otherwise (if it was).
		"""

		return self.notify.IsAllowed()

	def Veto(self):
		"""
		Prevents the change announced by this event from happening.

		:note: It is in general a good idea to notify the user about the reasons
		 for vetoing the change because otherwise the applications behaviour (which
		 just refuses to do what the user wants) might be quite surprising.
		"""

		self.notify.Veto()

	def Allow(self):
		"""
		This is the opposite of L{Veto}: it explicitly allows the event to be processed.
		For most events it is not necessary to call this method as the events are
		allowed anyhow but some are forbidden by default (this will be mentioned
		in the corresponding event description).
		"""

		self.notify.Allow()

	def SetSelection(self, nSel):
		"""
		Sets the event selection.

		:param `nSel`: an integer specifying the new selection.
		"""

		self._selection = nSel

	def SetOldSelection(self, nOldSel):
		"""
		Sets the id of the page selected before the change.

		:param `nOldSel`: an integer specifying the old selection.
		"""

		self._oldselection = nOldSel

	def GetSelection(self):
		""" Returns the currently selected page, or -1 if none was selected. """

		return self._selection

	def GetOldSelection(self):
		""" Returns the page that was selected before the change, -1 if none was selected. """

		return self._oldselection

# ---------------------------------------------------------------------------- #
# Class FNBRenderer
# ---------------------------------------------------------------------------- #

class FNBRenderer(object):
	"""
	Parent class for the defined renderer: `VC8`. This class implements the
	common methods of all renderers.
	"""

	def __init__(self):
		""" Default class constructor. """

		self._tabHeight = None

		if wx.Platform == "__WXMAC__":
			# Get proper highlight colour for focus rectangle from the
			# current Mac theme.  kThemeBrushFocusHighlight is
			# available on Mac OS 8.5 and higher
			if hasattr(wx, 'MacThemeColour'):
				c = wx.MacThemeColour(Carbon.Appearance.kThemeBrushFocusHighlight)
			else:
				brush = wx.Brush(wx.BLACK)
				brush.MacSetTheme(Carbon.Appearance.kThemeBrushFocusHighlight)
				c = brush.GetColour()
			self._focusPen = wx.Pen(c, 2, wx.SOLID)
		else:
			self._focusPen = wx.Pen(wx.BLACK, 1, wx.USER_DASH)
			self._focusPen.SetDashes([1, 1])
			self._focusPen.SetCap(wx.CAP_BUTT)

	def DrawTabsLine(self, pageContainer, dc):
		"""
		Draws a line over the tabs.

		:param `pageContainer`: an instance of L{FlatNotebook};
		:param `dc`: an instance of `wx.DC`;
		"""

		pc = pageContainer
		clntRect = pc.GetClientRect()

		dc.SetPen(wx.Pen(pc.GetSingleLineBorderColour()))
		dc.DrawLine(0, clntRect.height - 1, clntRect.width, clntRect.height - 1)
		dc.DrawLine(0, clntRect.height - 2, clntRect.width, clntRect.height - 2)

		dc.SetPen(wx.Pen(wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNSHADOW)))
		dc.DrawLine(0, clntRect.height - 3, clntRect.width, clntRect.height - 3)

	def CalcTabWidth(self, pageContainer, tabIdx, tabHeight):
		"""
		Calculates the width of the input tab.

		:param `pageContainer`: an instance of L{FlatNotebook};
		:param `tabIdx`: the index of the input tab;
		:param `tabHeight`: the height of the tab.
		"""

		pc = pageContainer
		dc = wx.MemoryDC()
		dc.SelectObject(wx.EmptyBitmap(1,1))

		boldFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
		boldFont.SetWeight(wx.FONTWEIGHT_BOLD)

		# Calculate the text length using the bold font, so when selecting a tab
		# its width will not change
		dc.SetFont(boldFont)
		width, pom = dc.GetTextExtent(pc.GetPageText(tabIdx))

		# Set a minimum size to a tab
		if width < 20:
			width = 20

		tabWidth = 2*pc._pParent.GetPadding() + width
		return tabWidth

	def CalcTabHeight(self, pageContainer):
		"""
		Calculates the height of the input tab.

		:param `pageContainer`: an instance of L{FlatNotebook}.
		"""

		if self._tabHeight:
			return self._tabHeight

		pc = pageContainer
		dc = wx.MemoryDC()
		dc.SelectObject(wx.EmptyBitmap(1,1))

		# For GTK it seems that we must do this steps in order
		# for the tabs will get the proper height on initialization
		# on MSW, preforming these steps yields wierd results
		normalFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
		boldFont = normalFont

		if "__WXGTK__" in wx.PlatformInfo:
			boldFont.SetWeight(wx.FONTWEIGHT_BOLD)
			dc.SetFont(boldFont)

		height = dc.GetCharHeight()

		tabHeight = height + FNB_HEIGHT_SPACER # We use 8 pixels as padding
		if "__WXGTK__" in wx.PlatformInfo:
			# On GTK the tabs are should be larger
			tabHeight += 6

		self._tabHeight = tabHeight
		return tabHeight

	def DrawFocusRectangle(self, dc, pageContainer, page):
		"""
		Draws a focus rectangle like the native `wx.Notebooks`.

		:param `dc`: an instance of `wx.DC`;
		:param `pageContainer`: an instance of L{FlatNotebook};
		:param `page`: an instance of L{PageInfo}, representing a page in the notebook.
		"""

		if not page._hasFocus:
			return

		tabPos = wx.Point(*page.GetPosition())
		vc8ShapeLen = self.CalcTabHeight(pageContainer) - VERTICAL_BORDER_PADDING - 2
		tabPos.x += vc8ShapeLen

		rect = wx.RectPS(tabPos, page.GetSize())
		rect = wx.Rect(rect.x+2, rect.y+2, rect.width-4, rect.height-8)

		if wx.Platform == '__WXMAC__':
			rect.SetWidth(rect.GetWidth() + 1)

		dc.SetBrush(wx.TRANSPARENT_BRUSH)
		dc.SetPen(self._focusPen)
		dc.DrawRoundedRectangleRect(rect, 2)


# ---------------------------------------------------------------------------- #
# Class FNBRendererMgr
# A manager that handles all the renderers defined below and calls the
# appropriate one when drawing is needed
# ---------------------------------------------------------------------------- #

class FNBRendererMgr(object):
	"""
	This class represents a manager that handles all the 4 renderers defined
	and calls the appropriate one when drawing is needed.
	"""

	def __init__(self):
		""" Default class constructor. """

		# register renderers

		self._renderers = {}
		self._renderers.update({FNB_VC8: FNBRendererVC8()})

	def GetRenderer(self, style):
		"""
		Returns the current renderer based on the style selected.

		:param `style`: represents one of the 4 implemented styles for L{FlatNotebook},
		 namely one of these bits:

		 ===================== ========= ======================
		 Tabs style            Hex Value Description
		 ===================== ========= ======================
		 ``FNB_VC8``               0x100 Use Visual Studio 2005 (VC8) style for tabs
		 ===================== ========= ======================

		"""

		# the default is to return the VC8 renderer
		return self._renderers[FNB_VC8]

#------------------------------------------------------------------
# Visual studio 2005 (VS8)
#------------------------------------------------------------------
class FNBRendererVC8(FNBRenderer):
	"""
	This class handles the drawing of tabs using the `VC8` renderer.
	"""

	def __init__(self):
		""" Default class constructor. """

		FNBRenderer.__init__(self)
		self._first = True
		self._factor = 1

	def DrawTabs(self, pageContainer, dc):
		"""
		Draws all the tabs using VC8 style.

		:param `pageContainer`: an instance of L{FlatNotebook};
		:param `dc`: an instance of `wx.DC`.
		"""

		pc = pageContainer

		bitmap = pc.GetHeaderBackground()
		if bitmap:
			dc.DrawBitmap(bitmap, 0, 0, True)

		if "__WXMAC__" in wx.PlatformInfo:
			# Works well on MSW & GTK, however this lines should be skipped on MAC
			if not pc._pagesInfoVec or pc._nFrom >= len(pc._pagesInfoVec):
				pc.Hide()
				return

		# Get the text hight
		tabHeight = self.CalcTabHeight(pageContainer)

		# Set the font for measuring the tab height
		normalFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
		boldFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
		boldFont.SetWeight(wx.FONTWEIGHT_BOLD)

		# Set the maximum client size
		pc.SetSizeHints(0, tabHeight)
		borderPen = wx.Pen(wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNSHADOW))

		# Create brushes
		noselBrush = wx.Brush(wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNFACE))
		selBrush = wx.Brush(pc._activeTabColour)
		size = pc.GetSize()

		# We always draw the bottom/upper line of the tabs regradless the style
		self.DrawTabsLine(pc, dc)

		# Restore the pen
		dc.SetPen(borderPen)

		# Draw labels
		dc.SetFont(boldFont)

		# Background
		dc.SetTextBackground(pc.GetBackgroundColour())
		dc.SetTextForeground(pc._activeTextColour)

		# Update all the tabs from 0 to 'pc.self._nFrom' to be non visible
		for i in xrange(pc._nFrom):
			pc._pagesInfoVec[i].SetPosition(wx.Point(-1, -1))
			pc._pagesInfoVec[i].GetRegion().Clear()

		# Draw the visible tabs, in VC8 style, we draw them from right to left
		vTabsInfo = self.NumberTabsCanFit(pc)

		activeTabPosx = 0
		activeTabWidth = 0
		activeTabHeight = 0

		for cur in xrange(len(vTabsInfo)-1, -1, -1):
			# 'i' points to the index of the currently drawn tab
			# in pc.GetPageInfoVector() vector
			i = pc._nFrom + cur
			dc.SetPen(borderPen)
			dc.SetBrush((i==pc.GetSelection() and [selBrush] or [noselBrush])[0])

			# Now set the font to the correct font
			dc.SetFont((i==pc.GetSelection() and [boldFont] or [normalFont])[0])

			# Add the padding to the tab width
			# Tab width:
			# +--------------------------+
			# | PADDING | TEXT | PADDING |
			# +--------------------------+

			tabWidth = self.CalcTabWidth(pageContainer, i, tabHeight)
			posx = vTabsInfo[cur].x

			# By default we clean the tab region
			# incase we use the VC8 style which requires
			# the region, it will be filled by the function
			# drawVc8Tab
			pc._pagesInfoVec[i].GetRegion().Clear()

			# Draw the tab
			# Incase we are drawing the active tab
			# we need to redraw so it will appear on top of all other tabs

			# when using the vc8 style, we keep the position of the active tab so we will draw it again later
			if i == pc.GetSelection():
				activeTabPosx = posx
				activeTabWidth = tabWidth
				activeTabHeight = tabHeight
			else:
				self.DrawTab(pc, dc, posx, i, tabWidth, tabHeight)

			# Restore the text forground
			dc.SetTextForeground(pc._activeTextColour)

			# Update the tab position & size
			pc._pagesInfoVec[i].SetPosition(wx.Point(posx, VERTICAL_BORDER_PADDING))
			pc._pagesInfoVec[i].SetSize(wx.Size(tabWidth, tabHeight))

		# Incase we are in VC8 style, redraw the active tab (incase it is visible)
		if pc.GetSelection() >= pc._nFrom and pc.GetSelection() < pc._nFrom + len(vTabsInfo):
			self.DrawTab(pc, dc, activeTabPosx, pc.GetSelection(), activeTabWidth, activeTabHeight)

		# Update all tabs that can not fit into the screen as non-visible
		for xx in xrange(pc._nFrom + len(vTabsInfo), len(pc._pagesInfoVec)):
			pc._pagesInfoVec[xx].SetPosition(wx.Point(-1, -1))
			pc._pagesInfoVec[xx].GetRegion().Clear()

	def DrawTab(self, pageContainer, dc, posx, tabIdx, tabWidth, tabHeight):
		"""
		Draws a tab using the `VC8` style.

		:param `pageContainer`: an instance of L{FlatNotebook};
		:param `dc`: an instance of `wx.DC`;
		:param `posx`: the x position of the tab;
		:param `tabIdx`: the index of the tab;
		:param `tabWidth`: the tab's width;
		:param `tabHeight`: the tab's height;
		"""

		pc = pageContainer
		borderPen = wx.Pen(pc._pParent.GetBorderColour())
		tabPoints = [wx.Point() for ii in xrange(8)]

		# If we draw the first tab or the active tab,
		# we draw a full tab, else we draw a truncated tab
		#
		#             X(2)                  X(3)
		#        X(1)                            X(4)
		#
		#                                           X(5)
		#
		# X(0),(7)                                  X(6)
		#
		#

		tabPoints[0].x = posx + self._factor
		tabPoints[0].y = tabHeight - 3

		tabPoints[1].x = tabPoints[0].x + tabHeight - VERTICAL_BORDER_PADDING - 3 - self._factor
		tabPoints[1].y = VERTICAL_BORDER_PADDING + 2

		tabPoints[2].x = tabPoints[1].x + 4
		tabPoints[2].y = VERTICAL_BORDER_PADDING

		tabPoints[3].x = tabPoints[2].x + tabWidth - 2
		tabPoints[3].y = VERTICAL_BORDER_PADDING

		tabPoints[4].x = tabPoints[3].x + 1
		tabPoints[4].y = tabPoints[3].y + 1

		tabPoints[5].x = tabPoints[4].x + 1
		tabPoints[5].y = tabPoints[4].y + 1

		tabPoints[6].x = tabPoints[2].x + tabWidth
		tabPoints[6].y = tabPoints[0].y

		tabPoints[7].x = tabPoints[0].x
		tabPoints[7].y = tabPoints[0].y

		pc._pagesInfoVec[tabIdx].SetRegion(tabPoints)

		# Draw the polygon
		br = dc.GetBrush()
		dc.SetBrush(wx.Brush((tabIdx == pc.GetSelection() and [pc._activeTabColour] or [(255, 0, 0)])[0]))
		dc.SetPen(wx.Pen((tabIdx == pc.GetSelection() and [wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNSHADOW)] or [pc._colourBorder])[0]))
		dc.DrawPolygon(tabPoints)

		# Restore the brush
		dc.SetBrush(br)
		rect = pc.GetClientRect()

		if tabIdx != pc.GetSelection():
			# Top default tabs
			dc.SetPen(wx.Pen(pc._pParent.GetBorderColour()))
			lineY = rect.height
			curPen = dc.GetPen()
			curPen.SetWidth(1)
			dc.SetPen(curPen)
			dc.DrawLine(posx, lineY, posx+rect.width, lineY)

		# Incase we are drawing the selected tab, we draw the border of it as well
		# but without the bottom
		if tabIdx == pc.GetSelection():
			borderPen = wx.Pen(wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNSHADOW))
			dc.SetPen(borderPen)
			dc.SetBrush(wx.TRANSPARENT_BRUSH)
			dc.DrawPolygon(tabPoints)

			# Delete the bottom line
			dc.SetPen(wx.WHITE_PEN)
			dc.DrawLine(tabPoints[0].x, tabPoints[0].y, tabPoints[6].x, tabPoints[6].y)

		# Text drawing offset from the left border of the rectangle

		vc8ShapeLen = tabHeight - VERTICAL_BORDER_PADDING - 2
		textOffset = pc._pParent.GetPadding() + vc8ShapeLen
		textYCoord = 8
		boldFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)

		# if selected tab, draw text in bold
		if tabIdx == pc.GetSelection():
			boldFont.SetWeight(wx.FONTWEIGHT_BOLD)

		dc.SetFont(boldFont)

		pageTextColour = pc._pParent.GetPageTextColour(tabIdx)
		if pageTextColour is not None:
			dc.SetTextForeground(pageTextColour)

		dc.DrawText(pc.GetPageText(tabIdx), posx + textOffset, textYCoord)

		self.DrawFocusRectangle(dc, pc, pc._pagesInfoVec[tabIdx])

	def NumberTabsCanFit(self, pageContainer, fr=-1):
		"""
		Calculates the number of tabs that can fit on the available space on screen.

		:param `pageContainer`: an instance of L{FlatNotebook};
		:param `fr`: the current first visible tab.
		"""

		pc = pageContainer

		rect = pc.GetClientRect()
		clientWidth = rect.width

		# Empty results
		vTabInfo = []
		tabHeight = self.CalcTabHeight(pageContainer)

		# The drawing starts from posx
		posx = pc._pParent.GetPadding()

		if fr < 0:
			fr = pc._nFrom

		for i in xrange(fr, len(pc._pagesInfoVec)):
			vc8glitch = tabHeight + FNB_HEIGHT_SPACER
			tabWidth = self.CalcTabWidth(pageContainer, i, tabHeight)

			if posx + tabWidth + vc8glitch >= clientWidth:
				break

			# Add a result to the returned vector
			tabRect = wx.Rect(posx, VERTICAL_BORDER_PADDING, tabWidth, tabHeight)
			vTabInfo.append(tabRect)

			# Advance posx
			posx += tabWidth + FNB_HEIGHT_SPACER

		return vTabInfo

# ---------------------------------------------------------------------------- #
# Class FlatNotebook
# ---------------------------------------------------------------------------- #

class FlatNotebook(wx.PyPanel):
	"""
	The L{FlatNotebook} is a full implementation of the `wx.Notebook`, and designed to be
	a drop-in replacement for `wx.Notebook`. The API functions are similar so one can
	expect the function to behave in the same way.
	"""

	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
				 style=0, agwStyle=0, name="FlatNotebook"):
		"""
		Default class constructor.

		:param `parent`: the L{FlatNotebook} parent;
		:param `id`: an identifier for the control: a value of -1 is taken to mean a default;
		:param `pos`: the control position. A value of (-1, -1) indicates a default position,
		 chosen by either the windowing system or wxPython, depending on platform;
		:param `size`: the control size. A value of (-1, -1) indicates a default size,
		 chosen by either the windowing system or wxPython, depending on platform;
		:param `style`: the underlying `wx.PyPanel` window style;
		:param `agwStyle`: the AGW-specific window style. This can be a combination of the
		 following bits:

		 ================================ =========== ==================================================
		 Window Styles                    Hex Value   Description
		 ================================ =========== ==================================================
		 ``FNB_VC8``                            0x100 Use Visual Studio 2005 (VC8) style for tabs.
		 ================================ =========== ==================================================

		:param `name`: the window name.
		"""

		self._nPadding = 6
		self._nFrom = 0
		self._windows = []
		self._agwStyle = agwStyle | FNB_VC8

		style |= wx.TAB_TRAVERSAL
		wx.PyPanel.__init__(self, parent, id, pos, size, style)

		self._pages = PageContainer(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, style)
		self.Bind(wx.EVT_NAVIGATION_KEY, self.OnNavigationKey)
		self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
		self.Init()

	def Init(self):
		""" Initializes all the class attributes. """

		self._pages._colourBorder = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNSHADOW)
		self._mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self._mainSizer)

		# The child panels will inherit this bg colour, so leave it at the default value
		#self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_APPWORKSPACE))

		# Set default page height
		dc = wx.ClientDC(self)

		if "__WXGTK__" in wx.PlatformInfo:
			# For GTK it seems that we must do this steps in order
			# for the tabs will get the proper height on initialization
			# on MSW, preforming these steps yields wierd results
			boldFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
			boldFont.SetWeight(wx.FONTWEIGHT_BOLD)
			dc.SetFont(boldFont)

		height = dc.GetCharHeight()
		tabHeight = height + FNB_HEIGHT_SPACER         # We use 8 pixels as padding

		if "__WXGTK__" in wx.PlatformInfo:
			tabHeight += 6

		self._pages.SetSizeHints(-1, tabHeight)
		# Add the tab container to the sizer
		self._mainSizer.Insert(0, self._pages, 0, wx.EXPAND)
		self._mainSizer.Layout()
		self._pages._nFrom = self._nFrom

	def SetHeaderBackground(self, bitmap):
		self._pages.SetHeaderBackground(bitmap)

	def GetHeaderRect(self):
		return self._pages.GetClientRect()

	def DoGetBestSize(self):
		"""
		Gets the size which best suits the window: for a control, it would be the
		minimal size which doesn't truncate the control, for a panel - the same
		size as it would have after a call to `Fit()`.

		:note: Overridden from `wx.PyPanel`.
		"""

		if not self._windows:
			# Something is better than nothing... no pages!
			return wx.Size(20, 20)

		maxWidth = maxHeight = 0
		tabHeight = self.GetPageBestSize().height

		for win in self._windows:
			# Loop over all the windows to get their best size
			width, height = win.GetBestSize()
			maxWidth, maxHeight = max(maxWidth, width), max(maxHeight, height)

		return wx.Size(maxWidth, maxHeight+tabHeight)

	def AddPage(self, page, text, select=False):
		"""
		Adds a page to the L{FlatNotebook}.

		:param `page`: specifies the new page;
		:param `text`: specifies the text for the new page;
		:param `select`: specifies whether the page should be selected;

		:return: ``True`` if successful, ``False`` otherwise.
		"""

		# sanity check
		if not page:
			return False

		# reparent the window to us
		page.Reparent(self)

		# Add tab
		bSelected = select or len(self._windows) == 0

		if bSelected:
			bSelected = False

			# Check for selection and send events
			oldSelection = self._pages._iActivePage
			tabIdx = len(self._windows)

			event = FlatNotebookEvent(wxEVT_FLATNOTEBOOK_PAGE_CHANGING, self.GetId())
			event.SetSelection(tabIdx)
			event.SetOldSelection(oldSelection)
			event.SetEventObject(self)

			if not self.GetEventHandler().ProcessEvent(event) or event.IsAllowed() or len(self._windows) == 0:
				bSelected = True

		curSel = self._pages.GetSelection()

		if not self._pages.IsShown():
			self._pages.Show()

		self._pages.AddPage(text, bSelected)
		self._windows.append(page)

		self.Freeze()

		# Check if a new selection was made
		if bSelected:
			if curSel >= 0:
				# Remove the window from the main sizer
				self._mainSizer.Detach(self._windows[curSel])
				self._windows[curSel].Hide()

			# We leave a space of 1 pixel around the window
			self._mainSizer.Add(page, 1, wx.EXPAND)

			# Fire a wxEVT_FLATNOTEBOOK_PAGE_CHANGED event
			event.SetEventType(wxEVT_FLATNOTEBOOK_PAGE_CHANGED)
			event.SetOldSelection(oldSelection)
			self.GetEventHandler().ProcessEvent(event)
		else:
			# Hide the page
			page.Hide()

		self.Thaw()
		self._mainSizer.Layout()
		self.Refresh()
		return True

	def GetPage(self, page):
		""" Returns the window at the given page position, or ``None``. """

		if page >= len(self._windows):
			return None

		return self._windows[page]

	def AdvanceSelection(self, forward=True):
		"""
		Cycles through the tabs.

		:param `forward`: if ``True``, the selection is advanced in ascending order
		 (to the right), otherwise the selection is advanced in descending order.

		:note: The call to this function generates the page changing events.
		"""

		self._pages.AdvanceSelection(forward)

	def SetSelection(self, page):
		"""
		Sets the selection for the given page.

		:param `page`: an integer specifying the new selected page.

		:note: The call to this function **does not** generate the page changing events.
		"""

		if page >= len(self._windows) or not self._windows:
			return

		curSel = self._pages.GetSelection()

		# program allows the page change
		self.Freeze()
		if curSel >= 0:
			# Remove the window from the main sizer
			self._mainSizer.Detach(self._windows[curSel])
			self._windows[curSel].Hide()

		# We leave a space of 1 pixel around the window
		self._mainSizer.Add(self._windows[page], 1, wx.EXPAND)

		self._windows[page].Show()
		self.Thaw()
		self._mainSizer.Layout()

		if page != self._pages._iActivePage:
			# there is a real page changing
			self._pages._iPreviousActivePage = self._pages._iActivePage

		self._pages._iActivePage = page
		self._pages.DoSetSelection(page)

	def GetSelection(self):
		""" Returns the currently selected page, or -1 if none was selected. """

		return self._pages.GetSelection()

	def GetPreviousSelection(self):
		""" Returns the previous selection. """

		return self._pages._iPreviousActivePage

	def GetPageCount(self):
		""" Returns the number of pages in the L{FlatNotebook} control. """

		return self._pages.GetPageCount()

	def OnNavigationKey(self, event):
		"""
		Handles the ``wx.EVT_NAVIGATION_KEY`` event for L{FlatNotebook}.

		:param `event`: a `wx.NavigationKeyEvent` event to be processed.
		"""

		if event.IsWindowChange():
			if len(self._windows) == 0:
				return
			# change pages
			self.AdvanceSelection(event.GetDirection())
		else:
			event.Skip()

	def GetPageBestSize(self):
		""" Return the page best size. """

		return self._pages.GetClientSize()

	def SetPadding(self, padding):
		"""
		Sets the amount of space around each page's icon and label, in pixels.

		:param `padding`: the amount of space around each page's icon and label,
		 in pixels.

		:note: Only the horizontal padding is considered.
		"""

		self._nPadding = padding.GetWidth()

	def GetPadding(self):
		""" Returns the amount of space around each page's icon and label, in pixels. """

		return self._nPadding

	def GetAGWWindowStyleFlag(self):
		"""
		Returns the L{FlatNotebook} window style.
		"""

		return self._agwStyle

	def GetPageText(self, page):
		"""
		Returns the string for the given page.

		:param `page`: an integer specifying the page index.
		"""

		return self._pages.GetPageText(page)

	def SetBorderColour(self, colour):
		"""
		Set the border colour.

		:param `colour`: a valid instance of `wx.Colour`.
		"""

		self._pages._colourBorder = colour

	def GetBorderColour(self):
		""" Returns the border colour. """

		return self._pages._colourBorder

	def SetActiveTabTextColour(self, textColour):
		"""
		Sets the text colour for the active tab.

		:param `textColour`: a valid `wx.Colour` object.
		"""

		self._pages._activeTextColour = textColour

	def GetActiveTabTextColour(self):
		""" Get the active tab text colour. """

		return self._pages._activeTextColour

	def SetNonActiveTabTextColour(self, colour):
		"""
		Sets the non active tabs text colour.

		:param `colour`: a valid instance of `wx.Colour`.
		"""

		self._pages._nonActiveTextColour = colour

	def GetNonActiveTabTextColour(self):
		""" Returns the non active tabs text colour. """

		return self._pages._nonActiveTextColour

	def SetPageTextColour(self, page, colour):
		"""
		Sets the tab text colour individually.

		:param `page`: an integer specifying the page index;
		:param `colour`: an instance of `wx.Colour`. You can pass ``None`` or
		 `wx.NullColour` to return to the default page text colour.
		"""

		self._pages.SetPageTextColour(page, colour)

	def GetPageTextColour(self, page):
		"""
		Returns the tab text colour if it has been set previously, or ``None`` otherwise.

		:param `page`: an integer specifying the page index.
		"""

		return self._pages.GetPageTextColour(page)

	def SetActiveTabColour(self, colour):
		"""
		Sets the active tab colour.

		:param `colour`: a valid instance of `wx.Colour`.
		"""

		self._pages._activeTabColour = colour

	def GetActiveTabColour(self):
		""" Returns the active tab colour. """

		return self._pages._activeTabColour

	def EnsureVisible(self, page):
	   """
	   Ensures that a tab is visible.

	   :param `page`: an integer specifying the page index.
	   """

	   self._pages.DoSetSelection(page)


# ---------------------------------------------------------------------------- #
# Class PageContainer
# Acts as a container for the pages you add to FlatNotebook
# ---------------------------------------------------------------------------- #

class PageContainer(wx.Panel):
	"""
	This class acts as a container for the pages you add to L{FlatNotebook}.
	"""

	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=0):
		"""
		Default class constructor.

		Used internally, do not call it in your code!

		:param `parent`: the L{PageContainer} parent;
		:param `id`: an identifier for the control: a value of -1 is taken to mean a default;
		:param `pos`: the control position. A value of (-1, -1) indicates a default position,
		 chosen by either the windowing system or wxPython, depending on platform;
		:param `size`: the control size. A value of (-1, -1) indicates a default size,
		 chosen by either the windowing system or wxPython, depending on platform;
		:param `style`: the window style.
		"""

		self._iActivePage = -1
		self._nLeftClickZone = FNB_NOWHERE
		self._iPreviousActivePage = -1

		self._pParent = parent

		self._nHoveringOverTabIndex = -1
		self._nHoveringOverLastTabIndex = -1

		self._pagesInfoVec = []

		self._activeTabColour = wx.WHITE
		self._activeTextColour = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNTEXT)
		self._nonActiveTextColour = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNTEXT)

		self._nFrom = 0

		# Set default page height, this is done according to the system font
		memDc = wx.MemoryDC()
		memDc.SelectObject(wx.EmptyBitmap(1,1))

		if "__WXGTK__" in wx.PlatformInfo:
			boldFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
			boldFont.SetWeight(wx.BOLD)
			memDc.SetFont(boldFont)

		height = memDc.GetCharHeight()
		tabHeight = height + FNB_HEIGHT_SPACER # We use 10 pixels as padding

		wx.Panel.__init__(self, parent, id, pos, wx.Size(size.x, tabHeight),
						  style|wx.NO_BORDER|wx.NO_FULL_REPAINT_ON_RESIZE|wx.WANTS_CHARS)

		self._mgr = FNBRendererMgr()

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		self.Bind(wx.EVT_MOTION, self.OnMouseMove)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)
		self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
		self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

		self._paintCnt = 0
		self._headerBg = None

	def SetHeaderBackground(self, bitmap):
		self._headerBg = bitmap

	def GetHeaderBackground(self):
		return self._headerBg

	def OnEraseBackground(self, event):
		"""
		Handles the ``wx.EVT_ERASE_BACKGROUND`` event for L{PageContainer}.

		:param `event`: a `wx.EraseEvent` event to be processed.

		:note: This method is intentionally empty to reduce flicker.
		"""

		pass

	def OnPaint(self, event):
		"""
		Handles the ``wx.EVT_PAINT`` event for L{PageContainer}.

		:param `event`: a `wx.PaintEvent` event to be processed.
		"""

		self._paintCnt = self._paintCnt + 1
		dc = wx.PaintDC(self)
		renderer = self._mgr.GetRenderer(self.GetParent().GetAGWWindowStyleFlag())
		renderer.DrawTabs(self, dc)

	def AddPage(self, caption, selected=False):
		"""
		Adds a page to the L{PageContainer}.

		:param `page`: specifies the new page;
		:param `text`: specifies the text for the new page;
		:param `select`: specifies whether the page should be selected;
		"""

		if selected:
			self._iPreviousActivePage = self._iActivePage
			self._iActivePage = len(self._pagesInfoVec)

		# Create page info and add it to the vector
		pageInfo = PageInfo(caption)
		self._pagesInfoVec.append(pageInfo)
		self.Refresh()

	def OnSize(self, event):
		"""
		Handles the ``wx.EVT_SIZE`` event for L{PageContainer}.

		:param `event`: a `wx.SizeEvent` event to be processed.
		"""

		# When resizing the control, try to fit to screen as many tabs as we can
		agwStyle = self.GetParent().GetAGWWindowStyleFlag()
		renderer = self._mgr.GetRenderer(agwStyle)

		fr = 0
		page = self.GetSelection()

		for fr in xrange(self._nFrom):
			vTabInfo = renderer.NumberTabsCanFit(self, fr)
			if page - fr >= len(vTabInfo):
				continue
			break

		self._nFrom = fr

		self.Refresh() # Call on paint
		event.Skip()

	def OnLeftDown(self, event):
		"""
		Handles the ``wx.EVT_LEFT_DOWN`` event for L{PageContainer}.

		:param `event`: a `wx.MouseEvent` event to be processed.
		"""

		self._nLeftClickZone, tabIdx = self.HitTest(event.GetPosition())

		if self._nLeftClickZone == FNB_TAB:
			if self._iActivePage != tabIdx:
				# In case the tab is disabled, we dont allow to choose it
				if len(self._pagesInfoVec) > tabIdx:
					self.FireEvent(tabIdx)

	def HitTest(self, pt):
		"""
		HitTest method for L{PageContainer}.

		:param `pt`: an instance of `wx.Point`, to test for hits.

		:return: The hit test flag (if any) and the hit page index (if any). The return
		 value can be one of the following bits:

		 ========================= ======= =================================
		 HitTest Flag               Value  Description
		 ========================= ======= =================================
		 ``FNB_NOWHERE``                 0 Indicates mouse coordinates not on any tab of the notebook
		 ``FNB_TAB``                     1 Indicates mouse coordinates inside a tab
		 ========================= ======= =================================

		"""

		tabIdx = -1

		if len(self._pagesInfoVec) == 0:
			return FNB_NOWHERE, tabIdx

		# Test whether a left click was made on a tab
		bFoundMatch = False

		for cur in xrange(self._nFrom, len(self._pagesInfoVec)):
			pgInfo = self._pagesInfoVec[cur]
			if pgInfo.GetPosition() == wx.Point(-1, -1):
				continue

			if self._pagesInfoVec[cur].GetRegion().Contains(pt.x, pt.y):
				if bFoundMatch or cur == self.GetSelection():
					return FNB_TAB, cur

				tabIdx = cur
				bFoundMatch = True

		if bFoundMatch:
			return FNB_TAB, tabIdx

		# Default
		return FNB_NOWHERE, -1

	def SetSelection(self, page):
		"""
		Sets the selected page.

		:param `page`: an integer specifying the page index.
		"""

		book = self.GetParent()
		book.SetSelection(page)
		self.DoSetSelection(page)

	def DoSetSelection(self, page):
		"""
		Does the actual selection of a page.

		:param `page`: an integer specifying the page index.
		"""

		if page < len(self._pagesInfoVec):
			#! fix for tabfocus
			da_page = self._pParent.GetPage(page)

			if da_page != None:
				da_page.SetFocus()

		if not self.IsTabVisible(page):
			# Try to remove one tab from start and try again
			if not self.CanFitToScreen(page):
				if self._nFrom > page:
					self._nFrom = page
				else:
					while self._nFrom < page:
						self._nFrom += 1
						if self.CanFitToScreen(page):
							break
		self.Refresh()

	def IsMouseHovering(self, page):
		"""
		Returns whether or not the mouse is hovering over this page's tab

		:param `page`: an integer specifying the page index.
		"""
		return page == self._nHoveringOverTabIndex

	def IsTabVisible(self, page):
		"""
		Returns whether a tab is visible or not.

		:param `page`: an integer specifying the page index.
		"""

		iLastVisiblePage = self.GetLastVisibleTab()
		return page <= iLastVisiblePage and page >= self._nFrom

	def OnMouseMove(self, event):
		"""
		Handles the ``wx.EVT_MOTION`` event for L{PageContainer}.

		:param `event`: a `wx.MouseEvent` event to be processed.
		"""

		if self._pagesInfoVec and self.IsShown():
			bRedrawTabs = False
			self._nHoveringOverTabIndex = -1

			where, tabIdx = self.HitTest(event.GetPosition())
			if where == FNB_TAB:
				# Call virtual method for showing tooltip
				self._nHoveringOverTabIndex = tabIdx

			if self._nHoveringOverTabIndex != self._nHoveringOverLastTabIndex:
				self._nHoveringOverLastTabIndex = self._nHoveringOverTabIndex
				bRedrawTabs = True

			if bRedrawTabs:
				dc = wx.ClientDC(self)
				self.Refresh()

		event.Skip()

	def GetLastVisibleTab(self):
		""" Returns the last visible tab in the tab area. """

		if self._nFrom < 0:
			return -1

		ii = 0

		for ii in xrange(self._nFrom, len(self._pagesInfoVec)):
			if self._pagesInfoVec[ii].GetPosition() == wx.Point(-1, -1):
				break
		return ii-1

	def AdvanceSelection(self, forward=True):
		"""
		Cycles through the tabs.

		:param `forward`: if ``True``, the selection is advanced in ascending order
		 (to the right), otherwise the selection is advanced in descending order.

		:note: The call to this function generates the page changing events.
		"""

		nSel = self.GetSelection()

		if nSel < 0:
			return

		nMax = self.GetPageCount() - 1

		if forward:
			newSelection = (nSel == nMax and [0] or [nSel + 1])[0]
		else:
			newSelection = (nSel == 0 and [nMax] or [nSel - 1])[0]

		self.FireEvent(newSelection)

	def OnMouseLeave(self, event):
		"""
		Handles the ``wx.EVT_LEAVE_WINDOW`` event for L{PageContainer}.

		:param `event`: a `wx.MouseEvent` event to be processed.
		"""

		self._nHoveringOverTabIndex = -1
		self._nHoveringOverLastTabIndex = -1

		agwStyle = self.GetParent().GetAGWWindowStyleFlag()
		render = self._mgr.GetRenderer(agwStyle)

		dc = wx.ClientDC(self)

		render.DrawTabs(self,dc)

		selection = self.GetSelection()

		if selection == -1:
			event.Skip()
			return

		if not self.IsTabVisible(selection):
			if selection == len(self._pagesInfoVec) - 1:
				if not self.CanFitToScreen(selection):
					event.Skip()
					return
			else:
				event.Skip()
				return

		render.DrawFocusRectangle(dc, self, self._pagesInfoVec[selection])
		event.Skip()

	def GetPageTextColour(self, page):
		"""
		Returns the tab text colour if it has been set previously, or ``None`` otherwise.

		:param `page`: an integer specifying the page index.
		"""

		if page < len(self._pagesInfoVec):
			return self._pagesInfoVec[page].GetPageTextColour()
		return None

	def SetPageTextColour(self, page, colour):
		"""
		Sets the tab text colour individually.

		:param `page`: an integer specifying the page index;
		:param `colour`: an instance of `wx.Colour`. You can pass ``None`` or
		 `wx.NullColour` to return to the default page text colour.
		"""

		if page < len(self._pagesInfoVec):
			self._pagesInfoVec[page].SetPageTextColour(colour)
			self.Refresh()

	def CanFitToScreen(self, page):
		"""
		Returns wheter a tab can fit in the left space in the screen or not.

		:param `page`: an integer specifying the page index.
		"""

		# Incase the from is greater than page,
		# we need to reset the self._nFrom, so in order
		# to force the caller to do so, we return false
		if self._nFrom > page:
			return False

		agwStyle = self.GetParent().GetAGWWindowStyleFlag()
		render = self._mgr.GetRenderer(agwStyle)

		vTabInfo = render.NumberTabsCanFit(self)

		if page - self._nFrom >= len(vTabInfo):
			return False

		return True

	def GetSingleLineBorderColour(self):
		""" Returns the colour for the single line border. """

		return wx.WHITE

	def GetAGWWindowStyleFlag(self):
		"""
		Returns the L{FlatNotebook} window style.

		:see: The L{FlatNotebook.__init__} method for the `agwStyle` parameter description.
		"""

		return self.GetParent().GetAGWWindowStyleFlag()

	def OnSetFocus(self, event):
		"""
		Handles the ``wx.EVT_SET_FOCUS`` event for L{PageContainer}.

		:param `event`: a `wx.FocusEvent` event to be processed.
		"""

		if self._iActivePage < 0:
			event.Skip()
			return

		self.SetFocusedPage(self._iActivePage)

	def OnKillFocus(self, event):
		"""
		Handles the ``wx.EVT_KILL_FOCUS`` event for L{PageContainer}.

		:param `event`: a `wx.FocusEvent` event to be processed.
		"""

		self.SetFocusedPage()

	def OnKeyDown(self, event):
		"""
		Handles the ``wx.EVT_KEY_DOWN`` event for L{PageContainer}.

		:param `event`: a `wx.KeyEvent` event to be processed.

		:note: When the L{PageContainer} has the focus tabs can be changed with
		 the left/right arrow keys.
		"""

		key = event.GetKeyCode()
		if key == wx.WXK_LEFT:
			self.GetParent().AdvanceSelection(False)
			self.SetFocus()
		elif key == wx.WXK_RIGHT:
			self.GetParent().AdvanceSelection(True)
			self.SetFocus()
		elif key == wx.WXK_TAB and not event.ControlDown():
			flags = 0
			if not event.ShiftDown(): flags |= wx.NavigationKeyEvent.IsForward
			if event.CmdDown():       flags |= wx.NavigationKeyEvent.WinChange
			self.Navigate(flags)
		else:
			event.Skip()

	def SetFocusedPage(self, pageIndex=-1):
		"""
		Sets/Unsets the focus on the appropriate page.

		:param `pageIndex`: an integer specifying the page index. If `pageIndex`
		 is defaulted to -1, we have lost focus and no focus indicator is drawn.
		"""

		for indx, page in enumerate(self._pagesInfoVec):
			if indx == pageIndex:
				page._hasFocus = True
			else:
				page._hasFocus = False

		self.Refresh()

	def FireEvent(self, selection):
		"""
		Fires the ``EVT_FLATNOTEBOOK_PAGE_CHANGING`` and ``EVT_FLATNOTEBOOK_PAGE_CHANGED``
		events called from other methods (from menu selection or `Smart Tabbing`).

		This is an utility function.

		:param `selection`: the new selection inside L{FlatNotebook}.
		"""

		if selection == self._iActivePage:
			# No events for the same selection
			return

		oldSelection = self._iActivePage

		event = FlatNotebookEvent(wxEVT_FLATNOTEBOOK_PAGE_CHANGING, self.GetParent().GetId())
		event.SetSelection(selection)
		event.SetOldSelection(oldSelection)
		event.SetEventObject(self.GetParent())

		if not self.GetParent().GetEventHandler().ProcessEvent(event) or event.IsAllowed():

			self.SetSelection(selection)

			# Fire a wxEVT_FLATNOTEBOOK_PAGE_CHANGED event
			event.SetEventType(wxEVT_FLATNOTEBOOK_PAGE_CHANGED)
			event.SetOldSelection(oldSelection)
			self.GetParent().GetEventHandler().ProcessEvent(event)


	def GetSelection(self):
		""" Returns the current selected page. """

		return self._iActivePage

	def GetPageCount(self):
		""" Returns the number of tabs in the L{FlatNotebook} control. """

		return len(self._pagesInfoVec)

	def GetPageText(self, page):
		"""
		Returns the tab caption of the page.

		:param `page`: an integer specifying the page index.
		"""

		if page < len(self._pagesInfoVec):
			return self._pagesInfoVec[page].GetCaption()
		else:
			return u''
