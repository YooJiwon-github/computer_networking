# -*- coding: utf-8 -*-
import socket
import threading
import time

# 초기 설정
congestion_window = 1  # 초기 혼잡 윈도우 크기
threshold = 6  # 초기 임계값
timeout_duration = 2  # 타임아웃 기간(초)
PKT_NUM = 100  # 패킷 번호 초기값
base = 0  # 혼잡 윈도우 base 부분
ack_count = 1  # 누적 ack 값
timer = None

# 혼잡 윈도우 및 임계값 조절 함수
def update_cwnd():
    global congestion_window, threshold
    if congestion_window < threshold:
        congestion_window *= 2
    else:
        congestion_window += 1


# 패킷 송신 함수
def send_packet(client_socket, addr, packet):
    data = packet.encode()
    length = len(data)
    client_socket.sendto(length.to_bytes(4, byteorder="little") + data, addr)
    print('------------> packet', packet, 'send')
    time.sleep(0.8)


# 패킷 송신 - 3개의 중복 ack 상황
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

# 패킷 송신 함수 - 타임아웃
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

# 패킷 송신 함수
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

# ACK 수신 함수
def receive_ack(client_socket):
    ack_data, _ = client_socket.recvfrom(1024)
    ack_length = int.from_bytes(ack_data[:4], "little")
    lastReceivedACK = ack_data[4:].decode()
    return lastReceivedACK

# 3개 중복 ACK 이벤트 처리 함수
def three_dup_ack_event(retrans_packet):
    global threshold, congestion_window, ack_count
    print('\n<<<3-Dup ACK Event Occurred!>>>\n')
    threshold = congestion_window / 2
    congestion_window /= 2

    print('- cwid: 1/2 decreased -> ', congestion_window)
    print('- threshold : ', threshold)
    print('-------------> ' + str(retrans_packet) + ' Retransmission\n')

    ack_count = 1

# Timeout 이벤트 처리 함수
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

# UDP 서버 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 9999)
server_socket.bind(server_address)

while True:
    data, client_address = server_socket.recvfrom(1024)
    sender(server_socket, client_address)
