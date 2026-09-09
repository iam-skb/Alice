from setuptools import setup, find_packages

setup(
    name="alice-chat",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["websockets", "pycryptodome", "cryptography"],
    entry_points={
        "console_scripts": [
            "alice=alice_chat.cli:main",
        ],
    },
    author="TheAnonSpider",
    description="Chat chiffré E2EE en ligne de commande",
    license="MIT",
)
