# -*- coding: utf-8 -*-
import socket
import threading
import time

# �ʱ� ����
congestion_window = 1  # �ʱ� ȥ�� ������ ũ��
threshold = 6  # �ʱ� �Ӱ谪
timeout_duration = 2  # Ÿ�Ӿƿ� �Ⱓ(��)
PKT_NUM = 100  # ��Ŷ ��ȣ �ʱⰪ
base = 0  # ȥ�� ������ base �κ�
ack_count = 1  # ���� ack ��
timer = None

# ȥ�� ������ �� �Ӱ谪 ���� �Լ�
def update_cwnd():
    global congestion_window, threshold
    if congestion_window < threshold:
        congestion_window *= 2
    else:
        congestion_window += 1


# ��Ŷ �۽� �Լ�
def send_packet(client_socket, addr, packet):
    data = packet.encode()
    length = len(data)
    client_socket.sendto(length.to_bytes(4, byteorder="little") + data, addr)
    print('------------> packet', packet, 'send')
    time.sleep(0.8)


# ��Ŷ �۽� - 3���� �ߺ� ack ��Ȳ
def send_packets_thee_dup_ACK(client_socket, addr, start, end):
    global ack_count, congestion_window, base, timer
    pkt_num = start

    i = start
    while i < end:
        packet = str(pkt_num)
        pkt_num += 1

        if i == 103:
            print('------------> packet', packet, 'LOST')
            i += 1
            continue

        send_packet(client_socket, addr, packet)
        lastSentPacket = packet

        lastReceivedACK = receive_ack(client_socket)

        if lastReceivedACK != lastSentPacket:
            print('<----', lastReceivedACK)
            ack_count += 1
            if ack_count == 3:
                pkt_num = int(lastReceivedACK) + 1
                three_dup_ack_event(str(pkt_num))
                start = pkt_num
                end = pkt_num + int(congestion_window)

                j = start
                while j < end:
                    packet = str(pkt_num)
                    send_packet(client_socket, addr, packet)
                    lastReceivedACK = receive_ack(client_socket)
                    print('<----', lastReceivedACK)
                    time.sleep(0.8)
                    pkt_num += 1
                    base = pkt_num
                    j += 1
                return
        else:
            print('<----', lastReceivedACK)
            time.sleep(0.8)
            base = 0
        i += 1

# ��Ŷ �۽� �Լ� - Ÿ�Ӿƿ�
def send_packets_timeout(client_socket, addr, start, end):
    global congestion_window, base, timer
    pkt_num = start

    i = start
    while i < end:

        packet = str(pkt_num)
        pkt_num += 1

        if i == 103:
            print('------------> packet', packet, 'LOST Timer Start')
            timer = threading.Timer(timeout_duration, timeout_event, args=(client_socket, addr, packet))
            timer.start()
            i += 1
            continue

        send_packet(client_socket, addr, packet)
        lastSentPacket = packet
        lastReceivedACK = receive_ack(client_socket)

        if lastReceivedACK == lastSentPacket:
            print('<----', lastReceivedACK)
            time.sleep(0.8)

        i += 1

    return

# ��Ŷ �۽� �Լ�
def send_packets(client_socket, addr, start, end):
    global congestion_window, base, timer
    pkt_num = start

    i = start
    while i < end:

        packet = str(pkt_num)
        pkt_num += 1

        send_packet(client_socket, addr, packet)
        lastSentPacket = packet

        lastReceivedACK = receive_ack(client_socket)

        if lastReceivedACK == lastSentPacket:
            print('<----', lastReceivedACK)
            time.sleep(0.8)

        i += 1

    return

# ACK ���� �Լ�
def receive_ack(client_socket):
    ack_data, _ = client_socket.recvfrom(1024)
    ack_length = int.from_bytes(ack_data[:4], "little")
    lastReceivedACK = ack_data[4:].decode()
    return lastReceivedACK

# 3�� �ߺ� ACK �̺�Ʈ ó�� �Լ�
def three_dup_ack_event(retrans_packet):
    global threshold, congestion_window, ack_count
    print('\n<<<3-Dup ACK Event Occurred!>>>\n')
    threshold = congestion_window / 2
    congestion_window /= 2

    print('- cwid: 1/2 decreased -> ', congestion_window)
    print('- threshold : ', threshold)
    print('-------------> ' + str(retrans_packet) + ' Retransmission\n')

    ack_count = 1

# Timeout �̺�Ʈ ó�� �Լ�
def timeout_event(client_socket, addr, retrans_packet):
    global threshold, congestion_window, base, timer

    print("\nTimeout occurred! Resending packets . . . ")
    timer.cancel()
    threshold = congestion_window / 2
    congestion_window = 1

    print('- cwid: set 1 -> ', congestion_window)
    print('- threshold : ', threshold)
    print('-------------> ' + str(retrans_packet) + ' Retransmission\n')

    start = int(retrans_packet)
    end = start + int(congestion_window)

    j = start
    while j < end:
        packet = str(start)
        send_packet(client_socket, addr, packet)
        lastReceivedACK = receive_ack(client_socket)
        print('<----', lastReceivedACK)
        time.sleep(0.8)
        start += 1
        base = start
        j += 1

    return

def sender(client_socket, addr):
    global congestion_window, ack_count, threshold, PKT_NUM, base

    print('Connected by', addr)

    pkt_num = PKT_NUM

    try:
        i = 0
        while i < 20:
            if base != 0:
                start_packet_number = base
                end_packet_number = start_packet_number + int(congestion_window)
            else:
                start_packet_number = pkt_num
                end_packet_number = start_packet_number + int(congestion_window)

            send_packets(client_socket, addr, start_packet_number, end_packet_number)
            # send_packets_thee_dup_ACK(client_socket, addr, start_packet_number, end_packet_number)
            # send_packets_timeout(client_socket, addr, start_packet_number, end_packet_number)
            pkt_num += int(congestion_window)
            update_cwnd()
            print(' => cwin increase(', str(congestion_window), ')')
            i = i + congestion_window
            base = pkt_num

    except Exception as e:
        print("Exception:", e)

# UDP ���� ���� ����
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 9999)
server_socket.bind(server_address)

while True:
    data, client_address = server_socket.recvfrom(1024)
    sender(server_socket, client_address)
