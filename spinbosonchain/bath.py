# Copyright 2021 D-Wave Systems Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

r"""Contains class definitions for the model components of the bath.

``spinbosonchain`` is a library for simulating the dynamics of a generalized
spin-boson chain model, where both the :math:`z`- and :math:`y`-components of
the spins are coupled to bosonic baths, rather than only the
:math:`z`-components. A convenient way to discuss both finite and infinite
chains is to express the Hamiltonian of the aforementioned spin-boson model as a
sum of :math:`2N+1` 'unit cell' Hamiltonians:

.. math ::
    \hat{H}\left(t\right)\equiv\sum_{u=-N}^{N}\hat{H}_{u}\left(t\right),
    :label: bath_total_Hamiltonian

where :math:`N` is a non-negative integer, and :math:`\hat{H}_{u}\left(t\right)`
is the Hamiltonian of the :math:`u^{\mathrm{th}}` 'unit cell' of the model:

.. math ::
    \hat{H}_{u}\left(t\right)=\hat{H}_{u}^{\left(A\right)}\left(t\right)
    +\hat{H}_{u}^{\left(B\right)}+\hat{H}_{u}^{\left(AB\right)},
    :label: bath_unit_cell_Hamiltonian

with :math:`\hat{H}_{u}^{\left(A\right)}\left(t\right)` being the system part of
:math:`\hat{H}_{u}\left(t\right)`, which encodes all information regarding
energies associated exclusively with the spins;
:math:`\hat{H}_{u}^{\left(B\right)}` being the bath part of
:math:`\hat{H}_{u}\left(t\right)`, which encodes all information regarding
energies associated with the components of the bosonic environment; and
:math:`\hat{H}_{u}^{\left(AB\right)}` is the system-bath coupling part of
:math:`\hat{H}_{u}\left(t\right)`, which describes all energies associated with
the coupling between the system and the environment.

:math:`\hat{H}_{u}^{\left(B\right)}` describes a collection of decoupled harmonic 
oscillators:

.. math ::
    \hat{H}_{u}^{\left(B\right)}=\sum_{r=0}^{L-1}\sum_{\epsilon}
    \left\{ \omega_{y;\epsilon}\hat{b}_{y;r+uL;\epsilon}^{\dagger}
    \hat{b}_{y;r+uL;\epsilon}^{\vphantom{\dagger}}
    +\omega_{z;\epsilon}\hat{b}_{z;r+uL;\epsilon}^{\dagger}
    \hat{b}_{z;r+uL;\epsilon}^{\vphantom{\dagger}}\right\},
    :label: bath_bath_hamiltonian

with :math:`\epsilon` being the oscillator mode index, :math:`L` being
the number of sites in every 'unit cell', and
:math:`\hat{b}_{\nu; r; \epsilon}^{\dagger}` and
:math:`\hat{b}_{\nu; r; \epsilon}^{\vphantom{\dagger}}` being the bosonic
creation and annihilation operators respectively for the harmonic oscillator at
site :math:`r` in mode :math:`\epsilon` with angular frequency 
:math:`\omega_{\nu; \epsilon}`, coupled to the :math:`\nu`-component of the spin
at the same site.

:math:`\hat{H}_{u}^{\left(AB\right)}\left(t\right)` is given by

.. math ::
    \hat{H}_{u}^{\left(AB\right)}=-\sum_{r=0}^{L-1}
    \left\{ \hat{\sigma}_{y;r+uL}\hat{\mathcal{Q}}_{y;r+uL}
    \left(t\right)+\hat{\sigma}_{z;r+uL}
    \hat{\mathcal{Q}}_{z;r+uL}\left(t\right)\right\},
    :label: bath_system_bath_hamiltonian

where :math:`\hat{\mathcal{Q}}_{\nu;r}(t)` is the generalized reservoir force 
operator at site :math:`r` that acts on the :math:`\nu`-component of the spin at
the same site:

.. math ::
    \hat{\mathcal{Q}}_{\nu;r+uL}\left(t\right)
    =\mathcal{E}_{\nu;r}^{\left(\lambda\right)}\left(t\right)\hat{Q}_{\nu;r+uL},
    :label: bath_generalized_reservoir_force

with :math:`\mathcal{E}_{\nu;r}^{(\lambda)}(t)` being a time-dependent energy
scale, :math:`\hat{Q}_{\nu;r}` being a rescaled generalized reservoir force:

.. math ::
    \hat{Q}_{\nu;r+uL}=-\sum_{\epsilon}\lambda_{\nu;r;\epsilon}
    \left\{ \hat{b}_{\nu;r+uL;\epsilon}^{\dagger}
    +\hat{b}_{\nu;r+uL;\epsilon}^{\vphantom{\dagger}}\right\},
    :label: bath_rescaled_generalized_reservoir_force

:math:`\lambda_{\nu;r;\epsilon}` being the coupling strength between the
:math:`\nu`-component of the spin at site :math:`r` and the harmonic oscillator 
at the same site in mode :math:`\epsilon`. 

For finite chains, we set :math:`N=0`. For infinite chains, we take the limit of
:math:`N\to\infty`.

Rather than specify the bath model parameters :math:`\omega_{\nu; \epsilon}` and
:math:`\lambda_{\nu;r;\epsilon}`, one can alternatively specify the spectral
densities of noise coupled to the :math:`y`- and :math:`z`-components of the 
system's spins at temperature :math:`T`, which contain the same information as 
the aforementioned model parameters. This alternative approach is easier to 
incorporate into the QUAPI formalism, upon which ``spinbosonchain`` is based on.

We define the spectral density of the noise coupled to the :math:`\nu`-component
of the spin at site :math:`r` and temperature :math:`T` as:

.. math ::
    A_{\nu;r;T}(\omega)=\int_{-\infty}^{\infty}dt\,e^{i\omega t}C_{\nu;r;T}(t),
    :label: bath_spectral_density_1

where :math:`C_{\nu;r;T}(t)` is the bath correlation function of the noise
coupled to the :math:`\nu`-component of the spin at site :math:`r` and 
temperature :math:`T`:

.. math ::
    C_{\nu;r;T}(t)=\text{Tr}^{(B)}\left\{ \hat{\rho}^{(i,B)}
    \hat{Q}_{\nu;r}^{(B)}(t) \hat{Q}_{\nu;r}^{(B)}(0)\right\},
    :label: bath_bath_correlation_function

with :math:`\hat{Q}_{\nu;r}^{(B)}(t)` being the rescaled reservoir force
operator in the Heisenberg picture:

.. math ::
    \hat{Q}_{\nu;r}^{(B)}(t)=e^{i\hat{H}^{(B)}t}
    \hat{Q}_{\nu;r}e^{-i\hat{H}^{(B)}t},
    :label: bath_Q_heisenberg_picture

:math:`\mathrm{Tr}^{(B)}\left\{\cdots\right\}` is the partial trace with
respect to the bath degrees of freedom, :math:`\hat{\rho}^{(i,B)}` is the 
bath's reduced state operator at :math:`t=0`:

.. math ::
    \hat{\rho}^{(i,B)}\equiv\frac{e^{-\beta\hat{H}^{(B)}}}
    {\mathrm{Tr}^{(B)}\left\{e^{-\beta\hat{H}^{(B)}}\right\}},
    :label: bath_initial_bath_reduced_state_operator

with :math:`\beta=1/(k_B T)`, and :math:`k_B` being the Boltzmann constant. 

Because the system is coupled to its environment, the dynamics of the system not
only depend on its current state, but also its history. The degree to which the
dynamics depend on the history of the system can be characterized by a quantity
known as the bath correlation time, or “memory”. The dynamics at the present
time depend on events ranging further back in time as the system's memory
increases. In ``spinbosonchain``, the user specifies the system's memory: if
chosen too small, the simulation will not be accurate.

This module contains classes to specify all the necessary model components of 
the bath: namely the system-bath coupling energy scales 
:math:`\mathcal{E}_{\nu;r}^{(\lambda)}(t)`, the spectral densities
:math:`A_{\nu;r;T}(\omega)`, and the system's memory :math:`\tau`.
"""



