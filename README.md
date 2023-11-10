## Decode protobuf without message definition.
## Try it online
An old Golang protod as the backend: http://168.138.55.177/. See [aproto](https://github.com/aj3423/aproto) if you need a Golang module.
# Screenshot
![protod](https://github.com/aj3423/protod/assets/4710875/bb8986db-ed7e-4cbf-967b-9d28cc6d4237)
## Install
`pip install protod`
## The command line tool
```
usage: protod [-h] [--file FILE] [--hex] [--b64] [--max_bin n] ...

positional arguments:
  rest         hex string to parse, eg: "08 01..."

options:
  -h, --help   show this help message and exit
  --file FILE  file path that contains proto data
  --hex        content is hex string, eg: "080102..."
  --b64        content is base64
  --max_bin n  binary exceeds `n` bytes is truncated and followed by a "..."
```
eg:
- `protod 080102...`
- `protod 08 01 02...` (with space/tab/newline)
- `protod --b64 CAEIAQ==`
- `protod --file ~/pb.bin`
- ...
  
## library protod
Use different `Renderer` to generate different output:
1. For console:
```python
print(protod.dump(proto)) # it uses ConsoleRenderer by default
```
2. For html:
```python
html_tag = protod.dump(proto, protod.HtmlRenderer())
# send the html_tag to client browser
 $('#div').text(html_tag)
```
3. For other custom format:   
This [example](https://github.com/aj3423/protod/blob/master/example/mitmproxy_proto_view.py) demonstrates implementing a custom `Renderer`, it's for decoding protobuf in [mitmproxy](https://github.com/mitmproxy/mitmproxy/)

   ![image](https://github.com/aj3423/protod/assets/4710875/aca8a5b1-4c05-4cc4-8346-f3b91a6ca8d7)

