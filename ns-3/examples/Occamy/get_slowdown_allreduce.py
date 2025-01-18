import os
import xml.etree.ElementTree as etree
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import csv

data = {}
data_array = {}
method_array = ["DT-1.0",  "ABM-2.0","PUSHOUT-1.0", "pBuffer-8.0"]
tcp_protocol_array = ["DCTCP"]
web_load_array = ["0.10", "0.20", "0.30", "0.40", "0.50", "0.60", "0.70","0.80"]
request_size_rate_array = ["0.3"]
request_flow_rate_array = ["200.0"]
buffer_size_array = ["4194304"]
queue_num_array = ["2"]
performance_parameter = ["query_QCT_ave_slowdown","web_FCT_99th_slowdown"]
alpha_array = ["1.0","2.0", "4.0", "8.0"]

def parse_one_xml(file_name):
    print()
    print(file_name)
    root = etree.parse(file_name).getroot()
    flow_stats = root[0]
    ipv4_flow_classifier = root[1]
    flow_dict = {}
    zhengxiangflow = 0
    for child in ipv4_flow_classifier:
        flow_id = child.attrib["flowId"]
        src_ip = child.attrib["sourceAddress"]
        dst_ip = child.attrib["destinationAddress"]
        protocol = child.attrib["protocol"]
        src_port = child.attrib["sourcePort"]
        dst_port = child.attrib["destinationPort"]
        flow_key = (src_ip, dst_ip, src_port, dst_port, protocol)

        index = int(flow_id) - 1
        flow_stats_attr = flow_stats[index].attrib
        start_time = float(flow_stats_attr["timeFirstTxPacket"].replace("+","").replace("ns",""))
        stop_time = float(flow_stats_attr["timeLastRxPacket"].replace("+","").replace("ns",""))
        loss_packets = int(flow_stats_attr["lostPackets"])
        receive_packets = int(flow_stats_attr["rxPackets"])
        receive_bytes = int(flow_stats_attr["rxBytes"])

        complete_time = stop_time - start_time

        flow_dict[flow_key] = {}
        flow_dict[flow_key]["startTime"] = start_time
        flow_dict[flow_key]["stopTime"] = stop_time
        flow_dict[flow_key]["completeTime"] = complete_time
        flow_dict[flow_key]["isPositive"] = "UDP"   #   the first set Flase, we can delete
        flow_dict[flow_key]["lostPackets"] = loss_packets
        flow_dict[flow_key]["rxPackets"] = receive_packets
        flow_dict[flow_key]["rxBytes"] = receive_bytes
        flow_dict[flow_key]["flowid"] = int(flow_id)

        #spine_leaf RTT
        base_rtt = 2.0 * 40 / 1000000

        if(src_ip.split(".")[2] != dst_ip.split(".")[2]):
            base_rtt = 2.0 * 40 / 1000000
        
        #flow slow down
        slowdown = complete_time/ 1000000000 / (base_rtt * 2.0 + receive_bytes * 8.0 / 100000000000)
        flow_dict[flow_key]["fctSlowdown"] = slowdown
        
        opposite_flow_key = (dst_ip, src_ip, dst_port, src_port, protocol)
        if opposite_flow_key in flow_dict.keys():
            
            if(flow_dict[flow_key]["flowid"] < flow_dict[opposite_flow_key]["flowid"]):
                flow_dict[flow_key]["isPositive"] = "TCP-TRUE"
                flow_dict[opposite_flow_key]["isPositive"] = "TCP-FALSE"
            else:
                flow_dict[flow_key]["isPositive"] = "TCP-FALSE"
                flow_dict[opposite_flow_key]["isPositive"] = "TCP-TRUE"
                    
            
            zhengxiangflow = zhengxiangflow+1

    print("flow no: ", len(flow_dict))
    print("zhengxiangflow: ", zhengxiangflow)
    # query msg
    loss_packets_sum = 0
    receive_packets_sum = 0
    burst_count = 0
    FCT = []
    FCT_slowdown = []
    QCT = {}
    QCT_slowdown = {}
    test=0
    for flow_key, flow_value in flow_dict.items():
        dst_port = int(flow_key[3])
        dst_ip = flow_key[1]
        if flow_value["isPositive"] == "TCP-TRUE" :
            if dst_port < 20010:
            # if dst_port >= 0:
                continue
            # print(flow_key,end="=")
            # print(flow_value["lostPackets"], end="=")
            # print(flow_value["completeTime"])
            burst_count = burst_count + 1
            loss_packets_sum = loss_packets_sum + flow_value["lostPackets"]
            receive_packets_sum = receive_packets_sum + flow_value["rxPackets"]
            FCT.append(flow_value["completeTime"])
            FCT_slowdown.append(flow_value["fctSlowdown"])
            qct_key = (dst_ip, flow_value["startTime"])
            if qct_key not in QCT.keys():
                QCT[qct_key] = flow_value["completeTime"]
                QCT_slowdown[qct_key] = flow_value["rxBytes"]
            else:
                QCT[qct_key] = max(QCT[qct_key], flow_value["completeTime"])
                QCT_slowdown[qct_key] = QCT_slowdown[qct_key] + flow_value["rxBytes"]
    


    ans = {}

    QCT_list = []
    QCT_slowdown_list = []
    for key, value in QCT.items():
        QCT_list.append(value)
        QCT_slowdown_list.append(value/ 1000000000 / (2.0 * 40 / 1000000 * 2.0 + QCT_slowdown[key] * 8.0 / 100000000000))
    # print(QCT_slowdown_list)
    QCT_list.sort()
    QCT_slowdown_list.sort()
    QCT_99th_index =  math.ceil(len(QCT_list)/100*99) - 1
    ans["query_QCT_ave"] = np.mean(QCT_list)
    ans["query_QCT_99th"] = QCT_list[QCT_99th_index]

    ans["query_QCT_ave_slowdown"] = np.mean(QCT_slowdown_list)
    ans["query_QCT_99th_slowdown"] = QCT_slowdown_list[QCT_99th_index]
    # ans["query_QCT_ave"] = 0
    # ans["query_QCT_99th"] = 0

    # ans["query_QCT_ave_slowdown"] = 0
    # ans["query_QCT_99th_slowdown"] = 0

    print("burst_count: ", burst_count)
    print(len(QCT))
    

    print("burst loss: " + str(loss_packets_sum))
    print("burst receive: " + str(receive_packets_sum))
    
    #============================================================
    try:
        ans["query_pkt_loss_rate"] = loss_packets_sum/receive_packets_sum
        print("receive_packets:" + str(receive_packets_sum))
    except:
        ans["query_pkt_loss_rate"] = 0
    #============================================================
    FCT.sort()
    FCT_slowdown.sort()
    FCT_99th_index =  math.ceil(len(FCT)/100*99) - 1

    # ans["query_FCT_ave"] = np.mean(FCT)
    # ans["query_FCT_99th"] = FCT[FCT_99th_index]

    # ans["query_FCT_ave_slowdown"] = np.mean(FCT_slowdown)
    # ans["query_FCT_99th_slowdown"] = FCT_slowdown[FCT_99th_index]
    ans["query_FCT_ave"] = 0
    ans["query_FCT_99th"] = 0

    ans["query_FCT_ave_slowdown"] = 0
    ans["query_FCT_99th_slowdown"] = 0
    print("burst flow: ", end=" ")
    print(len(FCT))

    # web msg====================================================================================
    loss_packets_sum = 0
    receive_packets_sum = 0
    FCT = []
    FCT_slowdown = []
    for flow_key, flow_value in flow_dict.items():
        dst_port = int(flow_key[3])
        dst_ip = flow_key[1]
        if flow_value["isPositive"] == "TCP-TRUE" :
            if dst_port < 20010:
            #if dst_port >= 0:
                loss_packets_sum = loss_packets_sum + flow_value["lostPackets"]
                receive_packets_sum = receive_packets_sum + flow_value["rxPackets"]
                FCT.append(flow_value["completeTime"])
                FCT_slowdown.append(flow_value["fctSlowdown"])
                
    print("web loss: " + str(loss_packets_sum))
    print("web receive: " + str(receive_packets_sum))
    try:
        ans["web_pkt_loss_rate"] = loss_packets_sum/receive_packets_sum
    except:
        ans["web_pkt_loss_rate"] = 0

    FCT.sort()
    FCT_slowdown.sort()
    FCT_99th_index =  math.ceil(len(FCT)/100*99) - 1
    ans["web_FCT_ave"] = np.mean(FCT)
    ans["web_FCT_99th"] = FCT[FCT_99th_index]

    ans["web_FCT_ave_slowdown"] = np.mean(FCT_slowdown)
    ans["web_FCT_99th_slowdown"] = FCT_slowdown[FCT_99th_index]

    #print("web count: ", len(FCT))


    #============================================================
    ans["small_web_pkt_loss_rate"] = 0
    ans["small_web_FCT_ave"] = 0
    ans["small_web_FCT_99th"] = 0
    ans["small_web_FCT_ave_slowdown"] = 0
    ans["small_web_FCT_99th_slowdown"] = 0


    #============================================================
    ans["medium_web_pkt_loss_rate"] = 0
    ans["medium_web_FCT_ave"] = 0
    ans["medium_web_FCT_99th"] = 0
    ans["medium_web_FCT_ave_slowdown"] = 0
    ans["medium_web_FCT_99th_slowdown"] = 0

    #============================================================
    ans["large_web_pkt_loss_rate"] = 0
    ans["large_web_FCT_ave"] = 0
    ans["large_web_FCT_99th"] = 0
    ans["large_web_FCT_ave_slowdown"] = 0
    ans["large_web_FCT_99th_slowdown"] = 0

    return ans