#####################################
## Load libraries/packages/modules ##
#####################################

# For deep copies of objects.
import copy



# For evaluating special math functions.
import numpy as np

# For evaluating numerically integrals.
import scipy.integrate



# Assign an alias to the ``spinbosonchain`` library.
import spinbosonchain as sbc



############################
## Authorship information ##
############################

__author__     = "D-Wave Systems Inc."
__copyright__  = "Copyright 2021"
__credits__    = ["Matthew Fitzpatrick"]
__maintainer__ = "D-Wave Systems Inc."
__email__      = "support@dwavesys.com"
__status__     = "Development"



##############################################
## Define classes, functions, and instances ##
##############################################

# List of public objects in objects.
__all__ = ["SpectralDensity",
           "SpectralDensity0T",
           "SpectralDensityCmpnt",
           "SpectralDensityCmpnt0T",
           "Model",
           "noise_strength",
           "correlation"]



class SpectralDensity():
    r"""A finite-temperature spectral density of noise.

    For background information on spectral densities, see the documentation for
    the module :mod:`spinbosonchain.bath`. 

    This class represents a spectral density of noise at temperature :math:`T`,
    where the noise is coupled to the :math:`\nu`-component of the spin at site 
    :math:`r`, with :math:`\nu\in\{y,z\}`. We denote this spectral density of 
    noise by :math:`A_{\nu;r;T}(\omega)`. 

    In our detailed exposition on our QUAPI+TN approach found :manual:`here <>`,
    we show that :math:`A_{\nu;r;T}(\omega)` can be expressed as

    .. math ::
        A_{\nu;r;T}(\omega)=\text{sign}(\omega)
        \frac{A_{\nu;r;T=0}\left(\left|\omega\right|\right)}
        {1-e^{-\beta\omega}},
        :label: bath_spectral_density_expr

    where

    .. math ::
        \text{sign}\left(\omega\right)=\begin{cases}
        1 & \text{if }\omega>0,\\
        -1 & \text{if }\omega<0,
        \end{cases}
        :label: bath_spectral_density_sign_function

    :math:`A_{\nu;r;T=0}(\omega)` is the zero-temperature limit of
    :math:`A_{\nu;r;T}(\omega)`, and :math:`\beta=1/(k_B T)` with :math:`k_B` 
    being the Boltzmann constant. The quantity :math:`A_{\nu;r;T=0}(\omega)` is
    represented by the :class:`spinbosonchain.bath.SpectralDensity0T` class. See
    the documentation for the aforementioned class for more details on
    :math:`A_{\nu;r;T=0}(\omega)`.

    In many applications of interest, :math:`A_{\nu;r;T=0}(\omega)` will 
    comprise of multiple components:

    .. math ::
        A_{\nu;r;T=0}(\omega)=\sum_{\varsigma}A_{\nu;r;T=0;\varsigma}(\omega),
        :label: bath_spectral_density_0T_breakdown_1

    where :math:`A_{\nu;r;T=0;\varsigma}(\omega)` is the 
    :math:`\varsigma^{\mathrm{th}}` component of :math:`A_{\nu;r;T=0}(\omega)`.
    As an example, :math:`A_{\nu;r;T=0}(\omega)` may be strongly peaked at 
    multiple frequencies, in which case it naturally decomposes into multiple 
    components. If :math:`A_{\nu;r;T=0}(\omega)` naturally decomposes into 
    multiple components, it is best to treat each component separately in 
    our QUAPI+TN approach rather than treat :math:`A_{\nu;r;T=0}(\omega)` as a 
    single entity. For further discussion on this matter, see our detailed 
    exposition of our QUAPI+TN approach found :manual:`here <>`. 

    From Eqs. :eq:`bath_spectral_density_expr` and 
    :eq:`bath_spectral_density_0T_breakdown_1`, we can write

    .. math ::
        A_{\nu;r;T}(\omega)=\sum_{\varsigma}A_{\nu;r;T;\varsigma}(\omega),
        :label: bath_spectral_density_breakdown

    where

    .. math ::
        A_{\nu;r;T;\varsigma}(\omega)=\text{sign}(\omega)
        \frac{A_{\nu;r;T=0;\varsigma}\left(\left|\omega\right|\right)}
        {1-e^{-\beta\omega}}.
        :label: bath_spectral_density_cmpnt_expr_1

    We refer to the :math:`A_{\nu;r;T;\varsigma}(\omega)` as the components of
    :math:`A_{\nu;r;T}(\omega)`. The quantity 
    :math:`A_{\nu;T;\varsigma}(\omega)` is represented by the 
    :class:`spinbosonchain.bath.SpectralDensityCmpnt` class.

    Parameters
    ----------
    limit_0T : :class:`spinbosonchain.bath.SpectralDensity0T`
        The zero-temperature limit of the spectral density of noise of interest,
        :math:`A_{\nu;r;T=0}(\omega)`.
    beta : `float`
        The inverse temperature, :math:`\beta=1/(k_B T)`, with :math:`k_B` 
        being the Boltzmann constant and :math:`T` being the temperature.

    Attributes
    ----------
    cmpnts : `array_like` (:class:`spinbosonchain.bath.SpectralDensityCmpnt`, ndim=1), read-only
        The components of :math:`A_{\nu;r;T}(\omega)`, i.e. the
        :math:`A_{\nu;r;T;\varsigma}(\omega)`.
    """
    def __init__(self, limit_0T, beta):
        self.cmpnts = []
        for cmpnt_0T in limit_0T.cmpnts:
            self.cmpnts += [SpectralDensityCmpnt(cmpnt_0T, beta)]

        return None



    def eval(self, omega):
        r"""Evaluate :math:`A_{\nu;r;T}(\omega)` at frequency ``omega``.

        Parameters
        ----------
        omega : `float`
            Frequency.

        Returns
        -------
        result : `float`
            The value of :math:`A_{\nu;r;T}(\omega)` at frequency ``omega``.
        """
        result = 0.0
        for cmpnt in self.cmpnts:
            result += cmpnt.eval(omega)

        return result



