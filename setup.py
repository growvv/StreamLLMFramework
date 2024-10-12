from setuptools import setup, find_packages

setup(
    name='streamllm',
    version='0.1.0',
    description='StreamLLM: A Stream Processing Framework for Language Models',
    author='lfr',
    author_email='作者邮箱',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'zhipuai',
        'openai',
        'flask',
        'flask-socketio',
        'pyyaml',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Framework :: Flask',
        'Topic :: Software Development :: Agent ::Stream',
    ],
)
