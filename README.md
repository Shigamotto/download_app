# Downloader app

This application is created for downloading files with handle retries and partial downloads.
The program can accept a single URI or a list of URIs to download.

Before start app you need to install requerements: `pip install -r requerements.txt`

To start app use `python download.py <list of URIs[]>` 
with available parameters: 
`--max_retries=<num>`(the num of maximum retries), 
`--parallel`(run program in parallel mode)

## How new protocols can be added.
For this you need to create new interface based on [BaseDownloadInterface](./provider/base.py).
And after that you need to register this interface in [init_service](./service.py) function
