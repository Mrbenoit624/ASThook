How to contribute
=================

For all modification on core code you just need to clone the project and make a merge-request

.. note:: 
  
  If you don't have the capabilities to make your idea open a issue and wait ;)

But the best way to add some functionality is to add a plugin module.
Static module and dynamic module are easy to add and have quietly same
organization.

For instance for the seekLitteral module you need to create a directory on the
module folder with __init__.py file inside

.. code-block:: bash

  asthook/static/module/seekLiteral/
  ├── __init__.py
  └── seek_literal.py

Inside `__init__.py` you need to have one class.
This class have a decorator `@ModuleStaticCmd` for static and
`@ModuleDynamicCmd` for dynamic

.. code-block:: python

  @ModuleStaticCmd("seek_literal", "seek Literal specify with regexp", str, "+")

This decorator contain:

- Name: how to call it
- Description for help
- Type of parameters
- Number of parameters (Optional : 0 if bool 1 else)

Create your module
******************

.. toctree::
  :maxdepth: 1
  :titlesonly:

  how.contribute.module.static
  how.contribute.module.dynamic

