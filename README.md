## AVL AK collector
通过AK指令采集AK数据
## Usage
0. 安装```Doctopus```采集库
1. 修改```conf/conf.toml```中user_conf.check.ak相关host与port参数，与ak server相连
2. 修改同文件allowed_cmds里的指令，这些为需要发送的ak指令
3. 修改```lib/ak_process.py```里的process_dict,添加相关的ak指令处理函数
4. ```python manage.py -t ziyan```即可运行

## Attention
- 当前转鼓所做试验车型无法直接通过指令获取，需进行两步：
    1. ```ASIA```指令获取所有车辆模型参数，并作成字典结构，保存到redis中
    2. ```ASME```指令获取车辆相关参数，然后到redis中与数据库进行匹配，找到当前车型