class SpectralDensity0T():
    r"""The zero-temperature limit of some spectral density of noise.

    For background information on spectral densities, see the documentation for
    the module :mod:`spinbosonchain.bath`, and the class 
    :class:`spinbosonchain.bath.SpectralDensity`. 

    This class represents the zero-temperature limit of some spectral density of
    noise, where the noise is coupled to the :math:`\nu`-component of the spin 
    at site :math:`r`, with :math:`\nu\in\{y,z\}`. We denote the 
    zero-temperature limit of this spectral density of noise by 
    :math:`A_{\nu;r;T=0}(\omega)`. 

    In many applications of interest, :math:`A_{\nu;r;T=0}(\omega)` will 
    comprise of multiple components:

    .. math ::
        A_{\nu;r;T=0}(\omega)=\sum_{\varsigma}A_{\nu;r;T=0;\varsigma}(\omega),
        :label: bath_spectral_density_0T_breakdown_2

    where :math:`A_{\nu;r;T=0;\varsigma}(\omega)` is the 
    :math:`\varsigma^{\mathrm{th}}` component. As an example, 
    :math:`A_{\nu;T=0}(\omega)` may be strongly peaked at multiple frequencies, 
    in which case it naturally decomposes into multiple components. If
    :math:`A_{\nu;r;T=0}(\omega)` naturally decomposes into multiple 
    components, it is best to treat each component separately in our 
    QUAPI+TN approach rather than treat :math:`A_{\nu;r;T=0}(\omega)` as a 
    single entity. For further discussion on this matter, see our detailed 
    exposition of our QUAPI+TN approach found :manual:`here <>`. 

    The quantity :math:`A_{\nu;r;T=0;\varsigma}(\omega)` is represented by the
    :class:`spinbosonchain.bath.SpectralDensityCmpnt0T` class. See the
    documentation for the aforementioned class for more details on
    :math:`A_{\nu;r;T=0;\varsigma}(\omega)`.

    Parameters
    ----------
    cmpnts : `array_like` (:class:`spinbosonchain.bath.SpectralDensityCmpnt0T`, ndim=1)
        The components of :math:`A_{\nu;r;T=0}(\omega)`, i.e. the
        :math:`A_{\nu;r;T=0;\varsigma}(\omega)`.

    Attributes
    ----------
    cmpnts : `array_like` (:class:`spinbosonchain.bath.SpectralDensityCmpnt0T`, ndim=1), read-only
        The components of :math:`A_{\nu;r;T=0}(\omega)`, i.e. the
        :math:`A_{\nu;r;T=0;\varsigma}(\omega)`.
    """
    def __init__(self, cmpnts):
        self.cmpnts = cmpnts

        return None



    def eval(self, omega):
        r"""Evaluate :math:`A_{\nu;r;T=0}(\omega)` at frequency ``omega``.

        Parameters
        ----------
        omega : `float`
            Frequency.

        Returns
        -------
        result : `float`
            The value of :math:`A_{\nu;r;T=0}(\omega)` at frequency ``omega``.
        """
        result = 0.0
        for cmpnt in self.cmpnts:
            result += cmpnt.eval(omega)

        return result



    def __eq__(self, obj):
        # Defining custom equality method.
        if not isinstance(obj, SpectralDensity0T):
            result = False
        else:
            if self.cmpnts == obj.cmpnts:
                result = True
            else:
                result = False

        return result



    def __hash__(self):
        # Custom __eq__ makes class unhashable by default. The following is
        # necessary in order for the class to behave properly with sets and
        # dictionaries.
        result = hash((self.cmpnts,))

        return result