def deal_with_every_xml(file_dir):
    xml_list = []
    for root, dirs, files in os.walk(file_dir, topdown=False):
        xml_list = files
    for file_name in sorted(xml_list):
        print(file_name)
        ans = parse_one_xml(file_dir + "/" + file_name)
        #print(ans)
        print()
        print()

def write_to_txt(file_dir, output_file):
    xml_list = []
    for root, dirs, files in os.walk(file_dir, topdown=False):
        xml_list = files

    with open(output_file, "w") as f:

    
        for file_name in sorted(xml_list):
            ans = parse_one_xml(file_dir + "/" + file_name)
            parameter = file_name.replace(".xml","")
            output = parameter

            for key, value in ans.items():
                output = output + " " + str(value)
            
            # print(output)
            f.writelines(output)
            f.write("\n")
    f.close()

def unitize_data(output_file):
    with open(output_file, "r") as f:
        for line in f.readlines():
            line = line.strip('\n').split()
            key = line[0]
            value_dict = {}
            value_dict["query_QCT_ave"] = float(line[1])
            value_dict["query_QCT_99th"] = float(line[2])
            value_dict["query_QCT_ave_slowdown"] = float(line[3])
            value_dict["query_QCT_99th_slowdown"] = float(line[4])

            value_dict["query_pkt_loss_rate"] = float(line[5])
            value_dict["query_FCT_ave"] = float(line[6])
            value_dict["query_FCT_99th"] = float(line[7])
            value_dict["query_FCT_ave_slowdown"] = float(line[8])
            value_dict["query_FCT_99th_slowdown"] = float(line[9])
 
            value_dict["web_pkt_loss_rate"] = float(line[10])
            value_dict["web_FCT_ave"] = float(line[11])
            value_dict["web_FCT_99th"] = float(line[12])
            value_dict["web_FCT_ave_slowdown"] = float(line[13])
            value_dict["web_FCT_99th_slowdown"] = float(line[14])

            value_dict["small_web_pkt_loss_rate"] = float(line[15])
            value_dict["small_web_FCT_ave"] = float(line[16])
            value_dict["small_web_FCT_99th"] = float(line[17])
            value_dict["small_web_FCT_ave_slowdown"] = float(line[18])
            value_dict["small_web_FCT_99th_slowdown"] = float(line[19])

            value_dict["medium_web_pkt_loss_rate"] = float(line[20])
            value_dict["medium_web_FCT_ave"] = float(line[21])
            value_dict["medium_web_FCT_99th"] = float(line[22])
            value_dict["medium_web_FCT_ave_slowdown"] = float(line[23])
            value_dict["medium_web_FCT_99th_slowdown"] = float(line[24])

            value_dict["large_web_pkt_loss_rate"] = float(line[25])
            value_dict["large_web_FCT_ave"] = float(line[26])
            value_dict["large_web_FCT_99th"] = float(line[27])
            value_dict["large_web_FCT_ave_slowdown"] = float(line[28])
            value_dict["large_web_FCT_99th_slowdown"] = float(line[29])
            data[key] = value_dict
    
    f.close()
    
    #use DT as the base
    for key, value in data.items():
        method = key.split("~")[0]
        parameter = key.split("~")[1]
        if method == "DT-1.0":
            continue
        for value_key, value_value in value.items():
            if data["DT-1.0"+"~"+parameter][value_key] == 0:
                data[key][value_key] = 0
            else:
                data[key][value_key] = (data["DT-1.0"+"~"+parameter][value_key] -data[key][value_key]) / data["DT-1.0"+"~"+parameter][value_key]
    
    for key, value in data.items():
        method = key.split("~")[0]
        parameter = key.split("~")[1]
        if method == "DT-1.0":
            for value_key, value_value in value.items():
                data[key][value_key] = 0

    #store the data in data_array
    for key, value in data.items():
        method = key.split("~")[0]
        parameter = key.split("~")[1].split("-")
        tcp_protocol = parameter[0]
        web_load = parameter[1]
        request_size_rate = parameter[2]
        request_flow_rate = parameter[3]
        buffer_size = parameter[4]
        queue_num = parameter[5]

        data_array[(method, tcp_protocol, web_load, request_size_rate, request_flow_rate, buffer_size, queue_num)] = value


