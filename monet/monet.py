from __future__ import absolute_import, print_function

from builtins import object

# This is the new driver for MONET
# import verify


class MONET(object):
    def __init__(self):
        self.model = None
        self.obs = None
        self.combined = None
        self.verify = None

    def add_model(self, model='CMAQ', **kwargs):
        """Short summary.

        Parameters
        ----------
        model : type
            Description of parameter `model` (the default is 'CMAQ').
        **kwargs : type
            Description of parameter `**kwargs`.

        Returns
        -------
        type
            Description of returned object.

        """
        """ adds model to monet object

                 for more information on kwargs see: self.add_cmaq
                                           self.add_camx
         """
        if model.upper() == 'CMAQ':
            self.add_cmaq(**kwargs)
        if model.upper() == 'CAMX':
            self.add_camx(**kwargs)

    def add_cmaq(self, gridcro2d=None, emission=None, metcro2d=None, metcro3d=None, depn=None, conc=None):
        """Short summary.

        Parameters
        ----------
        gridcro2d : type
            Description of parameter `gridcro2d` (the default is None).
        emission : type
            Description of parameter `emission` (the default is None).
        metcro2d : type
            Description of parameter `metcro2d` (the default is None).
        metcro3d : type
            Description of parameter `metcro3d` (the default is None).
        depn : type
            Description of parameter `depn` (the default is None).
        conc : type
            Description of parameter `conc` (the default is None).

        Returns
        -------
        type
            Description of returned object.

        """
        from .models.cmaq import CMAQ
        self.model = CMAQ()
        if gridcro2d is not None:
            self.model.set_gridcro2d(gridcro2d)
        if emission is not None:
            self.model.open_cmaq(emission)
        if metcro2d is not None:
            self.model.open_cmaq(metcro2d)
        if metcro3d is not None:
            self.model.open_cmaq(metcro3d)
        if depn is not None:
            self.model.open_cmaq(depn)
        if conc is not None:
            self.model.open_cmaq(conc)

    def add_camx(self, met2d=None, sfc2d=None, cld3d=None, kv=None, met3d=None, avrg=None, emission=None, depn=None):
        """Short summary.

        Parameters
        ----------
        met2d : type
            Description of parameter `met2d` (the default is None).
        sfc2d : type
            Description of parameter `sfc2d` (the default is None).
        cld3d : type
            Description of parameter `cld3d` (the default is None).
        kv : type
            Description of parameter `kv` (the default is None).
        met3d : type
            Description of parameter `met3d` (the default is None).
        avrg : type
            Description of parameter `avrg` (the default is None).
        emission : type
            Description of parameter `emission` (the default is None).
        depn : type
            Description of parameter `depn` (the default is None).

        Returns
        -------
        type
            Description of returned object.

        """
        from .models.camx import CAMx
        self.model = CAMx()
        if met2d is not None:
            self.model.set_gridcro2d(met2d)
        if sfc2d is not None:
            self.model.open_cmaq(sfc2d)
        if cld3d is not None:
            self.model.open_cmaq(cld3d)
        if kv is not None:
            self.model.open_cmaq(kv)
        if met3d is not None:
            self.model.open_cmaq(met3d)
        if avrg is not None:
            self.model.open_cmaq(avrg)
        if emission is not None:
            self.model.open_cmaq(emission)
        if depn is not None:
            self.model.open_cmaq(depn)

    def add_obs(self, obs='AirNOW', **kwargs):
        """Short summary.

        Parameters
        ----------
        obs : type
            Description of parameter `obs` (the default is 'AirNOW').
        **kwargs : type
            Description of parameter `**kwargs`.

        Returns
        -------
        type
            Description of returned object.

        """
        if obs.upper() == 'AIRNOW':
            self.add_airnow(**kwargs)
        if obs.upper() == 'AERONET':
            self.add_aeronet(**kwargs)
        if obs.upper() == 'TOLNET':
            self.add_tolnet(**kwargs)
        if obs.upper() == 'AQS':
            self.add_aqs(**kwargs)
        if obs.upper() == 'ISH':
            self.add_ish(**kwargs)
        if obs.upper() == 'CRN':
            self.add_crn(**kwargs)
        if obs.upper() == 'IMPROVE':
            self.add_improve(**kwargs)

    def add_airnow(self, dates=[]):
        """Short summary.

        Parameters
        ----------
        dates : type
            Description of parameter `dates` (the default is []).

        Returns
        -------
        type
            Description of returned object.

        """
        from .obs.airnow import AirNow
        self.obs = AirNow()
        self.obs.dates = dates
        self.obs.aggragate_files()

    def add_aqs(self, dates=[], daily=False):
        """Short summary.

        Parameters
        ----------
        dates : type
            Description of parameter `dates` (the default is []).
        daily : type
            Description of parameter `daily` (the default is False).

        Returns
        -------
        type
            Description of returned object.

        """
        from .obs.aqs import AQS
        self.obs = AQS()
        if daily:
            self.obs.load_all_daily_data(dates)
        else:
            self.obs.load_all_hourly_data(dates)

    def add_aeronet(self, dates=[], latlonbox=None):
        """Short summary.

        Parameters
        ----------
        dates : type
            Description of parameter `dates` (the default is []).
        latlonbox : type
            Description of parameter `latlonbox` (the default is None).

        Returns
        -------
        type
            Description of returned object.

        """
        from .obs.aeronet import AERONET
        self.obs = AERONET()
        self.obs.dates = dates
        self.obs.latlonbox = latlonbox
        self.obs.build_url()
        self.obs.read_aeronet()

    def add_tolnet(self, fname=None):
        """Short summary.

        Parameters
        ----------
        fname : type
            Description of parameter `fname` (the default is None).

        Returns
        -------
        type
            Description of returned object.

        """
        from .obs.tolnet import TOLNET
        self.obs = TOLNet()
        if fname is not None:
            self.obs.open_data(fname)

    def add_ish(self):
        print('this is a dummy right now')

    def add_crn(self):
        print('this is a dummy right now')

    def add_improve(self):
        print('this is a dummy right now')

    def combine(self):
        """Short summary.

        Returns
        -------
        type
            Description of returned object.

        """
        if self.model is not None and self.obs is not None:
            from .verification.combine import combine as pair
            self.combined = pair(model=self.model, obs=self.obs)
            from .verification.verify import VERIFY
            self.verify = VERIFY(model=self.model, obs=self.obs, dset=self.combined)