class SpectralDensityCmpnt():
    r"""A component of some finite-temperature spectral density of noise.

    For background information on spectral densities, see the documentation for
    the module :mod:`spinbosonchain.bath`, and the class
    :class:`spinbosonchain.bath.SpectralDensity`. The latter introduces the
    concept of breaking down a given finite-temperature spectral density of
    noise into components. We denote these components by
    :math:`A_{\nu;r;T;\varsigma}(\omega)`, with :math:`\varsigma` indicating the
    component.
    
    This class represents a single :math:`A_{\nu;r;T;\varsigma}(\omega)`.

    As briefly discussed in the documentation for the class
    :class:`spinbosonchain.bath.SpectralDensity`,
    :math:`A_{\nu;r;T;\varsigma}(\omega)` can be expressed as

    .. math ::
        A_{\nu;r;T;\varsigma}(\omega)=\text{sign}(\omega)
        \frac{A_{\nu;r;T=0;\varsigma}\left(\left|\omega\right|\right)}
        {1-e^{-\beta\omega}},
        :label: bath_spectral_density_cmpnt_expr_2

    where

    .. math ::
        \text{sign}\left(\omega\right)=\begin{cases}
        1 & \text{if }\omega>0,\\
        -1 & \text{if }\omega<0,
        \end{cases}
        :label: bath_spectral_density_cmpnt_sign_function

    :math:`A_{\nu;r;T=0;\varsigma}(\omega)` is the zero-temperature limit of
    :math:`A_{\nu;r;T;\varsigma}(\omega)`, and :math:`\beta=1/(k_B T)` with 
    :math:`k_B` being the Boltzmann constant and :math:`T` being the 
    temperature. 

    The quantity :math:`A_{\nu;r;T=0;\varsigma}(\omega)` is represented by the
    :class:`spinbosonchain.bath.SpectralDensityCmpnt0T` class.

    Parameters
    ----------
    limit_0T : :class:`spinbosonchain.bath.SpectralDensityCmpnt0T`
        The zero-temperature limit of :math:`A_{\nu;r;T;\varsigma}(\omega)`, 
         i.e. :math:`A_{\nu;r;T=0;\varsigma}(\omega)`.
    beta : `float`
        The inverse temperature, :math:`\beta=1/(k_B T)`, with :math:`k_B` 
        being the Boltzmann constant and :math:`T` being the temperature.

    Attributes
    ----------
    limit_0T : :class:`spinbosonchain.bath.SpectralDensityCmpnt0T`, read-only
        The zero-temperature limit of :math:`A_{\nu;r;T;\varsigma}(\omega)`, 
        i.e. :math:`A_{\nu;r;T=0;\varsigma}(\omega)`.
    beta : `float`, read-only
        The inverse temperature, :math:`\beta=1/(k_B T)`, with :math:`k_B` 
        being the Boltzmann constant and :math:`T` being the temperature.

    """
    def __init__(self, limit_0T, beta):
        self.limit_0T = limit_0T
        self.beta = beta

        return None



    def eval(self, omega):
        r"""Evaluate :math:`A_{\nu;r;T;\varsigma}(\omega)` at frequency 
        ``omega``.

        Parameters
        ----------
        omega : `float`
            Frequency.

        Returns
        -------
        result : `float`
            The value of :math:`A_{\nu;r;T;\varsigma}(\omega)` at frequency 
            ``omega``.
        """
        if self.limit_0T.ir_cutoff <= np.abs(omega) <= self.limit_0T.uv_cutoff:
            result = self._eval(omega)
        else:
            result = 0

        return result



    def _eval(self, omega):
        # See Appendix C of detailed manuscript on our QUAPI-TN approach for
        # the rational behind the following implementation. In particular, see
        # Eqs. (582) to Eq. (585).
        if omega == 0.0:
            result = self.limit_0T.zero_pt_derivative / self.beta
        else:
            abs_omega = np.abs(omega)
            beta_omega = self.beta * omega
            if 0 < abs_omega * self.beta < 1.0e-3:
                result = (np.sign(omega)
                          * (self.limit_0T._eval(abs_omega) / beta_omega)
                          * (1.0 + beta_omega/2.0
                             + (beta_omega**2)/12.0 - (beta_omega**4) / 720.0))
            elif beta_omega <= -1.0e-3:
                result = -(np.exp(beta_omega) * self.limit_0T._eval(abs_omega)
                           / (np.exp(beta_omega) - 1.0))
            else:
                result = (self.limit_0T._eval(abs_omega)
                          / (1.0 - np.exp(-beta_omega)))

        return result

    

