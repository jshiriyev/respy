import numpy

class RectCuboid():

	def __init__(self,xdelta:tuple=None,ydelta:tuple=None,zdelta:tuple=None,flodim:int=None):
		"""Three-dimensional reservoir model can be initialized with:

		xdelta	: length of grids in ft, (Nlength,)
		ydelta	: width of grids in ft, (Nwidth,)
		zdelta	: height of grids in ft, (Nheight,)

		flodim 	: flow dimension it can be 1, 2, or 3

		The object has methods to calculate the control volume implementation parameters.

		"""
		self._xdelta = numpy.asarray(xdelta).astype(numpy.float_)*0.3048
		self._ydelta = numpy.asarray(ydelta).astype(numpy.float_)*0.3048
		self._zdelta = numpy.asarray(zdelta).astype(numpy.float_)*0.3048

		self._length = self._xdelta.sum()
		self._width  = self._ydelta.sum()
		self._height = self._zdelta.sum()

		self._nums 	 = (len(xdelta),len(ydelta),len(zdelta))

		# The parameters starting with underscore are defined in SI units.
		# The same parameters without underscore are in Oil Field units.

		if flodim is not None:
			self.flodim = flodim
		elif self._nums[2]>1:
			self.flodim = 3
		elif self._nums[1]>1:
			self.flodim = 2
		else:
			self.flodim = 1

		self.set_gplat()

		self.set_dims()
		self.set_area()
		self.set_volume()

	def set_gplat(self):

		nums = self._nums

		idx = numpy.arange(self.numtot,dtype=numpy.int_)

		self.gplat = numpy.tile(idx,(1+self.flodim*2,1)).T

		self.gplat[idx.reshape(-1,nums[0])[:,1:].ravel(),1] -= 1
		self.gplat[idx.reshape(-1,nums[0])[:,:-1].ravel(),2] += 1

		if self.flodim>1:
			self.gplat[idx.reshape(nums[2],-1)[:,nums[0]:],3] -= nums[0]
			self.gplat[idx.reshape(nums[2],-1)[:,:-nums[0]],4] += nums[0]

		if self.flodim>2:
			self.gplat[idx.reshape(nums[2],-1)[1:,:],5] -= nums[0]*nums[1]
			self.gplat[idx.reshape(nums[2],-1)[:-1,:],6] += nums[0]*nums[1]

	def set_dims(self):
		"""should be depreciated later"""

		self._xdims = numpy.tile(
			self._xdelta,self._nums[1]*self._nums[2]).reshape((-1,1))

		self._ydims = numpy.tile(
			numpy.repeat(self._ydelta,self._nums[0]),self._nums[2]).reshape((-1,1))

		self._zdims = numpy.repeat(
			self._zdelta,self._nums[0]*self._nums[1]).reshape((-1,1))

	def set_area(self):

		self._xarea = self._ydims*self._zdims
		self._yarea = self._zdims*self._xdims
		self._zarea = self._xdims*self._ydims

	def set_volume(self):

		self._volume = self._xdims*self._ydims*self._zdims

	def get_property(self,quality,conversion_factor=1.,dtype=None):

		quality = numpy.asarray(quality)

		if dtype is not None:
			quality = quality.astype(dtype)

		quality = quality.flatten()*conversion_factor

		if quality.size==1:
			quality = quality.repeat(self.numtot)

		return quality.reshape((-1,1))

	def set_depth(self,depth):
		"""Assigns the depth values in ft to the grids."""
		self._depth = self.get_property(depth,conversion_factor=0.3048,dtype=numpy.float_)

	def set_poro(self,poro):
		"""Assigns the porosity values in fractions to the grids."""

		self._poro = self.get_property(poro,dtype=numpy.float_)

	def set_perm(self,xperm,yperm=None,zperm=None,yreduce=1.,zreduce=1.):
		"""Assigns the permeability values in mD to the grids."""

		self._xperm = self.get_property(
			xperm,conversion_factor=9.869233e-16,dtype=numpy.float_)

		self._yperm = self._xperm*yreduce if yperm is None else self.get_property(
			yperm,conversion_factor=9.869233e-16,dtype=numpy.float_)

		self._zperm = self._xperm*zreduce if zperm is None else self.get_property(
				zperm,conversion_factor=9.869233e-16,dtype=numpy.float_)

	@property
	def nums(self):
		return self._nums

	@property
	def numtot(self):
		return numpy.prod(self._nums).item()

	@property
	def xdelta(self):
		return self._xdelta/0.3048

	@property
	def ydelta(self):
		return self._ydelta/0.3048

	@property
	def zdelta(self):
		return self._zdelta/0.3048
	
	@property
	def length(self):
		return self._length/0.3048

	@property
	def width(self):
		return self._width/0.3048

	@property
	def height(self):
		return self._height/0.3048

	@property
	def _xaxis(self):

		side2 = numpy.cumsum(self._xdelta)
		side1 = numpy.roll(side2,1)

		side1[0] = 0

		return (side1+side2)/2

	@property
	def _yaxis(self):

		side2 = numpy.cumsum(self._ydelta)
		side1 = numpy.roll(side2,1)

		side1[0] = 0

		return (side1+side2)/2

	@property
	def _zaxis(self):

		side2 = numpy.cumsum(self._zdelta)
		side1 = numpy.roll(side2,1)

		side1[0] = 0

		return (side1+side2)/2

	@property
	def xaxis(self):
		return self._xaxis/0.3048

	@property
	def yaxis(self):
		return self._yaxis/0.3048

	@property
	def zaxis(self):
		return self._zaxis/0.3048

	@property
	def xdims(self):
		return self._xdims/0.3048

	@property
	def ydims(self):
		return self._ydims/0.3048

	@property
	def zdims(self):
		return self._zdims/0.3048

	@property
	def xarea(self):
		return self._xarea/0.3048**2

	@property
	def yarea(self):
		return self._yarea/0.3048**2

	@property
	def zarea(self):
		return self._zarea/0.3048**2

	@property
	def volume(self):
		return self._volume/0.3048**3

	@property
	def depth(self):
		return self._depth/0.3048
	
	@property
	def poro(self):
		return self._poro

	@property
	def xperm(self):
		return self._xperm/9.869233e-16

	@property
	def yperm(self):
		return self._yperm/9.869233e-16

	@property
	def zperm(self):
		return self._zperm/9.869233e-16

	@property
	def xmin(self):
		"""Properties of grids on x-minimum boundary"""
		return RectCuboidSub(self,1,edge=True)

	@property
	def xpos(self):
		"""Properties of grids that has x-positive neighbors"""
		return RectCuboidSub(self,2)

	@property
	def xneg(self):
		"""Properties of grids that has x-negative neighbors"""
		return RectCuboidSub(self,1)

	@property
	def xmax(self):
		"""Properties of grids on x-maximum boundary"""
		return RectCuboidSub(self,2,edge=True)

	@property
	def ymin(self):
		"""Properties of grids on y-minimum boundary"""
		if self.flodim>1:
			return RectCuboidSub(self,3,edge=True)

	@property
	def ypos(self):
		"""Properties of grids that has y-positive neighbors"""
		if self.flodim>1:
			return RectCuboidSub(self,4)

	@property
	def yneg(self):
		"""Properties of grids that has y-negative neighbors"""
		if self.flodim>1:
			return RectCuboidSub(self,3)

	@property
	def ymax(self):
		"""Properties of grids on y-maximum boundary"""
		if self.flodim>1:
			return RectCuboidSub(self,4,edge=True)

	@property
	def zmin(self):
		"""Properties of grids on z-minimum boundary"""
		if self.flodim>2:
			return RectCuboidSub(self,5,edge=True)

	@property
	def zpos(self):
		"""Properties of grids that has z-positive neighbors"""
		if self.flodim>2:
			return RectCuboidSub(self,6)

	@property
	def zneg(self):
		"""Properties of grids that has z-negative neighbors"""
		if self.flodim>2:
			return RectCuboidSub(self,5)

	@property
	def zmax(self):
		"""Properties of grids on z-maximum boundary"""
		if self.flodim>2:
			return RectCuboidSub(self,6,edge=True)

