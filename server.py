# -*- coding: utf-8 -*-
import socket, threading
import time # 타임아웃을 위해 time 모듈 추가
import random

#초기 설정
MSS = 1024 # Maximum Segment Size
congestion_window = 1 # 초기 혼잡 윈도우 크기
threshold = 6 # 초기 임계값
timeout_duration = 0.1 # Timeout이 발생할 시간(초)
PKT_NUM = 100 # 패킷 번호 초기화
transmission_rate = 0.1 # 전송률
expected_ACK = None 
previous_ACK = None
ack_count = 1


#혼잡 윈도우 및 임계값 조절 함수
def update_cwnd():
    global congestion_window, threshold
    if congestion_window < threshold:
        congestion_window *= 2 # 임계값 도달 전에는 두배씩 지수적으로 증가시킴
    else:
        congestion_window += 1 # 임계값 도달 시 + 1씩 선형적으로 증가시킴

# 패킷 송신 함수
def send_packet(client_socket, packet) :
    data = packet.encode()
    length = len(data)
    client_socket.sendall(length.to_bytes(4, byteorder="little"))
    client_socket.sendall(data)
    print('------------> packet', packet, 'send')


# ACK 수신 함수
def receive_ack(client_socket) :
    ack_data = client_socket.recv(4)
    ack_length = int.from_bytes(ack_data, "little")
    ack_data = client_socket.recv(ack_length)
    return ack_data.decode()

# 3개 중복 ACK 이벤트 처리 함수
def three_dup_ack_event(client_socket):
    global threshold, congestion_window, ack_count

    print('<<<3-Dup ACK Event Occurred!>>>\n') 
    # 이벤트가 발생한 타이밍에서의 혼잡 윈도의 크기의 절반으로 설정
    threshold = congestion_window / 2 
    # 혼잡 윈도의 값을 절반으로 감소시킴
    congestion_window /= 2

    print('- cwid: 1/2 decreased -> ', congestion_window)
    print('- threshold : ', threshold)

    send_packet(client_socket, previous_ACK.decode())
    print('-------------> ' + previous_ACK.decode() + ' Retransmission')

    ack_count = 1

# Timeout 이벤트 처리 함수
def timeout_event(client_socket, data, length):
    global threshold, congestion_window

    print("Timeout occurred! Resending packets . . . ")
    threshold = congestion_window / 2
    congestion_window = 1

    # Timeout이 발생하면 패킷 재전송함
    for j in range(int(congestion_window)):
        client_socket.sendall(length.to_bytes(4, byteorder="little"))
        client_socket.sendall(data)
        j += 1


    
def sender(client_socket, addr):
    global congestion_window, ack_count, timeout_duration, transmission_rate, threshold, expected_ACK, previous_ACK

    print('Connected by', addr)

    try:
        for i in range(20):
            # 패킷 생성
            packet = str(100 + i)

            # 패킷 송신
            send_packet(client_socket, packet)
            expected_ACK = packet

            # 수신 ack 처리
            ack_msg = receive_ack(client_socket)

            if ack_msg != expected_ACK:
                #중복 ack 처리
                ack_count += 1
                if ack_count == 3:

                    three_dup_ack_event(client_socket)

                    """
                    print('<<<3-Dup ACK Event Occurred!>>>\n') 
                    # 이벤트가 발생한 타이밍에서의 혼잡 윈도의 크기의 절반으로 설정
                    threshold = congestion_window / 2 
                    # 혼잡 윈도의 값을 절반으로 감소시킴
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

            #Timeout 이벤트 발생 여부 확인
            if random.random() < transmission_rate:
                # 10% 확률로 Timeout 이벤트 발생
                timeout_event(client_socket, packet.encode(), len(packet.encode()))


            # 패킷 전송 간격 조절
            # time.sleep(transmission_rate)


    except Exception as e:
        print("Exception:", e)
    finally:
        client_socket.close()

# 송신자 소켓 설정
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sender_socket.connect(('127.0.0.1', 9999))

# 수신자 측에 연결된 스레드 시작
sender_thread = threading.Thread(target=sender, args=(sender_socket, ('127.0.0.1', 9999)))
sender_thread.start()