class SpectralDensityCmpnt0T():
    r"""A component of the zero-temperature limit of some spectral density of 
    the noise.

    For background information on spectral densities, see the documentation for
    the module :mod:`spinbosonchain.bath`, and the class
    :class:`spinbosonchain.bath.SpectralDensity0T`. The latter discusses the
    concept of breaking down the zero-temperature limit of a given spectral
    density of noise into components. We denote these components by
    :math:`A_{\nu;r;T=0;\varsigma}(\omega)`, with :math:`\varsigma` indicating
    the component.
    
    This class represents a single :math:`A_{\nu;r;T=0;\varsigma}(\omega)`.

    In the continuum limit, :math:`A_{\nu;r;T=0;\varsigma}(\omega)` becomes a 
    continuous function of :math:`\omega` satisfying:

    .. math ::
        A_{\nu;r;T=0;\varsigma}(\omega) \ge 0,
        :label: bath_spectral_density_cmpnt_0T_properties_1

    and

    .. math ::
        A_{\nu;r;T=0;\varsigma}(\omega \le 0) = 0,
        :label: bath_spectral_density_cmpnt_0T_properties_2

    In order for the open-system dynamics to be "well-behaved", 
    :math:`A_{\nu;r;T=0;\varsigma}(\omega)` must satisfy:

    .. math ::
        \left|\lim_{\omega \to 0} 
        \frac{A_{\nu;r;T=0;\varsigma}}{\omega}\right| < \infty.
        :label: bath_spectral_density_cmpnt_0T_requirement

    In our QUAPI+TN approach, frequency integrals are performed with integrands
    containing the :math:`A_{\nu;r;T=0;\varsigma}(\omega)`. Each integrand
    contains a removable singularity at :math:`\omega=0`. In order to handle
    these integrands properly in our approach, we require the limit of the
    derivative of each :math:`A_{\nu;r;T=0;\varsigma}(\omega)` as :math:`\omega`
    approaches zero from the right.

    Parameters
    ----------
    func_form : `func` (`float`, `**kwargs`)
        The functional form of :math:`A_{\nu;r;T=0;\varsigma}(\omega)`, where 
        the first function argument of ``func_form`` is the frequency
        :math:`\omega`. ``func_form`` needs to be well-defined for non-negative 
        frequencies and must satisfy 
        Eqs. :eq:`bath_spectral_density_cmpnt_0T_properties_1`  and
        :eq:`bath_spectral_density_cmpnt_0T_requirement`. Note that 
        ``func_form`` is effectively ignored for negative frequencies as
        :math:`A_{\nu;r;T=0;\varsigma}(\omega)` is assumed to be zero for those
        frequencies.
    func_kwargs : `dict`
        A dictionary specifying specific values of the keyword arguments of
        ``func_form``. If there are no keyword arguments, then an empty
        dictionary should be passed.
    uv_cutoff : `float`
        A hard ultraviolet cutoff frequency. For frequencies ``omega`` 
        satisfying ``omega > uv_cutoff``, 
        :math:`A_{\nu;r;T=0;\varsigma}(\omega)` evaluates to zero. 
        ``uv_cutoff`` is expected to be positive.
    ir_cutoff : `float`, optional
        A hard infrared cutoff frequency. For frequencies ``omega`` 
        satisfying ``omega < ir_cutoff``, 
        :math:`A_{\nu;r;T=0;\varsigma}(\omega)` evaluates to zero. 
        ``ir_cutoff`` is expected to be positive.
    zero_pt_derivative : `float` | `None`, optional
        The limit of the derivative of :math:`A_{\nu;r;T=0;\varsigma}(\omega)` 
        as :math:`\omega` approaches zero from the right. If 
        ``zero_pt_derivative`` is set to `None` [i.e. the default value], then 
        it will be estimated automatically by ``spinbosonchain``.

    Attributes
    ----------
    func_form : `func` (`float`, `**kwargs`), read-only
        The functional form of :math:`A_{\nu;r;T=0;\varsigma}(\omega)`, where 
        the first function argument of ``func_form`` is the frequency
        :math:`\omega`. Note that ``func_form`` is effectively ignored for 
        negative frequencies as :math:`A_{\nu;r;T=0;\varsigma}(\omega)` is 
        assumed to be zero for those frequencies.
    func_kwargs : `dict`, read-only
        A dictionary specifying specific values of the keyword arguments of
        ``func_form``.
    uv_cutoff : `float`, read-only
        A hard ultraviolet cutoff frequency. For frequencies ``omega`` 
        satisfying ``omega > uv_cutoff``, 
        :math:`A_{\nu;r;T=0;\varsigma}(\omega)` evaluates to zero. 
    ir_cutoff : `float`, read-only
        A hard infrared cutoff frequency. For frequencies ``omega`` 
        satisfying ``omega < ir_cutoff``, 
        :math:`A_{\nu;r;T=0;\varsigma}(\omega)` evaluates to zero. 
    zero_pt_derivative : `float`, read-only
        The limit of the derivative of :math:`A_{\nu;r;T=0;\varsigma}(\omega)` 
        as :math:`\omega` approaches zero from the right.

    """
    def __init__(self,
                 func_form,
                 func_kwargs,
                 uv_cutoff,
                 ir_cutoff=0,
                 zero_pt_derivative=None):
        # uv_cutoff should always be greater than or equal to ir_cutoff.
        self.uv_cutoff = abs(uv_cutoff)
        self.ir_cutoff = min(abs(ir_cutoff), self.uv_cutoff)
        
        try:
            omega = 0.5 * (self.ir_cutoff + self.uv_cutoff)
            func_form(omega, **func_kwargs)  # Check TypeErrors.
        except:
            raise TypeError(_spectral_density_cmpnt_0T_init_err_msg_1)
        
        self.func_form = func_form
        self.func_kwargs = copy.deepcopy(func_kwargs)

        self.zero_pt_derivative = zero_pt_derivative
        if zero_pt_derivative is None:
            self.zero_pt_derivative = self._eval(1.0e-30) / 1.0e-30

        return None



    def eval(self, omega):
        r"""Evaluate :math:`A_{\nu;r;T=0;\varsigma}(\omega)` at frequency 
        ``omega``.

        Parameters
        ----------
        omega : `float`
            Frequency.

        Returns
        -------
        result : `float`
            The value of :math:`A_{\nu;r;T=0;\varsigma}(\omega)` at frequency 
            ``omega``.
        """
        if self.ir_cutoff <= omega <= self.uv_cutoff:
            result = self._eval(omega)
        else:
            result = 0

        return result



    def _eval(self, omega):
        result = self.func_form(omega, **self.func_kwargs)

        return result



    def __eq__(self, obj):
        # Defining custom equality method.
        if not isinstance(obj, SpectralDensityCmpnt0T):
            result = False
        else:
            co_code_1 = self.func_form.__code__.co_code  # Bytecode.
            co_code_2 = obj.func_form.__code__.co_code
            func_kwargs_1 = self.func_kwargs
            func_kwargs_2 = obj.func_kwargs
            uv_cutoff_1 = self.uv_cutoff
            uv_cutoff_2 = obj.uv_cutoff
            ir_cutoff_1 = self.ir_cutoff
            ir_cutoff_2 = obj.ir_cutoff
            zero_pt_derivative_1 = self.zero_pt_derivative
            zero_pt_derivative_2 = obj.zero_pt_derivative
            if ((co_code_1 == co_code_2)
                and (func_kwargs_1 == func_kwargs_2)
                and (uv_cutoff_1 == uv_cutoff_2)
                and (ir_cutoff_1 == ir_cutoff_2)
                and (zero_pt_derivative_1 == zero_pt_derivative_2)):
                result = True
            else:
                result = False

        return result



    def __hash__(self):
        # Custom __eq__ makes class unhashable by default. The following is
        # necessary in order for the class to behave properly with sets and
        # dictionaries.
        func_form_co_code = self.func_form.__code__.co_code  # Bytecode.
        func_kwargs_in_tuple_form = tuple(sorted(self.func_kwargs.items()))
        uv_cutoff = self.uv_cutoff
        ir_cutoff = self.ir_cutoff
        zero_pt_derivative = self.zero_pt_derivative
        tuple_to_hash = (func_form_co_code, func_kwargs_in_tuple_form,
                         uv_cutoff, ir_cutoff, zero_pt_derivative)
        result = hash(tuple_to_hash)

        return result



