from dataclasses import dataclass

@dataclass(frozen=True)
class Boundary:

    #shape factor, {C_A} value
    factor: float

    # PSS is exact for higher values
    time1: float
    # PSS gives less than 1% error for higher values
    time2: float = None
    # Use infinite system solution with less than 1 % Error for lesser values
    time3: float = None

class Pseudo():

    gamma = 1.781

    GEOMETRY = {
    "circle": Boundary(31.62,0.1),
    "triangle": Boundary(27.6,0.2),
    "square": Boundary(30.8828,0.1),
    "hexagon": Boundary(31.6,0.1),
    }

    def __init__(self,flow_rate,shape="circle"):

        if shape=="square" or shape=="rectangle":
            geo = "rectangle"
        elif shape=="circle" or shape=="ellipse":
            geo = "ellipse"

        self.PorRock = PorRock(geo=geo)(window=None)

        self.set_shapefactor(shape)
        
        # There can be two slightly compressible fluids where the
        # second one is at irreducible saturation, not mobile

        self.Fluids = Fluids()(number=2)

        self.Well = Wells()(number=1)

        self.Well.set_flowconds("rate",flow_rate,"mobfluid")

    def initialize(self,pressure0,Swirr=0,ctotal=None):

        steady.initialize(self,pressure0,Swirr,ctotal)

    def set_tmin(self):

        self.tmin = self.exactdimtime*self.PorRock.area/self.diffusivity

    def set_tmax(self,tmax=None):

        if tmax is None:
            tmax = self.tmin+1_000_000

        self.tmax = tmax

    def set_times(self,times=None,timespace="linear"):

        if not hasattr(self,"tmin"):
            self.set_tmin()

        if not hasattr(self,"tmax"):
            self.set_tmax()

        if times is None:
            if timespace=="linear":
                times = np.linspace(self.tmin,self.tmax,1000)
            elif timespace=="log":
                times = np.logspace(np.log10(self.tmin),np.log10(self.tmax),1000)
        else:
            validtimes = times>self.tmin
            times = times[validtimes]

        self.times = times.reshape((1,-1))

    def solve(self):

        if not hasattr(self,"times"):
            self.set_times()

        rateNumer = self.Well.limits*self.Fluids.viscosity[0]
        rateDenom = self.PorRock.permeability*self.PorRock.thickness

        constRate = (rateNumer)/(2*np.pi*rateDenom)

        inner1 = (4*self.PorRock.area)/(self.gamma*self.shapefactor*self.Well.radii[0]**2)
        inner2 = 2*np.pi*self.diffusivity*self.times/self.PorRock.area

        self.deltap = constRate*(1/2*np.log(inner1)+inner2)

        self.pressure = self.pressure0-self.deltap
