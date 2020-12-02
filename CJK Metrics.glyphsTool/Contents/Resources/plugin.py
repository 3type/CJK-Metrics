# encoding: utf-8

###########################################################################################################
#
#
#	Select Tool Plugin: CJK Metrics
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/SelectTool
#
#
##############################################################################################

import objc

from Foundation import NSAffineTransform, NSBezierPath, NSColor

from GlyphsApp import *
from GlyphsApp.plugins import *

from vanilla import *


CJK_GUIDE_GLYPH = '_cjkguide'

# Our own patched Vanilla Group class
# class PatchedGroup(Group):
# 	nsViewClass = objc.lookUpClass('GSInspectorView')
# 	nsViewClass = GSInspectorView


class CJKMetrics(SelectTool):

	@objc.python_method
	def settings(self):
		self.name = 'CJK Metrics'
		self.keyboardShortcut = 'c'

		self.medialAxesState = True
		self.centralAreaState = True
		self.cjkGuideState = True
		self.cjkGuideScalingState = False

		self.centralAreaSpacing = 500.0
		self.centralAreaWidth = 100.0
		self.centralAreaPosition = 50.0

		viewWidth = 150
		viewHeight = 40
		self.sliderWindow = Window((viewWidth, viewHeight))
		self.sliderWindow.group = Group((0, 0, viewWidth, viewHeight))
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

		self.generalContextMenus = self.buildContextMenus()

		# See https://forum.glyphsapp.com/t/how-to-create-an-info-box-in-plugin/14198
		GSCallbackHandler.addCallback_forOperation_(self, 'GSInspectorViewControllersCallback')


	# def start(self):
	# 	Glyphs.menu[VIEW_MENU].append(self.menuItem)


	@objc.python_method
	def activate(self):
		self.initCjkGuideGlyph()


	@objc.python_method
	def inspectorViewControllersForLayer_(self, layer):
		return [self]


	@objc.python_method
	def view(self):
		return self.sliderWindow.group.getNSView()


	@objc.python_method
	def initCjkGuideGlyph(self):
		font = Glyphs.font
		if font.glyphs[CJK_GUIDE_GLYPH] is None:
			# TODO: dialogue
			font.glyphs.append(GSGlyph(CJK_GUIDE_GLYPH))
			print('[INFO]: Add glyph \'{}\'!'.format(CJK_GUIDE_GLYPH))

			cjkGuideGlyph = font.glyphs[CJK_GUIDE_GLYPH]
			cjkGuideGlyph.export = False
			for layer in cjkGuideGlyph.layers:
				layer.width = 1000.0  # TODO: use real width


	@objc.python_method
	def editTextCentralAreaSpacingCallback(self, sender):
		self.centralAreaSpacing = toFloat(sender.get())


	@objc.python_method
	def editTextCentralAreaWidthCallback(self, sender):
		self.centralAreaWidth = toFloat(sender.get())


	@objc.python_method
	def sliderCentralAreaPositionCallback(self, sender):
		self.centralAreaPosition = sender.get()
		self.sliderWindow.group.textBoxCentralAreaPosition.set('{:.1f}%'.format(sender.get()))


	@objc.python_method
	def buildContextMenus(self, sender=None):
		return [
			{
				'name': 'CJK Metrics Options:', 
				'action': None,
			},
			{
				'name': 'Show Medial Axes',
				'action': self.toggleMedialAxes,
				'state': self.medialAxesState,
			},
			{
				'name': 'Show Central Area',
				'action': self.toggleCentralArea,
				'state': self.centralAreaState,
			},
			{
				'name': 'Show CJK Guide',
				'action': self.toggleCjkGuide,
				'state': self.cjkGuideState,
			},
			{
				'name': 'Scale CJK Guide',
				'action': self.toggleCjkGuideScaling,
				'state': self.cjkGuideScalingState,
			},
		]


	def toggleMedialAxes(self):
		self.medialAxesState = not self.medialAxesState
		self.generalContextMenus = self.buildContextMenus()


	def toggleCentralArea(self):
		self.centralAreaState = not self.centralAreaState
		self.generalContextMenus = self.buildContextMenus()


	def toggleCjkGuide(self):
		self.cjkGuideState = not self.cjkGuideState
		self.generalContextMenus = self.buildContextMenus()


	def toggleCjkGuideScaling(self):
		self.cjkGuideScalingState = not self.cjkGuideScalingState
		self.generalContextMenus = self.buildContextMenus()


	@objc.python_method
	# def background(self, layer):
	def foreground(self, layer):
		# TODO: use foreground() temporarily
		if self.medialAxesState:
			self.drawMedialAxes(layer)
		if self.centralAreaState:
			self.drawCentralArea(layer)
		if self.cjkGuideState:
			self.drawCjkGuide(layer)


	@objc.python_method
	def drawMedialAxes(self, layer):
		'''Draw the medial axes (水平垂直轴线).'''
		# TODO: set vertical and horizontal in dialog
		vertical = 0.5
		horizontal = 0.5

		scale = self.getScale()

		view = self.editViewController().graphicView()
		visibleRect = view.visibleRect()
		activePosition = view.activePosition()

		viewOriginX = (visibleRect.origin.x - activePosition.x) / scale
		viewOriginY = (visibleRect.origin.y - activePosition.y) / scale
		viewWidth = visibleRect.size.width / scale
		viewHeight = visibleRect.size.height / scale

		master = layer.associatedFontMaster()
		height = master.ascender - master.descender
		width  = layer.width

		x = horizontal * width
		y = master.descender + vertical * height

		# TODO: color
		color = NSColor.systemGreenColor()
		color.set()

		path = NSBezierPath.bezierPath()
		path.moveToPoint_((viewOriginX, y))
		path.lineToPoint_((viewOriginX + viewWidth, y))
		path.moveToPoint_((x, viewOriginY))
		path.lineToPoint_((x, viewOriginY + viewHeight))
		path.setLineWidth_(1 / scale)
		path.stroke()


	@objc.python_method
	def drawCentralArea(self, layer):
		'''Draw the central area (第二中心线).'''
		spacing = self.centralAreaSpacing
		width = self.centralAreaWidth
		postion = layer.width * self.centralAreaPosition / 100

		master = layer.associatedFontMaster()
		descender = master.descender
		ascender = master.ascender
		height = ascender - descender

		# TODO: color
		color = NSColor.systemGrayColor().colorWithAlphaComponent_(0.2)
		color.set()

		NSBezierPath.fillRect_(((postion - spacing / 2 - width / 2, descender), (width, height)))
		NSBezierPath.fillRect_(((postion + spacing / 2 - width / 2, descender), (width, height)))


	@objc.python_method
	def drawCjkGuide(self, layer):
		'''Draw the CJK guide (汉字参考线).'''

		# TODO: color
		color = NSColor.systemOrangeColor().colorWithAlphaComponent_(0.1)
		color.set()

		cjkGuideLayer = Glyphs.font.glyphs['_cjkguide'].layers[0]

		trans = NSAffineTransform.transform()
		if self.cjkGuideScalingState == ONSTATE:
			# TODO: currently only xScale is necessary
			# cjkGuideMaster = cjkGuideLayer.associatedFontMaster()
			# cjkGuideDescender = cjkGuideMaster.descender
			# cjkGuideAscender = cjkGuideMaster.ascender
			# cjkGuideHeight = cjkGuideAscender - cjkGuideDescender
 
			# master = layer.associatedFontMaster()
			# descender = master.descender
			# ascender = master.ascender
			# height = ascender - descender

			xScale = layer.width / cjkGuideLayer.width
			# yScale = height / cjkGuideHeight

			# trans.translateXBy_yBy_(0, cjkGuideDescender)
			# trans.scaleXBy_yBy_(xScale, yScale)
			# trans.translateXBy_yBy_(0, -descender)

			trans.scaleXBy_yBy_(xScale, 1)

		if cjkGuideLayer.bezierPath is not None:
			path = cjkGuideLayer.bezierPath.copy()
			path.transformUsingAffineTransform_(trans)
			path.fill()

	@objc.python_method
	def getScale(self):
		'''Get the scale of graphic view.'''
		try:
			return self.editViewController().graphicView().scale()
		except:
			return 1.0


	@objc.python_method
	def __file__(self):
		'''Please leave this method unchanged'''
		return __file__


def toFloat(s):
	'''Safely convert a string to float number.'''
	try:
		return float(s)
	except ValueError:
		return 0.0
