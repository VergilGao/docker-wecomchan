from http.server import BaseHTTPRequestHandler
from requests import post as requests_post
from requests import get as requests_get
from json import loads as json_loads
from json import dumps as json_dumps
from urllib.parse import parse_qs, unquote
from re import match as re_match


class ResquestHandler(BaseHTTPRequestHandler):

    __cid: str = ""
    __aid: str = ""
    __secret: str = ""

    @classmethod
    def set_cid(cls, cid: str):
        cls.__cid = cid

    @classmethod
    def get_cid(cls):
        return cls.__cid

    @classmethod
    def set_aid(cls, aid: str):
        cls.__aid = aid

    @classmethod
    def get_aid(cls):
        return cls.__aid

    @classmethod
    def set_secret(cls, secret: str):
        cls.__secret = secret

    @classmethod
    def get_secret(cls):
        return cls.__secret

    def do_GET(self):
        self.__send_response(415, 'Only post is supported')

    def do_POST(self):
        if '?' in self.path:
            split = self.path.split('?', 1)
            path = split[0]
            parameters = parse_qs(unquote(split[1]))
        else:
            path = self.path

        routeMatch = re_match(r'^/api/([0-9a-zA-Z]+)[/\n\r]*$', path)

        if not routeMatch:
            self.__send_response(
                200, {'code': 1400, 'error_message': 'route error'})
            return

        route: str = routeMatch.group(1)

        if route == 'text':
            result, token = self.__get_token()
            if not result:
                self.__send_response(
                    200,  {'code': 1302, 'error_message': 'request token error'})
                return

            touser: str = parameters["touser"][0] if parameters and "touser" in parameters else '@all'.replace(
                '"', '')
            send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}'
            length = int(self.headers['content-length'])
            content = self.rfile.read(length)
            content = json_dumps(content.decode(
                encoding='utf-8'), ensure_ascii=False)
            data = f'''{{ 
"touser" : "{touser}",
"msgtype": "{route}",
"agentid" : {self.get_aid()},
"text" : {{
"content": {content}
}},
"enable_duplicate_check": 0,
"duplicate_check_interval": 300
}}'''.encode(encoding='utf-8')
            send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}'
            response = requests_post(send_msg_url, data=data)

            if not response.ok:
                self.__send_response(
                    200, {'code': 1301, 'error_message': 'message send error'})
                return

            response = json_loads(response.content)
            respose_code = response.get('errcode')

            if respose_code == 0:
                self.__send_response(200,  {'code': 0, 'error_message': ''})
            else:
                self.__send_response(
                    200,  {'code': 1300, 'error_message': f'wecom return error: {respose_code}'})
            return

        self.__send_response(
            200, {'code': 1400, 'error_message': 'route error'})
        return

    def __get_token(self) -> tuple[bool, str]:
        response = requests_get(
            f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.get_cid()}&corpsecret={self.get_secret()}")
        if not response.ok:
            return False, response.content.decode()
        response_message = json_loads(response.content)
        errcode = response_message.get('errcode')
        if errcode == 0:
            token: str = response_message.get('access_token')
            if token and len(token) > 0:
                return True, token
        else:
            return False, response_message

    def __send_response(self, code: int, content: dict | str | None):
        if isinstance(content, dict):
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json_dumps(content).encode(encoding='utf-8'))
        else:
            self.send_response(code)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(content.encode(encoding='utf-8'))
