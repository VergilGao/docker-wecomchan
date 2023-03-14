import os
from server import ResquestHandler
from http.server import HTTPServer
from argparse import ArgumentParser
from configparser import ConfigParser


def main(ip: str, port: int, cid: str, aid: str, secret: str) -> None:
    try:
        server = HTTPServer((ip, port), ResquestHandler)
        ResquestHandler.set_cid(cid)
        ResquestHandler.set_aid(aid)
        ResquestHandler.set_secret(secret)
        print(f"Starting server, listen at: {ip}:{port}")
        server.serve_forever()
    except KeyboardInterrupt as e:
        os._exit(0)
    except Exception as e:
        print(e)
        os._exit(1)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--config', type=str, default='/config/.wecomchan.ini')
    args = parser.parse_args()
    parser = ConfigParser()
    parser.read(args.config, encoding='utf-8')
    ip = parser.get('server', 'ip', raw=True).strip()
    port = int(parser.get('server', 'port', raw=True).strip())
    cid = parser.get('wecom', 'cid', raw=True).strip()
    aid = parser.get('wecom', 'aid', raw=True).strip()
    secret = parser.get('wecom', 'secret', raw=True).strip()
    main(ip, port, aid=aid, cid=cid, secret=secret)
