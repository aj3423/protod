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
  
## library protod
It uses different `Renderer` to generate different output:
- For console:
```python
print(protod.dump(proto_bytes)) # ConsoleRenderer is used by default
```

There are [examples](https://github.com/aj3423/protod/blob/master/example) demonstrate how to write custom `Renderer`s:
- json

 ![image](https://github.com/aj3423/protod/assets/4710875/2c3bddb2-06e7-44b4-844f-eaaff6a26d6f)

- html

 ![image](https://github.com/aj3423/protod/assets/4710875/39583ae3-1d77-4c22-b4a0-ed9d12bd8305)

- Mitmproxy addon:
 
 ![image](https://github.com/aj3423/protod/assets/4710875/aca8a5b1-4c05-4cc4-8346-f3b91a6ca8d7)

