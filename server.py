# -*- coding: utf-8 -*-
import socket, threading
import time # Ÿ�Ӿƿ��� ���� time ��� �߰�
import random

#�ʱ� ����
MSS = 1024 # Maximum Segment Size
congestion_window = 1 # �ʱ� ȥ�� ������ ũ��
threshold = 6 # �ʱ� �Ӱ谪
timeout_duration = 0.1 # Timeout�� �߻��� �ð�(��)
PKT_NUM = 100 # ��Ŷ ��ȣ �ʱ�ȭ
transmission_rate = 0.1 # ���۷�
expected_ACK = None 
previous_ACK = None
ack_count = 1


#ȥ�� ������ �� �Ӱ谪 ���� �Լ�
def update_cwnd():
    global congestion_window, threshold
    if congestion_window < threshold:
        congestion_window *= 2 # �Ӱ谪 ���� ������ �ι辿 ���������� ������Ŵ
    else:
        congestion_window += 1 # �Ӱ谪 ���� �� + 1�� ���������� ������Ŵ

# ��Ŷ �۽� �Լ�
def send_packet(client_socket, packet) :
    data = packet.encode()
    length = len(data)
    client_socket.sendall(length.to_bytes(4, byteorder="little"))
    client_socket.sendall(data)
    print('------------> packet', packet, 'send')


# ACK ���� �Լ�
def receive_ack(client_socket) :
    ack_data = client_socket.recv(4)
    ack_length = int.from_bytes(ack_data, "little")
    ack_data = client_socket.recv(ack_length)
    return ack_data.decode()

# 3�� �ߺ� ACK �̺�Ʈ ó�� �Լ�
def three_dup_ack_event(client_socket):
    global threshold, congestion_window, ack_count

    print('<<<3-Dup ACK Event Occurred!>>>\n') 
    # �̺�Ʈ�� �߻��� Ÿ�ֿ̹����� ȥ�� ������ ũ���� �������� ����
    threshold = congestion_window / 2 
    # ȥ�� ������ ���� �������� ���ҽ�Ŵ
    congestion_window /= 2

    print('- cwid: 1/2 decreased -> ', congestion_window)
    print('- threshold : ', threshold)

    send_packet(client_socket, previous_ACK.decode())
    print('-------------> ' + previous_ACK.decode() + ' Retransmission')

    ack_count = 1

# Timeout �̺�Ʈ ó�� �Լ�
def timeout_event(client_socket, data, length):
    global threshold, congestion_window

    print("Timeout occurred! Resending packets . . . ")
    threshold = congestion_window / 2
    congestion_window = 1

    # Timeout�� �߻��ϸ� ��Ŷ ��������
    for j in range(int(congestion_window)):
        client_socket.sendall(length.to_bytes(4, byteorder="little"))
        client_socket.sendall(data)
        j += 1


    
def sender(client_socket, addr):
    global congestion_window, ack_count, timeout_duration, transmission_rate, threshold, expected_ACK, previous_ACK

    print('Connected by', addr)

    try:
        for i in range(20):
            # ��Ŷ ����
            packet = str(100 + i)

            # ��Ŷ �۽�
            send_packet(client_socket, packet)
            expected_ACK = packet

            # ���� ack ó��
            ack_msg = receive_ack(client_socket)

            if ack_msg != expected_ACK:
                #�ߺ� ack ó��
                ack_count += 1
                if ack_count == 3:

                    three_dup_ack_event(client_socket)

                    """
                    print('<<<3-Dup ACK Event Occurred!>>>\n') 
                    # �̺�Ʈ�� �߻��� Ÿ�ֿ̹����� ȥ�� ������ ũ���� �������� ����
                    threshold = congestion_window / 2 
                    # ȥ�� ������ ���� �������� ���ҽ�Ŵ
                    congestion_window /= 2

                    print('- cwid: 1/2 decreased -> ', congestion_window)
                    print('- threshold : ', threshold)

                    send_packet(client_socket, previous_ACK.decode())
                    print('-------------> ' + previous_ACK.decode() + ' Retransmission')

                    ack_count = 1
                    """
                    
            else :
                print('<----', ack_msg)
                update_cwnd()
                print(' => cwin 1 increase(' + str(congestion_window) + ')')

            #Timeout �̺�Ʈ �߻� ���� Ȯ��
            if random.random() < transmission_rate:
                # 10% Ȯ���� Timeout �̺�Ʈ �߻�
                timeout_event(client_socket, packet.encode(), len(packet.encode()))


            # ��Ŷ ���� ���� ����
            # time.sleep(transmission_rate)


    except Exception as e:
        print("Exception:", e)
    finally:
        client_socket.close()

# �۽��� ���� ����
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sender_socket.connect(('127.0.0.1', 9999))

# ������ ���� ����� ������ ����
sender_thread = threading.Thread(target=sender, args=(sender_socket, ('127.0.0.1', 9999)))
sender_thread.start()
