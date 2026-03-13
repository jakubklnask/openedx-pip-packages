
from setuptools import setup

setup(
    name="tutor-mycors",
    version="0.2.0",
    description="Tutor plugin to add multiple CORS/CSRF origins for edu.technologie.sp.nask.pl, apps.edu.technologie.sp.nask.pl and studio.edu.technologie.sp.nask.pl",
    packages=["mycors"],
    entry_points={
        "tutor.plugin.v1": [
            "mycors = mycors"
        ]
    },
)