def donot_unitize_data(output_file):
    dt_qct_99th = {}
    abm_qct_99th = {}
    pushout_qct_99th = {}
    pbuffer_qct_99th = {}
    dt_qct_99th_com = {}
    abm_qct_99th_com = {}
    pushout_qct_99th_com = {}
    pbuffer_qct_99th_com = {}
    with open(output_file, "r") as f:
        for line in f.readlines():
            line = line.strip('\n').split()
            key = line[0]
            parts = key.split('-')
            load = parts[2] + "-" + parts[3]
            value_dict = {}
            value_dict["query_QCT_ave"] = float(line[1])
            value_dict["query_QCT_99th"] = float(line[2])
            value_dict["query_QCT_ave_slowdown"] = float(line[3])
            value_dict["query_QCT_99th_slowdown"] = float(line[4])

            value_dict["query_pkt_loss_rate"] = float(line[5])
            value_dict["query_FCT_ave"] = float(line[6])
            value_dict["query_FCT_99th"] = float(line[7])
            value_dict["query_FCT_ave_slowdown"] = float(line[8])
            value_dict["query_FCT_99th_slowdown"] = float(line[9])
 
            value_dict["web_pkt_loss_rate"] = float(line[10])
            value_dict["web_FCT_ave"] = float(line[11])
            value_dict["web_FCT_99th"] = float(line[12])
            value_dict["web_FCT_ave_slowdown"] = float(line[13])
            value_dict["web_FCT_99th_slowdown"] = float(line[14])

            value_dict["small_web_pkt_loss_rate"] = float(line[15])
            value_dict["small_web_FCT_ave"] = float(line[16])
            value_dict["small_web_FCT_99th"] = float(line[17])
            value_dict["small_web_FCT_ave_slowdown"] = float(line[18])
            value_dict["small_web_FCT_99th_slowdown"] = float(line[19])

            value_dict["medium_web_pkt_loss_rate"] = float(line[20])
            value_dict["medium_web_FCT_ave"] = float(line[21])
            value_dict["medium_web_FCT_99th"] = float(line[22])
            value_dict["medium_web_FCT_ave_slowdown"] = float(line[23])
            value_dict["medium_web_FCT_99th_slowdown"] = float(line[24])

            value_dict["large_web_pkt_loss_rate"] = float(line[25])
            value_dict["large_web_FCT_ave"] = float(line[26])
            value_dict["large_web_FCT_99th"] = float(line[27])
            value_dict["large_web_FCT_ave_slowdown"] = float(line[28])
            value_dict["large_web_FCT_99th_slowdown"] = float(line[29])
            data[key] = value_dict
    
    #store the data in data_array
    for key, value in data.items():
        method = key.split("~")[0]
        parameter = key.split("~")[1].split("-")
        tcp_protocol = parameter[0]
        web_load = parameter[1]
        request_size_rate = parameter[2]
        request_flow_rate = parameter[3]
        buffer_size = parameter[4]
        queue_num = parameter[5]

        data_array[(method, tcp_protocol, web_load, request_size_rate, request_flow_rate, buffer_size, queue_num)] = value


