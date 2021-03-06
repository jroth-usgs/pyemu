from __future__ import print_function, division
import os
import copy
import math
import numpy as np
import pandas as pd
from pyemu.en import ParameterEnsemble,ObservationEnsemble
from pyemu.mat import Cov, Matrix
from pyemu.pst import Pst


class EnsembleSmoother():

    def __init__(self,pst,parcov=None,obscov=None):
        assert isinstance(pst,Pst)
        self.pst = pst
        if parcov is not None:
            assert isinstance(parcov,Cov)
        else:
            parcov = Cov.from_parameter_data(self.pst)
        if obscov is not None:
            assert isinstance(obscov,Cov)
        else:
            obscov = Cov.from_observation_data(pst)

        self.parcov = parcov
        self.obscov = obscov

        self.__initialized = False
        self.num_reals = 0
        self.half_parcov_diag = None
        self.half_obscov_diag = None
        self.delta_par_prior = None
        self.iter_num = 0


    def initialize(self,num_reals):
        '''
        (re)initialize the process
        '''
        self.num_reals = int(num_reals)
        self.parensemble = ParameterEnsemble(self.pst)
        self.parensemble.draw(cov=self.parcov,num_reals=num_reals)

        self.obsensemble_0 = ObservationEnsemble(self.pst)
        self.obsensemble_0.draw(cov=self.obscov,num_reals=num_reals)
        self.obsensemble = self.obsensemble_0.copy()

        if self.parcov.isdiagonal:
            self.half_parcov_diag = self.parcov.inv.sqrt
        else:
            self.half_parcov_diag = Cov(x=np.diag(self.parcov.x),
                                        names=self.parcov.col_names,
                                        isdiagonal=True).inv.sqrt
        #if self.obscov.isdiagonal:
        #self.half_obscov_inv = self.obscov.inv.sqrt
       # else:
        #    self.half_obscov_diag = Cov(x=np.diag(self.obscov.x),
        #                                names=self.obscov.col_names,
        #                                isdiagonal=True)

        self.delta_par_prior = self._calc_delta_par()

        self.__initialized = True

    def _calc_delta_par(self):
        '''
        calc the scaled parameter ensemble differences from the mean
        '''
        mean = np.array(self.parensemble.mean(axis=0))
        delta = self.parensemble.as_pyemu_matrix()
        for i in range(self.num_reals):
            delta.x[i,:] -= mean
        #delta = Matrix(x=(self.half_parcov_diag * delta.transpose()).x,
        #               row_names=self.parensemble.columns)
        delta = self.half_parcov_diag * delta.T
        return delta * (1.0 / np.sqrt(float(self.num_reals - 1.0)))

    def _calc_delta_obs(self):
        '''
        calc the scaled observation ensemble differences from the mean
        '''

        mean = np.array(self.obsensemble.mean(axis=0))
        delta = self.obsensemble.as_pyemu_matrix()
        for i in range(self.num_reals):
            delta.x[i,:] -= mean
        delta = self.obscov.inv.sqrt * delta.T
        return delta * (1.0 / np.sqrt(float(self.num_reals - 1.0)))


    def _calc_obs(self):
        '''
        propagate the ensemble forward...
        '''
        self.parensemble.to_csv(os.path.join("smoother","sweep_in.csv"))
        os.chdir("smoother")
        print(os.listdir('.'))
        os.system("sweep freyberg.pst")
        os.chdir('..')
        obs = ObservationEnsemble.from_csv(os.path.join(\
                "smoother",'sweep_out.csv'))
        obs.columns = [item.lower() for item in obs.columns]
        self.obsensemble = ObservationEnsemble.from_dataframe(df=obs.loc[:,self.obscov.row_names],pst=self.pst)
        #todo: modifiy sweep to be interactive...
        return

    @property
    def current_lambda(self):
        return 10.0

    def update(self):
        if not self.__initialized:
            raise Exception("must call initialize() before update()")
        self._calc_obs()
        delta_obs = self._calc_delta_obs()
        u,s,v = delta_obs.pseudo_inv_components()
        #print(v)
        #print(s)
        #print(v)
        diff = self.obsensemble.as_pyemu_matrix() - self.obsensemble_0.as_pyemu_matrix()
        #print(diff)
        x1 = u.T * self.obscov.inv.sqrt * diff.T
        x1.autoalign = False
        #print(x1)
        x2 = (Cov.identity_like(s) + s**2).inv * x1
        #print(x2)
        x3 = v * s * x2
        #print(x3)
        upgrade_1 = (self.half_parcov_diag * self._calc_delta_par() * x3).to_dataframe()
        upgrade_1.index.name = "parnme"
        print(upgrade_1)
        self.parensemble += upgrade_1.T
        print(self.parensemble)
        if self.iter_num > 0:
            raise NotImplementedError()

        print(upgrade_1.shape)

