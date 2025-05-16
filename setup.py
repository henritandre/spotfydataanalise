from setuptools import setup

setup(
    name="spotify-analytics",
    version="0.1",
    install_requires=[
      'streamlit==1.32.0',
      'plotly==5.18.0',
      'pandas==2.1.4',
      'numpy==1.26.2',
      'scikit-learn==1.3.2',
      'python-dateutil==2.8.2',
      'pycountry==22.3.5'
    ],
)
