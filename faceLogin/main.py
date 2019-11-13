from flask import Flask, jsonify, render_template, request
import dlib, numpy
import base64
# from skimage import io
import cv2
import simplejson
import imageio

############################

# 人脸识别模型
predictor_path = 'shape_predictor_68_face_landmarks.dat'
face_rec_model_path = 'dlib_face_recognition_resnet_model_v1.dat'
# 需识别的人脸
img_path = "1.jpg"
# 1.加载正脸检测器
detector = dlib.get_frontal_face_detector()
# 2.加载人脸关键点检测器
sp = dlib.shape_predictor(predictor_path)
# 3. 加载人脸识别模型
facerec = dlib.face_recognition_model_v1(face_rec_model_path)
m_data = ''



# 人脸对比主要函数
def face_compare(face_threshold=0.35):
    # 候选人脸描述子list
    descriptors = []
    candidate = []
    descriptor = numpy.load("desc_file.npy")
    candidate = numpy.load("candidate_file.npy")
    if len(descriptor)==0 and len(candidate)== 0:
         return 1

    for i in descriptor:
        array = numpy.array(i)
        descriptors.append(array)
    dist = []
    # img = imageio.imread(img_path)
    img = cv2.imread(img_path)
    dets = detector(img, 1)
    if len(dets) >= 2:
        # 假如检测到多张脸，直接返回检测失败：0
        return 0

    for k, d in enumerate(dets):
        shape = sp(img, d)
        face_descriptor = facerec.compute_face_descriptor(img, shape)
        d_test = numpy.array(face_descriptor)
        # 计算欧式距离
        for i in descriptors:
            dist_ = numpy.linalg.norm(i - d_test)
            dist.append(dist_)
    # 候选人和距离组成一个dict
    c_d = dict(zip(candidate, dist))
    cd_sorted = sorted(c_d.items(), key=lambda d: d[1])
    if (len(cd_sorted)):
        if (cd_sorted[0][1] < face_threshold):
            return cd_sorted[0]
        else:
            return 1  # 暂无此人信息
    else:
        return 0


############################


# 定义接口
app = Flask(__name__)



@app.route('/api/face_recog', methods=['post'])
def face_recog():
    """
    人脸验证
    成功后 :数组 [姓名,欧几里得距离值] 0 :没有识别到人脸,1 :暂无此人信息
    """
    base64_1 = request.json
    imgdata = base64.b64decode(base64_1.get('data'))
    file = open(img_path, 'wb')
    file.write(imgdata)
    file.close()
    zhi = face_compare()
    return jsonify(results=[zhi])


@app.route('/api/add_face', methods=['post'])
def add_face():
    """
     0 :'请输入名字' 1:'添加成功' 2:'人脸信息与已经存在的人脸相似'
     3 :'人脸信息已存在'4 : '未识别到人脸，请重新拍照'
    """

    jsonData = simplejson.loads(request.json.get('data'))


    base64_11 = jsonData["base64_11"]
    username = jsonData["user_name"]
    imgdata1 = base64.b64decode(base64_11)
    # print(imgdata1)
    file = open(img_path, 'wb')
    if username != "":
        file.write(imgdata1)
        file.close()
        descriptor = numpy.load("desc_file.npy")
        candidate = list(numpy.load("candidate_file.npy"))
        for j in candidate:
            if j == username:
                return jsonify(results=[3])
            else:
                continue
        file_ = face_compare(face_threshold=0.35)
        if file_ == 0:
            return jsonify(results=[4])
        elif file_ == 1:
            descriptors = []
            for i in descriptor:
                array = numpy.array(i)
                descriptors.append(array)
            candidate.append(str(username))
            # img = imageio.imread(img_path)##fixme
            img = cv2.imread(img_path)
            dets = detector(img, 1)
            for k, d in enumerate(dets):
                shape = sp(img, d)
                face_descriptor = facerec.compute_face_descriptor(img, shape)
                d_test = numpy.array(face_descriptor)
                descriptors.append(d_test)
            numpy.save('desc_file.npy', descriptors)
            numpy.save('candidate_file.npy', candidate)
            print("添加成功")
            return jsonify(results=[1])
        else:
            return jsonify(results=[2])
    else:
        return jsonify(results=[0])


@app.route('/api/show_face', methods=['post'])
def show_face():
    """
    显示人脸
    返回已经存在的名字列表
    """
    candidate = list(numpy.load("candidate_file.npy"))
    return jsonify(results=candidate)


@app.route('/api/del_face', methods=['get'])
def del_face():
    """
    接收照片和用户名的id进行删除
    1：删除成功 0 :删除失败
    """
    del_id = int(request.args.get("id"))
    descriptor = numpy.load("desc_file.npy")
    candidate = list(numpy.load("candidate_file.npy"))
    print(len(candidate))
    username = candidate[del_id]
    new_c = []
    new_d = []
    print(descriptor.shape)
    if len(descriptor) == len(candidate):
        for i, j in enumerate(descriptor):
            # print(i)
            # print(j)
            if candidate[i] != username:
                new_c.append(candidate[i])
                new_d.append(j)
        new_d = numpy.array(new_d)
        numpy.save('desc_file.npy', new_d)
        numpy.save('candidate_file.npy', new_c)
        return jsonify(results=[1])
    else:
        return jsonify(results=[0])



@app.route('/add_face')
def add_face2html():
    return render_template('add_face.html')


@app.route('/show_face')
def show_face2html():
    return render_template('show_face.html')


# 绑定前台页面
@app.route('/')
def main():
    return render_template('index.html')


if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=5002, debug='True')
