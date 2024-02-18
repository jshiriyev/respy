import matplotlib.pyplot as plt

import numpy

from scipy.sparse import linalg

from scipy.sparse import identity
from scipy.sparse import diags
from scipy.sparse import csr_matrix as csr

# It should include Slightly Compressible and Compressible Flows

class Tclass():

    def __init__(self,grid):

        self.grid = grid

        self.set_delta()
        self.set_perm()
        self.set_static()

    def set_delta(self):
        """delta has the shape of (number of grid, flow dimension x 2),
        and the columns are dx_m, dx_p, dy_m, dy_p, dz_m, dz_p."""

        self._delta = numpy.zeros((self.grid.numtot,self.grid.dimension*2))

        # self._delta = (self.grid._size+self.grid._size[self.grid.index[:,1:],:])/2

        self._delta[:,0] = (self.grid._size[:,0]+self.grid._size[self.grid.index[:,1],0])/2
        self._delta[:,1] = (self.grid._size[:,0]+self.grid._size[self.grid.index[:,2],0])/2

        if self.grid.dimension>1:
            self._delta[:,2] = (self.grid._size[:,1]+self.grid._size[self.grid.index[:,3],1])/2
            self._delta[:,3] = (self.grid._size[:,1]+self.grid._size[self.grid.index[:,4],1])/2

        if self.grid.dimension>2:
            self._delta[:,4] = (self.grid._size[:,2]+self.grid._size[self.grid.index[:,5],2])/2
            self._delta[:,5] = (self.grid._size[:,2]+self.grid._size[self.grid.index[:,6],2])/2

    def set_perm(self):
        """perm has the shape of (number of grid, flow dimension x 2),
        and the columns are kx_m, kx_p, ky_m, ky_p, kz_m, kz_p."""

        self._perm = numpy.zeros((self.grid.numtot,self.grid.dimension*2))

        self._perm[:,0] = (2*self._delta[:,0])/(self.grid._size[:,0]/self.grid._perm[:,0]+
            self.grid._size[self.grid.index[:,1],0]/self.grid._perm[self.grid.index[:,1],0])
        self._perm[:,1] = (2*self._delta[:,1])/(self.grid._size[:,0]/self.grid._perm[:,0]+
            self.grid._size[self.grid.index[:,2],0]/self.grid._perm[self.grid.index[:,2],0])

        if self.grid.dimension>1:
            self._perm[:,2] = (2*self._delta[:,2])/(self.grid._size[:,1]/self.grid._perm[:,1]+
                self.grid._size[self.grid.index[:,3],1]/self.grid._perm[self.grid.index[:,3],1])
            self._perm[:,3] = (2*self._delta[:,3])/(self.grid._size[:,1]/self.grid._perm[:,1]+
                self.grid._size[self.grid.index[:,4],1]/self.grid._perm[self.grid.index[:,4],1])

        if self.grid.dimension>2:
            self._perm[:,4] = (2*self._delta[:,4])/(self.grid._size[:,2]/self.grid._perm[:,2]+
                self.grid._size[self.grid.index[:,5],2]/self.grid._perm[self.grid.index[:,5],2])
            self._perm[:,5] = (2*self._delta[:,5])/(self.grid._size[:,2]/self.grid._perm[:,2]+
                self.grid._size[self.grid.index[:,6],2]/self.grid._perm[self.grid.index[:,6],2])

    def set_static(self):
        """static part of the transmissibility values,
        has the shape of (number of grids, flow dimension x 2)."""
        self._static = (self._perm*self.grid._area)/(self._delta)

    def array(self,fluid):
        """transmissibility arrays of the size (number of grids, flow dimension x 2)"""
        return self._static/fluid._viscosity

    def Tmatrix(self,array):

        tmatrix = csr(self.shape)

        tmatrix = self.Tcharge(tmatrix,0,array)
        tmatrix = self.Tcharge(tmatrix,1,array)

        if self.grid.dimension>1:
            tmatrix = self.Tcharge(tmatrix,2,array)
            tmatrix = self.Tcharge(tmatrix,3,array)

        if self.grid.dimension>2:
            tmatrix = self.Tcharge(tmatrix,4,array)
            tmatrix = self.Tcharge(tmatrix,5,array)

        return tmatrix

    def Tcharge(self,tmatrix:csr,column:int,array:numpy.ndarray):
        """
        Returns updated transmissibility matrix:

        tmatrix : csr_matrix object defined for transmissibility matrix
 
        column  : integer indicating the direction:
            0   : xmin direction
            1   : xmax direction
            2   : ymin direction
            3   : ymax direction
            4   : zmin direction
            5   : zmax direction

        array   : transmissibility array with the size of
                  (number of grids, 2*dimension) and float type

        The transmissibility matrix is updated for:

        1. transmissibility matrix diagonal entries 
        2. transmissibility matrix offset entries

        """
        notOnBorder = ~(self.grid.index[:,0]==self.grid.index[:,column+1])

        # indices of grids not located at the border for the given direction
        diag_indices = (self.grid.index[notOnBorder,0],self.grid.index[notOnBorder,0])

        # indices of neighbor grids in that direction
        offs_indices = (self.grid.index[notOnBorder,0],self.grid.index[notOnBorder,column+1])

        tmatrix += csr((array[notOnBorder,column],diag_indices),shape=tmatrix.shape)
        tmatrix -= csr((array[notOnBorder,column],offs_indices),shape=tmatrix.shape)

        return tmatrix

    def Jmatrix(self,array,*pconst):
        """
        array   : transmissibility array of size (number of grids, flow dimension x 2)
        columns : integer indicating the direction where the
            constant pressure boundary condition is implemented:

            0   : xmin direction
            1   : xmax direction
            2   : ymin direction
            3   : ymax direction
            4   : zmin direction
            5   : zmax direction

        Return J matrix filled with 2 x transmissibility values.

        """

        jmatrix = csr(self.shape)

        for column, _ in pconst:

            fringes = (self.grid.index[:,0]==self.grid.index[:,column+1])

            indices = (self.grid.index[fringes,0],self.grid.index[fringes,0])

            jmatrix += csr((2*array[fringes,column],indices),shape=self.shape)

        return jmatrix

    def Amatrix(self,tstep):

        pore_volume = self.grid._volume*self.grid._poro

        return diags(pore_volume.flatten()/tstep)

    def Qvector(self,array,*pconst):
        """
        array    : transmissibility array of size (number of grids, flow dimension x 2)
        pconst   : constant pressure boundary condition tuple (column,pressure)
        columns  : integer indicating the direction where the
            constant pressure boundary condition is implemented:

            0    : xmin direction
            1    : xmax direction
            2    : ymin direction
            3    : ymax direction
            4    : zmin direction
            5    : zmax direction

        pressure : the value of the constant pressure in psi.

        Return Q vector filled with 2 x transmissibility x pressure values.

        """

        shape = (self.grid.numtot,1)

        qvector = csr(shape)

        for column,pressure in pconst:

            fringes = (self.grid.index[:,0]==self.grid.index[:,column+1])

            indices = (self.grid.index[fringes,0],numpy.zeros(fringes.sum()))

            qvector += csr((2*array[fringes,column]*pressure*6894.76,indices),shape=shape)

        return qvector

    def Gvector(self,array,fluid):

        return fluid._density*self.gravity*self.Tmatrix(array).dot(self.grid._depth)

    @property
    def gravity(self):
        return 9.807

    @property
    def shape(self):
        return (self.grid.numtot,self.grid.numtot)

    @staticmethod
    def toSI(value):
        """Converts transmissibility value from
        Oil Field Units to SI Units."""
        return value/(3.28084**3*(24*60*60)*6894.76)

    @staticmethod
    def toFU(value):
        """Converts transmissibility value from
        SI Units to Oil Field Units."""
        return value*(3.28084**3*(24*60*60)*6894.76)