def get_allreduce_size(webLoad):
    size_map = {
        0.1: 16 * 1024,
        0.2: 32 * 1024,
        0.3: 64 * 1024,
        0.4: 128 * 1024,
        0.5: 256 * 1024,
        0.6: 512 * 1024,
        0.65: 786 * 1024,
        0.7: 1024 * 1024,
        0.72: 1280 * 1024,
        0.74: 1536 * 1024,
        0.76: 1792 * 1024,
        0.8: 2 * 1024 * 1024,
        0.9: 2304 * 1024,
        1.0: 2560 * 1024,
        1.1: 2816 * 1024,
        1.2: 3072 * 1024,
        1.3: 4 * 1024 * 1024,
    }
    
    return size_map.get(webLoad, None)

def get_allreduce_size_string(webLoad):
    size_map = {
        0.1: "16KB",
        0.2: "32KB",
        0.3: "64KB",
        0.4: "128KB",
        0.5: "256KB",
        0.6: "512KB",
        0.65: "786KB",
        0.7: "1MB",
        0.72: "1.25MB",
        0.74: "1.5MB",
        0.76: "1.75MB",
        0.8: "2MB",
        0.9: "2.25MB",
        1.0: "2.5MB",
        1.1: "2.75 * 1024",
        1.2: "3MB",
        1.3: "4MB",
    }
    
    return size_map.get(webLoad, None)

