#!/bin/env python
# -*- coding: utf-8 -*-  
#pip install boto
#pip install dns

import boto, sys, getopt, dns
from boto.route53.connection import Route53Connection
from boto.route53.record import ResourceRecordSets

reload(sys)
sys.setdefaultencoding('utf8')


#把一个具体record信息转成字典
#return: dict
def get_rrset_dict(rrset):
    rrset_dict = {}
    #recoed 名
    rrset_dict['name'] = rrset.name
    rrset_dict['type'] = rrset.type
    rrset_dict['ttl'] = rrset.ttl
    rrset_dict['records'] = rrset.resource_records
    #返回字典
    return rrset_dict

#输出
out = sys.stdout.write

#查询DNS
#args: name
#Type: str
#comment: www.example.com
#return: 未check
def resolve_name_ip(host_zone_name):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [
        '8.8.8.8',
        '8.8.4.4'
    ]
    answer = resolver.query(host_zone_name)
    """
    >>> answer.response.answer[0].to_text()
    home.mydomain.com. 60 IN A 192.168.0.2'
    >>> answer.response.answer[0].items
    [<DNS IN A rdata: 192.168.0.2>]
    >>> answer.response.answer[0].items[0].address
    '192.168.0.2'
    """
    return answer.response.answer[0].items[0].address

#输出所有信息
def out_host_zones(route53,short = 0):
    #返回所有route53上域名
    lm_get_zones_info = route53.get_all_hosted_zones()
    #获取域名数量
    host_zone_len = len(lm_get_zones_info['ListHostedZonesResponse']['HostedZones'])
    out_put = ""
    #循环所有域名
    for host_zone_info in range(0, host_zone_len):
        #line============================
        if host_zone_info == 0 and short == 0:
            out_put += "="*120 + '\n'
        elif host_zone_info != 0 and short == 0:
            out_put += "-"*120 + '\n'
        #line over=======================

        #域名ID
        host_zone_id = lm_get_zones_info['ListHostedZonesResponse']['HostedZones'][host_zone_info]['Id'].replace('/hostedzone/', '')
        #域名名称
        host_zone_name = lm_get_zones_info['ListHostedZonesResponse']['HostedZones'][host_zone_info]['Name'].strip('.')
        #打印名称 & ID
        out_put += "Host zone: %-15s   Host ID: %-20s\n" % (host_zone_name, host_zone_id)
        #获取域名所有记录
        rrsets = route53.get_all_rrsets(host_zone_id)
        rrset_dicts = []
        #把记录内所有信息放在字典内
        for rrset in rrsets:
            rrset_dicts.append(get_rrset_dict(rrset))
        #输出所有域名、记录等  默认
        if short == 0:
            #制表格式化
            out_put += "\n%-15s\t%5s\t%-6s\t%s \n" % ("Name", "Type", "TTL", "Record")
            #循环每个域名
            for rrset_dict in rrset_dicts:
                 rrset_records_len = len(rrset_dict['records'])      
                 for i in range(0,rrset_records_len):
                     if i == 0 :
                         out_put += "%-15s\t%5s\t%-6s\t%s \n" % (rrset_dict['name'],\
                            rrset_dict['type'],rrset_dict['ttl'],rrset_dict['records'][i])
                     #当有多条record记录时
                     else:
                         out_put += " "*15+"\t"+" "*5+"\t"+" "*6+"\t"+"%s\n" % (rrset_dict['records'][i])


        #line==============================
        if host_zone_info == host_zone_len-1 and short == 0:
            out_put += "="*120 + '\n'
        #line over=========================
    out(out_put)

