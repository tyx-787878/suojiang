document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureBtn = document.getElementById('capture');
    const recordBtn = document.getElementById('record');
    const unlockBtn = document.getElementById('unlock');
    const status = document.getElementById('status');
    const resultDiv = document.getElementById('result');
    
    let faceImage = null;
    let voiceBlob = null;
    
    // 访问摄像头
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(stream) {
                video.srcObject = stream;
            })
            .catch(function(error) {
                console.error("Camera access error:", error);
            });
    }
    
    // 捕获人脸图像
    captureBtn.addEventListener('click', function() {
        canvas.getContext('2d').drawImage(video, 0, 0, 400, 300);
        faceImage = canvas.toDataURL('image/jpeg');
        status.textContent = "Face captured! Now record your voice.";
    });
    
    // 录音逻辑
    let mediaRecorder;
    let audioChunks = [];
    
    recordBtn.addEventListener('mousedown', startRecording);
    recordBtn.addEventListener('mouseup', stopRecording);
    recordBtn.addEventListener('touchstart', startRecording);
    recordBtn.addEventListener('touchend', stopRecording);
    
    function startRecording(e) {
        e.preventDefault();
        status.textContent = "Recording... Speak your unlock phrase now.";
        audioChunks = [];
        
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
                
                mediaRecorder.ondataavailable = function(e) {
                    audioChunks.push(e.data);
                };
            })
            .catch(err => {
                console.error("Microphone access error:", err);
                status.textContent = "Error accessing microphone";
            });
    }
    
    function stopRecording(e) {
        e.preventDefault();
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            mediaRecorder.onstop = function() {
                voiceBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(voiceBlob);
                document.getElementById('audio').src = audioUrl;
                status.textContent = "Recording complete! Ready to unlock.";
                if (faceImage) {
                    unlockBtn.disabled = false;
                }
            };
        }
    }
    
    // 解锁按钮点击事件
    unlockBtn.addEventListener('click', function() {
        if (!faceImage || !voiceBlob) return;
        
        unlockBtn.disabled = true;
        status.textContent = "Processing...";
        
        // 创建FormData对象
        const formData = new FormData();
        formData.append('face_image', dataURItoBlob(faceImage), 'face.jpg');
        formData.append('voice_sample', voiceBlob, 'voice.wav');
        
        // 发送到服务器
        fetch('/unlock/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                resultDiv.innerHTML = `
                    <div class="result-box success">
                        <h4>Access Granted!</h4>
                        <p>Welcome, ${data.username}</p>
                        <p>Face match score: ${(data.face_score * 100).toFixed(1)}%</p>
                    </div>
                `;
            } else {
                resultDiv.innerHTML = `
                    <div class="result-box error">
                        <h4>Access Denied</h4>
                        <p>Verification failed</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultDiv.innerHTML = `
                <div class="result-box error">
                    <h4>Error</h4>
                    <p>An error occurred during verification</p>
                </div>
            `;
        })
        .finally(() => {
            unlockBtn.disabled = false;
        });
    });
    
    // 辅助函数
    function dataURItoBlob(dataURI) {
        const byteString = atob(dataURI.split(',')[1]);
        const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);
        for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }
        return new Blob([ab], { type: mimeString });
    }
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});