# docker-wecomchan

[GPL LICENSE](https://github.com/vergilgao/docker-wecomchan/blob/master/LICENSE)

建立应用详情见： [easychen/wecomchan](https://github.com/easychen/wecomchan)

## docker 部署

```sh
docker run --name wecomchan -itd -v ${PWD}/config:/config -e UID=$(stat -c %u test) -e GID=$(stat -c %g test) -p 9877:9877 ghcr.io/vergilgao/wecomchan:latest
```

首次运行时我们将在挂载的`config`目录下创建配置文件。

```
[server]
ip=127.0.0.1
port=9877

[wecom]
cid=
aid=
secret=
```

一般来说，你只需要修改`wecom`节点下的3个配置:

- cid 企业微信公司ID
- aid 企业应用的ID
- secret 企业微信应用Secret

修改完成后，你需要重新启动docker容器。

## api

api只支持 post

当前版本只支持发送 text 消息

api 路径为 /api/text

发送的 body 内容即为推送的消息内容，其中引号无需转义：

```
你的快递已到，请携带工卡前往邮件中心领取。
出发前可查看<a href="http://work.weixin.qq.com">邮件中心视频实况</a>，聪明避开排队。
```

服务器收到命令后，统一响应 http 代码为 200
返回的消息体为如下格式：

```
{
    "code": 0
    "error_message": ""
}
```

当 code 为 0 时，说明一切正常。
其他 code 代码的说明如下：

- 1300 发送消息到企业微信接口返回错误，响应代码见 error_message
- 1301 发送消息到企业微信接口失败，对端响应错误
- 1302 请求企业微信token错误
- 1400 请求了当前服务器不支持的路由