#获取单个域名内所有信息
#args:host_zone_id: 
#type:str
#comment:host id
#return: 
def host_zone_info_single(host_zone_id, silent=0):
    #获取host zone info
    lm_get_zone_info = route53.get_hosted_zone(host_zone_id)
    host_zone_info = lm_get_zone_info
    out_put = "="*120 + '\n'
    #域名ID
    host_zone_id = host_zone_info['GetHostedZoneResponse']['HostedZone']['Id'].replace('/hostedzone/', '')
    #域名名称
    host_zone_name = host_zone_info['GetHostedZoneResponse']['HostedZone']['Name'].strip('.')
    #打印名称 & ID
    out_put += "Host zone: %-15s   Host ID: %-20s\n" % (host_zone_name, host_zone_id)
    #获取域名所有记录
    rrsets = route53.get_all_rrsets(host_zone_id)
    rrset_dicts = []
    #把记录内所有信息放在字典内
    for rrset in rrsets:
        rrset_dicts.append(get_rrset_dict(rrset))
    
    
    #制表格式化
    out_put += "\n%-15s\t%5s\t%-6s\t%s \n" % ("Name", "Type", "TTL", "Record")
    #循环每个域名
    for rrset_dict in rrset_dicts:
        rrset_records_len = len(rrset_dict['records'])      
        for i in range(0,rrset_records_len):
            if i == 0 :
                out_put += "%-15s\t%5s\t%-6s\t%s \n" % (rrset_dict['name'],\
                rrset_dict['type'],rrset_dict['ttl'],rrset_dict['records'][i])
            #当有多条record记录时
            else:
                out_put += " "*15+"\t"+" "*5+"\t"+" "*6+"\t"+"%s\n" % (rrset_dict['records'][i])
    #line   
    out_put += "="*120 + '\n'
    #是否静默
    if silent == 0:
       out(out_put)
    return host_zone_info, rrset_dicts

#删除指定域名记录
#args:route53
#type:object
#host_zone_id
#type: str
#host_zone_AND_ip:
#type: str like 'www.example.com:114.114.114.114' 可能日后会延长
#silent
#type: number
#comment: 是否输出系统信息
#return:
#type: number
#comment only 1 (success)& 0 (failed) 
def host_zone_delete(route53, host_zone_id, host_zone_AND_ip, silent=0):
    #调用函数获取域名所有信息和域名所有记录
    host_zone_info, host_zone_rrsets_dicts = host_zone_info_single(host_zone_id, 1)
    #实例化records
    changes = ResourceRecordSets(route53, host_zone_id, '')
    #分割参数 host_zone:ip:...
    host_zone_delete_info = host_zone_AND_ip.split(':')
    #输出的系统信息初始化
    out_put = ""
    #输入得参数是否与现有的dns记录匹配的标志
    is_matched = 0
    #循环所有记录词典
    for record in host_zone_rrsets_dicts:
        #dns上记录是否与输入的记录 名匹配
        if record['name'].strip('.') == host_zone_delete_info[0]:
            if ',' in host_zone_delete_info[1]:
                host_zone_delete_ip_arr = sorted(host_zone_delete_info[1].split(','))
                record['records'] = sorted(record['records'])
                if host_zone_delete_ip_arr == record['records']:
                    is_matched = 1
                    chan = changes.add_change("DELETE", host_zone_delete_info[0], record['type'], record['ttl'])
                    for host_zone_delete_ip_str in host_zone_delete_ip_arr:
                        chan.add_value(host_zone_delete_ip_str)
                        #执行删除
                    commit = changes.commit()
                    break
            elif record['records'][0] == host_zone_delete_info[1]:
                #修改标志位
                is_matched = 1
                out_put += 'Host zone 记录符合，删除%s %s %s\n' % (record['name'].strip('.'), host_zone_delete_info[1], record['type'])
                #pending 删除
                chan = changes.add_change("DELETE", host_zone_delete_info[0], record['type'], record['ttl'])
                chan.add_value(host_zone_delete_info[1])
                #执行删除
                commit = changes.commit()
                break
    #匹配检查,未匹配输出系统信息
    if is_matched == 0:
        out_put += "Host zone 记录与 参数不匹配\n"
    #是否输出系统信息 静默标志位检查
    if silent == 0:
        out(out_put)
    #返回是否成功
    return is_matched
    
