# encoding: utf-8

###########################################################################################################
#
#
#	Reporter Plugin: CJK Metrics
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
##############################################################################################

import objc

from GlyphsApp import *
from GlyphsApp.plugins import *

from vanilla import *
from vanilla.vanillaGroup import Group


# Our own patched Vanilla Group class
class PatchedGroup(Group):
    nsViewClass = objc.lookUpClass('GSInspectorView')


class CJKMetrics(SelectTool):

	@objc.python_method
	def settings(self):
		self.name = 'CJK Metrics'
		self.keyboardShortcut = 'c'
		self.menuItem = NSMenuItem('Show ' + self.name, self.toggleMenuItem)


	def start(self):
		Glyphs.menu[VIEW_MENU].append(self.menuItem)


	def activate(self):
		self.centralAreaSpacing = 500.0
		self.centralAreaWidth = 100.0
		self.centralAreaPosition = 50.0

		viewWidth = 150
		viewHeight = 40
		self.sliderWindow = Window((viewWidth, viewHeight))
		self.sliderWindow.group = PatchedGroup((0, 0, viewWidth, viewHeight))
		self.sliderWindow.group.editTextCentralAreaSpacing = EditText(
			(0, 2, 60, 16),
			sizeStyle='small',
			placeholder='500',
			callback=self.editTextCentralAreaSpacingCallback)
		self.sliderWindow.group.editTextCentralAreaWidth = EditText(
			(80, 2, 60, 16),
			sizeStyle='small',
			placeholder='100',
			callback=self.editTextCentralAreaWidthCallback)
		self.sliderWindow.group.sliderCentralAreaPosition = Slider(
			(0, 20, 100, 12),
			sizeStyle='small',
			callback=self.sliderCentralAreaPositionCallback)
		self.sliderWindow.group.textBoxCentralAreaPosition = TextBox(
			(100, 20, 45, 12),
			text=str(self.centralAreaPosition) + '%',
			sizeStyle='small')

		# See https://forum.glyphsapp.com/t/how-to-create-an-info-box-in-plugin/14198
		GSCallbackHandler.addCallback_forOperation_(self, 'GSInspectorViewControllersCallback')


	def inspectorViewControllersForLayer_(self, layer):
		return [self]


	def view(self):
		return self.sliderWindow.group.getNSView()


	def toggleMenuItem(self, menuItem):
		'''The callback invoked when click the CJK Metrics menu item.'''
		if menuItem.state() == ONSTATE:
			menuItem.setState_(OFFSTATE)
		elif menuItem.state() == OFFSTATE:
			menuItem.setState_(ONSTATE)


	def editTextCentralAreaSpacingCallback(self, sender):
		self.centralAreaSpacing = toFloat(sender.get())


	def editTextCentralAreaWidthCallback(self, sender):
		self.centralAreaWidth = toFloat(sender.get())


	def sliderCentralAreaPositionCallback(self, sender):
		self.centralAreaPosition = sender.get()
		self.sliderWindow.group.textBoxCentralAreaPosition.set('{:.1f}%'.format(sender.get()))


	def foreground(self, layer):
		self.drawMedialAxes(layer)
		self.drawCentralArea(layer)


	def drawMedialAxes(self, layer):
		# TODO: draw real medial axes
		NSBezierPath.strokeLineFromPoint_toPoint_((0,0), (1000,2000))


	def drawCentralArea(self, layer):
		spacing = self.centralAreaSpacing
		width = self.centralAreaWidth
		postion = layer.width * self.centralAreaPosition / 100

		master = layer.associatedFontMaster()
		descender = master.descender
		ascender = master.ascender
		height = ascender - descender

		drawRect((postion - spacing / 2 - width / 2, descender), (width, height))
		drawRect((postion + spacing / 2 - width / 2, descender), (width, height))


	@objc.python_method
	def __file__(self):
		'''Please leave this method unchanged'''
		return __file__


def drawRect(origin, size):
	'''Draw a rectange with `origin` and `size`.'''
	NSBezierPath.fillRect_((origin, size))


def toFloat(s):
	'''Safely convert a string to float number.'''
	try:
		return float(s)
	except ValueError:
		return 0.0
