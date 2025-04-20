.. _changelog:

---------
Changelog
---------

Version 1.0.4  - 4/19/25
-----------------------

    - Updated typing, notably on Form.create_form

Version 1.0.3 - 10/05/24
------------------------

    - Updated i18n for changes to Quart-Babel.
    - Updated package to include py.typed file.

Version 1.0.2 - 9/10/24
-----------------------

    - Updated dependencies for package.
    - General file cleanup. 
    - Doc cleanup. 

Version 1.0.1 - 11/26/23
-----------------------

    - Tested extension using Python 3.12.
    - Extension now supports Python 3.11 and 3.12.
    - devcontainer.json: Changed name, vscode extensions, and `postCreateCommand`. `postCreateCommand` doesn't use shell script anymore.
    - Dockerfile: Updated docker version to be 3.12 and removed unused commands.
    - Removed `postCreateCommand.sh` file, since no longer needed.
    - Changed version number to match this release.
    - Added Python 3.11 and 3.12 to classifiers.
    - Updated Python version to be >= 3.8.
    - Updated Quart version to match latest  #5  
    - Added tool.black
    - Added tool.isort
    - Added tool.mypy

Version 1.0.0 - 5/4/23
-----------------------

First initial release of Quart-WTF.