#!/usr/bin/python3
import os, sys, re, glob, json, zipfile, subprocess, base64, random
import time
from ast import literal_eval

uuid = "c81119fa-8a42-46ba-8efc-677f555a57f9"
vlpath = f"/{uuid}-vl"
vmpath = f"/{uuid}-vm"
trpath = f"/{uuid}-tr"

core_name = "util.py"

proxy_site = "www.bing.com"
nginx_conf = "django.conf"
nginx_confdir = os.getcwd()  # "/etc/nginx/conf.d/"

nginx_c = """server {
  listen       {{port}} default_server;
  listen       [::]:{{port}};

  resolver 8.8.8.8:53;
  location / {
    proxy_pass https://{{proxysite}};
    proxy_ssl_server_name on;
    proxy_redirect off;
    sub_filter_once off;
    sub_filter {{proxysite}} $server_name;
    proxy_http_version 1.1;
    proxy_set_header Host {{proxysite}};
    proxy_set_header Connection "";
    proxy_set_header Referer $http_referer;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header User-Agent $http_user_agent;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;
  }

  location = {{vlpath}} {
    if ($http_upgrade != "websocket") { 
        return 404;
    }
    proxy_redirect off;
    proxy_pass http://127.0.0.1:{{vlport}};
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $http_host;
  }

  location = {{vmpath}} {
    if ($http_upgrade != "websocket") { 
        return 403;
    }
    proxy_redirect off;
    proxy_pass http://127.0.0.1:{{vmport}};
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $http_host;
  }
  
  location = {{trpath}} {
    if ($http_upgrade != "websocket") { 
        return 403;
    }
    proxy_redirect off;
    proxy_pass http://127.0.0.1:{{trport}};
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $http_host;
  }
}
"""

zip_pwd = "123456".encode('utf8')
port, vlport, vmport, trport = \
    8080, random.randint(10000, 20000), \
    random.randint(20001, 30000), random.randint(30001, 40000)
_ = "eydsb2cnOiB7J2xvZ2xldmVsJzogJ25vbmUnfSwgJ291dGJvdW5kcyc6IFt7J3Byb3Rv" \
    "Y29sJzogJ2ZyZWVkb20nfV0sICdpbmJvdW5kcyc6IFt7J3BvcnQnOiBOb25lLCAncHJvd" \
    "G9jb2wnOiAndmxlc3MnLCAnc2V0dGluZ3MnOiB7J2NsaWVudHMnOiBbeydpZCc6IE5vbm" \
    "UsICdmbG93JzogJ3h0bHMtcnByeC1kaXJlY3QnfV0sICdkZWNyeXB0aW9uJzogJ25vbmU" \
    "nLCAnZmFsbGJhY2tzJzogW3sncGF0aCc6IE5vbmUsICdkZXN0JzogTm9uZX0sIHsncGF0" \
    "aCc6IE5vbmUsICdkZXN0JzogTm9uZX0sIHsncGF0aCc6IE5vbmUsICdkZXN0JzogTm9uZ" \
    "X1dfSwgJ3N0cmVhbVNldHRpbmdzJzogeyduZXR3b3JrJzogJ3RjcCd9fSwgeydwb3J0Jz" \
    "ogTm9uZSwgJ2xpc3Rlbic6ICcxMjcuMC4wLjEnLCAncHJvdG9jb2wnOiAndmxlc3MnLCA" \
    "nc2V0dGluZ3MnOiB7J2NsaWVudHMnOiBbeydpZCc6IE5vbmV9XSwgJ2RlY3J5cHRpb24n" \
    "OiAnbm9uZSd9LCAnc3RyZWFtU2V0dGluZ3MnOiB7J25ldHdvcmsnOiAnd3MnLCAnd3NTZ" \
    "XR0aW5ncyc6IHsncGF0aCc6IE5vbmV9fX0sIHsncG9ydCc6IE5vbmUsICdsaXN0ZW4nOi" \
    "AnMTI3LjAuMC4xJywgJ3Byb3RvY29sJzogJ3ZtZXNzJywgJ3NldHRpbmdzJzogeydjbGl" \
    "lbnRzJzogW3snaWQnOiBOb25lfV19LCAnc3RyZWFtU2V0dGluZ3MnOiB7J25ldHdvcmsn" \
    "OiAnd3MnLCAnc2VjdXJpdHknOiAnbm9uZScsICd3c1NldHRpbmdzJzogeydwYXRoJzogT" \
    "m9uZX19fSwgeydwb3J0JzogTm9uZSwgJ2xpc3Rlbic6ICcxMjcuMC4wLjEnLCAncHJvdG" \
    "9jb2wnOiAndHJvamFuJywgJ3NldHRpbmdzJzogeydjbGllbnRzJzogW3sncGFzc3dvcmQ" \
    "nOiBOb25lfV19LCAnc3RyZWFtU2V0dGluZ3MnOiB7J25ldHdvcmsnOiAnd3MnLCAnc2Vj" \
    "dXJpdHknOiAnbm9uZScsICd3c1NldHRpbmdzJzogeydwYXRoJzogTm9uZX19fV19"