# Define a trivial spectral density which always evaluates to zero.
_trivial_spectral_density_cmpnt_0T = \
    SpectralDensityCmpnt0T(func_form=lambda omega: 0.0,
                           func_kwargs={},
                           uv_cutoff=1.0e-10,
                           zero_pt_derivative=0.0)
_trivial_spectral_density_0T = \
    SpectralDensity0T(cmpnts=[_trivial_spectral_density_cmpnt_0T])
_trivial_spectral_density = \
    SpectralDensity(limit_0T=_trivial_spectral_density_0T, beta=1.0)



class Model():
    r"""The bath's model components.

    For background information on system-bath coupling energy scales, spectral
    densities, system memory, and unit cells, see the documentation for the
    module :mod:`spinbosonchain.bath`, and the class
    :class:`spinbosonchain.bath.SpectralDensity`.

    Parameters
    ----------
    L : `int`
        The number of spin sites in every unit cell. Note that in the case of a 
        finite chain there is only one unit cell, whereas for an infinite chain 
        there is an arbitrarily large number of unit cells. 
    beta : `float`
        The inverse temperature, :math:`\beta=1/(k_B T)`, with :math:`k_B` 
        being the Boltzmann constant and :math:`T` being the temperature.
    memory : `float`
        The bath correlation time, also known as the system's memory 
        :math:`\tau`. ``memory`` is expected to be non-negative.
    y_coupling_energy_scales : `array_like` (`float` | :class:`spinbosonchain.scalar.Scalar`, shape=(``L``,)) | `None`, optional
        The energy scales :math:`\mathcal{E}_{y;r}^{(\lambda)}(t)` 
        [introduced in Eq. :eq:`bath_generalized_reservoir_force`] associated 
        with the couplings between the environment and the :math:`y`-components 
        of the system's spins. If ``y_coupling_energy_scales`` is an array, then
        ``y_coupling_energy_scales[r]`` is the energy scale for site ``r``.
        Note that the energy scales can be either time-dependent or independent.
        All time-independent field energy scales are converted to trivial
        instances of :class:`spinbosonchain.scalar.Scalar`. If 
        ``y_coupling_energy_scales`` is set to `None` (i.e. the default value), 
        then the environment is not coupled to the :math:`y`-components of the 
        system's spins.
    z_coupling_energy_scales : `array_like` (`float` | :class:`spinbosonchain.scalar.Scalar`, shape=(``L``,)) | `None`, optional
        The energy scales :math:`\mathcal{E}_{z;r}^{(\lambda)}(t)` 
        [introduced in Eq. :eq:`bath_generalized_reservoir_force`] associated 
        with the couplings between the environment and the :math:`z`-components 
        of the system's spins. If ``z_coupling_energy_scales`` is an array, then
        ``z_coupling_energy_scales[r]`` is the energy scale for site ``r``.
        Note that the energy scales can be either time-dependent or independent.
        All time-independent field energy scales are converted to trivial
        instances of :class:`spinbosonchain.scalar.Scalar`. If 
        ``z_coupling_energy_scales`` is set to `None` (i.e. the default value), 
        then the environment is not coupled to the :math:`z`-components of the 
        system's spins.
    y_spectral_densities_0T : `array_like` (0 | :class:`spinbosonchain.bath.SpectralDensity0T`, shape=(``L``,)) | `None`, optional
        The zero-temperature limits of the spectral densities of noise coupled
        to the :math:`y`-components of the system's spins. If 
        ``y_spectral_densities_0T`` is an array, then
        ``y_spectral_densities_0T[r]`` is the spectral density for site ``r``,
        :math:`A_{y;r;T=0}(\omega)`. If ``y_spectral_densities_0T[r]`` is set to
        ``0``, then it is converted into a trivial instance of 
        :class:`spinbosonchain.bath.SpectralDensity0T` which always evaluates to
        zero, i.e. there is no coupling between the bath and the 
        :math:`y`-component of the spin at site ``r`` in this case. If 
        ``y_spectral_densities_0T`` is set to `None` (i.e. the default value), 
        then the environment is not coupled to the :math:`y`-components of the 
        system's spins.
    z_spectral_densities_0T : `array_like` (0 | :class:`spinbosonchain.bath.SpectralDensity0T`, shape=(``L``,)) | `None`, optional
        The zero-temperature limits of the spectral densities of noise coupled
        to the :math:`z`-components of the system's spins. If 
        ``z_spectral_densities_0T`` is an array, then
        ``z_spectral_densities_0T[r]`` is the spectral density for site ``r``,
        :math:`A_{z;r;T=0}(\omega)`. If ``z_spectral_densities_0T[r]`` is set to
        ``0``, then it is converted into a trivial instance of 
        :class:`spinbosonchain.bath.SpectralDensity0T` which always evaluates to
        zero, i.e. there is no coupling between the bath and the 
        :math:`z`-component of the spin at site ``r`` in this case. If 
        ``z_spectral_densities_0T`` is set to `None` (i.e. the default value), 
        then the environment is not coupled to the :math:`z`-components of the 
        system's spins.

    Attributes
    ----------
    L : `int`, read-only
        The number of spin sites in every unit cell.
    memory : `float`, read-only
        The bath correlation time, also known as the system's memory 
        :math:`\tau`.
    y_coupling_energy_scales : `array_like` (:class:`spinbosonchain.scalar.Scalar`, shape=(``L``,)) | `None`, read-only
        The energy scales :math:`\mathcal{E}_{y;r}^{(\lambda)}(t)` 
        [introduced in Eq. :eq:`bath_generalized_reservoir_force`] associated 
        with the couplings between the environment and the :math:`y`-components 
        of the system's spins. If ``y_coupling_energy_scales`` is an array, then
        ``y_coupling_energy_scales[r]`` is the energy scale for site ``r``.
        If ``y_coupling_energy_scales`` is set to `None`, then the environment 
        is not coupled to the :math:`y`-components of the system's spins.
    z_coupling_energy_scales : `array_like` (:class:`spinbosonchain.scalar.Scalar`, shape=(``L``,)) | `None`, read-only
        The energy scales :math:`\mathcal{E}_{z;r}^{(\lambda)}(t)` 
        [introduced in Eq. :eq:`bath_generalized_reservoir_force`] associated 
        with the couplings between the environment and the :math:`z`-components 
        of the system's spins. If ``z_coupling_energy_scales`` is an array, then
        ``z_coupling_energy_scales[r]`` is the energy scale for site ``r``.
        If ``z_coupling_energy_scales`` is set to `None`, then the environment 
        is not coupled to the :math:`z`-components of the system's spins.
    y_spectral_densities : `array_like` (:class:`spinbosonchain.bath.SpectralDensity`, shape=(``L``,)) | `None`, read-only
        The spectral densities of noise coupled to the :math:`y`-components of 
        the system's spins at temperature :math:`T`. If ``y_spectral_densities``
        is an array, then ``y_spectral_densities[r]`` is the spectral density 
        for site ``r``, :math:`A_{y;r;T}(\omega)`. If ``y_spectral_densities`` 
        is set to `None` (i.e. the default value), then the environment is not 
        coupled to the :math:`y`-components of the system's spins.
    z_spectral_densities : `array_like` (:class:`spinbosonchain.bath.SpectralDensity`, shape=(``L``,)) | `None`, read-only
        The spectral densities of noise coupled to the :math:`z`-components of 
        the system's spins at temperature :math:`T`. If ``z_spectral_densities``
        is an array, then ``z_spectral_densities[r]`` is the spectral density 
        for site ``r``, :math:`A_{z;r;T}(\omega)`. If ``z_spectral_densities`` 
        is set to `None` (i.e. the default value), then the environment is not 
        coupled to the :math:`z`-components of the system's spins.
    """
    def __init__(self,
                 L,
                 beta,
                 memory,
                 y_coupling_energy_scales=None,
                 z_coupling_energy_scales=None,
                 y_spectral_densities_0T=None,
                 z_spectral_densities_0T=None):
        self.L = L
        self.memory = memory if memory >= 0.0 else 0.0

        partial_ctor_param_list = [y_coupling_energy_scales,
                                   z_coupling_energy_scales,
                                   y_spectral_densities_0T,
                                   z_spectral_densities_0T]

        for idx, _ in enumerate(partial_ctor_param_list):
            if partial_ctor_param_list[idx] is None:
                partial_ctor_param_list[(idx+2)%4] = None
            else:
                if ((len(partial_ctor_param_list[idx]) == 0)
                    or all(elem == 0 for elem in partial_ctor_param_list[idx])):
                    partial_ctor_param_list[idx] = None
                    partial_ctor_param_list[(idx+2)%4] = None

        self._check_partial_ctor_param_list(partial_ctor_param_list)

        self.y_coupling_energy_scales = \
            self._construct_attribute(partial_ctor_param_list[0])
        self.z_coupling_energy_scales = \
            self._construct_attribute(partial_ctor_param_list[1])
        self.y_spectral_densities = \
            self._construct_attribute(partial_ctor_param_list[2], beta)
        self.z_spectral_densities = \
            self._construct_attribute(partial_ctor_param_list[3], beta)

        self._map_btwn_site_indices_and_unique_local_model_cmpnt_sets = \
            self._calc_map_btwn_site_indices_and_unique_local_model_cmpnt_sets()

        return None



    def _check_partial_ctor_param_list(self, partial_ctor_param_list):
        candidate_Ls = set()
        for ctor_param in partial_ctor_param_list:
            if ctor_param is not None:
                if len(ctor_param) != 0:
                    candidate_Ls.add(len(ctor_param))

        if len(candidate_Ls) != 0:
            L = candidate_Ls.pop()
            if (L != self.L) or (len(candidate_Ls) != 0):
                raise IndexError(_model_check_partial_ctor_param_list_err_msg_1)

        return None



    def _construct_attribute(self, ctor_param, beta=None):
        if ctor_param is None:
            attribute = None
            return attribute

        expected_type = sbc.scalar.Scalar if beta is None else SpectralDensity0T

        attribute = list(ctor_param)
        elem_already_set = [False] * self.L
        for idx1 in range(self.L):
            if elem_already_set[idx1] == False:
                elem = attribute[idx1]
            
                if isinstance(elem, expected_type):
                    updated_elem = (elem if expected_type == sbc.scalar.Scalar
                                    else SpectralDensity(elem, beta))
                    attribute[idx1] = updated_elem
                else:
                    trivial_updated_elem = \
                        (expected_type(elem)
                         if expected_type == sbc.scalar.Scalar
                         else _trivial_spectral_density)
                    attribute[idx1] = trivial_updated_elem

            for idx2 in range(idx1+1, self.L):
                if ctor_param[idx2] == ctor_param[idx1]:
                    attribute[idx2] = attribute[idx1]
                    elem_already_set[idx2] = True
                
        return attribute



    def _calc_map_btwn_site_indices_and_unique_local_model_cmpnt_sets(self):
        attributes = (self.y_coupling_energy_scales,
                      self.z_coupling_energy_scales,
                      self.y_spectral_densities,
                      self.z_spectral_densities)

        local_model_cmpnt_sets = [None] * self.L
        for idx in range(self.L):
            local_model_cmpnt_set = []
            for attribute in attributes:
                if attribute is not None:
                    local_model_cmpnt_set += [attribute[idx]]
            local_model_cmpnt_sets[idx] = local_model_cmpnt_set

        result = list(range(self.L))
        for idx1 in range(self.L):
            for idx2 in range(idx1+1, self.L):
                if local_model_cmpnt_sets[idx2] == local_model_cmpnt_sets[idx1]:
                    result[idx2] = result[idx1]

        return result



