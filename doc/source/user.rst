pyspextools.model: Interfaces for SPEX models
=============================================

.. automodule:: pyspextools.model

The pyspextools module can provide interfaces to SPEX models. Currently, there is only a
helper class for the SPEX 'user' and 'musr' models, which provides the opportunity for
users to import their own models into SPEX.

.. _usermodel:

SPEX user model interface module
--------------------------------

This is a Python helper class for the development of user defined models in SPEX. 
The 'user' and 'musr' components in SPEX can calculate an additive and multiplicative
model, respectively, based on a user program. See the SPEX manual for details:
http://var.sron.nl/SPEX-doc/ 

The 'user' component can run an executable provided by the user. This module provides 
the class that helps to exchange the relevant information between SPEX and the user
provided executable. Documentation for an example program is here: :ref:`user-example`.

**SPEX output and executable input:**

The SPEX user component will provide an energy grid and a list of model parameters to 
the executable through a text file, for example input-01-01.prm. Using this information,
the user provided program should calculate the spectrum on the provided grid using the
input parameters.

**Executable output and SPEX input:**

The spectrum (and the weights) can be written to the provided sener (and wener) arrays
in this module. The write_spc function will write the calculated spectrum to an output
file named, for example, output-01-01.spc. This file will be read again by the SPEX 
user model and the resulting values will be used in the SPEX fit. 

   .. autoclass:: pyspextools.model.User
      :members:  