class Well:

    def __init__(self,name:str,block:tuple,sort:str,radius:float,skin:float):
        """It is a well dictionary used in the simulator.
        
        name    : name of the well
        block   : block indices containing the well 
        sort    : vertical or horizontal

        raidus  : well radius, ft
        skin    : skin factor of the well, dimensionless

        """
        self._name   = name
        self._block  = block
        self._sort   = sort

        self._radius = radius*0.3048
        self._skin   = skin

        self._conds  = []

    def add(self,cond:str,value:float,time:float=0):
        """Adds a well condition to the conds property of the well:

        cond    : constant RATE or constant BHP
        value   : the value of constant RATE or BHP
        time    : the time for implementing the condition, days
        """
        self._conds.append((cond,value,time*24*60*60))

    @property
    def name(self):
        return self._name

    @property
    def block(self):
        return self._block

    @property
    def sort(self):
        return self._sort

    @property
    def radius(self):
        return self._radius

    @property
    def skin(self):
        return self._skin

    @property
    def conds(self):
        return self._conds  

class MixedSolver():
    """
    This class solves for single phase reservoir flow in Rectangular Cuboids.
    """

    def __init__(self,grid,fluid,well=None,theta=0):
        """
        grid  : It is a RecCuboid (rectangular cuboid) object.

        fluid : There is only one mobile phase in the system. There can be
            two slightly compressible fluids where the second one is at irreducible
            saturation, not mobile.
        
        well  : well schedule object.

        theta : solution type determined in the mixed solver
            when theta = 0, it reduces to Implicit method
            when theta = 1, it reduces to Explicit method
            when theta = 1/2, it is Crank-Nicolson method

        """

        self.grid  = grid
        self.fluid = fluid
        self.well  = well

        self.theta = theta

        self.tclass = Tclass(self.grid)

    def set_time(self,tstep:float,total:float=None,nstep:int=1):
        """
        tstep   : time step defined in days
        total   : total simulation time defined in days
        nstep   : number of time steps
        """

        self._tstep = tstep*24*60*60

        if total is None:
            self._ttime = self._tstep*nstep
            self._nstep = nstep
        else:
            self._ttime = total*24*60*60
            self._nstep = int(self._ttime/self._tstep)

        self._time = numpy.arange(
            self._tstep,self._ttime+self._tstep/2,self._tstep)

    def initialize(self,pref,ctotal):
        """Initializing the reservoir pressure
        
        pref    : reference depth and pressure,
                  tuple of (depth in ft, pressure in psi)

        ctotal  : total compressibility 1/psi
        """

        depth,pressure = pref

        depth_diff = (self.grid._depth-depth*0.3048)

        hydro_diff = self.fluid._density*self.tclass.gravity*depth_diff

        self._pinit = pressure*6894.76+hydro_diff

        self._ctotal = ctotal/6894.76

        self._pressure = numpy.zeros((self.grid.numtot,self._time.size))

    def solve(self,pconsts):

        array = self.tclass.array(self.fluid)

        P = self._pinit

        T = self.tclass.Tmatrix(array)
        J = self.tclass.Jmatrix(array,*pconsts)
        A = self.tclass.Amatrix(self._tstep)
        Q = self.tclass.Qvector(array,*pconsts)
        G = self.tclass.Gvector(array,self.fluid)
        
        for k in range(self.nstep):

            if self.theta==0:
                P = self.implicit(P,T,J,A,Q,G)
            elif self.theta==1:
                P = self.explicit(P,T,J,A,Q,G)
            else:
                P = self.mixed(P,T,J,A,Q,G)

            print(f"{k} time step is complete...")
            
            self._pressure[:,k] = P

            P = P.reshape((-1,1))

    def implicit(self,P,T,J,A,Q,G):

        Act = A*self._ctotal

        return linalg.spsolve(T+J+Act,csr.dot(Act,P)+Q+G)

    def mixed(self,P,T,J,A,Q,G):

        Act = A*self._ctotal

        LHS = (1-self.theta)(T+J)+Act
        RHS = csr.dot(Act-self.theta*(T+J),P)+Q+G

        return linalg.spsolve(LHS,RHS)

    def explicit(self,P,T,J,A,Q,G):

        Act = A*self._ctotal

        return P+linalg.spsolve(Act,csr.dot(-(T+J),P)+Q+G)

    def postprocess(self):

        Y = int((self.grid.numtot-1)/2)

        Pwf = self.pressure[Y,:]+self.Q[Y]/self.JR*self.Fluids.viscosity[0]

        return Pwf

    @property
    def shape(self):
        return (self.grid.numtot,self.grid.numtot)

    @property
    def pinit(self):
        return self._pinit/6894.76

    @property
    def ctotal(self):
        return self._ctotal*6894.76

    @property
    def tstep(self):
        return self._tstep/(24*60*60)

    @property
    def ttime(self):
        return self._ttime/(24*60*60)

    @property
    def nstep(self):
        return self._nstep
    
    @property
    def time(self):
        return self._time/(24*60*60)

    @property
    def pressure(self):
        return self._pressure/6894.76
    