def format_size(size_in_bytes):
    units = ['B', 'kB', 'MB', 'GB', 'TB']
    size = float(size_in_bytes)
    for unit in units:
        if size < 1024.0:
            return f"{size:.2f}{unit}"
        size /= 1024.0
    return f"{size:.2f}PB"

def draw_allreduce_size(folder_name):
    for tcp_protocol in tcp_protocol_array:
        for request_size_rate in request_size_rate_array:
            for request_flow_rate in request_flow_rate_array:
                for buffer_size in buffer_size_array:
                    for queue_num in queue_num_array:

                        for performance in performance_parameter:
                            labels = []
                            for method in method_array:
                                x = []
                                y = []
                                for web_load in web_load_array:
                                    key = (method, tcp_protocol, web_load, request_size_rate, request_flow_rate, buffer_size, queue_num)
                                    x.append(get_allreduce_size_string(float(web_load)))
                                    y.append(float(data_array[key][performance]))
                                plt.plot(range(len(x)), y, marker='o', linestyle='-', linewidth=1.5, label=method)

                            plt.xticks(ticks=range(len(x)), labels=x, rotation=45, fontsize=10)
                            plt.xlabel("Allreduce Size", fontsize=12)
                            
                            if performance == "web_FCT_ave_slowdown":
                                ylabel = "Allreduce Avg FCT Slowdown"
                            elif performance == "web_FCT_99th_slowdown":
                                ylabel = "Allreduce 99th FCT Slowdown"
                            else:
                                ylabel = performance
                            plt.ylabel(ylabel, fontsize=12)

                            plt.legend(loc="best", fontsize=10)
                            figure_name = (f"{performance}-{tcp_protocol}-XX-"
                                           f"{request_size_rate}-{request_flow_rate}-{buffer_size}-{queue_num}")
                            plt.title(figure_name, fontsize=14)
                            
                            plt.grid(True, linestyle='--', linewidth=0.5)
                            
                            plt.tight_layout()
                            
                            print(folder_name + figure_name + ".jpg")
                            plt.savefig(folder_name + figure_name + ".jpg", dpi=300)
                            plt.cla() 



if __name__ == '__main__':

    file_dir = "100g_allreduce/"
    data_output_file = "data/100g_allreduce.txt"
    figure_output_folder = "figure/100g_allreduce/"

    os.makedirs(os.path.dirname(data_output_file), exist_ok=True)
    os.makedirs(figure_output_folder, exist_ok=True)

    write_to_txt(file_dir, data_output_file)

    donot_unitize_data(data_output_file)

    draw_allreduce_size(figure_output_folder)
