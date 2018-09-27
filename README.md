# url_metadata
An URL metadata getter Flask micro website

To launch the application:

    docker build -t url_metadata .
    docker run -ti -p 5000:5000 -v /tmp/var:/app/var url_metadata

With a virtual env:
    
    clone the url_metadata project
    cd url_metadata
    virtualenv -p python3 url_metadata_env
    source url_metadata_env/bin/activate
    pip install -r requirements.txt
    python -m url_metadata

Run tests
    python -m unittest tests