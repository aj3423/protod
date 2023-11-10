## Decode protobuf without message definition.
## Try it online
http://168.138.55.177/
# Screenshot
![protod](https://github.com/aj3423/protod/assets/4710875/bb8986db-ed7e-4cbf-967b-9d28cc6d4237)
## Install
`pip install protod`
## The command line tool

- `protod 080102...`
- `protod 08 01 02...` (with space/tab/newline)
- `protod --b64 CAEIAQ==`
- `protod --file ~/pb.bin`
- type `protod` for detail
  
## library protod
It uses different `Renderer` to generate different output:
- For console:
```python
print(protod.dump(proto)) # ConsoleRenderer is used by default
```
- For html:
```python
html_tag = protod.dump(proto, protod.HtmlRenderer())
# send the html_tag to client browser
 $('#div').text(html_tag)
```
- For other format:   
This [example](https://github.com/aj3423/protod/blob/master/example/mitmproxy_proto_view.py) demonstrates how to implemente custom `Renderer`, it's an addon for [mitmproxy](https://github.com/mitmproxy/mitmproxy/)

   ![image](https://github.com/aj3423/protod/assets/4710875/aca8a5b1-4c05-4cc4-8346-f3b91a6ca8d7)

