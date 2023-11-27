# -*- coding: utf-8 -*-
import socket, threading
import time # Ÿ�Ӿƿ��� ���� time ��� �߰�
import random

#�ʱ� ����
MSS = 1024 # Maximum Segment Size
congestion_window = 1 # �ʱ� ȥ�� ������ ũ��
threshold = 6 # �ʱ� �Ӱ谪
SS_THRESH = threshold # �ߺ� ACK �̺�Ʈ �߻� �� ������ �Ӱ谪 �ʱ�ȭ
timeout_duration = 0.1 # Timeout�� �߻��� �ð�(��)
PKT_NUM = 100 # ��Ŷ ��ȣ �ʱ�ȭ
transmission_rate = 1 # ���۷�


#ȥ�� ������ �� �Ӱ谪 ���� �Լ�
def update_cwnd():
    global congestion_window, threshold
    if congestion_window < threshold:
        congestion_window *= 2 # �Ӱ谪 ���� ������ �ι辿 ���������� ������Ŵ
    else:
        congestion_window += 1 # �Ӱ谪 ���� �� + 1�� ���������� ������Ŵ

# ��Ŷ ���� �Լ�
def make_packet():
    global PKT_NUM
    packet = PKT_NUM + 1
    return str(packet)
    
def sender(client_socket, addr):
    global PKT_NUM, congestion_window

    print('Connected by', addr)

    try:
        for i in range(20):
            # ��Ŷ ����
            packet = str(100 + i)
            send_msg = 'packet ' + packet + ' send'

            if random.random() < 0.3: # 20%�� Ȯ���� ��Ŷ �ս�
                print('Packet lost!')
                continue # ��Ŷ �ս� �� ���� ��Ŷ���� �̵�

            # Timeout�� ����Ű�� ���� ACK ��� �ð��� ª�� ������
            client_socket.settimeout(timeout_duration)

            # ��Ŷ �۽�
            data = packet.encode()
            length = len(data)
            client_socket.sendall(length.to_bytes(4, byteorder="little"))
            client_socket.sendall(data)
            print('----------> ' + send_msg)

            # ��Ŷ ���� ���� ����
            time.sleep(transmission_rate)
        

            try:
                # ���� ACK ó��
                ack_data = client_socket.recv(4)
                ack_length = int.from_bytes(ack_data, "little")
                ack_data = client_socket.recv(ack_length)
                ack_msg = ack_data.decode()

                # �ߺ� ACK �̺�Ʈ �߻� ��
                if "duplicate ACK" in ack_msg:
                    print("Duplicate ACK event occurred!")
                    SS_THRESH = congestion_window / 2  # �̺�Ʈ�� �߻��� Ÿ�ֿ̹����� ȥ�� ������ ũ���� �������� ����
                    threshold = SS_THRESH
                    congestion_window /= 2  # ȥ�� ������ ���� �������� ���ҽ�Ŵ

                    # �ߺ��� 3���� ACK�� �����ϰ� �ش� ��Ŷ�� ������
                    for _ in range(3):
                        client_socket.sendall(length.to_bytes(4, byteorder="little"))
                        client_socket.sendall(data)
                        print('------------> ' + send_msg + ' (Retransmission)')

                else:
                    print('<---- ', ack_msg)
                    # ȥ�� ������ �� �Ӱ谪 ����
                    update_cwnd()
                    # ȥ�� ������ �� ���
                    print('=> cwin 1 increase(' + str(congestion_window) + ')')

            except socket.timeout:
                print("Timeout occurred! Resending packets . . . ")
                SS_THRESH = congestion_window / 2
                threshold = SS_THRESH
                congestion_window = 1

                # Timeout�� �߻��ϸ� ��Ŷ ��������
                for j in range(int(congestion_window)):
                    client_socket.sendall(length.to_bytes(4, byteorder="little"))
                    client_socket.sendall(data)
                    j+=1

            # Timeout ���� �ʱ�ȭ
            client_socket.settimeout(None)

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