#创建指定域名记录
#args:route53
#type:object
#host_zone_id
#type: str
#host_zone_AND_ip:
#type: str like 'www.example.com:114.114.114.114' 可能日后会延长
#silent
#type: number
#comment: 是否输出系统信息
#return:
#type: number
#comment only 1 (success)& 0 (failed)  未校验
def host_zone_create(route53, host_zone_id, host_zone_AND_ip, silent=0):
    #调用函数获取域名所有信息和域名所有记录
    host_zone_info, host_zone_rrsets_dicts = host_zone_info_single(host_zone_id, 1)
    #实例化records
    changes = ResourceRecordSets(route53, host_zone_id, '')
    #分割参数 host_zone:ip:...
    host_zone_delete_info = host_zone_AND_ip.split(':')
    #输出的系统信息初始化
    out_put = ""
    #输入得参数是否与现有的dns记录匹配的标志
    is_matched = 0
    #循环所有记录词典
    for record in host_zone_rrsets_dicts:
        #dns上记录是否与输入的记录 名匹配
        if record['name'].strip('.') == host_zone_delete_info[0]:
            for record_ip in record['records']:
                if ',' in host_zone_delete_info[1]:
                    host_zone_delete_ip_arr = host_zone_delete_info[1].split(',')
                    if record_ip in host_zone_delete_ip_arr:
                        record_ip ==  host_zone_delete_info[1]
                        #修改标志位
                        is_matched = 1
                        out_put += 'Host zone 记录已存在，新建失败！ %s %s %s\n' % (record['name'].strip('.'), record_ip, record['type'])
                        #pending 删除
                        #chan = changes.add_change("DELETE", host_zone_delete_info[0], record['type'], record['ttl'])
                        #chan.add_value(host_zone_delete_info[1])
                        #执行删除
                        #commit = changes.commit()
                        break 
                #IP是否匹配
                elif record_ip ==  host_zone_delete_info[1]:
                    #修改标志位
                    is_matched = 1
                    out_put += 'Host zone 记录已存在，新建失败！ %s %s %s\n' % (record['name'].strip('.'), record_ip, record['type'])
                    #pending 删除
                    #chan = changes.add_change("DELETE", host_zone_delete_info[0], record['type'], record['ttl'])
                    #chan.add_value(host_zone_delete_info[1])
                    #执行删除
                    #commit = changes.commit()
                    break
    #匹配检查,未匹配输出系统信息
    if is_matched == 0:
        chan =changes.add_change('CREATE', host_zone_delete_info[0],  host_zone_delete_info[2], ttl=host_zone_delete_info[3])
        if ',' in host_zone_delete_info[1]:
            host_zone_delete_ip_arr = host_zone_delete_info[1].split(',')
            for host_zone_delete_ip_str in host_zone_delete_ip_arr:
                chan.add_value(host_zone_delete_ip_str)
        else:
        #out_put += "Host zone 记录与 参数不匹配\n"
            chan.add_value(host_zone_delete_info[1])
        commit = changes.commit()
    #是否输出系统信息 静默标志位检查
    if silent == 0:
        out(out_put)
    #返回是否成功
    return is_matched




#初始化
#def init():
#    pass

def get_args(route53):
    try:
        opts, args = getopt.getopt(sys.argv[1:],"I:d:c:u:U:hv",['ID=','help','version','short','all'])
    except getopt.GetoptError:
        pass
    for op,value in opts:
        #指定域名ID
        if op in ("-I", "--ID"):
            flag = 0
            for o, v in opts:
                if o in ("-d"):
                    flag = 1
                    host_zone_delete(route53, value, v)
                if o in ("-c"):
                    flag = 1
                    host_zone_create(route53, value, v)
            for o, v in opts:
                if o in ("-u") and flag != 1:
                    for o2,v2 in opts:
                        if o2 in ("-U"):
                            host_zone_delete(route53, value, v)
                            host_zone_create(route53, value, v2)
            #if flag == 0:
            #    host_zone_info_single(value)
            host_zone_info_single(value)
        #帮助
        if op in ("-h", "--help"):
            pass
        #版本号
        if op in ("-v", "--version"):
            pass
        if op not in ("-I","-h","-v","--ID","--help","--version"):
            if op in ("--short"):
                out_host_zones(route53, short=1)       
            elif op in ("--all"):
                out_host_zones(route53)

if __name__ == "__main__":
    #初始化函数
    #init()
    #建立连接对象
    route53 = boto.connect_route53()
    #取得函数
    get_args(route53)


#python ./rou53.py --all ok
#python ./rou53.py --short  ok
#python ./rou53.py -I Z2GJJUHWQ6G8I4 -d blog2.aa-v.com:54.92.67.181 ok
#python ./rou53.py -I Z2GJJUHWQ6G8I4 -d blog.aa-v.com:8.8.8.11,8.8.8.12,8.8.8.13 ok
#python ./rou53.py -I Z2GJJUHWQ6G8I4 -c blog2.aa-v.com:54.92.67.181:A:300 ok 
#python ./rou53.py -I Z2GJJUHWQ6G8I4 -c blog.aa-v.com:8.8.8.11,8.8.8.12,8.8.8.13:A:300 ok
#python ./rou53.py -I Z2GJJUHWQ6G8I4 -u blog2.aa-v.com:54.92.67.181:A:300 -U blog2.aa-v.com:54.92.67.181:A:300 ok


