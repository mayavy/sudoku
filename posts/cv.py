# from PIL import Image


from django.core.files.storage import default_storage
import cv2
import numpy as np
import pytesseract
#   #
# r'E:\ocr\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = r'E:\ocr\Tesseract-OCR\tesseract.exe'#r'/usr/bin/tesseract'

# image cleaning
# original = cv2.imread('C:/Users/sksha/Desktop/test2.png', 0)


# local functions
def center_in_array(centerx, centery, cnt_array):
    if centerx >= 0 and centery >= 0:
        contour = np.array(cnt_array)
        x, y, w, h = cv2.boundingRect(contour)
        return x <= centerx <= w+x and y <= centery <= h+y
    else:
        print('Unable to check')
        return False


def maxarea_contour(contours):
    maxArea = 0
    best = np.array([[[10,  6]], [[10, 6]]])  # dummy
    for contour in contours:
        area = cv2.contourArea(np.array(contour))
        if area > maxArea:
            maxArea = area
            best = contour
    return best


def cleanbottom(lst, fullx):
    """returns coords list after removing high 'y' valued coord"""
    half = fullx//2
    clean = []
    for coord in lst:
        px, py = coord
        if py < half:
            clean += [coord]
    return clean


def cleantop(lst, fullx):
    """returns coords list after removing low 'y' valued coord"""
    half = fullx//2
    clean = []
    for coord in lst:
        px, py = coord
        if py > half:
            clean += [coord]
    return clean


def check(xx, yy, ww, hh, warped):
    """check if digit is present in the cell -> digit cell image or black cell image"""
    crop = warped.copy()
    ROIp = crop[yy:yy+hh, xx:xx+ww]
    p0 = [0, 0]
    p1 = [ww, 0]
    p2 = [ww, hh]
    p3 = [0, hh]
    r = round(0.15*ww)
    corners = [p0, p1, p2, p3]
    ROIp[:r, ww//2: ww//2+2] = 0
    ROIp[ww//2: ww//2+2, :r] = 0
    ROIp[ww//2: ww//2+2, -r:] = 0

    for corner in corners:
        ROIp = cv2.circle(ROIp, corner, r, [0, 0, 0], r*2)

    contours, _ = cv2.findContours(image=ROIp, mode=cv2.RETR_LIST,
                                   method=cv2.CHAIN_APPROX_NONE)
    cnt = maxarea_contour(contours)
    x, y, w, h = cv2.boundingRect(cnt)
    ROIp[0:y, :-1] = 0  # out side cnt black
    ROIp[y+h:, :-1] = 0
    ROIp[y:y+h, :x] = 0
    ROIp[y:y+h, x+w:] = 0

    if contours == ():
        return ROIp*0

    centerx, centery = ww//2, hh//2
    if not center_in_array(centerx, centery, cnt):
        return ROIp*0
    try:
        if x == 0 or y == 0 or x+w == ww or y+h == hh:
            if x == 0:
                xx = xx-round(ww*0.1)
            elif x+w == ww:
                xx = xx+round(ww*0.1)
            if y == 0:
                yy = yy-round(hh*0.1)
            elif y+h == hh:
                yy = yy+round(hh*0.1)

            ROIp = check(xx, yy, ww, hh, warped)
    except:
        None

    return ROIp

# **********

# call from utils


def img_str(img_obj):
    """from sudoku django.core.files.uploadedfile.InMemoryUploadedFile object
 -> string of 81 characters with zeros as empty places """
    try:
        original = cv2.imdecode(np.fromstring(
            img_obj.file.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
        # print('imnty', type(img_obj))

        img_gray = original.copy()

        size_y, size_x = img_gray.shape
        if size_y > 500 and size_x > 500:
            ratio = size_x/size_y
            size_x = 500
            size_y = int(size_x//ratio)
            img_gray = cv2.resize(img_gray, (size_x, size_y))

        blur = cv2.GaussianBlur(img_gray, (0, 0), sigmaX=33, sigmaY=33)
        contrast = cv2.divide(img_gray, blur, scale=255)

        inverted = cv2.bitwise_not(contrast)

        thresh = cv2.threshold(inverted, 10, 255, cv2.THRESH_OTSU)[1]

        contours, _ = cv2.findContours(
            image=thresh, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_NONE)

        valid = maxarea_contour(contours)

        mask = thresh.copy()*0  # black mask
        cnt = cv2.convexHull(valid)
        rect = cv2.minAreaRect(np.array(cnt))
        H = rect[1][0]

        cv2.drawContours(image=mask, contours=(cnt,), contourIdx=-1, color=(255, 255, 255), thickness=2,
                         lineType=cv2.LINE_AA)  # mask + only contour

        lines = cv2.HoughLinesP(mask, rho=1, theta=np.pi/180, threshold=100,
                                minLineLength=H*0.9, maxLineGap=0)

        arr = lines[:, 0]  # array of [line array]s
        coord = []
        for line in arr:
            # points [x,y] in coord
            coord += [line[:2].tolist()]+[line[2:].tolist()]

        coord = sorted(coord, key=lambda ar: ar[1])  # sort wrt 'y' value
        bottom = sorted(coord[:(len(coord)//2)],
                        key=lambda ar: ar[0])  # points from origin to 'y'/2
        top = sorted(coord[(len(coord)//2):],
                     key=lambda ar: ar[0])  # points from 'y'/2  to y
        _, fullx = mask.shape
        # remove any high 'y' valued coords
        bottom = cleanbottom(bottom, fullx)
        top = cleantop(top, fullx)  # remove any low 'y' valued coords

        p0 = bottom[0]  # 4 corner points , hopefully !
        p1 = bottom[-1]
        p3 = top[0]
        p2 = top[-1]

        # pass 4 corner points for prespective transform
        src = np.array([p0, p1, p2, p3], np.float32)
        length = round(
            pow(((p0[0]-p2[0])*(p0[0]-p2[0])+(p0[-1]-p2[-1])*(p0[-1]-p2[-1])), 1/2))

        # desired corners of warped image
        dst = np.array(
            [[0, 0], [length, 0], [length, length], [0, length]], np.float32)

        M = cv2.getPerspectiveTransform(src, dst)
        warped = cv2.warpPerspective(thresh, M, (length, length))
        warped = cv2.threshold(warped, 10, 255, cv2.THRESH_BINARY)[1]
        cv2.imwrite('E:\dev\sudoku\media\warped.png', warped)
        

        # **********

        # **********

        x, y = (0, 0)
        h, w = warped.shape
        l_x = w//9  # single cell length along x , y direction
        l_y = h//9
        required81 = []

        for r in range(9):
            for c in range(9):
                xx, yy, ww, hh = (x+(l_x*c), y+(l_y*r), l_x, l_y)

                piece = check(xx, yy, ww, hh, warped)
        #         cv2.imshow('pi', piece)
        #         cv2.waitKey(0)

                kernel = np.ones((2, 1), np.uint8)
                eroded = cv2.erode(piece, kernel, iterations=1)

                # text = pytesseract.image_to_string( #version >5.0
                #     eroded, config='--psm 10 --oem 3 -c tessedit_char_whitelist=123456789')
                text = pytesseract.image_to_string(  # version <=4.0
                    eroded, config='--psm 10 --oem 0 -c tessedit_char_whitelist=123456789')
                text = text.strip()
                # print(text)
                num = int(text) if text.isnumeric() else '0'

                required81 += [num]
    except Exception as E:
        print(E)
        required81 = list(
            'ONLY00000CAPTURE00SUDOKU---BLOCK00INIMAGE0TO0BE0000000UPLOADED.ENTER0000MANUALLY!')

    return required81
