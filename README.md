## Decode protobuf without proto.
## Try it online
http://168.138.55.177/
# Screenshot
![protod](https://github.com/aj3423/protod/assets/4710875/bb8986db-ed7e-4cbf-967b-9d28cc6d4237)
## Install
`pip install protod`
## The command line tool

- `protod 080102...`
- `protod '08 01 02...'` (with space/tab/newline)
- `protod --b64 CAEIAQ==`
- `protod --file ~/pb.bin`
- `protod` for help
  
## Library protod

- For console:
```python
print(protod.dump(proto)) # ConsoleRenderer by default
```
- Costumize `Renderer` to generate different output:
```python
print(protod.dump(
    proto,

    renderer = JsonRenderer(), # see example/json_renderer.py

    # The default string decoder will try to detect all encodings,
    # provide a custom decoder to increase the accuracy if you know the encoding.
    str_decoder = decode_utf8, # see example/json_renderer.py
))
```
- [A sample addon](https://github.com/aj3423/protod/blob/master/example/mitmproxy_proto_view.py) for [mitmproxy](https://github.com/mitmproxy/mitmproxy/)

   ![image](https://github.com/aj3423/protod/assets/4710875/aca8a5b1-4c05-4cc4-8346-f3b91a6ca8d7)

