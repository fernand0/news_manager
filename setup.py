from setuptools import setup, find_packages

setup(
    name='news-manager',
    version='0.1.0',
    description='A CLI tool for generating news articles using Google Gemini API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Fernando Tricas',
    author_email='fernand0@gmail.com',
    url='https://github.com/fernand0/news_manager',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'google-generativeai',
        'requests',
        'beautifulsoup4',
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'news-manager = news_manager.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
)