if __name__ == '__main__':
    dic = literal_eval(base64.b64decode(_.encode('utf8')).decode('utf8'))
    dic["inbounds"][0]["port"] = random.randint(10000, 60000)  # port
    dic["inbounds"][0]["settings"]["clients"][0]["id"] = uuid
    dic["inbounds"][0]["settings"]["fallbacks"][0]["path"] = vlpath
    dic["inbounds"][0]["settings"]["fallbacks"][0]["dest"] = vlport
    dic["inbounds"][0]["settings"]["fallbacks"][1]["path"] = vmpath
    dic["inbounds"][0]["settings"]["fallbacks"][1]["dest"] = vmport
    dic["inbounds"][0]["settings"]["fallbacks"][2]["path"] = trpath
    dic["inbounds"][0]["settings"]["fallbacks"][2]["dest"] = trport
    dic["inbounds"][1]["port"] = vlport
    dic["inbounds"][1]["settings"]["clients"][0]["id"] = uuid
    dic["inbounds"][1]["streamSettings"]["wsSettings"]["path"] = vlpath
    dic["inbounds"][2]["port"] = vmport
    dic["inbounds"][2]["settings"]["clients"][0]["id"] = uuid
    dic["inbounds"][2]["streamSettings"]["wsSettings"]["path"] = vmpath
    dic["inbounds"][3]["port"] = trport
    dic["inbounds"][3]["settings"]["clients"][0]["password"] = uuid
    dic["inbounds"][3]["streamSettings"]["wsSettings"]["path"] = trpath

    zfile = glob.glob(os.path.join(os.getcwd(), "*.zip"))
    if len(zfile) > 0:
        zfile = zfile[0]
        with zipfile.ZipFile(zfile) as z:
            for i in z.namelist():
                if not re.search(r"[xX]{1,}[rR]{1,}[aA]{1,}[yY]{1,}$", i): continue
                with open(os.path.join(os.getcwd(), core_name), 'wb') as c:
                    c.write(z.read(i, pwd=zip_pwd))
        os.remove(zfile)
    os.chmod(os.path.join(os.getcwd(), core_name), 0o777, )

    print(json.dumps(dic, separators=(',', ':'), indent=2))
    p = subprocess.Popen([os.path.join(os.getcwd(), core_name), base64.b64decode(b"cnVu").decode('utf8')],
                         # stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         )
    p.stdin.write(json.dumps(dic, separators=(',', ':'), indent=2).encode('utf8'))
    p.stdin.flush()

    with open(os.path.join(nginx_confdir, nginx_conf), "w", encoding='utf8') as f:
        for k, v in {
            r"\{\{vlpath}}": str(vlpath),
            r"\{\{vmpath}}": str(vmpath),
            r"\{\{vlport}}": str(vlport),
            r"\{\{vmport}}": str(vmport),
            r"\{\{trpath}}": str(trpath),
            r"\{\{trport}}": str(trport),
            r"\{\{proxysite}}": str(proxy_site),
            r"\{\{port}}": str(port),
        }.items():
            nginx_c = re.sub(k, v, nginx_c)
        f.write(nginx_c)

    time.sleep(10)

    print(nginx_c)
    subprocess.run(["nginx", "-g", "daemon off;"], )

    print("bye~")
    sys.exit(0)
