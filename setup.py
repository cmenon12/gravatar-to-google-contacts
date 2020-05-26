import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gravatarcontacts-cmenon12",
    version="1.0.1",
    author="Christopher Menon",
    description="A package to copy Gravatar profile pictures to your "
                "Google Contacts.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cmenon12/gravatar-to-google-contacts",
    packages=setuptools.find_packages(),
    license="GNU GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: "
        "GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Natural Language :: English"
    ],
    python_requires='>=3.7.4',
    install_requires=["requests>=2.23.0",
                      "google_api_python_client>=1.8.3",
                      "google_auth_oauthlib>=0.4.1",
                      "libgravatar>=0.2.3",
                      "Pillow>=7.1.2",
                      "protobuf>=3.12.1"]
)
