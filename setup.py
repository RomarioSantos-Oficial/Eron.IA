"""
Setup script para Eron.IA
Assistente de IA personalizado com interface web e Telegram
"""

from setuptools import setup, find_packages
import os

# Ler README para descrição longa
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Ler requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        lines = fh.readlines()
        requirements = []
        for line in lines:
            line = line.strip()
            # Ignorar comentários e linhas vazias
            if line and not line.startswith('#'):
                requirements.append(line)
        return requirements

setup(
    name="eron-ia",
    version="2.0.0",
    author="Romario Santos",
    author_email="romario@example.com",
    description="Assistente de IA personalizado com interface web e Telegram",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/RomarioSantos-Oficial/Eron.IA",
    project_urls={
        "Bug Tracker": "https://github.com/RomarioSantos-Oficial/Eron.IA/issues",
        "Documentation": "https://github.com/RomarioSantos-Oficial/Eron.IA/wiki",
        "Source Code": "https://github.com/RomarioSantos-Oficial/Eron.IA",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
        "analysis": [
            "textblob>=0.17.1",
            "nltk>=3.8.1",
        ],
        "monitoring": [
            "psutil>=5.9.6",
            "memory-profiler>=0.61.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "eron-ia=run_all:main",
            "eron-web=web.app:main",
            "eron-telegram=telegram_bot.bot_main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "templates/*.html",
            "templates/**/*.html",
            "static/*.css",
            "static/**/*.css",
            "static/*.js",
            "static/**/*.js",
            "exemplos/*.csv",
        ],
    },
    zip_safe=False,
    keywords=[
        "ai", "assistant", "chatbot", "telegram", "flask", 
        "personalization", "nlp", "conversation", "bot"
    ],
    license="MIT",
)