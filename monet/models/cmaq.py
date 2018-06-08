from __future__ import absolute_import, division, print_function

# This file is to deal with CMAQ code - try to make it general for cmaq 4.7.1 --> 5.1
from builtins import object, zip
from gc import collect

import pandas as pd
import xarray as xr
from dask.diagnostics import ProgressBar
from numpy import array, zeros
from past.utils import old_div

from monet.models.basemodel import BaseModel

ProgressBar().register()


class CMAQ(BaseModel):
    def __init__(self):
        self.grid = None
        BaseModel.__init__(self)
        self.objtype = 'CMAQ'
        self.dust_pm25 = array([
            'ASO4J', 'ANO3J', 'ACLJ', 'ANH4J', 'ANAJ', 'ACAJ', 'AMGJ', 'AKJ',
            'APOCJ', 'APNCOMJ', 'AECJ', 'AFEJ', 'AALJ', 'ASIJ', 'ATIJ', 'AMNJ',
            'AOTHRJ'
        ])
        self.dust_total = array([
            'ASO4J', 'ASO4K', 'ANO3J', 'ANO3K', 'ACLJ', 'ACLK', 'ANH4J',
            'ANAJ', 'ACAJ', 'AMGJ', 'AKJ', 'APOCJ', 'APNCOMJ', 'AECJ', 'AFEJ',
            'AALJ', 'ASIJ', 'ATIJ', 'AMNJ', 'AOTHRJ', 'ASOIL'
        ])
        self.aitken = array([
            'ACLI', 'AECI', 'ANAI', 'ANH4I', 'ANO3I', 'AOTHRI', 'APNCOMI',
            'APOCI', 'ASO4I', 'AORGAI', 'AORGPAI', 'AORGBI'
        ])
        self.accumulation = array([
            'AALJ', 'AALK1J', 'AALK2J', 'ABNZ1J', 'ABNZ2J', 'ABNZ3J', 'ACAJ',
            'ACLJ', 'AECJ', 'AFEJ', 'AISO1J', 'AISO2J', 'AISO3J', 'AKJ',
            'AMGJ', 'AMNJ', 'ANAJ', 'ANH4J', 'ANO3J', 'AOLGAJ', 'AOLGBJ',
            'AORGCJ', 'AOTHRJ', 'APAH1J', 'APAH2J', 'APAH3J', 'APNCOMJ',
            'APOCJ', 'ASIJ', 'ASO4J', 'ASQTJ', 'ATIJ', 'ATOL1J', 'ATOL2J',
            'ATOL3J', 'ATRP1J', 'ATRP2J', 'AXYL1J', 'AXYL2J', 'AXYL3J',
            'AORGAJ', 'AORGPAJ', 'AORGBJ'
        ])
        self.coarse = array(
            ['ACLK', 'ACORS', 'ANH4K', 'ANO3K', 'ASEACAT', 'ASO4K', 'ASOIL'])
        self.noy_gas = array([
            'NO', 'NO2', 'NO3', 'N2O5', 'HONO', 'HNO3', 'PAN', 'PANX', 'PNA',
            'NTR', 'CRON', 'CRN2', 'CRNO', 'CRPX', 'OPAN'
        ])
        self.pec = array(['AECI', 'AECJ'])
        self.pso4 = array(['ASO4I', 'ASO4J'])
        self.pno3 = array(['ANO3I', 'ANO3J'])
        self.pnh4 = array(['ANH4I', 'ANH4J'])
        self.pcl = array(['ACLI', 'ACLJ'])
        self.poc = array([
            'AOTHRI', 'APNCOMI', 'APOCI', 'AORGAI', 'AORGPAI', 'AORGBI',
            'ATOL1J', 'ATOL2J', 'ATOL3J', 'ATRP1J', 'ATRP2J', 'AXYL1J',
            'AXYL2J', 'AXYL3J', 'AORGAJ', 'AORGPAJ', 'AORGBJ', 'AOLGAJ',
            'AOLGBJ', 'AORGCJ', 'AOTHRJ', 'APAH1J', 'APAH2J', 'APAH3J',
            'APNCOMJ', 'APOCJ', 'ASQTJ', 'AISO1J', 'AISO2J', 'AISO3J',
            'AALK1J', 'AALK2J', 'ABNZ1J', 'ABNZ2J', 'ABNZ3J', 'AORGAI',
            'AORGAJ', 'AORGPAI', 'AORGPAJ', 'AORGBI', 'AORGBJ'
        ])
        self.minerals = array([
            'AALJ', 'ACAJ', 'AFEJ', 'AKJ', 'AMGJ', 'AMNJ', 'ANAJ', 'ATIJ',
            'ASIJ'
        ])

    def get_dates(self):
        """Short summary.

        Returns
        -------
        type
            Description of returned object.

        """
        print('Reading CMAQ dates...')
        idims = len(self.dset.TFLAG.dims)
        if idims == 2:
            tflag1 = array(self.dset['TFLAG'][:, 0], dtype='|S7')
            tflag2 = array(
                self.dset['TFLAG'][:, 1] // 10000, dtype='|S6')
        else:
            tflag1 = array(self.dset['TFLAG'][:, 0, 0], dtype='|S7')
            tflag2 = array(
                self.dset['TFLAG'][:, 0, 1] // 10000, dtype='|S6')
        date = pd.to_datetime(
            [(i + j.zfill(2)).decode() for i, j in zip(tflag1, tflag2)], format='%Y%j%H')
        indexdates = pd.Series(date).drop_duplicates(keep='last').index.values
        self.dset = self.dset.isel(time=indexdates)
        self.dset['time'] = date[indexdates]

    def open_files(self, flist=None, grid=None):
        """Short summary.

        Parameters
        ----------
        flist : type
            Description of parameter `flist`.
        grid : type
            Description of parameter `grid`.

        Returns
        -------
        type
            Description of returned object.

        """
        self.set_gridcro2d(grid)
        self.add_files(flist)
        # for fname in flist:
        #     self.add_files(fname)

    def add_files(self, mfile):
        """Short summary.

        Parameters
        ----------
        mfile : type
            Description of parameter `mfile`.

        Returns
        -------
        type
            Description of returned object.

        """
        from glob import glob
        from numpy import sort
        nameset = {'COL': 'x', 'ROW': 'y', 'TSTEP': 'time', 'LAY': 'z'}
        if type(mfile) == str:
            fname = sort(array(glob(mfile)))
        else:
            fname = sort(array(mfile))
        if fname.shape[0] >= 1:
            if self.dset is None:
                self.dset = xr.open_mfdataset(
                    fname.tolist(), concat_dim='TSTEP').rename(nameset)
            else:
                dset = xr.open_mfdataset(
                    fname.tolist(), concat_dim='TSTEP').rename(nameset)
                self.dset = xr.merge([self.dset, dset])
        else:
            print('Files not found')
        if self.grid is not None:
            self.dset = self.dset.assign(latitude=self.grid.LAT.squeeze())
            self.dset = self.dset.assign(longitude=self.grid.LON.squeeze())
            self.dset = self.dset.set_coords(['latitude', 'longitude'])
        self.get_dates()
        self.keys = list(self.dset.keys())

    def check_z(self, varname):
        """Short summary.

        Parameters
        ----------
        varname : type
            Description of parameter `varname`.

        Returns
        -------
        type
            Description of returned object.

        """
        if pd.Series(self.dset[varname].dims).isin(['z']).max():
            return True
        else:
            return False

    def add_multiple_fields(self, findkeys, lay=None, weights=None):
        """Short summary.

        Parameters
        ----------
        findkeys : type
            Description of parameter `findkeys`.
        lay : type
            Description of parameter `lay`.
        weights : type
            Description of parameter `weights`.

        Returns
        -------
        type
            Description of returned object.

        """
        from numpy import ones
        keys = self.keys
        newkeys = pd.Series(findkeys).loc[pd.Series(findkeys).isin(
            keys)].values
        if weights is None:
            w = ones(len(newkeys))
        var = self.dset[newkeys[0]] * w[0]
        for i, j in zip(newkeys[1:], w[1:]):
            var = var + self.dset[i] * j
        return select_layer(var, lay=lay)
        # if self.check_z(newkeys[0]):
        #     if lay is not None:
        #         var = self.dset[newkeys[0]][:, 0, :, :].squeeze() * w[0]
        #         for i, j in zip(newkeys[1:], w[1:]):
        #             var += self.dset[i][:, 0, :, :].squeeze() * j
        #     else:
        #         var = self.dset[newkeys[0]][:, :, :, :].squeeze() * w[0]
        #         for i, j in zip(newkeys[1:], w[1:]):
        #             var += self.dset[i][:, :, :, :].squeeze() * j
        # else:
        #     var = self.dset[newkeys[0]][:, :, :].copy() * w[0]
        #     for i, j in zip(newkeys[1:], w[1:]):
        #         var += self.dset[i][:, :, :].squeeze() * j
        # return var

    @staticmethod
    def select_layer(variable, lay=None):
        if lay is not None:
            try:
                var = variable.sel(z=lay)
            except ValueError:
                print(
                    'Dimension \'z\' not in Dataset.  Returning Dataset anyway'
                )
                var = variable
        else:
            var = variable
        return var

    def get_dust_total(self, lay=None):
        """Short summary.

        Parameters
        ----------
        lay : type
            Description of parameter `lay`.

        Returns
        -------
        type
            Description of returned object.

        """
        return self.add_multiple_fields(self.dust_totl, lay=lay)

    def get_noy(self, lay=None):
        """Short summary.

        Parameters
        ----------
        lay : type
            Description of parameter `lay`.

        Returns
        -------
        type
            Description of returned object.

        """
        keys = self.keys
        if 'NOY' in keys:
            var = self.select_layer(self.dset['NOY'], lay=lay)
        else:
            var = self.add_multiple_fields(self.noy_gas, lay=lay)
        return var

    def get_nox(self, lay=None):
        """Short summary.

        Parameters
        ----------
        lay : type
            Description of parameter `lay`.

        Returns
        -------
        type
            Description of returned object.

        """
        var = self.add_multiple_fields(['NO', 'NO2'], lay=lay)
        return var

    def get_dust_pm25(self, lay=None):
        """Short summary.

        Parameters
        ----------
        lay : type
            Description of parameter `lay`.

        Returns
        -------
        type
            Description of returned object.

        """
        return self.add_multiple_fields(self.dust_pm25, lay=lay)

    def get_pm25(self, lay=None):
        """Short summary.

        Parameters
        ----------
        lay : type
            Description of parameter `lay`.

        Returns
        -------
        type
            Description of returned object.

        """
        from numpy import concatenate
        keys = self.keys
        allvars = concatenate([self.aitken, self.accumulation, self.coarse])
        weights = array([
            1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,
            1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,
            1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,
            1., 1., 1., 1., 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2
        ])
        if 'PM25_TOT' in keys:
            var = self.select_layer(self.dset['PM25_TOT'], lay=lay)
        else:
            index = pd.Series(allvars).isin(keys)
            newkeys = allvars[index]
            neww = weights[index]
            var = self.add_multiple_fields(newkeys, lay=lay, weights=neww)
        var.name = 'PM2.5'
        var['long_name'] = 'PM2.5'
        var['var_desc'] = 'Variable PM2.5'
        return var

    def get_pm10(self, lay=None):
        """Short summary.

        Parameters
        ----------
        lay : type
            Description of parameter `lay`.

        Returns
        -------
        type
            Description of returned object.

        """
        from numpy import concatenate
        keys = self.keys
        allvars = concatenate([self.aitken, self.accumulation, self.coarse])
        var = None
        if 'PMC_TOT' in keys:
            var = self.select_layer(self.dset['PMC_TOT'], lay=lay)
        elif 'PM10' in keys:
            var = self.select_layer(self.dset['PM10'], lay=lay)
        else:
            index = pd.Series(allvars).isin(keys)
            newkeys = allvars[index]
            neww = weights[index]
            var = self.add_multiple_fields(newkeys, lay=lay, weights=neww)
        var.name = 'PM10'
        var['long_name'] = 'PM10'
        var['var_desc'] = 'Variable PM10'
        return var

    def get_clf(self, lay=None):
        """Short summary.

        Parameters
        ----------
        lay : type
            Description of parameter `lay`.

        Returns
        -------
        type
            Description of returned object.

        """
        keys = self.keys
        allvars = array(['ACLI', 'ACLJ', 'ACLK'])
        weights = array([1, 1, .2])
        var = None
        if 'PM25_CL' in keys:
            var = self.select_layer(self.dset['PM25_CL'], lay=lay)
        else:
            index = pd.Series(allvars).isin(keys)
            newkeys = allvars[index]
            neww = weights[index]
            var = self.add_multiple_fields(newkeys, lay=lay, weights=neww)
        var.name = 'PM25_CL'
        var['long_name'] = 'PM25_CL'
        var['var_desc'] = 'Variable PM25_CL'
        return var

    def get_naf(self, lay=None):
        """Short summary.

        Parameters
        ----------
        lay : type
            Description of parameter `lay`.

        Returns
        -------
        type
            Description of returned object.

        """
        keys = self.keys
        allvars = array(['ANAI', 'ANAJ', 'ASEACAT', 'ASOIL', 'ACORS'])
        weights = array(
            [1, 1, .2 * 837.3 / 1000., .2 * 62.6 / 1000., .2 * 2.3 / 1000.])
        if 'PM25_NA' in keys:
            var = self.select_layer(self.dset['PM25_NA'], lay=lay)
        else:
            index = pd.Series(allvars).isin(keys)
            newkeys = allvars[index]
            neww = weights[index]
            var = self.add_multiple_fields(newkeys, lay=lay, weights=neww)
        var.name = 'PM25_NA'
        var['long_name'] = 'PM25_NA'
        var['var_desc'] = 'Variable PM25_NA'
        return var

    def get_kf(self, lay=None):
        """Short summary.

        Parameters
        ----------
        lay : type
            Description of parameter `lay`.

        Returns
        -------
        type
            Description of returned object.

        """
        keys = self.keys
        allvars = array(['AKI', 'AKJ', 'ASEACAT', 'ASOIL', 'ACORS'])
        weights = array(
            [1, 1, .2 * 31. / 1000., .2 * 24. / 1000., .2 * 17.6 / 1000.])
        if 'PM25_K' in keys:
            var = self.select_layer(self.dset['PM25_K'], lay=lay)
        else:
            index = pd.Series(allvars).isin(keys)
            newkeys = allvars[index]
            neww = weights[index]
            var = self.add_multiple_fields(newkeys, lay=lay, weights=neww)
        var.name = 'PM25_K'
        var['long_name'] = 'PM25_K'
        var['var_desc'] = 'Variable PM25_K'

        return var

    def get_caf(self, lay=None):
        keys = self.keys
        allvars = array(['ACAI', 'ACAJ', 'ASEACAT', 'ASOIL', 'ACORS'])
        weights = array(
            [1, 1, .2 * 32. / 1000., .2 * 83.8 / 1000., .2 * 56.2 / 1000.])
        if 'PM25_CA' in keys:
            var = self.select_layer(self.dset['PM25_CA'], lay=lay)
        else:
            index = pd.Series(allvars).isin(keys)
            newkeys = allvars[index]
            neww = weights[index.values]
            var = self.add_multiple_fields(newkeys, lay=lay, weights=neww)
        var.name = 'PM25_CA'
        var['long_name'] = 'PM25_CA'
        var['var_desc'] = 'Variable PM25_CA'
        return var
        """Short summary.

        Parameters
        ----------
        lay : type
            Description of parameter `lay`.

        Returns
        -------
        type
            Description of returned object.

        """

    def get_so4f(self, lay=None):
        keys = self.keys
        allvars = array(['ASO4I', 'ASO4J', 'ASO4K'])
        weights = array([1., 1., .2])
        if 'PM25_SO4' in keys:
            var = self.select_layer(self.dset['PM25_SO4'], lay=lay)
        else:
            index = pd.Series(allvars).isin(keys)
            newkeys = allvars[index]
            neww = weights[index.values]
            var = self.add_multiple_fields(newkeys, lay=lay, weights=neww)
        var.name = 'PM25_SO4'
        var['long_name'] = 'PM25_SO4'
        var['var_desc'] = 'Variable PM25_SO4'
        return var
        """Short summary.

        Parameters
        ----------
        lay : type
            Description of parameter `lay`.

        Returns
        -------
        type
            Description of returned object.

        """

    def get_nh4f(self, lay=None):
        keys = self.keys
        allvars = array(['ANH4I', 'ANH4J', 'ANH4K'])
        weights = array([1., 1., .2])
        var = None
        if 'PM25_NH4' in keys:
            var = self.select_layer(self.dset['PM25_NH4'], lay=lay)
        else:
            print('    Computing PM25_NH4...')
            index = pd.Series(allvars).isin(keys)
            newkeys = allvars[index]
            neww = weights[index]
            var = self.add_multiple_fields(newkeys, lay=lay, weights=neww)
        var.name = 'PM25_NH4'
        var['long_name'] = 'PM25_NH4'
        var['var_desc'] = 'Variable PM25_NH4'

        return var
        """Short summary.

        Parameters
        ----------
        lay : type
            Description of parameter `lay`.

        Returns
        -------
        type
            Description of returned object.

        """

    def get_no3f(self, lay=None):
        keys = self.keys
        allvars = array(['ANO3I', 'ANO3J', 'ANO3K'])
        weights = array([1., 1., .2])
        var = None
        if 'PM25_NO3' in keys:
            var = self.select_layer(self.dset['PM25_NO3'], lay=lay)
        else:
            index = pd.Series(allvars).isin(keys)
            newkeys = allvars[index]
            neww = weights[index]
            var = self.add_multiple_fields(newkeys, lay=lay, weights=neww)
        var.name = 'PM25_NO3'
        var['long_name'] = 'PM25_NO3'
        var['var_desc'] = 'Variable PM25_NO3'
        return var
        """Short summary.

        Parameters
        ----------
        lay : type
            Description of parameter `lay`.

        Returns
        -------
        type
            Description of returned object.

        """

    def get_ec(self, lay=None):
        keys = self.keys
        allvars = array(['AECI', 'AECJ'])
        weights = array([1., 1.])
        var = None
        if 'PM25_EC' in keys:
            var = self.select_layer(self.dset['PM25_EC'], lay=lay)
        else:
            index = pd.Series(allvars).isin(keys)
            newkeys = allvars[index]
            neww = weights[index]
            var = self.add_multiple_fields(newkeys, lay=lay, weights=neww)
        var.name = 'PM25_EC'
        var['long_name'] = 'PM25_EC'
        var['var_desc'] = 'Variable PM25_EC'

        return var
        """Short summary.

        Parameters
        ----------
        lay : type
            Description of parameter `lay`.

        Returns
        -------
        type
            Description of returned object.

        """

    def get_var(self, param, lay=None):
        p = param.upper()
        print(param)
        if p == 'PM25':
            var = self.get_pm25(lay=lay)
        elif p == 'PM10':
            var = self.get_pm10(lay=lay)
        elif p == 'PM25_DUST':
            var = self.get_dust_pm25(lay=lay)
        elif p == 'PM10_DUST':
            var = self.get_dust_total(lay=lay)
        elif p == 'NOX':
            var = self.get_nox(lay=lay)
        elif p == 'NOY':
            var = self.get_noy(lay=lay)
        elif p == 'CLF':
            var = self.get_clf(lay=lay)
        elif p == 'CAF':
            var = self.get_caf(lay=lay)
        elif p == 'NAF':
            var = self.get_naf(lay=lay)
        elif p == 'KF':
            var = self.get_kf(lay=lay)
        elif (p == 'SO4F') | (p == 'PM2.5_SO4'):
            var = self.get_so4f(lay=lay)
        elif p == 'NH4F':
            var = self.get_nh4f(lay=lay)
        elif (p == 'NO3F') | (p == 'PM2.5_NO3'):
            var = self.get_no3f(lay=lay)
        elif (p == 'PM2.5_EC') | (p == 'ECF'):
            var = self.get_ec(lay=lay)
        elif p == 'OC':
            var = self.get_oc(lay=lay)
        elif p == 'VOC':
            var = self.select_layer(self.dset['VOC'], lay=lay)
        elif p == 'RH':
            var = self.get_metcro2d_rh('param', lay=lay)
        else:
            var = self.select_layer(self.dset[param], lay=lay)
        return var
        """Short summary.

        Parameters
        ----------
        param : type
            Description of parameter `param`.
        lay : type
            Description of parameter `lay`.

        Returns
        -------
        type
            Description of returned object.

        """

    def get_metcro2d_rh(self, lay=None):
        import atmos
        data = {
            'T': self.dset['TEMP2'][:].compute().values,
            'rv': self.dset['Q2'][:].compute().values,
            'p': self.dset['PRSFC'][:].compute().values
        }
        if lay is None:
            a = atmos.calculate('RH', **data)[:, :, :, :].squeeze()
        else:
            atmos.calculate('RH', **data)[:, lay, :, :].squeeze()
        return a
        """Short summary.

        Parameters
        ----------
        lay : type
            Description of parameter `lay`.

        Returns
        -------
        type
            Description of returned object.

        """

    def set_gridcro2d(self, filename):
        """Short summary.

        Parameters
        ----------
        filename : type
            Description of parameter `filename`.

        Returns
        -------
        type
            Description of returned object.

        """
        self.grid = xr.open_dataset(filename).rename({
            'COL': 'x',
            'ROW': 'y'
        }).drop('TFLAG').squeeze()
        lat = 'LAT'
        lon = 'LON'
        self.latitude = self.grid[lat][:][:, :].squeeze()
        self.longitude = self.grid[lon][:][:, :].squeeze()
        #self.load_conus_basemap(res='l')

    # def load_conus_basemap(self, res='l'):
    #     from mpl_toolkits.basemap import Basemap
    #     if isinstance(self.map, type(None)):
    #         lat1 = self.grid.P_ALP
    #         lat2 = self.grid.P_BET
    #         lon1 = self.grid.P_GAM
    #         lon0 = self.grid.XCENT
    #         lat0 = self.grid.YCENT
    #         m = Basemap(
    #             projection='lcc',
    #             resolution=res,
    #             lat_1=lat1,
    #             lat_2=lat2,
    #             lat_0=lat0,
    #             lon_0=lon0,
    #             lon_1=lon1,
    #             llcrnrlat=self.latitude[0, 0],
    #             urcrnrlat=self.latitude[-1, -1],
    #             llcrnrlon=self.longitude[0, 0],
    #             urcrnrlon=self.longitude[-1, -1],
    #             rsphere=6371200.,
    #             area_thresh=50.)
    #         self.map = m
    #     else:
    #         m = self.map
    #     return self.map
