# abuse-ssl-bypass-waf

**Helping you find the SSL/TLS Cipher that WAF cannot decrypt and Server can decrypt same time**



Referer article [Bypassing Web-Application Firewalls by abusing SSL/TLS](https://0x09al.github.io/waf/bypass/ssl/2018/07/02/web-application-firewall-bypass.html)

#### Attack idea

![](pictures/mind.png)



#### Usage

`python abuse-ssl-bypass-waf.py -h`

**Notice**: If you are worry about WAF drop the connection, you have better not use `-thread` option.



#### Thirdparty

**curl**

**sslcan**

**Notice**: If your operation system is not Windows, you should be modify `config.py` ，adjust `curl`  and `sslscan` path & command values.



#### Running

![](pictures/example.png)