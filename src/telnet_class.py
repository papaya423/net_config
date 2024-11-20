import logging
import telnetlib
import time

import re


def remove_invisible_characters(s):
    # 正则表达式匹配所有不可见字符
    pattern = re.compile(r'[\x00-\x1F\x7F-\x9F]')
    # 使用正则表达式的sub方法替换匹配到的字符为空字符串
    return pattern.sub('', s)
class TelnetClient():
    def __init__(self, ):
        self.tn = telnetlib.Telnet()

    # 此函数实现telnet登录主机
    def login_host(self, host_ip, port, username, password):
        try:
            print("ad host:", host_ip, "port:", port);
            self.tn = telnetlib.Telnet(host_ip, port=23)

        except:
            logging.warning('%s网络连接失败' % host_ip)
            return False
        # 等待login出现后输入用户名，最多等待10秒
        # 不用输入用户名
        # self.tn.write(username.encode('ascii') + b'\r\n')
        # 等待Password出现后输入用户名，最多等待10秒
        self.tn.read_until(b'Password: ', timeout=1)
        self.tn.write(password.encode('ascii') + b'\n')
        # 延时两秒再收取返回结果，给服务端足够响应时间
        time.sleep(0.1)
        # 获取登录结果
        # read_very_eager()获取到的是的是上次获取之后本次获取之前的所有输出
        command_result = self.tn.read_very_eager().decode('ascii')
        if '<' in command_result and '>' in command_result:
            logging.warning('%s登录成功' % host_ip)
            print(command_result)
            return True
        else:
            logging.warning('%s登录失败，用户名或密码错误' % host_ip)
            return False

    # 此函数实现执行传过来的命令，并输出其执行结果
    def execute_some_command(self, command):
        # 执行命令
        command_result=""
        self.tn.write(command.encode('ascii') + b'\n')
        # self.tn.write(b'\nver\n')
        time.sleep(0.1)
        # 获取命令结果
        tmp = self.tn.read_very_eager()
        tmp = tmp.decode('ascii')
        command_result = command_result + tmp
        command_result = command_result.replace("---- More ----", "\r\n")
        while "---- More ----" in tmp:
            self.tn.write(b'\r\n')
            time.sleep(0.1)
            tmp = self.tn.read_very_eager().decode('ascii')
            tmpdata=tmp
            tmpdata = tmpdata.replace("---- More ----","\r\n")
            tmpdata = remove_invisible_characters(tmpdata)
            tmpdata = tmpdata.replace("[42D","")
            tmpdata = tmpdata.lstrip()
            command_result =command_result+"\r\n"+tmpdata

            print(f"tmp={tmp}")
            print(f"command_result={command_result}")
        logging.warning('命令执行结果：\n%s' % command_result)
        # print("***********结果返回**************：\n", command_result);
        return command_result;

    # 退出telnet
    def logout_host(self):
        self.tn.write(b"exit\n")


if __name__ == '__main__':
    host_ip = '192.168.17.2'
    port = 23
    username = ''
    password = 'huawei'
    command = ""
    telnet_client = TelnetClient()
    # 如果登录结果返加True，则执行命令，然后退出
    if telnet_client.login_host(host_ip, port, username, password):
        while True:
            command = input("input:")
            if str(command).lower() == "exit":
                telnet_client.logout_host()
                break;
            # command="\r\n"+command+"\r\n";
            result = telnet_client.execute_some_command(command)