def noise_strength(spectral_density):
    r"""Calculate strength of a given source of noise.

    For background information on spectral densities, see the documentation for
    the module :mod:`spinbosonchain.bath`. 

    For a given source of noise, described by the spectral density of
    noise :math:`A_{\nu;r;T}(\omega)` at temperature :math:`T`, we can
    characterize the strength of this noise by calculating:

    .. math ::
        W_{\nu; r; T} = \int_{-\infty}^{\infty}\frac{d\omega}{2\pi} A_{\nu;r;T}(\omega).
        :label: bath_W_expr

    The function :func:`spinbosonchain.bath.noise_strength` calculates the
    quantity :math:`W_{\nu; r; T}` given a spectral density
    :math:`A_{\nu;r;T}(\omega)`.

    Parameters
    ----------
    spectral_density : :class:`spinbosonchain.bath.SpectralDensity` | :class:`spinbosonchain.bath.SpectralDensityCmpnt` | :class:`spinbosonchain.bath.SpectralDensity0T` | :class:`spinbosonchain.bath.SpectralDensityCmpnt0T`
        The spectral density of noise of interest :math:`A_{\nu;r;T}(\omega)`.

    Returns
    -------
    W : `float`
        The strength of the noise :math:`W_{\nu; r; T}`.

    """
    integrand = lambda omega: spectral_density.eval(omega) / 2.0 / np.pi
    pts = _get_integration_pts(spectral_density)
    limit = 10000

    # If zero temperature spectral density, the integrand is zero for all
    # negative frequencies.
    quad = scipy.integrate.quad
    W = quad(integrand, a=pts[2], b=pts[3], limit=limit)[0]
    if isinstance(spectral_density, (SpectralDensity, SpectralDensityCmpnt)):
        W += quad(integrand, a=pts[0], b=pts[1], limit=limit)[0]
    W = np.sqrt(W)

    return W



