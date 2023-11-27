# -*- coding: utf-8 -*-
import socket, threading
import time # 타임아웃을 위해 time 모듈 추가
import random

#초기 설정
MSS = 1024 # Maximum Segment Size
congestion_window = 1 # 초기 혼잡 윈도우 크기
threshold = 6 # 초기 임계값
SS_THRESH = threshold # 중복 ACK 이벤트 발생 시 감소할 임계값 초기화
timeout_duration = 0.1 # Timeout이 발생할 시간(초)
PKT_NUM = 100 # 패킷 번호 초기화
transmission_rate = 1 # 전송률


#혼잡 윈도우 및 임계값 조절 함수
def update_cwnd():
    global congestion_window, threshold
    if congestion_window < threshold:
        congestion_window *= 2 # 임계값 도달 전에는 두배씩 지수적으로 증가시킴
    else:
        congestion_window += 1 # 임계값 도달 시 + 1씩 선형적으로 증가시킴

# 패킷 생성 함수
def make_packet():
    global PKT_NUM
    packet = PKT_NUM + 1
    return str(packet)
    
def sender(client_socket, addr):
    global PKT_NUM, congestion_window

    print('Connected by', addr)

    try:
        for i in range(20):
            # 패킷 생성
            packet = str(100 + i)
            send_msg = 'packet ' + packet + ' send'

            if random.random() < 0.3: # 20%의 확률로 패킷 손실
                print('Packet lost!')
                continue # 패킷 손실 시 다음 패킷으로 이동

            # Timeout을 일으키기 위해 ACK 대기 시간을 짧게 설정함
            client_socket.settimeout(timeout_duration)

            # 패킷 송신
            data = packet.encode()
            length = len(data)
            client_socket.sendall(length.to_bytes(4, byteorder="little"))
            client_socket.sendall(data)
            print('----------> ' + send_msg)

            # 패킷 전송 간격 조절
            time.sleep(transmission_rate)
        

            try:
                # 수신 ACK 처리
                ack_data = client_socket.recv(4)
                ack_length = int.from_bytes(ack_data, "little")
                ack_data = client_socket.recv(ack_length)
                ack_msg = ack_data.decode()

                # 중복 ACK 이벤트 발생 시
                if "duplicate ACK" in ack_msg:
                    print("Duplicate ACK event occurred!")
                    SS_THRESH = congestion_window / 2  # 이벤트가 발생한 타이밍에서의 혼잡 윈도의 크기의 절반으로 설정
                    threshold = SS_THRESH
                    congestion_window /= 2  # 혼잡 윈도의 값을 절반으로 감소시킴

                    # 중복된 3번의 ACK를 감지하고 해당 패킷을 재전송
                    for _ in range(3):
                        client_socket.sendall(length.to_bytes(4, byteorder="little"))
                        client_socket.sendall(data)
                        print('------------> ' + send_msg + ' (Retransmission)')

                else:
                    print('<---- ', ack_msg)
                    # 혼잡 윈도우 및 임계값 조절
                    update_cwnd()
                    # 혼잡 윈도우 값 출력
                    print('=> cwin 1 increase(' + str(congestion_window) + ')')

            except socket.timeout:
                print("Timeout occurred! Resending packets . . . ")
                SS_THRESH = congestion_window / 2
                threshold = SS_THRESH
                congestion_window = 1

                # Timeout이 발생하면 패킷 재전송함
                for j in range(int(congestion_window)):
                    client_socket.sendall(length.to_bytes(4, byteorder="little"))
                    client_socket.sendall(data)
                    j+=1

            # Timeout 설정 초기화
            client_socket.settimeout(None)

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