def newton_solver(grid,timestep,timesteps,T,J,Q):

    array = np.zeros((grid.numtot,timesteps))

    P = grid.pressure_initial

    for j in range(timesteps):

        Pk = P.copy()

        error = 1

        k = 1

        while error>1e-6:

            A = np.diag(100/Pk.flatten())

            F = -np.matmul(T+J+A,Pk)+np.matmul(A,P)+Q

            error = np.linalg.norm(F.flatten(),2)

            JACOB = -(T+J)+np.matmul(-A,np.diag(P.flatten()/Pk.flatten()))

            Pk += np.linalg.solve(JACOB,-F)

            print(f"iteration #{k}: {error = }")
            print(f"{Pk}\n")#{F}\n

            k += 1

        P = Pk.copy()

        array[:,j] = P.flatten()

    return array

def picard_solver(grid,timestep,timesteps,T,J,Q):

    array = np.zeros((grid.numtot,timesteps))

    P = grid.pressure_initial

    for j in range(timesteps):

        Pk = P.copy()

        firstIteration = True

        k = 1

        while firstIteration or error>1e-6:

            firstIteration = False

            A = np.eye(grid.numtot)*100/Pk

            D = T+J+A

            V = np.matmul(A,P)+Q

            F = -np.matmul(D,Pk)+V

            error = np.linalg.norm(F,2)

            Pk = np.linalg.solve(D,V)

            print(f"iteration #{k}: {error=}")
            print(f"{Pk}\n")

            k += 1

        P = Pk.copy()

        array[:,j] = P.flatten()

    return array

if __name__ == "__main__":

    import unittest

    from tests import test_porous_media

    unittest.main(test_porous_media)