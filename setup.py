from setuptools import setup

try:
    from pyqt_distutils.build_ui import build_ui
    cmdclass = {"build_ui": build_ui}
except ImportError:
    cmdclass = {}

setup(
    name="fruit3d",
    version="0.1",
    packages=["fruit3d"],
    cmdclass=cmdclass,
)
