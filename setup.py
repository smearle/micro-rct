import setuptools

setuptools.setup(
        name="micro-rct",
        version="0.0.1",
        author="Victoria Yen, Sam Earle, Michael Green, Dipika Rajesh, Lisa Soros",
        author_email="smearle93@gmail.com",
        description="A minimal rollercoaster tycoon-like simulation for training evolutionary and reinforcement learning-based planning agents.",
        url="https://github.com/smearle/micro-rct",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License:: OSI Approved :: MIT License",
            "Operating System :: OS Independend",
            ],
        python_requires='>=3.6',
        include_package_data=True,
        )



