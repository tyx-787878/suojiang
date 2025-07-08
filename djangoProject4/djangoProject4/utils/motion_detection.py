# utils/motion_detection.py
import cv2
import time


class MotionDetection:
    def __init__(self):
        self.static_back = None
        self.motion_list = [None, None]
        self.time = []
        self.video = None
        self.is_detecting = False

    def start_detection(self, video_source=0):
        # 开始运动检测
        self.video = cv2.VideoCapture(video_source)
        self.is_detecting = True

        while self.is_detecting:
            # 读取视频帧
            check, frame = self.video.read()
            if not check:
                break

            # 初始化静态背景
            if self.static_back is None:
                self.static_back = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                self.static_back = cv2.GaussianBlur(self.static_back, (21, 21), 0)
                continue

            # 将当前帧转换为灰度图并进行高斯模糊
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            # 计算当前帧与静态背景之间的差异
            diff_frame = cv2.absdiff(self.static_back, gray)

            # 如果像素值大于25，则将其设为255（白色），否则设为0（黑色）
            thresh_frame = cv2.threshold(diff_frame, 25, 255, cv2.THRESH_BINARY)[1]
            thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

            # 找到运动物体的轮廓
            contours, _ = cv2.findContours(thresh_frame.copy(),
                                           cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE)

            motion_detected = False

            for contour in contours:
                if cv2.contourArea(contour) < 10000:  # 调整阈值以过滤小的运动
                    continue
                motion_detected = True
                (x, y, w, h) = cv2.boundingRect(contour)
                # 在当前帧上绘制矩形
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

            # 更新运动状态
            self.motion_list.append(motion_detected)
            self.motion_list = self.motion_list[-2:]

            # 如果检测到有人然后又没有人了，触发关门操作
            if self.motion_list[-1] == False and self.motion_list[-2] == True:
                self.time.append(time.strftime("%Y-%m-%d %H:%M:%S"))
                print("检测到无人，触发关门操作")
                self.trigger_door_close()

            # 显示结果帧
            cv2.imshow("Motion Detection", frame)

            # 按ESC键退出
            key = cv2.waitKey(1)
            if key == 27:
                break

        self.video.release()
        cv2.destroyAllWindows()

    def stop_detection(self):
        # 停止运动检测
        self.is_detecting = False

    def trigger_door_close(self):
        # 触发关门操作
        # 这里应该调用硬件接口，控制门锁关闭
        print("正在关闭门...")
        # 模拟关门操作
        time.sleep(2)
        print("门已关闭")