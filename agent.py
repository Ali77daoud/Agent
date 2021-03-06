from tkinter import *
import time
from threading import Thread
import psutil
import platform
import requests

window = Tk()
window.configure(background='#006666')
window.geometry('300x300+500+50')
window.title('Agent')
window.iconphoto(False, PhotoImage(file='logoagent.png'))

t=True
def start():
    b1 = Button(text='Start', width=5, height=1, fg="#ccccb3", bg='#3333ff', activebackground="#3333ff", bd=5
               , cursor="hand2",relief=SUNKEN,state=DISABLED).place(x=80, y=180)
    d_ip = device_ip.get()
    s_ip = server_ip.get()
    s_port = port.get()
    t_interval = interval.get()
    device_url = 'https://' + s_ip + ':' + s_port + '/agent/'
    # OS
    system = str(platform.system())
    release = str(platform.release())
    os = system + ' ' + release

    device_pload = {'os': os, 'ip': d_ip}
    # add the device in the django server
    d_req = requests.post(device_url, data=device_pload, varify=False)
    time.sleep(5)
    # w
    disk_id = 0
    net_id  = 0
    while True :
        if_alert = False
        # send ram data
        ram_url = 'http://' + s_ip + ':' + s_port + '/ram/'
        ram = psutil.virtual_memory()
        # convert tuple to list
        r = list(ram)
        t_ram = r[0] / (1024 * 1024 * 1024)
        total_ram = round(t_ram, 1)
        a_space = r[1] / (1024 * 1024 * 1024)
        available_space = round(a_space, 1)
        percent_of_used = r[2]
        u_space = r[3] / (1024 * 1024 * 1024)
        used_space = round(u_space, 1)
        if percent_of_used >= 80:
            if_alert = True
        ram_pload = {'total': total_ram, 'av_space': available_space, 'percent_used': percent_of_used,
                     'us_space': used_space, 'ip': d_ip}
        ram_req = requests.post(ram_url, data=ram_pload)
        # send cpu data
        #########################################################
        cpu_url = 'http://' + s_ip + ':' + s_port + '/cpu/'
        # percent of cpu usage
        usage_of_cpu = psutil.cpu_percent(interval=2, percpu=False)
        cpu2 = psutil.cpu_times_percent(interval=2, percpu=False)
        c2 = list(cpu2)
        # percent of cpu usage in user mode
        user_mode = c2[0]
        # percent of cpu usage in kernel mode
        system_mode = c2[1]
        # idle of cpu
        idle = c2[2]
        # interrupt in cpu
        interrupt = c2[3]
        number_of_cores = psutil.cpu_count(logical=False)
        number_of_logical_processors = psutil.cpu_count(logical=True)
        # Processor frequency in GHZ
        cpu3 = psutil.cpu_freq(percpu=False)
        c3 = list(cpu3)
        c_freq = c3[0] / 1024
        current_freq = round(c_freq, 2)
        mi_freq = c3[1] / 1024
        min_freq = round(mi_freq, 2)
        ma_freq = c3[2] / 1024
        max_freq = round(ma_freq, 2)
        if usage_of_cpu >= 80:
            if_alert = True
        cpu_pload = {'usage': usage_of_cpu, 'user': user_mode, 'system': system_mode,
                     'idle': idle, 'interrupt': interrupt, 'cores': number_of_cores,
                     'logical': number_of_logical_processors, 'current': current_freq, 'min': min_freq,
                     'max': max_freq, 'ip': d_ip}
        cpu_req = requests.post(cpu_url, data=cpu_pload)
        # send Disk data
        ########################################################
        disk_url = 'http://' + s_ip + ':' + s_port + '/disk/'
        disk_info = psutil.disk_partitions()
        disk_id+=1
        for x in disk_info:
            try:
                disk = {
                    "name": x.device,
                    "mount_point": x.mountpoint,
                    "type": x.fstype,
                    "total_size": psutil.disk_usage(x.mountpoint).total,
                    "used_size": psutil.disk_usage(x.mountpoint).used,
                    "percent_used": psutil.disk_usage(x.mountpoint).percent
                }

                disk_name = disk["name"]
                disk_type = disk["type"]
                disk_size = disk["total_size"] / 1e+9
                usage = disk["used_size"] / 1e+9
                usage_percent = disk["percent_used"]
                if usage_percent >= 80:
                    if_alert = True
                disk_pload = {'name': disk_name, 'type': disk_type, 'size': disk_size,
                              'usage': usage, 'percent': usage_percent, 'di_id': disk_id, 'ip': d_ip}
                disk_req = requests.post(disk_url, data=disk_pload)
            except:
                print("")

        # send NICs data
        ############################################
        network_url = 'http://' + s_ip + ':' + s_port + '/network/'
        nics = []
        net_id += 1
        for name, snic_array in psutil.net_if_addrs().items():
            # Create NIC object
            nic = {
                "name": name,
                "mac": "",
                "address": "",
                "address6": "",
                "netmask": ""
            }
            # Get NiC values
            for snic in snic_array:
                if snic.family == -1:
                    nic["mac"] = snic.address
                elif snic.family == 2:
                    nic["address"] = snic.address
                    nic["netmask"] = snic.netmask
                elif snic.family == 23:
                    nic["address6"] = snic.address
            nics.append(nic)
            n = psutil.net_if_stats()
            x = list(n[nic["name"]])
            n_name = nic["name"]
            mac = nic["mac"]
            ip4 = nic["address"]
            subnet = nic["netmask"]
            ip6 = nic["address6"]
            is_up = x[0]
            network_pload = {'name': n_name, 'mac': mac, 'ip4': ip4,
                             'subnet': subnet, 'ip6': ip6, 'isup': is_up, 'ip': d_ip, 'ne_id': net_id}
            network_req = requests.post(network_url, data=network_pload)

        # send to alert table
        alert_url = 'http://' + s_ip + ':' + s_port + '/alert/'
        alert_pload = {'ip': d_ip, 'if_alert': if_alert}
        alert_req = requests.post(alert_url, data=alert_pload)

        time.sleep(int(t_interval))
        if(t==False):
            break

#start in new thread
def thr():
    global t
    t = True
    th = Thread(target=start)
    th.start()


def stop():
    global t
    t=False
    b1 = Button(text='Start', width=5, height=1, fg="#ffffff",bg='#006600', activebackground="#3333ff", bd=5
               , cursor="hand2", command=thr).place(x=80, y=180)


device_ip = Entry(bg='#e6e6ff')
device_ip.grid(row=0,column=1)

server_ip = Entry(bg='#e6e6ff')
server_ip.grid(row=1,column=1)

port = Entry(bg='#e6e6ff')
port.grid(row=2,column=1)

interval = Entry(bg='#e6e6ff')
interval.grid(row=3,column=1)

l1=Label(text='Device IP  ',fg="#ffffff",bg='#006666',font='Times').grid(row=0)
l2=Label(text='Server IP  ',fg="#ffffff",bg='#006666',font='Times').grid(row=1)
l3=Label(text='Server Port  ',fg="#ffffff",bg='#006666',font='Times').grid(row=2)
l4=Label(text='Time Interval  ',fg="#ffffff",bg='#006666',font='Times').grid(row=3)
b1 = Button(text='Start',width=5,height=1,fg="#ffffff",bg='#006600',activebackground="#3333ff",bd=5
           ,cursor="hand2",command=thr).place(x=80,y=180)
b2 = Button(text='Stop',width=5,height=1,fg="#ffffff",bg='dark red',activebackground="dark red",bd=5
           ,cursor="hand2",command=stop).place(x=160,y=180)
window.mainloop()