def correlation(t, spectral_density):
    r"""Evaluate the bath correlation function at a given time.

    For background information on bath correlation functions, see the 
    documentation for the module :mod:`spinbosonchain.bath`. 

    The bath correlation function is evaluated at time ``t`` by calculating
    numerically the inverse Fourier transform of the corresponding spectral
    density of the noise ``spectral_density``.

    Parameters
    ----------
    t : `float`
        The time at which to evaluate the bath correlation function.
    spectral_density : :class:`spinbosonchain.bath.SpectralDensity` | :class:`spinbosonchain.bath.SpectralDensityCmpnt` | :class:`spinbosonchain.bath.SpectralDensity0T` | :class:`spinbosonchain.bath.SpectralDensityCmpnt0T`
        The spectral density of noise that is the Fourier transform of the bath
        correlation function of interest.

    Returns
    -------
    result : `float`
        The value of the bath correlation function at time ``t``.
    """
    integrand = lambda omega: spectral_density.eval(omega) / 2.0 / np.pi
    pts = _get_integration_pts(spectral_density)
    limit = 2000 * max(int(max(pts) * t), 1)

    # If zero temperature spectral density, the integrand is zero for all
    # negative frequencies.
    quad = scipy.integrate.quad
    result = quad(integrand, a=pts[2], b=pts[3],
                  limit=limit, weight="cos", wvar=t)[0]
    result -= 1j*quad(integrand, a=pts[2], b=pts[3],
                      limit=limit, weight="sin", wvar=t)[0]
    if isinstance(spectral_density, (SpectralDensity, SpectralDensityCmpnt)):
        result += quad(integrand, a=pts[0], b=pts[1],
                       limit=limit, weight="cos", wvar=t)[0]
        result -= 1j*quad(integrand, a=pts[0], b=pts[1],
                      limit=limit, weight="sin", wvar=t)[0]

    return result



def _get_integration_pts(spectral_density):
    if isinstance(spectral_density, SpectralDensity):
        uv_cutoffs = [spectral_density_cmpnt.limit_0T.uv_cutoff
                      for spectral_density_cmpnt in spectral_density.cmpnts]
        ir_cutoffs = [spectral_density_cmpnt.limit_0T.ir_cutoff
                      for spectral_density_cmpnt in spectral_density.cmpnts]
    elif isinstance(spectral_density, SpectralDensityCmpnt):
        uv_cutoffs = [spectral_density.limit_0T.uv_cutoff]
        ir_cutoffs = [spectral_density.limit_0T.ir_cutoff]
    elif isinstance(spectral_density, SpectralDensity0T):
        uv_cutoffs = [spectral_density_cmpnt.uv_cutoff
                      for spectral_density_cmpnt in spectral_density.cmpnts]
        ir_cutoffs = [spectral_density_cmpnt.ir_cutoff
                      for spectral_density_cmpnt in spectral_density.cmpnts]
    elif isinstance(spectral_density, SpectralDensityCmpnt0T):
        uv_cutoffs = [spectral_density.uv_cutoff]
        ir_cutoffs = [spectral_density.ir_cutoff]

    max_uv_cutoff = max(uv_cutoffs)
    min_ir_cutoff = min(ir_cutoffs)
    pts = (-max_uv_cutoff, -min_ir_cutoff, min_ir_cutoff, max_uv_cutoff)

    return pts



_spectral_density_cmpnt_0T_init_err_msg_1 = \
    ("The given dictionary `func_kwargs` that is suppose to specify the "
     "keyword arguments of the given function `func_form`, used to construct "
     "an instance of the `spinbosonchain.bath.SpectralDensityCmpnt0T` class, "
     "is not compatible with `func_form`.")

_model_check_partial_ctor_param_list_err_msg_1 = \
    ("One or more of the following parameters: ``y_coupling_energy_scales``, "
     "``z_coupling_energy_scales``, ``y_spectral_densities_0T``, "
     "``z_spectral_densities_0T``, are of dimensions incompatible with the "
     "parameter ``L``.")
