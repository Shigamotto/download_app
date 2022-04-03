import argparse

from service import init_service

service = init_service()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A tutorial of argparse!'
    )
    parser.add_argument("locations", type=str, nargs='*', help="location of downloaded file")
    parser.add_argument("--max_retries", default=3, help='Num of retries to download file')
    parser.add_argument("--parallel", action='store_true')

    args = parser.parse_args()
    service.download(
        locations=args.locations,
        max_retries=args.max_retries,
        parallel=args.parallel,
    )
