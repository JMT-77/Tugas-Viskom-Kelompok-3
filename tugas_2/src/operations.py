import cv2

def read(path):
    image=cv2.imread(str(path),cv2.IMREAD_COLOR)
    if image is None: raise ValueError(f"Cannot read image: {path}")
    return image

def write(path,image):
    if not cv2.imwrite(str(path),image): raise IOError(f"Cannot write image: {path}")

def mirror(image,direction):
    if direction not in ('horizontal','vertical'): raise ValueError("direction must be horizontal or vertical")
    return cv2.flip(image,1 if direction=='horizontal' else 0)

def rotate(image,angle):
    return {90:cv2.rotate(image,cv2.ROTATE_90_CLOCKWISE),180:cv2.rotate(image,cv2.ROTATE_180),270:cv2.rotate(image,cv2.ROTATE_90_COUNTERCLOCKWISE)}[angle]

def edge(image,low,high,blur):
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY); gray=cv2.GaussianBlur(gray,(blur,blur),0); return cv2.Canny(gray,low,high)

def denoise(image,method,kernel):
    if kernel<3 or kernel%2==0: raise ValueError("kernel must be an odd integer >= 3")
    return {'gaussian':lambda:cv2.GaussianBlur(image,(kernel,kernel),0),'median':lambda:cv2.medianBlur(image,kernel),'bilateral':lambda:cv2.bilateralFilter(image,9,75,75)}[method]()
