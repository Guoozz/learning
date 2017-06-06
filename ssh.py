import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

client.connect("127.0.0.1", look_for_keys=True)
channel = client.invoke_shell()

buff = b''
channel.send("ls\n")

while channel.recv_ready():
    resp = channel.recv(9999)
    buff += resp.strip()

    print(buff.decode('utf-8'))