class RectCuboidSub(numpy.ndarray):

	def __new__(cls,grid,path,edge=False):
		"""
		grid 	: RecCuboid instance
		path 	: direction (1: west, 2: east, 3: south, 4: north, 5: down, 6: up)
		edge 	: boundary (True) or inner (False)
		"""

		item = (grid.gplat[:,0]==grid.gplat[:,path])

		if not edge:
			item = ~item

		obj = numpy.asarray(grid.gplat[item,0],dtype=numpy.int_).view(cls)

		obj.grid = grid

		obj.axis = int((path-1)/2)

		return obj

	def __array_finalize__(self,obj):

		if obj is None: return

		self.grid = getattr(obj,'grid',None)
		self.axis = getattr(obj,'axis',None)

	def __getattr__(self,key):

		("dims","area","volume","depth","poro","perm")

		unit = key[1:] if key.startswith('_') else key	

		if unit in ("volume","depth","poro"):
			return getattr(self.grid,key)[self,0]

		if unit[0] not in ("x","y","z"):
			return

		if unit[1:] in ("dims","area","perm"):
			return getattr(self.grid,key)[self,0]

def regcuboid(dims:tuple,nums:tuple,flodim:int=None):
	"""
	dims 	: reservoir dimensions (length x width x height)

	length 	: length of reservoir in ft, (x direction)
	width 	: width of reservoir in ft, (y direction)
	height 	: height of reservoir in ft, (z direction)

	num 	: number of grids, (Nlength, Nwidth, Nheight)

	flodim 	: flow dimension it can be 1, 2, or 3
	"""

	xdelta = numpy.repeat(dims[0]/num[0],num[0])
	ydelta = numpy.repeat(dims[1]/num[1],num[1])
	zdelta = numpy.repeat(dims[2]/num[2],num[2])

	return RectCuboid(xdelta,ydelta,zdelta,flodim)

if __name__ == "__main__":

	# cells = Hexahedron(
	# 	((-5,-5,5),(5,-5,5)),
	# 	((5,-5,5),(15,-5,5)),
	# 	((5,-5,-5),(15,-5,-5)),
	# 	((-5,-5,-5),(5,-5,-5)),
	# 	((-5,5,5),(5,5,5)),
	# 	((5,5,5),(15,5,5)),
	# 	((5,5,-5),(15,5,-5)),
	# 	((-5,5,-5),(5,5,-5)),
	# )

	# print(cells.unormal1)

	# print(cells.center)

	# print(cells.center1)
	# print(cells.center2)
	# print(cells.center3)
	# print(cells.center4)
	# print(cells.center5)
	# print(cells.center6)

	# print(cells.volume)

	# grids = RectCuboid((4,1,1))

	# print(grids.gplat)
	# print(grids.area)
	# print(grids.zaxis)
	# print(grids.volume)

	grid = RectCuboid((750,1000,1250),(750,1000,1250),(20,))

	# print(grid.size)

	# print(grid.size_test)

	# print(grid.size_test.ypos)

	print(grid.xneg1._area)

	# print(area.xmin)