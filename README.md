# OLGram

本项目拉取自olgram的项目,是一个telegram转发机器人,通过谷歌翻译中文,可提供有限的协助,也欢迎其他用户提供优秀的改良意见

[![Static Analysis Status](https://github.com/civsocit/olgram/workflows/Linter/badge.svg)](https://github.com/civsocit/olgram/actions?workflow=Linter) 
[![Deploy Status](https://github.com/civsocit/olgram/workflows/Deploy/badge.svg)](https://github.com/civsocit/olgram/actions?workflow=Deploy)
[![Documentation](https://readthedocs.org/projects/olgram/badge/?version=latest)](https://olgram.readthedocs.io)

----------------------------------------------------------------------------------------------------------------
[@OlgramBot](https://t.me/olgrambot) - Telegram 中的反馈机器人构造函数

操作文档: https://olgram.readthedocs.io


**Olgram** [@OlgramBot](https://t.me/olgrambot) 是一个构造函数，允许您创建反馈机器人
在电报中。 连接到 Olgram 后，您的机器人用户将能够编写将在聊天中发送给您的消息，您可以在其中回复它们。

此类机器人可能对您有用，例如：

   *示例 1.* 您管理 Telegram 频道并希望让您的订阅者有机会与您联系，但不想留下他们的个人联系方式。 然后你可以创建一个反馈机器人：订阅者会写信给机器人，你会通过机器人匿名回复。

   *示例 2.* 您在 Telegram 或技术支持小组中组织了一个小型呼叫中心。 使用反馈机器人，您可以在专家的一般聊天中接受用户的请求，讨论这些请求并直接从该聊天中回复用户。

阅读更多: https://olgram.readthedocs.io


----------------------------------------------------------------------------------------------------------------
对于开发人员
下载和构建
你可以在你的服务器上部署 Olgram。您将需要自己的 VPS 或任何具有静态地址或域的主机。

1、创建一个.env文件，像example.env一样 填写需要填写的变量：

BOT_TOKEN- 新的机器人令牌，来自@botfather

POSTGRES_PASSWORD- 任何随机密码

TOKEN_ENCRYPTION_KEY- 除 POSTGRES_PASSWORD 以外的任何随机密码

WEBHOOK_HOST- 项目运行所在服务器的IP地址或域名

2. 在 .env 文件旁边，保存 docker-compose.yaml文件并构建它：


sudo docker-compose up -d   保存已修改内容并重构它

Olgram 已启动并运行！

警告:不要丢失 TOKEN_ENCRYPTION_KEY！它无法恢复。如果您丢失了 TOKEN_ENCRYPTION_KEY，您将丢失用户在您的机器人上注册的所有机器人的令牌。

----------------------------------------------------------------------------------------------------------------







自定义修改机器人

----------------------------------------------------------------------------------------------------------------

您可能希望对项目进行更改并使用这些更改运行机器人。

1  克隆存储库
git clone https://github.com/civsocit/olgram


2  对代码进行任何更改

3  在包含存储库的目录中（在 .yaml 文件旁边），创建一个 .env 文件并按照上面的说明进行填写

4  构建并启动服务器：
sudo docker-compose -f docker-compose-src.yaml up -d

----------------------------------------------------------------------------------------------------------------

Docker-compose.yaml 包含最低配置。对于在严肃的项目中使用，我们建议：
*购买域名并为您的主机设置
*设置反向代理和自动续订证书 - 例如，使用Traefik
*使用Cloudflare隐藏服务器 IP，以便 bot 用户无法从 bot 的 Webhook 中找到主机的 IP 地址。
*更复杂的配置示例在docker-compose-full.yaml 文件中

如何限制对机器人的访问
默认情况下，所有 Telegram 用户都可以写入您的 Olgram 并在那里注册他们的机器人。要限制对机器人的访问，请在环境变量（.env 文件）中指定：

ADMIN_ID=<聊天ID>

聊天 ID 是您的 Telegram ID 或 Telegram 群聊 ID。可以使用 /chatid 命令查看标识符。

语言设置
默认语言是俄语。可以按照 locales/ 文件夹中的中文模式添加对其他语言的支持（Chinese - zh）。在 .env 设置中指定语言代码

O_LANG=<语言代码>
